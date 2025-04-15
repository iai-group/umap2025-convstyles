"""BM25 retrieval using ElasticSearch."""

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional

from elasticsearch.client import Elasticsearch

from ada.config import Config
from ada.domain.article import ScoredArticle
from ada.external.article_recommender.ranking import Ranking
from ada.external.article_recommender.recommender import Recommender

_ESquery = Dict[str, Any]
logger = logging.getLogger(__name__)
es_logger = logging.getLogger("elasticsearch")
es_logger.setLevel(logging.INFO)


class BM25Recommender(Recommender):
    def __init__(
        self,
        index: str = None,
        host: str = None,
        field: str = None,
        **kwargs,
    ) -> None:
        """Initializes an Elasticsearch instance on a given host.

        Args:
            index_name: Index name.
            hostname: Host name and port (defaults to
                "localhost:9200").
            **kwargs: Additional keyword arguments to be provided to the
                Elasticsearch instance.
        """
        config = Config().es
        self._index_name = index or config.index
        self._field = field or config.field
        self._es = Elasticsearch(host or config.host, debug=False)
        super().__init__(**kwargs)

    def recommend(
        self,
        include_topics: List[str],
        exclude_topics: Optional[List[str]] = None,
        n_topics_explanation=3,
        query_id: str = "0",
    ) -> Ranking:
        """Makes recommendations based on list of topics and returns a list of
        articles. The score of each article is calculated as the sum of the
        score of each topics, and the explanation is contains all topics that
        matched an article.
        'n_topics_explanation' is how many of the top topics that will be
        included in the explanation."""
        articles = defaultdict(list)
        for topic in include_topics:
            query = self._get_articles_by_topic_query(topic)
            include_topic_search = self._retrieve(query)
            for article in include_topic_search:
                articles[article.item_id].append((article.score, topic))

        # TODO search for articles that mention any of the exclude topics
        exclude_topics = exclude_topics or []
        for topic in exclude_topics:
            query = self.filter_query(topic, list(articles.keys()))
            exclude_topic_search = self._retrieve(query)
            for article in exclude_topic_search:
                articles[article.item_id].append((-article.score, topic))
                assert len(articles[article.item_id]) > 1

        result = []
        for article_id, score_topic_list in articles.items():
            sorted_topics = [topic for _, topic in sorted(score_topic_list)]

            explanation = self._create_explanation(
                sorted_topics[:n_topics_explanation]
            )
            result.append(
                ScoredArticle(
                    item_id=article_id,
                    score=sum(score for score, _ in score_topic_list),
                    explanation=explanation,
                )
            )
        return Ranking(query_id, result)

    def recommend_by_query(self, query_id: str, query: str) -> Ranking:
        """Makes recommendations based on a query and returns a list of
        articles.

        Args:
            query_id: Query ID.
            query: Query.

        Returns:
            Ranking of articles.
        """

        es_query = self.match_query(query)
        search = self._retrieve(es_query)
        result = [
            ScoredArticle(
                item_id=article.item_id,
                score=article.score,
            )
            for article in search
        ]
        return Ranking(query_id, result)

    def _retrieve(
        self, query: Optional[_ESquery] = None, num_results: int = 100
    ) -> List[ScoredArticle]:
        """Performs retrieval for elastic search query.

        Args:
            query: Elasticsearch query.
            num_results: Number of documents to return.
            source: Weather to include document content in the return set.

        Returns:
            List of scored documents.
        """
        res = self._es.search(
            body={"query": query},
            index=self._index_name,
            _source=False,
            size=num_results,
        )

        return [
            ScoredArticle(
                item_id=hit["_id"],
                score=hit["_score"],
            )
            for hit in res["hits"]["hits"]
        ]

    def match_query(self, query: str, weight: float = 1.0) -> _ESquery:
        """Simple elasticsearch match query.

        Args:
            query: Full query to use for retrieval.
            weight: Weight for scaling the scores.

        Returns:
            Elasticsearch query.
        """
        return {"match": {self._field: {"query": query, "boost": weight}}}

    def _term_query(self, term: str, weight: float = 1.0) -> _ESquery:
        """Sub-query for a single term to be used as part of a larger query.

        Args:
            term: Single term to add to the query.
            weight: Weight for scaling the term (Defaults to 1.0).

        Returns:
            Partial elasticsearch query.
        """
        return {"term": {self._field: {"value": term, "boost": weight}}}

    def _phrase_query(self, phrase: str, weight: float = 1.0) -> _ESquery:
        """Sub-query for a single phrase to be used as part of a larger query.

        Args:
            phrase: Phrase to add to the query.
            weight: Weight for scaling the phrase (Defaults to 1.0).

        Returns:
            Partial elasticsearch query.
        """
        return {
            "match_phrase": {self._field: {"query": phrase, "boost": weight}}
        }

    def bool_query(
        self,
        weighted_terms: Dict[str, float],
        weighted_phrases: Dict[str, float] = None,
        weighted_match_queries: Dict[str, float] = None,
    ) -> _ESquery:
        """Query that computes the scores of each term or phrase individually.

        Args:
            weighted_terms: Dictionary of terms with weights as key-value pair.
            weighted_phrases: Dictionary of phrases with weights as key-value
              pair (Defaults to None).
            weighted_match_queries: Dictionary of match queries with weights as
              key-value pair.

        Returns:
            Elasticsearch query to return documents based on the aggregated
              scores.
        """
        return {
            "bool": {
                "should": [
                    *[
                        self._term_query(term, weight)
                        for term, weight in (weighted_terms or {}).items()
                    ],
                    *[
                        self._phrase_query(phrase, weight)
                        for phrase, weight in (weighted_phrases or {}).items()
                    ],
                    *[
                        self.match_query(match, weight)
                        for match, weight in (
                            weighted_match_queries or {}
                        ).items()
                    ],
                ]
            }
        }

    def filter_query(self, phrase: str, item_ids: List[str]) -> _ESquery:
        """Query that filters out documents that do not match the item_ids.

        Args:
            phrase: Phrase to add to the query.
            item_ids: List of item_ids to filter on.

        Returns:
            Elasticsearch query to return documents that match the item_ids.
        """
        return {
            "bool": {
                "must": [
                    self._phrase_query(phrase),
                ],
                "filter": {"ids": {"values": item_ids}},
            }
        }

    def _get_articles_by_topic_query(self, topic: str) -> _ESquery:
        """Retrieves articles from the Elasticsearch index mentioning 'topic',
        the 'window_size' is the number of days back in time articles will
        be included from.
        """
        return {
            "bool": {
                "should": {  # must?
                    "match": {
                        self._field: {
                            "query": topic,
                        }
                    }
                },
            }
        }

    def _add_date_constraint(
        self, es_query: Dict[str, Any], window_size: int = 7
    ) -> _ESquery:
        es_query["bool"]["filter"] = {
            "range": {"date": {"gte": "now-{}d".format(window_size)}}
        }
        return es_query

    def _create_explanation(self, topics):
        """ "Creates explanation from topics."""
        topics = ["**{}**".format(topic) for topic in topics]
        last = topics.pop()
        topic_str = ", ".join(topics)
        topic_str += " and " + last if topic_str else last
        explanation = "This article seems to be about {}.".format(topic_str)
        return explanation


if __name__ == "__main__":
    recommender = BM25Recommender(
        event_bus=None,
    )
    ranking = recommender.recommend(["covid-19"])
    print(ranking.fetch_topk_docs(5))
