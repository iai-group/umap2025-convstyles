import asyncio
from collections import Counter
from dataclasses import asdict
from typing import List, Optional

import numpy as np

from ada.agent.nlu.annotators.jointbert_annotator import JointBERTAnnotator
from ada.config import Config
from ada.core.span import Span
from ada.core.span_annotation import SpanAnnotation
from ada.domain.article import ScoredArticle
from ada.external.topic_suggestions.topic_suggestions import TopicSuggest

_MODEL_PATH = "models/joint_bert_extended_topics"


class JointBertTopicSuggest(TopicSuggest):
    def __init__(self, n_topics: int = 3, **kwargs) -> None:
        """Initializes the NLU module."""
        self._model = JointBERTAnnotator(
            Config().topic_suggestor.model_path or _MODEL_PATH
        )
        self._n_topics = n_topics
        super().__init__(**kwargs)

    def get_topic_suggestions(
        self,
        included_topics: List[Span],
        documents: List[ScoredArticle],
        excluded_topics: Optional[List[Span]] = None,
        k_suggestions: Optional[int] = 3,
    ) -> List[Span]:
        """Gets the topic suggestions for the given text.

        Args:
            text: The text to get the topic suggestions for.

        Returns:
            The topic suggestions.
        """
        query_topic_words = {
            word.strip()
            for query_topic in included_topics + (excluded_topics or [])
            for word in query_topic.lemma.split()
        }
        document_topics = asyncio.run(
            self.get_topics_from_texts(
                f"{doc.title}. {doc.abstract}" for doc in documents
            )
        )

        new_document_topics: List[Span] = []
        lemmas = set()
        for topic in document_topics:
            words = set(el.strip() for el in topic.lemma.split())
            if words.issubset(query_topic_words) or len(words) > 6:
                continue
            if topic.lemma in lemmas:
                continue
            new_document_topics.append(topic)
            lemmas.add(topic.lemma)

        # TODO Is there a better way? score based on each topic separately and
        # then add up scores?
        included_topics_embbeding = np.mean(
            [topic.get_embedding() for topic in included_topics], axis=0
        )
        embeddings = np.array(
            [topic.get_embedding() for topic in new_document_topics]
        )
        distances = np.argsort(
            np.linalg.norm(embeddings - included_topics_embbeding, axis=1)
        )

        return [
            new_document_topics[index] for index in distances[:k_suggestions]
        ]

    async def get_topics_from_text(self, text: str) -> List[Span]:
        """Gets the topics from the text.

        Args:
            text: The text to get the topics from.

        Returns:
            The topics.
        """
        keyphrases: List[SpanAnnotation] = self._model.annotate_text(text)
        return [keyphrase.value for keyphrase in keyphrases]

    async def get_topics_from_texts(self, texts: List[str]) -> List[Span]:
        """Gets the topics from the texts.

        Args:
            texts: The texts to get the topics from.

        Returns:
            The topics.
        """
        return [
            topic
            for topics in await asyncio.gather(
                *(self.get_topics_from_text(text) for text in texts)
            )
            for topic in topics
        ]


if __name__ == "__main__":
    from ada.external.article_recommender.bm25_recommender import (
        BM25Recommender,
    )

    config = Config().es
    suggestor = TopicSuggest()
    recommender = BM25Recommender(
        **asdict(config),
        event_bus=None,
    )

    while True:
        query = input("\nEnter text: ")
        # query = "conversational search"
        # query = "I am interested in implicit preference elicitation in conversational search and recommendation by asking goal-oriented questions"
        print()
        if len(query) == 0:
            print("Please enter a query.")
            continue
        if query == "exit":
            break
        included_topics = asyncio.run(suggestor.get_topics_from_text(query))
        if not included_topics:
            print("No topics found.")
            continue

        print("Included topics:")
        for topic in included_topics:
            print(topic.text)
        recommendations = recommender.recommend(
            [topic.text for topic in included_topics]
        ).fetch_topk_docs(10)
        print()
        suggestions = suggestor.get_topic_suggestions(
            included_topics, documents=recommendations
        )
        for sug in suggestions:
            print(sug.text)
