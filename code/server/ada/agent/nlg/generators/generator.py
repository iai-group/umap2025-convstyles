from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, List, Optional, Union

from dialoguekit.core import AnnotatedUtterance, Annotation
from dialoguekit.nlg import ConditionalNLG

from ada.agent.nlg.generators.util import load_templates
from ada.core.dialogue_act import AnnotationList, DialogueAct


class NLGenerator(ConditionalNLG, ABC):
    def __init__(
        self,
        path: str = None,
        style: str = "default",
        templates: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        self._style = style
        self._templates = templates or {}
        path = path or self._get_path_for_style(style)
        super().__init__(response_templates=load_templates(path), **kwargs)

    @abstractmethod
    def can_generate(self, dialogue_act: DialogueAct) -> bool:
        raise NotImplementedError

    @abstractmethod
    def generate_action(
        self, dialogue_act: DialogueAct
    ) -> Union[DialogueAct, AnnotatedUtterance]:
        raise NotImplementedError

    def load_templates(self, path: str) -> None:
        self._response_templates = load_templates(path)

    def _merge_values(self, values: List[str]) -> str:
        if len(values) == 1:
            return values[0]

        values[-1] = "and " + values[-1]
        return ", ".join(values)

    def _simplify_annotations(
        self, annotations: AnnotationList
    ) -> AnnotationList:
        annotations_dict = defaultdict(list)
        for annotation in annotations:
            annotations_dict[annotation.slot].append(annotation.value)

        output = AnnotationList()
        for slot, values in annotations_dict.items():
            output.append(Annotation(slot, self._merge_values(values)))

        return output

    def fill_template(self, dialogue_act: DialogueAct) -> AnnotatedUtterance:
        """Generates an utterance from a dialogue act."""
        annotations = self._simplify_annotations(dialogue_act.annotations)
        conditional = annotations.get_annotation_value("condition")
        conditional_value = annotations.get_annotation_value(conditional)
        utterance = self.generate_utterance_text_conditional(
            dialogue_act.intent,
            annotations,
            conditional=conditional,
            conditional_value=conditional_value,
            force_annotation=conditional is not None,
        )

        # TODO hack?
        utterance.annotations = dialogue_act.annotations
        return utterance

    def _get_path_for_style(self, style: str) -> Optional[str]:
        return next(
            (
                template.get("path")
                for template in self._templates
                if template.get("style") == style
            ),
            None,
        )

    def set_style(self, style: str) -> None:
        """Sets the style of the NLG."""
        if style == self._style:
            return

        self._style = style
        path = self._get_path_for_style(style)
        if path:
            self.load_templates(path)
