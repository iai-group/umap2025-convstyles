from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ada.event.event_handling_mixin import EventHandlingMixin
from ada.external.article_recommender.ranking import Ranking


class Recommender(ABC, EventHandlingMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def handle_request_recommendations(
        self,
        data: Dict[str, Any],
        **kwargs,
    ) -> Ranking:
        include_topics = [topic["value"] for topic in data.get("topics", [])]
        exclude_topics = [
            topic["value"] for topic in data.get("excluded_topics", [])
        ]
        return self.recommend(include_topics, exclude_topics, **kwargs)

    @abstractmethod
    def recommend(
        self,
        include_topics: List[str],
        exclude_topics: Optional[List[str]] = None,
        **kwargs,
    ) -> Ranking:
        raise NotImplementedError
