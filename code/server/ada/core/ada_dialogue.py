from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Optional

from dialoguekit.core import AnnotatedUtterance, Dialogue, Utterance

from ada.core.types import Action


class AdaDialogue(Dialogue):
    def __init__(
        self, agent_id: str, user_id: str, conversation_id: Optional[str] = None
    ) -> None:
        super().__init__(agent_id, user_id, conversation_id)
        self._actions: list[Action] = []

    def add_actions(self, actions: list[Action]) -> None:
        """Adds a list of actions to the dialogue.

        Args:
            actions: List of dialogue acts.
        """
        for action in actions:
            self.add_action(action)

    def add_action(self, action: Action) -> None:
        """Adds an action to the dialogue.

        Args:
            action: Dialogue act.
        """
        if isinstance(action, Utterance):
            self.add_utterance(action)

        self._actions.append(action)

    def utterance_to_dict(self, utterance: Utterance) -> Dict[str, Any]:
        utterance_info: Dict[str, Any] = {
            "participant": utterance.participant.name,
            "utterance": utterance.text,
            "utterance ID": utterance.utterance_id,
        }

        feedback = self._utterance_feedbacks.get(utterance.utterance_id)
        if feedback is not None:
            utterance_info["utterance_feedback"] = feedback.feedback.value

        if isinstance(utterance, AnnotatedUtterance):
            if utterance.intent is not None:
                utterance_info["intent"] = repr(utterance.intent)

            for k, v in utterance.metadata.items():
                if isinstance(v, list):
                    utterance_info[k] = [
                        asdict(el) if is_dataclass(el) else el for el in v
                    ]
                else:
                    utterance_info[k] = asdict(v) if is_dataclass(v) else v

            utterance_info["slot_values"] = [
                (
                    {
                        "slot": annotation.slot,
                        "value": annotation.value.to_dict(),
                    }
                    if annotation.value is not None
                    and hasattr(annotation.value, "to_dict")
                    else asdict(annotation)
                )
                for annotation in utterance.annotations
            ]

        return utterance_info

    # def dialogue_act_to_dict(self, dialogue_act: DialogueAct) -> Dict[str, Any]:
    #     dialogue_act_info: Dict[str, Any] = {}
    #     dialogue_act_info["intent"] = str(dialogue_act.intent)
    #     dialogue_act_info["annotations"] = [
    #         (
    #             {
    #                 "slot": annotation.slot,
    #                 "value": annotation.value.to_dict(),
    #             }
    #             if annotation.value is not None
    #             and hasattr(annotation.value, "to_dict")
    #             else {"slot": annotation.slot, "value": annotation.value}
    #         )
    #         for annotation in self.annotations
    #     ]
    #     return dialogue_act_info

    def to_dict(self) -> Dict[str, Any]:
        """Converts the dialogue to a dictionary.

        Returns:
            Dialogue as dictionary.
        """
        dialogue_as_dict: Dict[str, Any] = {
            "conversation ID": self._conversation_id,
            "conversation": [],
            "actions": [],
            "agent": self._agent_id,
            "user": self._user_id,
        }
        if self._metadata:
            dialogue_as_dict["metadata"] = self._metadata

        for utterance in self.utterances:
            dialogue_as_dict["conversation"].append(
                self.utterance_to_dict(utterance)
            )

        for action in self._actions:
            if isinstance(action, Utterance):
                action_info = self.utterance_to_dict(action)
            else:
                action_info = action.to_dict()
            dialogue_as_dict["actions"].append(action_info)
        return dialogue_as_dict
