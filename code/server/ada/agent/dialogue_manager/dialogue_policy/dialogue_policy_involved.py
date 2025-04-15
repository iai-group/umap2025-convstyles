"""Dialogue state policy."""

from typing import List

from dialoguekit.core import Annotation

from ada.agent.dialogue_manager.dialogue_policy import BaseDialoguePolicy
from ada.agent.dialogue_manager.dialogue_state.dialogue_state import (
    AdaDialogueState,
)
from ada.core.dialogue_act import DialogueAct
from ada.core.intents import SystemAction, SystemIntent, UserIntent


class InvolvedDialoguePolicy(BaseDialoguePolicy):

    def _generate_policy(self, state: AdaDialogueState) -> List[DialogueAct]:
        return []

    def _get_topic_suggestions(
        self, dialogue_state: AdaDialogueState
    ) -> List[DialogueAct]:
        suggestions = super()._get_topic_suggestions(dialogue_state)

        if not dialogue_state.topic_suggestions:
            return suggestions

        # TODO Move options logic somewhere else
        options = [
            Annotation(
                "option",
                DialogueAct(
                    UserIntent.REVEAL_PREFERENCE,
                    [
                        Annotation("topic", suggestion.value),
                    ],
                ),
            )
            for suggestion in dialogue_state.topic_suggestions
        ]
        options[0].value.annotations.add_annotation("intent", "confirm")

        if len(dialogue_state.topic_suggestions) > 1:
            options.append(
                Annotation(
                    "option",
                    DialogueAct(
                        UserIntent.REVEAL_PREFERENCE,
                        dialogue_state.topic_suggestions,
                    ),
                )
            )
        suggestions.append(
            DialogueAct(
                SystemAction.PROVIDE_OPTIONS,
                options,
            ),
        )
        return suggestions

    def _get_preferences(
        self, dialogue_state: AdaDialogueState
    ) -> List[DialogueAct]:
        dialogue_acts = super()._get_preferences(dialogue_state)
        return dialogue_acts + [
            DialogueAct(
                SystemIntent.ELICIT,
            ),
        ]

    def _get_keyphrase_explanation(
        self, dialogue_state: AdaDialogueState
    ) -> List[DialogueAct]:
        if not dialogue_state.discussion_topics:
            return self._rephrase_response(dialogue_state)

        options = [
            Annotation(
                "option",
                DialogueAct(
                    UserIntent.REVEAL_PREFERENCE,
                    [
                        Annotation("topic", discussion_topic.value),
                    ],
                ),
            )
            for discussion_topic in dialogue_state.discussion_topics
        ]
        options[0].value.annotations.add_annotation("intent", "confirm")

        if len(dialogue_state.discussion_topics) == 1:
            options[0].value.annotations.add_annotation("type", "yes_no")
            options.extend(
                [
                    Annotation(
                        "option",
                        DialogueAct(
                            UserIntent.REJECT,
                            [
                                Annotation("reason", "changed_mind"),
                                Annotation("type", "yes_no"),
                            ],
                        ),
                    ),
                    Annotation(
                        "option",
                        DialogueAct(
                            UserIntent.REJECT,
                            [
                                Annotation("reason", "wrong_keyword"),
                                Annotation("type", "yes_no"),
                            ],
                        ),
                    ),
                ]
            )
        elif len(dialogue_state.discussion_topics) > 1:
            options.append(
                Annotation(
                    "option",
                    DialogueAct(
                        UserIntent.REVEAL_PREFERENCE,
                        dialogue_state.discussion_topics,
                    ),
                )
            )

        return self._get_explanation(dialogue_state.discussion_topics) + [
            DialogueAct(
                SystemAction.PROVIDE_OPTIONS,
                options,
            ),
        ]
