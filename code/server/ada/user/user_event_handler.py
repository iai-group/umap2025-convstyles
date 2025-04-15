import json
import logging
from dataclasses import asdict
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from dialoguekit.core import AnnotatedUtterance, Annotation, Utterance
from dialoguekit.participant import DialogueParticipant, User

from ada.core.dialogue_act import AnnotationList, DialogueAct
from ada.core.intents import UserAction
from ada.core.types import Action
from ada.user.messages import Option, Response
from ada.user.style_chunker import StyleChunker

if TYPE_CHECKING:
    from ada.server.flask_socket_platform import ADAPlatform

Data = Optional[Dict[str, Any]]

logger = logging.getLogger(__name__)


class UserEventHandler(User):

    def __init__(
        self,
        user_id: str,
        platform: "ADAPlatform",
        **kwargs,
    ):
        self._platform = platform
        self._style_formater = StyleChunker()
        super().__init__(id=user_id, **kwargs)
        self._ready_for_input: bool = True

    def _emit_to_client(self, event: str, data: Any) -> None:
        """Emits an event to the client.

        Args:
            id: ID.
            event: Event.
            data: Data.
        """
        self._platform.emit_to_client(id=self.id, event=event, data=data)

    def receive_actions(self, actions: List[Action]) -> None:
        """Gets called every time there are new actions.

        Args:
            actions: Actions.
        """
        for action in actions:
            if isinstance(action, Utterance):
                self._style_formater.add_message(action.text)
            elif isinstance(action, DialogueAct):
                self.emit_dialogue_act(action)

        self._platform.stream_to_client(self.emit_stylized_utterance)

    def turn_completed(self) -> None:
        self._emit_to_client(event="EOT", data={})
        self._ready_for_input = True

    def emit_dialogue_act(self, dialogue_act: DialogueAct) -> None:
        handler = getattr(self, str(dialogue_act.intent), None)
        if not handler:
            logger.warning(f"No handler for dialogue_act: {dialogue_act}")
            return
        response = handler(dialogue_act)

        self._emit_to_client(
            event=response.event, data=asdict(response).get("data")
        )

    def emit_stylized_utterance(self) -> None:
        eot_flag = False
        for message, delay in self._style_formater.get_chunked_messages():
            self._platform._socketio.sleep(delay)
            self._emit_to_client(event="message", data=message)
            eot_flag = True

        if eot_flag:
            self.turn_completed()

    def provide_recommendations(self, action: DialogueAct) -> Response:
        """Provides recommendations.

        Args:
            action: Action.
        """
        return Response(
            "recommendations",
            action.annotations.get_annotations_values("article"),
        )

    def provide_bookmarks(self, action: DialogueAct) -> Response:
        """Provides recommendations.

        Args:
            action: Action.
        """
        return Response(
            "bookmarks",
            action.annotations.get_annotations_values("article"),
        )

    def provide_options(self, action: DialogueAct) -> Response:
        """Provides options.

        Args:
            action: Action.
        """
        options = []
        for option_dact in action.annotations.get_annotations("option"):
            option_annotation: AnnotationList = option_dact.value.annotations
            id = option_annotation.get_annotation_value("id")
            short_text = option_annotation.get_annotation_value("short")
            text = option_annotation.get_annotation_value("text")
            options.append(Option(id=id, short_text=short_text, text=text))
        return Response("options", options)

    def on_start_conversation(self, data: Data = None) -> None:
        """Starts conversation.

        Args:
            data: Data received from client.
        """
        self._ready_for_input = False
        logger.info(f"Conversation started: {data}")
        action = DialogueAct(
            UserAction.START_CONVERSATION,
        )
        self._dialogue_connector.register_user_action(action)

    def on_message(self, data: Data = None) -> None:
        """Handles a message.

        Args:
            message: Message.
        """
        if not self._ready_for_input:
            return

        self._ready_for_input = False
        utterance = AnnotatedUtterance(
            text=data["message"],
            participant=DialogueParticipant.USER,
            metadata=data.get("metadata", {}),
        )
        self._dialogue_connector.register_user_utterance(utterance)

    def on_select_option(self, data: Data) -> None:
        """Handles a select option event.

        Args:
            data: Data.
        """
        option = data.get("option")
        if not option:
            logger.error("No option provided.")
            return

        action = DialogueAct(
            UserAction.SELECT_OPTION,
            [Annotation("id", option["id"])],
        )
        self._dialogue_connector.register_user_action(action)

    def on_get_bookmarks(self, data: Data = None) -> None:
        """Receives bookmark request from client.

        Args:
            data: Data received from client.
        """
        action = DialogueAct(UserAction.GET_BOOKMARKS)
        self._dialogue_connector.register_user_action(action)

    def on_add_bookmark(self, data: Data = None) -> None:
        """Receives bookmark request from client.

        Args:
            data: Data received from client.
        """
        action = DialogueAct(
            UserAction.ADD_BOOKMARK, [Annotation("item_id", data["item_id"])]
        )
        self._dialogue_connector.register_user_action(action)

    def on_remove_bookmark(self, data: Data = None) -> None:
        """Receives bookmark request from client.

        Args:
            data: Data received from client.
        """
        action = DialogueAct(
            UserAction.REMOVE_BOOKMARK, [Annotation("item_id", data["item_id"])]
        )
        self._dialogue_connector.register_user_action(action)

    def on_get_explanation(self, data: Data = None) -> None:
        """Receives bookmark request from client.

        Args:
            data: Data received from client.
        """
        action = DialogueAct(
            UserAction.GET_RECOMMENDATION_EXPLANATION,
            [Annotation("item_id", data["item_id"])],
        )
        self._dialogue_connector.register_user_action(action)

    def on_set_style(self, data: Data = None) -> None:
        """Handles setting the style.

        Args:
            data: Data.
        """
        if not self.ready_for_input:
            return

        style = data.get("style", "default")
        self._style_formater.set_style(style=style)
        action = DialogueAct(
            UserAction.SET_STYLE,
            [Annotation("style", style)],
        )
        self._dialogue_connector.register_user_action(action)

    def on_log_event(self, data: Data = None) -> None:
        """Handles a log event.

        Args:
            data: Data.
        """
        logger.info(f"Log event received: {data}")
        log_file_path = f"export/log/{self.id}.jsonl"
        json_data = json.dumps(data)

        with open(log_file_path, "a") as log_file:
            log_file.write(json_data + "\n")
