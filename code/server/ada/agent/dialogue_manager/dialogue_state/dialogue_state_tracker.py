"""Dialogue state tracker."""

from typing import List

from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.dialogue_manager.dialogue_state_tracker import (
    DialogueStateTracker,
)
from dialoguekit.participant import DialogueParticipant

from ada.agent.dialogue_manager.dialogue_state.dialogue_state import (
    AdaDialogueState,
)
from ada.core.dialogue_act import ActionList, AnnotationList, DialogueAct
from ada.core.types import Action
from ada.event.event_handling_mixin import EventHandlingMixin
from ada.external.article_recommender.ranking import Ranking


class AdaDialogueStateTracker(DialogueStateTracker, EventHandlingMixin):
    def __init__(self, **kwargs):
        """Dialogue state tracker."""
        super().__init__(**kwargs)
        self._dialogue_state = AdaDialogueState()

    def reset_dialogue_state(self):
        self._dialogue_state = AdaDialogueState()

    def reset_options(self):
        state: AdaDialogueState = self.get_state()
        if len(state.options) > 0:
            state.flags.should_reset_options = True
            state.options = []

    def update_flags(self) -> None:
        state: AdaDialogueState = self.get_state()
        state.flags.update(state)

    def process_user_actions(self, actions: ActionList) -> None:
        """Updates the dialogue state with the annotated utterance.

        Args:
            annotated_utterance: The annotated utterance.
        """
        state: AdaDialogueState = self.get_state()

        state.user_actions = actions

        state.flags.reset()
        self._handle_actions(actions)
        state.turn_count += 1

    def process_agent_actions(self, actions: ActionList) -> None:
        """Updates the dialogue state with the annotated utterance.

        Args:
            annotated_utterance: The annotated utterance.
        """
        state: AdaDialogueState = self.get_state()

        state.system_actions = actions
        self._handle_actions(actions)

    def _handle_actions(self, actions: List[Action]) -> None:
        state: AdaDialogueState = self.get_state()
        reset_options = False
        for action in actions:
            print("\n\nHandling action")
            print(action)
            print("\n\n")
            if isinstance(action, AnnotatedUtterance):
                state.history += [action]
                if action.participant is DialogueParticipant.USER:
                    state.flags.agent_should_respond = True
                    reset_options = True
                    continue

                # TODO Fix this hack or remove AnnotatedUtterance from the
                # application
                action.annotations = AnnotationList(action.annotations)

            handler = getattr(self, f"_{action.intent}", None)
            if handler:
                handler(action)

        if reset_options:
            self.reset_options()

    # USER ACTIONS
    def _reveal_preference(self, dialogue_act: DialogueAct) -> None:
        state: AdaDialogueState = self.get_state()
        topics = dialogue_act.annotations.get_annotations("topic")
        excluded_topics = dialogue_act.annotations.get_annotations(
            "exclude_topic"
        )

        # TODO A bit sloppy
        if len(topics) > 0:
            state.discussion_topics = topics

        topics_need_explaining = [
            topic
            for topic in state.discussion_topics
            if topic.value not in state.explained_topics.get_values()
        ]

        if (
            state.flags.confirmation_required
            and not state.flags.confirmation_received
            and len(topics_need_explaining) > 0
        ):
            return

        current_topic_values = {
            topic.value for topic in state.topic_preferences.topics
        }
        for topic in topics:
            if topic.value in current_topic_values:
                continue

            state.topic_preferences.topics += [topic]
            state.flags.updated_preferences = True

        current_excluded_topic_values = {
            topic.value for topic in state.topic_preferences.excluded_topics
        }
        for excluded_topic in excluded_topics:
            if excluded_topic.value in current_excluded_topic_values:
                continue
            state.topic_preferences.excluded_topics += [excluded_topic]
            state.flags.updated_preferences = True

    def _remove_preference(self, dialogue_act: DialogueAct) -> None:
        state: AdaDialogueState = self.get_state()
        topics = dialogue_act.annotations.get_annotations("exclude_topic")
        if not topics:
            # TODO handle missing annotations
            return

        current_excluded_topic_values = {
            topic.value for topic in state.topic_preferences.excluded_topics
        }
        current_topic_values = {
            topic.value for topic in state.topic_preferences.topics
        }
        for topic in topics:
            if topic.value in current_excluded_topic_values:
                state.topic_preferences.excluded_topics = [
                    t
                    for t in state.topic_preferences.excluded_topics
                    if t.value != topic.value
                ]
                continue

            if topic.value in current_topic_values:
                state.topic_preferences.topics = [
                    t
                    for t in state.topic_preferences.topics
                    if t.value != topic.value
                ]
                continue

            state.topic_preferences.excluded_topics += [topic]

        state.flags.updated_preferences = True

    def _reset_preferences(self, dialogue_act: DialogueAct) -> None:
        state: AdaDialogueState = self.get_state()
        if (
            state.flags.confirmation_required
            and not state.flags.confirmation_received
        ):
            return

        state.topic_preferences.reset()
        state.flags.updated_preferences = True

        state.topic_suggestions = AnnotationList()
        state.suggested_topics = AnnotationList()

    def _get_keyphrase_explanation(self, dialogue_act: DialogueAct) -> None:
        self._dialogue_state.discussion_topics = (
            dialogue_act.annotations.get_annotations("topic")
        )

    def _select_option(self, dialogue_act: DialogueAct) -> None:
        state: AdaDialogueState = self.get_state()
        option_id = dialogue_act.annotations.get_annotation_value("id")
        # TODO This should be fine, but we could also check explicitly on id
        option_dact: DialogueAct = state.options[int(option_id)]
        self._convert_option_to_action(option_dact)

    def _convert_option_to_action(self, option_dact: DialogueAct) -> None:
        state: AdaDialogueState = self.get_state()
        if option_dact.annotations.get_annotation_value("intent") == "confirm":
            state.flags.confirmation_received = True
        text = option_dact.annotations.get_annotation("text").value
        utterance = AnnotatedUtterance(
            text,
            participant=DialogueParticipant.USER,
        )
        user_actions = [utterance, option_dact]
        self._dialogue_state.user_actions += user_actions
        print("Handling user actions")
        print(f"\t{utterance}")
        print(f"\t{option_dact}")
        print()
        self._handle_actions(user_actions)

    def _add_bookmark(self, dialogue_act: DialogueAct) -> None:
        state: AdaDialogueState = self.get_state()
        article_id = dialogue_act.annotations.get_annotation_value("item_id")
        article = state.recommendation.recommendation.get_doc_by_id(article_id)
        state.bookmarks += [article]

    def _remove_bookmark(self, dialogue_act: DialogueAct) -> None:
        state: AdaDialogueState = self.get_state()
        article_id = dialogue_act.annotations.get_annotation("item_id").value
        state.bookmarks = [
            article
            for article in state.bookmarks
            if article.item_id != article_id
        ]

    def _get_recommendation_explanation(
        self, dialogue_act: DialogueAct
    ) -> None:
        state: AdaDialogueState = self.get_state()
        item_id = dialogue_act.annotations.get_annotation("item_id").value
        article = state.recommendation.recommendation.get_doc_by_id(item_id)
        state.recommendation_item_in_focus = article
        state.flags.agent_should_respond = True
        self.reset_options()

    def _confirm(self, dialogue_act: DialogueAct) -> None:
        option_dact: DialogueAct = next(
            (
                option
                for option in self._dialogue_state.options
                if option.annotations.get_annotation_value("intent")
                == "confirm"
            ),
            None,
        )
        if option_dact:
            self._convert_option_to_action(option_dact)

    def _set_style(self, dialogue_act: DialogueAct) -> None:
        state: AdaDialogueState = self.get_state()
        state.style = dialogue_act.annotations.get_annotation("style")
        state.flags.style_changed = True
        state.flags.confirmation_required = state.style.value == "considerate"

    # SYSTEM ACTIONS
    def _provide_options(self, dialogue_act: DialogueAct) -> None:
        state: AdaDialogueState = self.get_state()
        options = dialogue_act.annotations.get_annotations("option")
        state.options += [option.value for option in options]

    def _provide_recommendations(self, dialogue_act: DialogueAct) -> None:
        state: AdaDialogueState = self.get_state()
        state.flags.new_recommendations = False

    def _explain_keyphrase(self, dialogue_act: DialogueAct) -> None:
        state: AdaDialogueState = self.get_state()
        state.explained_topics += dialogue_act.annotations.get_annotations(
            "topic"
        )

    def _suggest_topics(self, dialogue_act: DialogueAct) -> None:
        state: AdaDialogueState = self.get_state()
        state.suggested_topics += dialogue_act.annotations.get_annotations(
            "topic"
        )
        state.topic_suggestions = AnnotationList()

    # REST
    def update_recommendations(self, recommendations: Ranking) -> None:
        if len(recommendations) == 0:
            return
        state: AdaDialogueState = self.get_state()

        state.recommendation.set_recommendation(
            recommendations.fetch_topk_ranking(10)
        )

        if state.recommendation.get_overlap() < 1:
            state.flags.new_recommendations = True

    def update_topic_suggestions(self, suggestions: AnnotationList) -> None:
        self._dialogue_state.topic_suggestions = suggestions


if __name__ == "__main__":
    import random

    from ada.domain.article import ScoredArticle
    from ada.event.event_bus import EventBus

    event_bus = EventBus()
    tracker = AdaDialogueStateTracker(event_bus=event_bus)
    recommendation = Ranking(
        "test",
        [
            ScoredArticle(i, "title", "text", score=random.random())
            for i in range(3)
        ],
    )

    tracker.update_recommendations(recommendation)
    print(tracker.get_state().recommendation.recommendation._scored_docs)
