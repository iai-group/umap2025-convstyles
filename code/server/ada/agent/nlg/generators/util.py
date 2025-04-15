import re
from collections import defaultdict
from typing import Dict, List

import yaml
from dialoguekit.core import AnnotatedUtterance, Annotation
from dialoguekit.participant import DialogueParticipant

from ada.core.intents import SystemIntent


def _find_slots(
    text: str,
) -> List[str]:
    """Finds slots in a text.

    Args:
        text: Text.

    Returns:
        List of slots.
    """
    matches = re.findall(r"\{(.*?)\}", text)
    return matches


def _load_raw_templates(path: str) -> Dict[str, List[str]]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_templates(
    path: str,
) -> Dict[SystemIntent, List[AnnotatedUtterance]]:
    """Loads the templates from a yaml file.

    Args:
        path: Path to the yaml file.

    Returns:
        Dictionary of templates.
    """
    parsed_templates = defaultdict(list)
    for intent, utterances in _load_raw_templates(path).items():
        if intent in SystemIntent.__members__:  # TODO Remove this check
            for utterance in utterances:
                conditions: List[Dict[str, float]] = []
                if isinstance(utterance, dict):
                    utterance, conditions = list(utterance.items())[0]

                parsed_templates[SystemIntent[intent]].append(
                    AnnotatedUtterance(
                        text=utterance,
                        participant=DialogueParticipant.AGENT,
                        intent=SystemIntent[intent],
                        annotations=[
                            Annotation(slot) for slot in _find_slots(utterance)
                        ],
                        metadata={
                            key: val
                            for obj in conditions
                            for key, val in obj.items()
                        },
                    )
                )

    return parsed_templates
