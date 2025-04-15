from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, List, Optional, Union

import numpy as np


@dataclass
class Span:
    """Span represents a token, a word or a phrase in a sentence."""

    text: str
    source_text: str = ""
    start: int = 0
    end: Optional[int] = None
    tokens: Optional[List[Span]] = None
    embedding: Optional[np.ndarray] = None
    lemma: Optional[str] = None
    vector: Optional[np.ndarray] = None

    def get_embedding(self, aggregation="avg") -> np.ndarray:
        if self.embedding is not None:
            return self.embedding

        valid_embeddings = [
            token.embedding
            for token in self.tokens
            if token.embedding is not None
        ]

        if not valid_embeddings:
            return None

        if aggregation == "avg":
            self.embedding = np.mean(valid_embeddings, axis=0)
        elif aggregation == "sum":
            self.embedding = np.sum(valid_embeddings, axis=0)
        elif aggregation == "first":
            self.embedding = valid_embeddings[0]

        return self.embedding

    def __post_init__(self):
        if self.end is None:
            self.end = self.start + len(self.text)
        if self.tokens is None:
            self.tokens = [self]
        if self.lemma is None:
            self.lemma = self.text

    def __len__(self):
        return self.end - self.start

    def __add__(self, other: Span) -> Span:
        """Adds two spans together.

        Args:
            other: The other span to add.

        Returns:
            The concatenated span.
        """
        if self.source_text != other.source_text:
            raise ValueError(
                "Cannot concatenate spans from different source texts."
            )

        return Span(
            text=self.source_text[self.start : other.end],
            source_text=self.source_text,
            start=self.start,
            end=other.end,
            tokens=self.tokens + other.tokens,
            lemma=f"{self.lemma} {other.lemma}",
        )

    def __getitem__(self, key: Union[int, slice]) -> Span:
        """Gets a token from the span.

        Args:
            i: The index of the token to get.

        Returns:
            The token.
        """
        if isinstance(key, int):
            return Span(
                self.text[key],
                self.source_text,
                start=key,
            )

        token_start = next(
            (
                i
                for i, token in enumerate(self.tokens)
                if token.start >= key.start
            )
        )
        token_end = (
            next(
                (
                    i
                    for i, token in enumerate(
                        self.tokens[token_start:], token_start
                    )
                    if token.end >= key.stop
                )
            )
            + 1
        )
        return Span(
            self.source_text[key],
            self.source_text,
            start=key.start,
            end=key.stop,
            tokens=self.tokens[token_start:token_end],
            lemma=" ".join(
                token.lemma for token in self.tokens[token_start:token_end]
            ),
        )

    def __iter__(self) -> Iterator[Span]:
        """Iterates over the tokens in the span.

        Returns:
            An iterator over the tokens.
        """
        return iter(self.tokens)

    @classmethod
    def from_spans(cls, spans: List[Span]):
        source_text = spans[0].source_text
        start = spans[0].start
        end = spans[-1].end
        return cls(
            source_text[start:end],
            source_text,
            start,
            end,
            tokens=spans,
            lemma=" ".join(span.lemma for span in spans),
        )
