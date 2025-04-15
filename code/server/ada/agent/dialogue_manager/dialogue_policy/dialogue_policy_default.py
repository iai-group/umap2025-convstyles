"""Dialogue state policy."""

from typing import List

from ada.agent.dialogue_manager.dialogue_policy.dialogue_policy import (
    BaseDialoguePolicy,
)
from ada.agent.dialogue_manager.dialogue_state.dialogue_state import (
    AdaDialogueState,
)
from ada.core.dialogue_act import DialogueAct


class DefaultDialoguePolicy(BaseDialoguePolicy):
    def _generate_policy(self, state: AdaDialogueState) -> List[DialogueAct]:
        """Generates the next dialogue act based on user's last intent.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        return []
