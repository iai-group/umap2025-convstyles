from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Dict

from ada.core.dialogue_act import AnnotationList
from ada.event.events import Event
from ada.external.article_recommender.ranking import Ranking


@dataclass
class RequestResourceEvent(Event, ABC):
    return_class = None
    data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def get_snake_case_name(cls) -> str:
        return "request_resource"


@dataclass
class RequestRecommendationsEvent(RequestResourceEvent):
    return_class = Ranking

    @classmethod
    def get_snake_case_name(cls) -> str:
        return "request_recommendations"


@dataclass
class RequestSuggestionsEvent(RequestResourceEvent):
    return_class = AnnotationList

    @classmethod
    def get_snake_case_name(cls) -> str:
        return "request_suggestions"
