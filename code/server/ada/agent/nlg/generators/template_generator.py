from collections import defaultdict
from typing import Dict, List, Optional

from dialoguekit.core import AnnotatedUtterance, Annotation

from ada.agent.nlg.generators.generator import NLGenerator
from ada.core.dialogue_act import DialogueAct
from ada.core.intents import SystemIntent


class AdaTemplatelNLGenerator(NLGenerator):
    def __init__(
        self,
        templates: List[Dict[str, str]],
        **kwargs,
    ):
        """NLG module."""
        super().__init__(templates=templates, **kwargs)

    def can_generate(self, dialogue_act: DialogueAct) -> List[SystemIntent]:
        """Returns a list of available intents."""
        return dialogue_act.intent in self._response_templates

    def generate_action(self, dialogue_act: DialogueAct) -> AnnotatedUtterance:
        return self.fill_template(dialogue_act)


if __name__ == "__main__":
    nlg = AdaTemplatelNLGenerator(
        templates=[
            {"style": "default", "path": "data/nlg/templates/default.yaml"},
        ]
    )
    utterance = nlg.generate_action(DialogueAct(intent=SystemIntent.INITIAL))
    print(utterance.text)
