import importlib
from typing import Any, Dict, List

from dialoguekit.core import Annotation

from ada.agent.dialogue_manager.dialogue_state.dialogue_state import (
    AdaDialogueState,
)
from ada.agent.nlg.generators.generator import NLGenerator
from ada.config import Config, NLGeneratorConfig
from ada.core.dialogue_act import DialogueAct
from ada.core.intents import SystemIntent
from ada.core.types import Action
from ada.event.event_handling_mixin import EventHandlingMixin


class AdaNLG(EventHandlingMixin):
    def __init__(self, **kwargs) -> None:
        """Initializes the NLG module."""
        super().__init__(**kwargs)
        config = Config()
        self._generators = self.load_generators(config.nlg.generators)

    def load_generators(
        self, generator_configs: List[NLGeneratorConfig]
    ) -> List[NLGenerator]:
        """Loads the NLG generators."""
        generators = []
        for generator_config in generator_configs:
            generator = self._load_generator(generator_config)
            generators.append(generator)

        return generators

    def _load_generator(
        self, generator_config: NLGeneratorConfig
    ) -> NLGenerator:
        """Loads a single NLG generator."""
        module = importlib.import_module(name="ada.agent.nlg.generators")
        cls = getattr(module, generator_config.class_name)
        args = generator_config.args

        generator_instance = cls(**args) if args else cls()
        return generator_instance

    def generate_actions(
        self, dialogue_acts: List[Dict[str, Any]], state: AdaDialogueState
    ) -> List[Dict[str, Any]]:
        """Generates actions from dialogue acts."""
        if state.flags.style_changed:
            self.update_styles(state.style.value)

        actions = []
        for dialogue_act in dialogue_acts:
            action = self._generate_action(dialogue_act)
            actions.append(action)

        return actions

    def _generate_action(self, dialogue_act: DialogueAct) -> Action:
        """Generates an action from a dialogue act."""
        for generator in self._generators:
            if generator.can_generate(dialogue_act):
                action = generator.generate_action(dialogue_act)
                break
        else:
            action = dialogue_act

        return action

    def update_styles(self, style: str) -> None:
        """Updates the style of the NLG generators."""
        for generator in self._generators:
            generator.set_style(style)


if __name__ == "__main__":
    from ada.core.intents import SystemAction, SystemIntent

    dacts = [
        DialogueAct(SystemIntent.INITIAL),
        DialogueAct(SystemIntent.INFORM_PREFERENCES),
        DialogueAct(
            SystemIntent.EXPLAIN_KEYPHRASE,
            [Annotation("topic", "Salty dog")],
        ),
        DialogueAct(
            SystemAction.PROVIDE_OPTIONS,
            [Annotation("option", Option(0, "Salty dog"))],
        ),
        DialogueAct(SystemIntent.CLOSING),
    ]

    nlg = AdaNLG(event_bus=None)
    for act in nlg.generate_actions(dacts):
        if isinstance(act, DialogueAct):
            print(act.intent)
        else:
            print(act.text)
        print("Annotations:")
        for annotation in act.annotations:
            print(f"\t{annotation}")
