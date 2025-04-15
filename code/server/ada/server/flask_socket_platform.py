"""The Platform facilitates displaying of the conversation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable, Dict

from dialoguekit.core import AnnotatedUtterance
from dialoguekit.platforms import Platform
from flask import Flask
from flask_socketio import SocketIO

from ada.dialogue_connector.dialogue_connector_manager import (
    DialogueConnectorManager,
)
from ada.server.chat_namespace import ChatNamespace

if TYPE_CHECKING:
    from dialoguekit.core import Utterance


logger = logging.getLogger(__name__)


class ADAPlatform(Platform):

    def __init__(
        self, dialogue_connector_manager: DialogueConnectorManager
    ) -> None:
        """Represents a platform that uses Flask-SocketIO.

        Args:
            agent_class: The class of the agent.
        """
        self._dc_manager = dialogue_connector_manager
        self.app = Flask(__name__)
        self._socketio = SocketIO(self.app, cors_allowed_origins="*")
        self._socketio.on_namespace(
            ChatNamespace(
                namespace="/",
                dialogue_connector_manager=self._dc_manager,
                platform=self,
            )
        )

    def emit_to_client(self, id: str, event: str, data: Dict[str, Any]) -> None:
        """Emits data to the client.

        Args:
            event: Event.
            data: Data.
            room: Room.
        """
        self._socketio.emit(event, data, room=id)

    def stream_to_client(self, function: Callable, *args) -> None:
        """Streams data to the client.

        Args:
            event: Event.
            data: Data.
            room: Room.
        """
        self._socketio.start_background_task(function, *args)

    def send_to_client(self, id: str, data: Dict[str, Any]) -> None:
        """Sends data to the client.

        Args:
            data: Data.
            room: Room.
        """
        self._socketio.send(data, room=id)

    def start(
        self, host: str = "127.0.0.1", port: int = 5000, debug: bool = False
    ) -> None:
        """Starts the platform.

        Args:
            host: Hostname.
            port: Port.
        """
        self._socketio.run(self.app, host=host, port=port, debug=debug)

    def display_agent_utterance(
        self, user_id: str, utterance: AnnotatedUtterance
    ) -> None:
        """Emits agent utterance to the client.

        Args:
            user_id: User ID.
            utterance: An instance of Utterance.
        """
        logger.debug(f"Agent utterance: {utterance}")
        # message = Message.from_utterance(utterance)
        # self._socketio.send(
        #     asdict(Response(user_id, message)),
        #     room=user_id,
        # )

    # def display_user_action(self, user_id: str, action: Action) -> None:
    #     """Emits user action to the client.

    #     Args:
    #         user_id: User ID.
    #         action: User action.
    #     """
    #     logger.debug(f"Agent action: {action}")

    # def display_agent_dialogue_act(
    #     self, user_id: str, dialogue_act: DialogueAct
    # ) -> None:
    #     """Emits agent dialogue act to the client.

    #     Args:
    #         user_id: User ID.
    #         dialogue_act: Dialogue act.
    #     """
    #     event, payload = None, None
    #     for annotation in dialogue_act.annotations:
    #         if annotation.slot == "event":
    #             if event is not None:
    #                 raise ValueError("Multiple events in dialogue act.")
    #             event = annotation.value
    #         elif annotation.slot == "payload":
    #             if payload is not None:
    #                 raise ValueError("Multiple payloads in dialogue act.")
    #             payload = annotation.value

    #     if not event:
    #         raise ValueError("Event or payload missing in dialogue act.")

    #     self.emit_to_client(user_id, event, payload)

    # def display_agent_action(self, user_id: str, action: Action) -> None:
    #     """Overrides the method in Platform to avoid raising an error.

    #     This method is not used in FlaskSocketPlatform.

    #     Args:
    #         user_id: User ID.
    #         action: Agent action.
    #     """
    #     logger.debug(f"Agent action: {action}")
    #     if isinstance(action, DialogueAct):
    #         self.display_agent_dialogue_act(user_id, action)
    #     elif isinstance(action, Utterance):
    #         self.display_agent_utterance(user_id, action)
    #     else:
    #         raise ValueError(
    #             f"Supported action types: {DialogueAct}, {Utterance}, "
    #             f"not: {type(action)}"
    #         )

    def display_user_utterance(
        self, user_id: str, utterance: Utterance
    ) -> None:
        """Overrides the method in Platform to avoid raising an error.

        This method is not used in FlaskSocketPlatform.

        Args:
            user_id: User ID.
            utterance: An instance of Utterance.
        """
        logger.debug(f"User utterance: {utterance}")

    # def display_user_action(self, user_id: str, action: Action) -> None:
    #     """Emits user action to the client.

    #     Args:
    #         user_id: User ID.
    #         action: User action.
    #     """
    #     logger.debug(f"User action: {action}")

    # def initialize(
    #     self, user_id: str, mode: Optional[str], token: Optional[str]
    # ) -> None:
    #     """Initializes the client.

    #     Args:
    #         user_id: User ID.
    #         style: Style.
    #     """
    #     if mode == "study":
    #         # TODO: Find the current stage of the study and
    #         # emit initialization appropriately.
    #         emit(
    #             "init",
    #             {"style": {"name": "considerate", "showStyleSwitch": False}},
    #         )
    #     elif mode == "style_test":
    #         emit(
    #             "init",
    #             {"style": {"name": "considerate", "showStyleSwitch": True}},
    #         )
    #     else:
    #         emit(
    #             "init",
    #         )
