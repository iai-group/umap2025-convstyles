from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, List, Union

from dialoguekit.core import AnnotatedUtterance, Annotation, Utterance

from ada.core.intents import IntentEnum, SystemIntent, UserIntent


class AnnotationList(List[Annotation]):
    def add_annotation(self, slot: str, value: Any) -> None:
        """Adds an annotation to the list of annotations."""
        self.append(Annotation(slot=slot, value=value))

    def get_annotation(self, slot: str) -> Union[None, Annotation]:
        """Gets an annotation by slot name."""
        return next(
            (annotation for annotation in self if annotation.slot == slot),
            None,
        )

    def get_annotation_value(self, slot: str) -> Union[None, Any]:
        """Gets an annotation value by slot name."""
        annotation = self.get_annotation(slot)
        return annotation.value if annotation else None

    def get_annotations(self, slot: str) -> List[Annotation]:
        """Gets all annotations by slot name."""
        return [annotation for annotation in self if annotation.slot == slot]

    def get_annotations_values(self, slot: str) -> List[Any]:
        """Gets an annotation value by slot name."""
        return [annotation.value for annotation in self.get_annotations(slot)]

    def get_values(self) -> List[Any]:
        """Gets all annotation values."""
        return [annotation.value for annotation in self]

    def __in__(self, annotation: Annotation) -> bool:
        """Checks if an annotation exists by slot name."""
        return annotation.value in self.get_annotations_values(annotation.slot)


@dataclass(eq=True, unsafe_hash=True)
class DialogueAct:
    """Represents a dialogue act that is an intent and its annotations."""

    intent: Union[None, UserIntent, SystemIntent] = field(
        default=None, hash=True
    )
    annotations: AnnotationList = field(default_factory=AnnotationList)

    def __post_init__(self):
        if not isinstance(self.annotations, AnnotationList):
            self.annotations = AnnotationList(self.annotations)

    def to_dict(self) -> dict[str, Any]:
        """Converts the dialogue act to a dictionary."""
        return {
            "intent": repr(self.intent),
            "annotations": [
                (
                    {
                        "slot": annotation.slot,
                        "value": annotation.value.to_dict(),
                    }
                    if annotation.value is not None
                    and hasattr(annotation.value, "to_dict")
                    else asdict(annotation)
                )
                for annotation in self.annotations
            ],
        }


Action = Union[DialogueAct, Utterance, AnnotatedUtterance]


class ActionList(List[Action]):
    def add_action(self, action: Action) -> None:
        """Adds an action to the list of actions."""
        self.append(action)

    def get_action(self, index: int) -> Union[None, Action]:
        """Gets an action by index."""
        return self[index]

    def get_first_action_by_intent(
        self, intent: IntentEnum
    ) -> Union[None, Action]:
        """Gets an action by intent."""
        return next(
            (action for action in self if action.intent == intent),
            None,
        )

    def get_actions_by_intent(self, intent: IntentEnum) -> List[Action]:
        """Gets all actions by intent."""
        return [action for action in self if action.intent == intent]
