from typing import Dict, List

from dialoguekit.core import AnnotatedUtterance, Utterance

from ada.agent.nlg.generators.generator import NLGenerator
from ada.core.dialogue_act import AnnotationList, DialogueAct
from ada.core.intents import SystemIntent
from ada.external.llm.llm_ollama import LLMollama


class ADALLMNLGenerator(NLGenerator):
    def __init__(
        self, model: str, base_url: str, templates: Dict[str, str]
    ) -> None:
        self._model = LLMollama(model, base_url)
        super().__init__(templates=templates)

    @property
    def prompts(self) -> Dict[SystemIntent, List[Utterance]]:
        return self._response_templates

    def can_generate(self, dialogue_act: DialogueAct) -> bool:
        return dialogue_act.intent in self.prompts

    def generate_action(self, dialogue_act: DialogueAct) -> AnnotatedUtterance:
        prompt = self.fill_template(dialogue_act)
        llm_output = self._model.query(prompt.text)
        output = self.format_output(llm_output)
        return AnnotatedUtterance(
            output,
            participant=prompt.participant,
            intent=prompt.intent,
            annotations=AnnotationList(prompt.annotations),
        )

    def format_output(self, output: str) -> str:
        return output.replace("*", "\n")
