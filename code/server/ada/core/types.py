from typing import Union

from dialoguekit.core import AnnotatedUtterance, DialogueAct, Utterance

Action = Union[DialogueAct, Utterance, AnnotatedUtterance]
