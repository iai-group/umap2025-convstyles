"""Represents a ranked list of items.
"""

from __future__ import annotations

from dataclasses import asdict
from operator import attrgetter
from typing import List

from ada.domain.article import ScoredArticle
from ada.domain.mysql_connector import MySQLConnector


class Ranking:
    def __init__(
        self, query_id: str = None, scored_docs: List[ScoredArticle] = None
    ) -> None:
        """Instantiates a Ranking object using the query_id and a list of scored
        documents.

        Documents are stored unordered; sorting is done when fetching them.

        Args:
            query_id: Unique id for the query.
            scored_docs: List of scored documents. Not necessarily sorted.
        """
        self._query_id = query_id
        self._scored_docs = scored_docs or []

    def __len__(self):
        return len(self._scored_docs)

    @property
    def query_id(self) -> str:
        return self._query_id

    def get_item_ids(self) -> List[str]:
        """Returns documents and their contents.

        Returns:
            Two parallel lists, containing document IDs and their content.
        """
        return [doc.item_id for doc in self._scored_docs]

    def get_doc_by_id(self, doc_id: str) -> ScoredArticle:
        """Returns a document by its ID.

        Args:
            doc_id: The ID of the document.

        Returns:
            The document with the given ID.
        """
        return next(doc for doc in self._scored_docs if doc.item_id == doc_id)

    def add_doc(self, doc: ScoredArticle) -> None:
        """Adds a new document to the ranking.

        Note: it doesn't check whether the document is already present.

        Args:
            doc: A scored document.
        """
        self._scored_docs.append(doc)

    def add_docs(self, docs: List[ScoredArticle]) -> None:
        """Adds multiple documents to the ranking.

        Note: it doesn't check whether the document is already present.

        Args:
            docs: List of scored documents.
        """
        self._scored_docs.extend(docs)

    def update(self, docs: List[ScoredArticle]) -> None:
        """Adds multiple documents to the ranking uniquely.

        Args:
            docs: List of scored documents.
        """
        doc_ids = set(self.item_ids())
        self._scored_docs.extend(
            [doc for doc in docs if doc.item_id not in doc_ids]
        )

    def populated_docs(self, docs: List[ScoredArticle]) -> List[ScoredArticle]:
        """Returns a list of populated documents.

        Args:
            docs: List of scored documents.

        Returns:
            List of populated documents.
        """
        with MySQLConnector() as db:
            articles = db.get_articles_by_ids([doc.item_id for doc in docs])
            articles_dict = {
                article.item_id: asdict(article) for article in articles
            }
        return [
            ScoredArticle(
                **{**asdict(doc), **articles_dict.get(doc.item_id, {})}
            )
            for doc in docs
        ]

    def fetch_topk_docs(
        self, k: int = 1000, unique: bool = False
    ) -> List[ScoredArticle]:
        """Fetches the top-k docs based on their score.

            If k > len(self._scored_docs), the slicing automatically
            returns all elements in the list in sorted order.
            Returns an empty array if there are no documents in the ranking.

        Args:
            k: Number of docs to fetch.
            unique: If unique is True returns unique unique documents. In case
                of multiple documents with the same ID, returns the highest
                scoring. Defaults to False

        Returns:
            Ordered list of scored documents.
        """
        sorted_docs = sorted(self._scored_docs, key=attrgetter("score"))
        if unique:
            sorted_unique_docs = {doc.item_id: doc for doc in sorted_docs}
            sorted_docs = list(sorted_unique_docs.values())

        top_k = sorted_docs[: -k - 1 : -1]
        return self.populated_docs(top_k)

    def fetch_topk_ranking(
        self, k: int = 1000, unique: bool = False
    ) -> Ranking:
        docs = self.fetch_topk_docs(k, unique)
        return Ranking(self.query_id, docs)
