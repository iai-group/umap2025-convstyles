"""

User Intents

    REVEAL: User states or updates their research interests or topics.
    REMOVE: User expresses the desire to remove some of their existing
        preferences.
    RESTART: User wishes to reset their preferences and start afresh.
    HELP_REQUEST: User seeks help or clarification on how to use the system.
    CLOSING: User indicates they wish to end the session or leave the system.
    OTHER: User input falls outside the scope, domain, or capabilities of the
        system.

System Intents

    INITIAL: System introduces itself and its capabilities at the beginning of
        the interaction.
    ELICIT: System prompts the user to specify their research interests or
        topics.
    ACKNOWLEDGE: System acknowledges and confirms the user's stated preferences.
    RECOMMEND: System presents a list of recommendations based on the user's
        preferences.
    EXPLAIN: System provides a simple explanation of how the current
        preferences influence the recommendations.
    MODIFY_INFORM: System suggests the user modify their preferences to refine
        or broaden the recommendation scope.
    INFORM_HELP: System offers assistance or clarification on how to use its
        features effectively.
    CLOSING: System acknowledges the end of the session and says goodbye to the
        user.

"""

from __future__ import annotations

from enum import Enum, auto
from typing import Any, Dict


class IntentEnum(Enum):
    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"

    def __deepcopy__(self, memo: Dict[int, Any]) -> IntentEnum:
        return self


class UserIntent(IntentEnum):
    # generic
    # Request help
    HELP = auto()  # DONE
    # No need to respond
    IGNORE = auto()  # DONE
    # Not understood
    OTHER = auto()  # DONE
    # Finish conversation
    CLOSING = auto()  # DONE

    # domain specific
    # Add or update preference
    GET_PREFERENCES = auto()  # DONE
    # Add or update preference
    REVEAL_PREFERENCE = auto()  # DONE
    # Remove preference
    REMOVE_PREFERENCE = auto()  # DONE
    # Remove all preferences
    RESET_PREFERENCES = auto()  # DONE

    # Confirm prompt
    CONFIRM = auto()  # DONE
    # Reject prompt
    REJECT = auto()  # TODO

    # Ask for explanation
    GET_KEYPHRASE_EXPLANATION = auto()  # DONE
    # Get suggestions
    GET_TOPIC_SUGGESTIONS = auto()  # DONE


class UserAction(IntentEnum):
    # Actions
    # Direct response, no state change
    START_CONVERSATION = auto()  # DONE
    # Two types of options, Yes/No and multiple choice
    SELECT_OPTION = auto()  # DONE
    # Direct response, no state change
    GET_BOOKMARKS = auto()  # DONE
    # Doesnt affect policy (in this version)
    ADD_BOOKMARK = auto()  # DONE
    # Doesnt affect policy (in this version)
    REMOVE_BOOKMARK = auto()  # DONE
    # DM updates, not stored in history
    GET_RECOMMENDATION_EXPLANATION = auto()  # DONE
    SET_STYLE = auto()  # DONE


class SystemIntent(IntentEnum):
    # User facing system intents (Utterance)
    INITIAL = auto()  # DONE
    ELICIT = auto()  # DONE
    INFORM_PREFERENCES = auto()  # DONE
    SUGGEST_REMOVE_PREFERENCES = auto()  # DONE
    PROMPT_ADD_TO_PREFERENCES = auto()  # DONE
    PROMPT_TO_RESET_PREFERENCES = auto()  # DONE
    ACKNOWLEDGE_PREFERENCE_UPDATE = auto()  # DONE
    ACKNOWLEDGE_PREFERENCE_RESET = auto()  # DONE
    SUGGEST_TOPICS = auto()  # DONE
    EXPLAIN_KEYPHRASE = auto()  # DONE !NB uses LLM, Not a template.
    EXPLAIN_RECOMMENDATION = auto()  # DONE
    RECOMMEND = auto()  # DONE
    INFORM_HELP = auto()  # DONE
    CANT_HELP = auto()  # DONE
    CLOSING = auto()  # DONE


class SystemAction(IntentEnum):
    # User facing system intents (Dialogue Act)
    PROVIDE_RECOMMENDATIONS = auto()  # DONE
    PROVIDE_BOOKMARKS = auto()  # DONE
    PROVIDE_OPTIONS = auto()  # DONE


# class SystemInternalAction(IntentEnum):
# internal system intents

# TODO
# System intent: Preference has already been stated
