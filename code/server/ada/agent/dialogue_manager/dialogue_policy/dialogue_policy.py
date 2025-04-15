"""Dialogue state policy."""

from abc import ABC, abstractmethod
from typing import List

from dialoguekit.core.annotation import Annotation

from ada.agent.dialogue_manager.dialogue_state.dialogue_state import (
    AdaDialogueState,
)
from ada.core.dialogue_act import AnnotationList, DialogueAct
from ada.core.intents import SystemAction, SystemIntent, UserIntent


class BaseDialoguePolicy(ABC):
    def generate_policy(
        self, dialogue_state: AdaDialogueState
    ) -> List[DialogueAct]:
        """Generates the next dialogue act based on user's last intent.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        print("\n\n####################")
        print(dialogue_state.flags)
        print("####################\n")

        system_dialogue_acts = self._handle_user_actions(dialogue_state)
        system_dialogue_acts.extend(self._generate_policy(dialogue_state))
        should_recommend = (
            dialogue_state.flags.agent_should_respond
            and dialogue_state.flags.has_preferences
            and dialogue_state.flags.updated_preferences
        )
        if should_recommend:
            system_dialogue_acts.extend(self._recommend(dialogue_state))
            if dialogue_state.flags.new_recommendations:
                system_dialogue_acts.extend(
                    self._get_topic_suggestions(dialogue_state)
                )
            else:
                system_dialogue_acts.extend(
                    self._suggest_remove_preferences(dialogue_state)
                )
        if (
            dialogue_state.flags.agent_should_respond
            and not system_dialogue_acts
        ):
            system_dialogue_acts.extend(self._fallback_response(dialogue_state))
        return self._merge_options(
            system_dialogue_acts, dialogue_state=dialogue_state
        )

    @abstractmethod
    def _generate_policy(
        self, dialogue_state: AdaDialogueState
    ) -> List[DialogueAct]:
        """Generates the next dialogue act based on user's last intent.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    def _merge_options(
        self,
        system_dialogue_acts: List[DialogueAct],
        dialogue_state: AdaDialogueState,
    ) -> List[DialogueAct]:
        provide_options_dacts = [
            dact
            for dact in system_dialogue_acts
            if dact.intent == SystemAction.PROVIDE_OPTIONS
        ]
        if len(provide_options_dacts) == 0:
            if dialogue_state.flags.should_reset_options:
                system_dialogue_acts.append(
                    DialogueAct(SystemAction.PROVIDE_OPTIONS)
                )
            return system_dialogue_acts

        options = []
        for dact in provide_options_dacts:
            for option in dact.annotations:
                option.value.annotations.add_annotation("id", len(options))
                options.append(option)

        system_dialogue_acts = [
            dact
            for dact in system_dialogue_acts
            if dact.intent != SystemAction.PROVIDE_OPTIONS
        ]
        system_dialogue_acts.append(
            DialogueAct(SystemAction.PROVIDE_OPTIONS, options)
        )
        return system_dialogue_acts

    def _handle_user_actions(
        self, dialogue_state: AdaDialogueState
    ) -> List[DialogueAct]:
        system_acts = []
        for dact in dialogue_state.user_actions:
            # TODO rename handlers to "_handle_..." so that they are not
            # overwritten by accident
            handler = getattr(self, f"_{dact.intent}", None)
            if handler:
                system_acts.extend(handler(dialogue_state))
        return system_acts

    def _start_conversation(
        self, dialogue_state: AdaDialogueState
    ) -> List[DialogueAct]:
        return [
            DialogueAct(
                SystemIntent.INITIAL,
            ),
            DialogueAct(
                SystemIntent.ELICIT,
                [Annotation("condition", "initial"), Annotation("initial", 1)],
            ),
        ]

    def _help(self, dialogue_state: AdaDialogueState) -> List[DialogueAct]:
        return [
            DialogueAct(
                SystemIntent.INFORM_HELP,
            )
        ]

    def _closing(self, dialogue_state: AdaDialogueState) -> List[DialogueAct]:
        return [
            DialogueAct(
                SystemIntent.CLOSING,
            )
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

    def _get_explanation(self, phrases: List[Annotation]) -> List[DialogueAct]:
        condition = AnnotationList(
            [
                Annotation("condition", "count"),
                Annotation("count", len(phrases)),
            ]
        )

        return [
            DialogueAct(
                SystemIntent.EXPLAIN_KEYPHRASE,
                phrases + condition,
            ),
            DialogueAct(
                SystemIntent.PROMPT_ADD_TO_PREFERENCES,
                condition,
            ),
        ]

    def _get_topic_suggestions(
        self, dialogue_state: AdaDialogueState
    ) -> List[DialogueAct]:
        if dialogue_state.flags.new_topic_suggestions:
            return [
                DialogueAct(
                    SystemIntent.SUGGEST_TOPICS,
                    dialogue_state.topic_suggestions,
                )
            ]
        return self._fallback_response(dialogue_state)

    def _get_preferences(
        self, dialogue_state: AdaDialogueState
    ) -> List[DialogueAct]:
        return [
            DialogueAct(
                SystemIntent.INFORM_PREFERENCES,
                dialogue_state.topic_preferences.topics
                + dialogue_state.topic_preferences.excluded_topics,
            )
        ]

    def _get_bookmarks(
        self, dialogue_state: AdaDialogueState
    ) -> List[DialogueAct]:
        return [
            DialogueAct(
                SystemAction.PROVIDE_BOOKMARKS,
                [
                    Annotation("article", article)
                    for article in dialogue_state.bookmarks
                ],
            )
        ]

    def _get_recommendation_explanation(
        self, dialogue_state: AdaDialogueState
    ) -> List[DialogueAct]:
        article = dialogue_state.recommendation_item_in_focus
        return [
            DialogueAct(
                SystemIntent.EXPLAIN_RECOMMENDATION,
                [
                    Annotation(
                        "article",
                        article,
                    ),
                    Annotation(
                        "explanation",
                        article.explanation,
                    ),
                    Annotation(
                        "title",
                        article.title,
                    ),
                    Annotation(
                        "abstract",
                        article.abstract,
                    ),
                ],
            )
        ]

    def _reset_preferences(
        self, dialogue_state: AdaDialogueState
    ) -> List[DialogueAct]:
        return [
            DialogueAct(SystemIntent.ACKNOWLEDGE_PREFERENCE_RESET),
            DialogueAct(
                SystemIntent.ELICIT,
            ),
        ]

    def _other(self, dialogue_state: AdaDialogueState) -> List[DialogueAct]:
        dialogue_acts = [
            DialogueAct(
                SystemIntent.CANT_HELP,
            )
        ]
        if not dialogue_state.flags.has_preferences:
            dialogue_acts.append(DialogueAct(SystemIntent.ELICIT))
        return dialogue_acts

    def _fallback_response(
        self,
        dialogue_state: AdaDialogueState,
    ) -> List[DialogueAct]:
        return [
            DialogueAct(
                SystemIntent.CANT_HELP,
            )
        ]

    def _rephrase_response(
        self,
        dialogue_state: AdaDialogueState,
    ) -> List[DialogueAct]:
        return [
            DialogueAct(
                SystemIntent.CANT_HELP,
                [
                    Annotation("condition", "rephrase"),
                    Annotation("rephrase", 1),
                ],
            )
        ]

    def _suggest_remove_preferences(self, dialogue_state: AdaDialogueState):
        options = [
            Annotation(
                "option",
                DialogueAct(
                    UserIntent.REMOVE_PREFERENCE,
                    [
                        Annotation("exclude_topic", topic.value),
                    ],
                ),
            )
            for topic in dialogue_state.topic_preferences.topics
            + dialogue_state.topic_preferences.excluded_topics
        ]
        options.append(
            Annotation(
                "option",
                DialogueAct(
                    UserIntent.RESET_PREFERENCES,
                ),
            )
        )

        return [
            DialogueAct(SystemIntent.SUGGEST_REMOVE_PREFERENCES),
            DialogueAct(
                SystemAction.PROVIDE_OPTIONS,
                options,
            ),
        ]

    def _recommend(self, state: AdaDialogueState) -> List[DialogueAct]:
        """Decides whether to make a recommendation or not."""
        dialogue_acts = [
            DialogueAct(
                SystemIntent.RECOMMEND,
                [
                    Annotation(slot="condition", value="overlap"),
                    Annotation(
                        slot="overlap", value=state.recommendation.get_overlap()
                    ),
                ],
            )
        ]
        if state.flags.new_recommendations:
            dialogue_acts.append(
                DialogueAct(
                    SystemAction.PROVIDE_RECOMMENDATIONS,
                    [
                        Annotation("article", article)
                        for article in state.recommendation.get_recommended_articles()
                    ],
                )
            )
        return dialogue_acts

    def _reject(self, state: AdaDialogueState) -> List[DialogueAct]:
        return [DialogueAct(SystemIntent.ELICIT)]
