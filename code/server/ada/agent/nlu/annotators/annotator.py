"""Annotator base class."""

from abc import ABC, abstractmethod
from typing import List

from dialoguekit.core import Annotation, Utterance


class Annotator(ABC):
    @abstractmethod
    def annotate(self, utterance: Utterance) -> List[Annotation]:
        """Annotates the utterance.

        Args:
            utterance: Utterance.

        raises:
            NotImplementedError: If the method is not implemented.

        Returns:
            List of annotations.
        """
        raise NotImplementedError()
