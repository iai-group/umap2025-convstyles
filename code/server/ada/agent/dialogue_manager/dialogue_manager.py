from dataclasses import asdict
from typing import Dict, List

from ada.agent.dialogue_manager.dialogue_policy import (
    ConsiderateDialoguePolicy,
    DefaultDialoguePolicy,
    InvolvedDialoguePolicy,
)
from ada.agent.dialogue_manager.dialogue_policy.dialogue_policy import (
    BaseDialoguePolicy,
)
from ada.agent.dialogue_manager.dialogue_state import (
    AdaDialogueState,
    AdaDialogueStateTracker,
)
from ada.core.dialogue_act import ActionList, DialogueAct
from ada.event.event_handling_mixin import EventHandlingMixin
from ada.event.resources import (
    RequestRecommendationsEvent,
    RequestSuggestionsEvent,
)
from ada.external.article_recommender.ranking import Ranking


class AdaDialogueManager(EventHandlingMixin):

    def __init__(self, **kwargs) -> None:
        """Dialogue Manager.

        Args:
            user_id: User ID.
        """
        super().__init__(**kwargs)
        self._state_tracker = AdaDialogueStateTracker(
            event_bus=self.get_event_bus()
        )
        self._policies: Dict[str, BaseDialoguePolicy] = {
            "involved": InvolvedDialoguePolicy(),
            "considerate": ConsiderateDialoguePolicy(),
            "default": DefaultDialoguePolicy(),
        }
        self._current_policy = self._policies["default"]

    def get_state(self) -> AdaDialogueState:
        """Gets the dialogue state.

        Returns:
            Dialogue state.
        """
        return self._state_tracker.get_state()

    def process_user_actions(self, actions: List[DialogueAct]) -> None:
        """Processes the input.

        Args:
            user_dialogue_acts: User dialogue acts.
        """
        self._state_tracker.process_user_actions(actions)

    def process_agent_actions(self, utterances: ActionList) -> None:
        """Processes the input.

        Args:
            user_dialogue_acts: User dialogue acts.
        """
        self._state_tracker.process_agent_actions(utterances)

    def request_external_resources(self) -> None:
        """Requests external resources."""
        self._get_new_recommendations()
        self._get_new_topic_suggestions()
        self._state_tracker.update_flags()

    def next_actions(
        self,
    ) -> List[DialogueAct]:
        """Gets the next dialogue act.

        Args:
            user_dialogue_acts: User dialogue acts.

        Returns:
            Dialogue act.
        """
        state: AdaDialogueState = self._state_tracker.get_state()

        if state.flags.style_changed:
            self._current_policy = self._policies.get(state.style.value)

        agent_dialogue_acts = self._current_policy.generate_policy(state)
        return agent_dialogue_acts

    def _get_new_recommendations(self) -> None:
        state: AdaDialogueState = self._state_tracker.get_state()

        if len(state.topic_preferences.topics) == 0:
            self._state_tracker.update_recommendations(Ranking())
        elif state.flags.updated_preferences:
            recommendations: Ranking = self.request_resource(
                RequestRecommendationsEvent(
                    data=asdict(state.topic_preferences)
                )
            )
            self._state_tracker.update_recommendations(recommendations)

    def _get_new_topic_suggestions(self) -> None:
        state: AdaDialogueState = self._state_tracker.get_state()
        if len(state.recommendation) > 0 and len(state.topic_suggestions) == 0:
            data = {
                **asdict(state.topic_preferences),
                "recommendations": (
                    state.recommendation.get_recommended_articles()
                ),
            }
            data["excluded_topics"].extend(
                [asdict(annotation) for annotation in state.suggested_topics]
            )

            suggestions = self.request_resource(
                RequestSuggestionsEvent(data=data)
            )
            self._state_tracker.update_topic_suggestions(suggestions)
