import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from dialoguekit.core import Annotation

from ada.core.dialogue_act import AnnotationList
from ada.core.span import Span
from ada.core.span_annotation import SpanAnnotation
from ada.domain.article import ScoredArticle
from ada.event.event_handling_mixin import EventHandlingMixin


class TopicSuggest(EventHandlingMixin, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def handle_request_suggestions(
        self, data: Dict[str, Any]
    ) -> AnnotationList:
        phrases: List[SpanAnnotation] = asyncio.run(
            self.get_topics_from_text(
                f"My current preferences are: {', '.join(d['value'] for d in data['topics'])}"
            )
        )
        return AnnotationList(
            Annotation("topic", " ".join(span.text.strip().split()))
            for span in self.get_topic_suggestions(
                included_topics=phrases, documents=data["recommendations"]
            )
        )

    @abstractmethod
    def get_topic_suggestions(
        self,
        included_topics: List[Span],
        documents: List[ScoredArticle],
        excluded_topics: Optional[List[Span]] = None,
        k_suggestions: Optional[int] = 3,
    ) -> List[Span]:
        raise NotImplementedError

    @abstractmethod
    def get_topics_from_text(self, text: str) -> List[Span]:
        raise NotImplementedError
