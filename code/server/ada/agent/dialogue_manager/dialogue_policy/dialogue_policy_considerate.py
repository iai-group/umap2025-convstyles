"""Dialogue state policy."""

from typing import List

from dialoguekit.core import Annotation

from ada.agent.dialogue_manager.dialogue_policy import BaseDialoguePolicy
from ada.agent.dialogue_manager.dialogue_state.dialogue_state import (
    AdaDialogueState,
)
from ada.core.dialogue_act import DialogueAct
from ada.core.intents import SystemAction, SystemIntent, UserIntent


class ConsiderateDialoguePolicy(BaseDialoguePolicy):

    def _generate_policy(self, state: AdaDialogueState) -> List[DialogueAct]:
        return []

    def _get_topic_suggestions(
        self, dialogue_state: AdaDialogueState
    ) -> List[DialogueAct]:
        suggestions = super()._get_topic_suggestions(dialogue_state)

        if not dialogue_state.flags.new_topic_suggestions:
            return suggestions

        suggestions.append(
            DialogueAct(
                SystemIntent.EXPLAIN_KEYPHRASE,
                dialogue_state.topic_suggestions
                + [
                    Annotation("condition", "count"),
                    Annotation("count", len(dialogue_state.topic_suggestions)),
                ],
            )
        )

        return suggestions

    def _reject(self, state: AdaDialogueState) -> List[DialogueAct]:
        return [DialogueAct(SystemIntent.INFORM_HELP)]

    def _reveal_preference(self, state: AdaDialogueState) -> List[DialogueAct]:
        if state.flags.confirmation_received:
            return []

        discussion_topics = [
            topic
            for topic in state.discussion_topics
            if topic.value not in state.explained_topics.get_values()
        ]
        if discussion_topics:
            options = [
                DialogueAct(
                    SystemAction.PROVIDE_OPTIONS,
                    [
                        Annotation(
                            "option",
                            DialogueAct(
                                UserIntent.REVEAL_PREFERENCE,
                                state.discussion_topics
                                + [
                                    Annotation("intent", "confirm"),
                                    Annotation("type", "yes_no"),
                                ],
                            ),
                        ),
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
                    ],
                )
            ]
            return self._get_explanation(discussion_topics) + options

        return [
            DialogueAct(
                SystemIntent.ACKNOWLEDGE_PREFERENCE_UPDATE,
                state.discussion_topics,
            ),
        ]

    def _reset_preferences(self, state: AdaDialogueState) -> List[DialogueAct]:
        if state.flags.confirmation_received:
            return super()._reset_preferences(state)

        response = DialogueAct(SystemIntent.PROMPT_TO_RESET_PREFERENCES)

        options = [
            DialogueAct(
                SystemAction.PROVIDE_OPTIONS,
                [
                    Annotation(
                        "option",
                        DialogueAct(
                            UserIntent.RESET_PREFERENCES,
                            [
                                Annotation("intent", "confirm"),
                                Annotation("type", "yes_no"),
                            ],
                        ),
                    ),
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
                ],
            )
        ]
        return [response] + options

    # def _get_yes_no_option(self):
