"""Button options templates for the chatbot."""

from dataclasses import asdict
from typing import List

from ada.agent.nlg.generators.generator import NLGenerator
from ada.core.dialogue_act import DialogueAct
from ada.core.intents import SystemAction, UserIntent


class ADAOptionsGenerator(NLGenerator):
    def __init__(self):
        self._templates = {}
        self._style = "default"

    def can_generate(self, dialogue_act: DialogueAct) -> bool:
        return dialogue_act.intent == SystemAction.PROVIDE_OPTIONS

    def generate_action(self, dialogue_act: DialogueAct) -> DialogueAct:
        options: List[DialogueAct] = (
            dialogue_act.annotations.get_annotations_values("option")
        )
        for option in options:
            print(asdict(option))
            print("**************************")
            if option.annotations.get_annotation_value("type") == "yes_no":
                if (
                    option.annotations.get_annotation_value("intent")
                    == "confirm"
                ):
                    option.annotations.add_annotation("text", "Yes")
                    option.annotations.add_annotation("short", "Yes")
                elif (
                    option.annotations.get_annotation_value("reason")
                    == "wrong_keyword"
                ):
                    option.annotations.add_annotation(
                        "text", "No, thats not the topic I am interested in."
                    )
                    option.annotations.add_annotation(
                        "short", "No, wrong topic"
                    )
                elif (
                    option.annotations.get_annotation_value("reason")
                    == "changed_mind"
                ):
                    option.annotations.add_annotation(
                        "text", "Actually, I changed my mind."
                    )
                    option.annotations.add_annotation(
                        "short", "No, changed mind"
                    )

            else:
                option = self._add_text_and_short_text_to_option(option)

        return dialogue_act

    def _add_text_and_short_text_to_option(
        self, option: DialogueAct
    ) -> DialogueAct:
        if option.intent == UserIntent.REVEAL_PREFERENCE:
            preferences = option.annotations.get_annotations("topic")
            if len(preferences) == 1:
                option_text = preferences[0].value
                option.annotations.add_annotation("short", option_text)
                option.annotations.add_annotation("text", option_text)
            else:
                option.annotations.add_annotation("short", "Add all")
                option.annotations.add_annotation("text", "Add all")
        elif option.intent == UserIntent.REMOVE_PREFERENCE:
            preference = option.annotations.get_annotation_value(
                "topic"
            ) or option.annotations.get_annotation_value("exclude_topic")
            option.annotations.add_annotation("short", preference)
            option.annotations.add_annotation("text", preference)
        elif option.intent == UserIntent.RESET_PREFERENCES:
            option.annotations.add_annotation("short", "Reset")
            option.annotations.add_annotation("text", "Reset")

        elif option.intent == UserIntent.REJECT:
            option.annotations.add_annotation("short", "No")
            option.annotations.add_annotation("text", "No")

        return option
