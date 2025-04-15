"""ArXivDigest assistant (ADA) agent."""

from dataclasses import asdict
from typing import List

from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.participant.agent import Agent

from ada.agent.dialogue_manager import AdaDialogueManager
from ada.agent.nlg import AdaNLG
from ada.agent.nlu import AdaNLU
from ada.core.types import Action
from ada.event.event_handling_mixin import EventHandlingMixin
from ada.external.article_recommender.bm25_recommender import BM25Recommender
from ada.external.topic_suggestions.topic_suggestions_joint_bert import (
    JointBertTopicSuggest,
)
from ada.external.user_model.user_model import UserModel


class ADA(Agent, EventHandlingMixin):

    def __init__(self, id: str, user_model: UserModel, **kwargs):
        """ArXivDigest assistant (ADA).

        Args:
            agent_id: Agent ID.
        """
        super().__init__(
            id=id,
            stop_intent=None,
            **kwargs,
        )
        event_bus = self.get_event_bus()
        self._user_model = user_model

        self._nlu = AdaNLU(event_bus=event_bus)
        self._dm = AdaDialogueManager(event_bus=event_bus)
        self._nlg = AdaNLG(event_bus=event_bus)

        self.recomender = BM25Recommender(event_bus=event_bus)
        self.topic_suggestor = JointBertTopicSuggest(event_bus=event_bus)
        self.states = []

    def welcome(self) -> None:
        """Start the conversation by sending the agent's welcome message."""
        pass

    def goodbye(self) -> None:
        """End the conversation by sending the agent's goodbye message.

        NB! Not used in this model.
        """
        pass

    def receive_actions(self, actions: List[Action]) -> None:
        self._dm.process_user_actions(actions)
        self._dm.request_external_resources()
        agent_actions = self._dm.next_actions()

        agent_outputs = self._nlg.generate_actions(
            agent_actions, state=self._dm.get_state()
        )

        self._dm.process_agent_actions(agent_outputs)

        self.backup_state()

        self._dialogue_connector.register_agent_actions(agent_outputs)

    def receive_utterance(self, utterance: AnnotatedUtterance) -> None:
        """Gets called each time there is a new user utterance.

        Follows the standard pattern of an agent:
            1. Generate dialogue acts from the user utterance.
            2. Generate the next agent dialogue act.
            3. Generate the agent utterance from the dialogue act.

        Args:
            utterance: User utterance.
        """
        dialogue_acts = self._nlu.annotate(
            utterance, state=self._dm.get_state()
        )
        print(f"\nReceived user actions: \n\t{dialogue_acts}")

        self.receive_actions([utterance] + dialogue_acts)

    def handle_recommendation_feedback(self, item_id: str, value: int) -> None:
        """Gets called every time there is a new recommendation feedback.

        Args:
            item_id: Item ID.
            value: Feedback value.
        """
        pass

    def backup_state(self):
        state = self._dm.get_state()
        self.states.append(
            {
                "recommendations": (
                    state.recommendation.recommendation.get_item_ids()
                ),
                "preferences": asdict(state.topic_preferences),
                "bookmarks": [asdict(article) for article in state.bookmarks],
            }
        )

    def to_dict(self):
        output = super().to_dict()
        output["states"] = self.states
        return output
