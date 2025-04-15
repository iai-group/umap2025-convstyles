import logging
import threading
from typing import Any, Dict, cast

from dialoguekit.platforms import Platform
from flask import Request, request
from flask_socketio import Namespace

from ada.dialogue_connector.dialogue_connector_manager import (
    DialogueConnectorManager,
)

logger = logging.getLogger(__name__)
lock = threading.Lock()


class SocketIORequest(Request):
    sid: str


class ChatNamespace(Namespace):

    def __init__(
        self,
        namespace: str,
        dialogue_connector_manager: DialogueConnectorManager,
        platform: Platform,
    ) -> None:
        """Represents a namespace.

        Args:
            namespace: Namespace.
            platform: An instance of FlaskSocketPlatform.
        """
        super().__init__(namespace)
        self._platform = platform
        self._dc_manager = dialogue_connector_manager
        self._register_event_handlers()
        # self._started: Dict[str, bool] = {}

    def trigger_event(self, event, *args, **kwargs):
        with lock:
            logging.info(f"Event: {event}, Args: {args}, Kwargs: {kwargs}")
            handler = getattr(self, "on_" + event, None)
            if handler:
                return super(ChatNamespace, self).trigger_event(
                    event, *args, **kwargs
                )

            return self.fallback_event_handler(*args, **kwargs)

    def _get_sid(self) -> str:
        """Gets the sid from the request."""
        return cast(SocketIORequest, request).sid

    def _register_event_handlers(self):
        # Dynamically bind events based on handler methods
        user_event_handler_setup_instance = self._dc_manager.connect_user(
            "setup", platform=self._platform
        )
        for method_name in dir(user_event_handler_setup_instance):
            if method_name.startswith("on_"):
                event_name = method_name[3:]
                setattr(
                    self,
                    f"on_{event_name}",
                    self._create_event_handler(event_name),
                )

    def _create_event_handler(self, event_name: str):
        def event_handler(data: Dict[str, Any]):
            sid = self._get_sid()
            handler = self._dc_manager.get_user_event_handler(sid)
            if handler:
                getattr(handler, f"on_{event_name}")(data)

        return event_handler

    def on_connect(self) -> None:
        """Connects client to platform."""
        sid = self._get_sid()
        self._dc_manager.connect_user(sid, platform=self._platform)
        # mode = request.args.get("mode")
        # token = request.args.get("token")
        # self._platform.initialize(sid, mode, token)
        logger.info(f"Client connected; user_id: {sid}")

    def on_disconnect(self) -> None:
        """Disconnects client from server."""
        sid = self._get_sid()
        self._dc_manager.disconnect_user(sid)
        logger.info(f"Client disconnected; user_id: {sid}")

    def fallback_event_handler(self, *args, **kwargs):
        logger.warning(f"Event not found: {args}, {kwargs}")

    # def on_feedback(self, data: dict) -> None:
    #     """Receives feedback from client.

    #     Args:
    #         data: Data received from client.
    #     """
    #     sid = self._get_sid()
    #     logger.info(f"Utterance feedback received: {data}")
    #     self._platform.feedback(sid, data["utterance_id"], data["feedback"])

    # def on_recommendation_feedback(self, data: dict) -> None:
    #     """Receives feedback from client.

    #     Args:
    #         data: Data received from client.
    #     """
    #     sid = self._get_sid()
    #     logger.info(f"Item feedback received: {data}")
    #     agent = self.get_agent(sid)
    #     agent.handle_recommendation_feedback(data["item_id"], data["feedback"])

    # def on_get_preferences(self, data: dict) -> None:
    #     """Receives preferences request from client.

    #     Args:
    #         data: Data received from client.
    #     """
    #     sid = self._get_sid()
    #     agent = self._platform.get_agent(sid)
    #     logger.info(f"Sending preferences: {data}")
    #     emit("preferences", agent.get_preferences())

    # def on_remove_preference(self, data: dict) -> None:
    #     """Receives remove preference request from client.

    #     Args:
    #         data: Data received from client.
    #     """
    #     sid = self._get_sid()
    #     agent = self._platform.get_agent(sid)
    #     logger.info(f"Removing preference: {data}")
    #     agent.handle_remove_preference(data["topic"])
