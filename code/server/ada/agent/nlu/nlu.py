"""NLU module."""

from typing import List

from dialoguekit.core import AnnotatedUtterance
from dialoguekit.dialogue_manager.dialogue_state import DialogueState
from dialoguekit.nlu import NLU

from ada.agent.nlu.annotators.jointbert_annotator import JointBERTAnnotator
from ada.config import Config
from ada.core.dialogue_act import DialogueAct
from ada.event.event_handling_mixin import EventHandlingMixin

_MODEL_PATH = "models/joint_bert"


class AdaNLU(NLU, EventHandlingMixin):
    def __init__(self, **kwargs) -> None:
        """Initializes the NLU module."""
        model = JointBERTAnnotator(Config().nlu.model_path or _MODEL_PATH)
        super().__init__(
            intent_classifier=model, slot_annotators=[model], **kwargs
        )

    def annotate(
        self,
        annotated_utterance: AnnotatedUtterance,
        state: DialogueState = None,
    ) -> List[DialogueAct]:
        """Generates dialogue acts from the user utterance.

        Args:
            utterance: User utterance.

        Returns:
            List of dialogue acts.
        """
        intent = self.classify_intent(annotated_utterance)
        annotations = self.annotate_slot_values(annotated_utterance)

        return [DialogueAct(intent=intent, annotations=annotations)]
