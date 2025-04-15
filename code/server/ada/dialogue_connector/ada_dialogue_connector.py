from typing import List, Optional

from dialoguekit.connector import DialogueConnector
from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.participant.agent import Agent
from dialoguekit.participant.user import User

from ada.core.ada_dialogue import AdaDialogue
from ada.core.types import Action


class ADADialogueConnector(DialogueConnector):
    def __init__(
        self,
        agent: Agent,
        user: User,
        # platform: Platform,
        conversation_id: Optional[str] = None,
        save_dialogue_history: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(
            agent=agent,
            user=user,
            platform=None,
            conversation_id=conversation_id,
            save_dialogue_history=save_dialogue_history,
            **kwargs,
        )
        # self._has_started = False
        self._dialogue_history = AdaDialogue(agent.id, user.id, conversation_id)

    def start(self) -> None:
        """Starts the conversation."""
        pass
        # print("Received user start action:")
        # if not self._has_started:
        #     self._has_started = True
        #     print("Starting conversation...")
        #     self.register_user_action(action)

    def register_user_action(self, action: Action) -> None:
        """Registers an action from the user.

        Args:
            action: User action.
        """
        print(f"Conversation ID: {self.dialogue_history.conversation_id}")
        print(f"\nReceived user action: \n\t{action}")
        self._dialogue_history.add_action(action)
        # self._platform.display_user_action(self._user.id, action)
        self._agent.receive_actions([action])

    def register_user_utterance(
        self, annotated_utterance: AnnotatedUtterance
    ) -> None:
        print(f"Conversation ID: {self.dialogue_history.conversation_id}")
        print(f"\nReceived user utterance: \n\t{annotated_utterance}")
        self._dialogue_history.add_action(annotated_utterance)
        self._agent.receive_utterance(annotated_utterance)

    def register_agent_actions(self, actions: List[Action]) -> None:
        """Registers an action from the agent.

        Args:
            action: Agent action.
        """
        self._dialogue_history.add_actions(actions)
        print(f"Conversation ID: {self.dialogue_history.conversation_id}")
        print("\nReceived system actions: ")
        for action in actions:
            print(f"\t{action}")
        self._user.receive_actions(actions)
