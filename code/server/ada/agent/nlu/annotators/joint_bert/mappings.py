from enum import Enum


class JointBERTSlot(Enum):
    """JointBERT slot."""

    _OUT = 0
    B_TOPIC = 1
    I_TOPIC = 2
    B_EXCLUDE_TOPIC = 3
    I_EXCLUDE_TOPIC = 4
