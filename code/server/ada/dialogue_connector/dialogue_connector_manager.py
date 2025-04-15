from typing import Dict, Type

from dialoguekit.participant import Agent
from dialoguekit.platforms import Platform

from ada.agent.agent import ADA
from ada.dialogue_connector.ada_dialogue_connector import ADADialogueConnector
from ada.event.event_bus import EventBus
from ada.external.user_model.ada_user_model import AdaUserModel
from ada.user.user_event_handler import UserEventHandler


class DialogueConnectorManager:
    def __init__(
        self, agent_class: Type[Agent] = ADA, max_connections: int = 1000
    ):
        self._max_connections = max_connections
        self._agent_class = agent_class
        self._active_connections: Dict[str, ADADialogueConnector] = {}

    def connect_user(
        self, user_id: str, platform: Platform
    ) -> UserEventHandler:
        if user_id in self._active_connections:
            raise ValueError(f"User {user_id} is already connected.")

        if len(self._active_connections) >= self._max_connections:
            raise ValueError("Maximum number of connections reached.")

        event_bus = EventBus()
        user = UserEventHandler(
            user_id=user_id,
            platform=platform,
        )
        user_model = AdaUserModel(
            user_id=user_id,
            event_bus=event_bus,
        )
        agent = self._agent_class.get_instance(
            id=self._agent_class.get_name(),
            event_bus=event_bus,
            user_model=user_model,
        )
        dialogue_connector = ADADialogueConnector(
            agent=agent,
            user=user,
            # platform=platform,
        )
        self._active_connections[user_id] = dialogue_connector

        return user

    def disconnect_user(self, user_id: str) -> None:
        if user_id not in self._active_connections:
            raise ValueError(f"User {user_id} is not connected.")

        dc = self._active_connections.pop(user_id)
        dc.close()

    def get_user_event_handler(self, user_id: str) -> UserEventHandler:
        if user_id not in self._active_connections:
            raise ValueError(f"User {user_id} is not connected.")

        return self._active_connections[user_id].user
