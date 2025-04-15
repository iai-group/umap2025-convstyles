"""User model."""

import os
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set

from ada.core.dialogue_act import Action
from ada.core.span import Span
from ada.core.span_annotation import SpanAnnotation
from ada.domain.mysql_connector import MySQLConnector
from ada.event.event_handling_mixin import EventHandlingMixin
from ada.external.user_model.user_model import UserModel

USER_MODEL_BASE_PATH = "data/user_model/"


@dataclass
class TopicPreferences:
    included_topics: List[Span] = field(default_factory=list)
    excluded_topics: List[Span] = field(default_factory=list)


class AdaUserModel(UserModel, EventHandlingMixin):
    def __init__(
        self,
        user_id: str,
        **kwargs,
    ) -> None:
        """User model.

        Args:
            user_id: User ID.
        """
        # self.get_article_detail = get_article_detail
        # self._user_knowledge: UserKnowledge = UserKnowledge()
        self._user_preferences: TopicPreferences = TopicPreferences()
        self._last_user_preferences: List[str] = (
            []
        )  # TODO: Move to dialogue state
        self._saved_articles: Set[str] = set()
        self._new_user = True
        self._user_model_path = os.path.join(
            USER_MODEL_BASE_PATH, f"{user_id}.json"
        )
        # if self._verify_user_data_path():
        #     self._new_user = False
        #     self.load_user_model()
        super().__init__(user_id=user_id, **kwargs)

    @property
    def new_user(self) -> bool:
        return self._new_user

    def get_topic_preferences(self) -> Dict[str, Set[str]]:
        return asdict(self._user_preferences)

    # def get_topic_preferences_nl(self) -> str:
    #     """Gets the users positive and negative topic preferences.

    #     Returns:
    #         Tuple of included and excluded topics.
    #     """
    #     included_topics, excluded_topics = self.get_topic_preferences()
    #     inc_topics = list(included_topics)
    #     exc_topics = list(excluded_topics)

    #     if len(inc_topics) > 1:
    #         inc_topics[-1] = "and " + inc_topics[-1]
    #     if len(exc_topics) > 1:
    #         exc_topics[-1] = "and " + exc_topics[-1]

    #     return ", ".join(inc_topics) + (
    #         (", " if inc_topics else "") + "excluding " + ", ".join(exc_topics)
    #         if exc_topics
    #         else ""
    #     )

    def handle_request_user_preferences(
        self, action: Action
    ) -> Dict[str, Set[str]]:
        return UserPreferencesResource(payload=self.get_topic_preferences())

    def user_has_positive_preferences(self) -> bool:
        return len(self._user_preferences.included_topics) > 0

    def get_last_topic_preferences_nl(self) -> str:
        """Gets the users positive and negative topic preferences.

        Returns:
            Tuple of included and excluded topics.
        """
        if len(self._last_user_preferences) > 1:
            last_topic = self._last_user_preferences.pop()
            self._last_user_preferences[-1] += f" and {last_topic}"
        return ", ".join(self._last_user_preferences)

    def get_topic_preferences_nl(self) -> Optional[str]:
        """Gets the users positive and negative topic preferences.

        Returns:
            Tuple of included and excluded topics.
        """
        if not self.user_has_positive_preferences():
            return None

        inc_topics, exc_topics = self.get_topic_preferences_text()
        if len(inc_topics) > 1:
            last_inc_topic = inc_topics.pop()
            inc_topics[-1] += f" and {last_inc_topic}"
        if len(exc_topics) > 1:
            last_exc_topic = exc_topics.pop()
            exc_topics[-1] += f" and {last_exc_topic}"

        inc_topics = ", ".join(inc_topics)
        if not exc_topics:
            return inc_topics

        return inc_topics + ", excluding " + ", ".join(exc_topics)

    def update_preferences_for_topic(
        self, annotation: List[SpanAnnotation]
    ) -> None:
        """Updates the user preferences for a topic.

        Args:
            topic: Topic.
            value: Feedback value.
        """
        self._last_user_preferences = []
        for a in annotation:
            self.update_preference_for_topic(a)

    def update_preference_for_topic(self, annotation: SpanAnnotation) -> None:
        """Updates the user preferences for a topic.

        Args:
            topic: Topic.
            value: Feedback value.
        """
        inc_topics, exc_topics = self.get_topic_preferences_text()
        if annotation.slot == "topic":
            self._user_preferences.included_topics.append(annotation.value)
            self._last_user_preferences.append(
                f"adding {annotation.value.text}"
            )
        elif annotation.slot == "exclude_topic":
            if annotation.value.text in inc_topics:
                self._user_preferences.included_topics = [
                    topic
                    for topic in self._user_preferences.included_topics
                    if topic.text != annotation.value.text
                ]
                self._last_user_preferences.append(
                    f"removing {annotation.value.text}"
                )
            elif annotation.value.text in exc_topics:
                self._user_preferences.excluded_topics = [
                    topic
                    for topic in self._user_preferences.excluded_topics
                    if topic.text != annotation.value.text
                ]
                self._last_user_preferences.append(
                    f"removing exclude {annotation.value.text}"
                )
            else:
                self._user_preferences.excluded_topics.append(annotation.value)
                self._last_user_preferences.append(
                    f"excluding {annotation.value.text}"
                )

    def reset_preferences(self) -> None:
        """Resets the user preferences."""
        self._user_preferences = TopicPreferences()

    def bookmark_item(self, item_id: str) -> None:
        """Bookmarks an item.

        Args:
            item_id: Item ID.
        """
        self._saved_articles.append(item_id)

    def remove_bookmark(self, item_id: str) -> None:
        """Removes a bookmark.

        Args:
            item_id: Item ID.
        """
        self._saved_articles.remove(item_id)

    def get_bookmarks(self) -> List[dict[str, Any]]:
        """Returns the user's bookmarks.

        Returns:
            List of item IDs.
        """
        with MySQLConnector() as db:
            return [
                asdict(article)
                for article in db.get_articles_by_ids(
                    list(self._saved_articles)
                )
            ]

    def _verify_user_data_path(self) -> bool:
        """Verifies the user."""
        if not os.path.exists(USER_MODEL_BASE_PATH):
            os.makedirs(USER_MODEL_BASE_PATH)

        if os.path.isfile(self._user_model_path):
            return True
        return False
