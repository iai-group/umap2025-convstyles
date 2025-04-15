from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, List, Optional

from dialoguekit.core import Annotation
from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.dialogue_manager.dialogue_state import DialogueState

from ada.core.dialogue_act import AnnotationList, DialogueAct
from ada.core.types import Action
from ada.domain.article import Article, ScoredArticle
from ada.external.article_recommender.ranking import Ranking


class DeepCopyBase:
    def __getattribute__(self, name: str) -> Any:
        value = super().__getattribute__(name)
        if isinstance(value, DeepCopyBase) or (
            name not in super().__getattribute__("__dict__")
        ):
            return value
        return deepcopy(value)

    def __setattr__(self, name: str, value: Any) -> None:
        if isinstance(value, DeepCopyBase):
            super().__setattr__(name, value)
        super().__setattr__(name, deepcopy(value))


@dataclass
class TopicPreferences(DeepCopyBase):
    topics: AnnotationList = field(default_factory=AnnotationList)
    excluded_topics: AnnotationList = field(default_factory=AnnotationList)

    def reset(self) -> None:
        setattr(self, "topics", AnnotationList())
        setattr(self, "excluded_topics", AnnotationList())


@dataclass
class Recommendation(DeepCopyBase):
    recommendation: Ranking = field(default_factory=Ranking)
    previous_recommendation: Ranking = field(default_factory=Ranking)

    def __len__(self) -> int:
        return len(self.recommendation)

    def set_recommendation(self, recommendation: Ranking) -> None:
        setattr(self, "previous_recommendation", self.recommendation)
        setattr(self, "recommendation", recommendation)

    def get_overlap(self) -> float:
        recommended_items = set(self.recommendation.get_item_ids())
        previously_recommended_items = set(
            self.previous_recommendation.get_item_ids()
        )
        return len(recommended_items & previously_recommended_items) / len(
            recommended_items
        )

    def get_recommended_articles(self) -> List[ScoredArticle]:
        return self.recommendation.fetch_topk_docs(10)


@dataclass
class UpdateFlags(DeepCopyBase):
    is_start: bool = False
    updated_preferences: bool = False
    confirmation_required: bool = False
    confirmation_received: bool = False
    new_recommendations: bool = False
    agent_should_respond: bool = False
    style_changed: bool = False
    should_reset_options: bool = False
    new_discussion_topics: bool = False
    new_topic_suggestions: bool = False
    has_preferences: bool = False

    def update(self, state: AdaDialogueState) -> None:
        self.new_discussion_topics: bool = len(state.discussion_topics) > 0
        self.new_topic_suggestions: bool = len(state.topic_suggestions) > 0
        self.has_preferences: bool = len(state.topic_preferences.topics) > 0

    def reset(self) -> None:
        setattr(self, "style_changed", False)
        setattr(self, "updated_preferences", False)
        setattr(self, "confirmation_received", False)
        setattr(self, "agent_should_respond", False)
        setattr(self, "should_reset_options", False)


@dataclass
class AdaDialogueState(DialogueState, DeepCopyBase):
    """Dialogue state."""

    history: List[AnnotatedUtterance] = field(default_factory=list)
    user_actions: List[Action] = field(default_factory=list)
    system_actions: List[Action] = field(default_factory=list)

    topic_preferences: TopicPreferences = field(
        default_factory=TopicPreferences
    )
    topic_suggestions: AnnotationList = field(default_factory=AnnotationList)
    suggested_topics: AnnotationList = field(default_factory=AnnotationList)
    discussion_topics: Optional[AnnotationList] = field(
        default_factory=AnnotationList
    )
    explained_topics: AnnotationList = field(default_factory=AnnotationList)
    recommendation: Recommendation = field(default_factory=Recommendation)
    recommendation_item_in_focus: Optional[ScoredArticle] = None
    bookmarks: List[Article] = field(default_factory=list)
    options: List[DialogueAct] = field(default_factory=list)

    style: Annotation = Annotation("style", "default")
    turn_count: int = 0

    flags: Optional[UpdateFlags] = field(default_factory=UpdateFlags)
