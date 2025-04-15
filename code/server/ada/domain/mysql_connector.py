from collections import defaultdict
from typing import Dict, List, Tuple

import mysql.connector
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor

from ada.config import Config
from ada.domain.article import Article


class MySQLConnector:
    def __init__(
        self,
        host: str = None,
        user: str = None,
        password: str = None,
        database: str = None,
    ):
        self.sql_config = Config().sql
        host = host or self.sql_config.host
        user = user or self.sql_config.user
        password = password or self.sql_config.password
        database = database or self.sql_config.database
        self.conn: MySQLConnection = mysql.connector.connect(
            host=host, user=user, password=password, database=database
        )
        self.cursor: MySQLCursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def get_article_by_id(self, article_id: str) -> Article:
        query = (
            "SELECT title,abstract,journal FROM articles WHERE article_id = %s"
        )
        self.cursor.execute(query, (article_id,))
        title, abstract, journal = self.cursor.fetchone()
        authors = self._get_article_authors(article_id)
        return Article(
            item_id=article_id,
            title=title,
            abstract=abstract,
            journal=journal,
            authors=authors,
        )

    def get_articles_by_ids(self, article_ids: List[str]) -> List[Article]:
        if len(article_ids) == 0:
            return []

        authors_by_article = self._get_authors_by_article_ids(article_ids)

        format_strings = ",".join(["%s"] * len(article_ids))
        query = f"SELECT title, abstract, journal, article_id FROM articles WHERE article_id IN ({format_strings})"
        self.cursor.execute(query, tuple(article_ids))

        articles = []
        for title, abstract, journal, article_id in self.cursor.fetchall():
            articles.append(
                Article(
                    item_id=article_id,
                    title=title,
                    abstract=abstract,
                    journal=journal,
                    authors=authors_by_article.get(article_id, []),
                )
            )

        return articles

    def _get_article_authors(self, article_id: str) -> List[Tuple[str]]:
        query = "SELECT firstname, lastname FROM article_authors WHERE article_id = %s"
        self.cursor.execute(query, (article_id,))
        result = self.cursor.fetchall()
        return [f"{firstname} {lastname}" for firstname, lastname in result]

    def _get_authors_by_article_ids(
        self, article_ids: List[str]
    ) -> Dict[str, List[str]]:
        format_strings = ",".join(["%s"] * len(article_ids))
        query = f"SELECT firstname, lastname, article_id FROM article_authors WHERE article_id IN ({format_strings})"
        self.cursor.execute(query, tuple(article_ids))

        authors_by_article = defaultdict(list)
        for firstname, lastname, article_id in self.cursor.fetchall():
            author = f"{firstname} {lastname}"
            authors_by_article[article_id].append(author)

        return authors_by_article

    def close(self) -> None:
        self.cursor.close()
        self.conn.close()
