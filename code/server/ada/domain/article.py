from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Article:
    """Representation of an item."""

    item_id: str
    title: Optional[str] = None
    abstract: Optional[str] = None
    journal: Optional[str] = None
    authors: Optional[List[str]] = None


@dataclass
class ScoredArticle(Article):
    """Representation of a scored item."""

    raw_text: str = None
    score: float = 0.0
    explanation: Optional[str] = None
