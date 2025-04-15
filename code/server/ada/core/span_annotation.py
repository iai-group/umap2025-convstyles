from dialoguekit.core import Annotation

from ada.core.span import Span


class SpanAnnotation(Annotation):
    slot: str
    value: Span
