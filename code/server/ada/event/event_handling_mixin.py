from typing import Any, cast

from ada.event.event_bus import EventBus
from ada.event.events import Event
from ada.event.resources import RequestResourceEvent


class EventHandlingMixin:

    def __init__(
        self,
        event_bus: EventBus,
        **kwargs,
    ):
        """Initializes the event handling mixin."""
        self._event_bus = event_bus
        self._register_handlers()

        super().__init__(**kwargs)

    def _register_handlers(self):
        all_event_classes = (
            Event.__subclasses__() + RequestResourceEvent.__subclasses__()
        )
        for event_class in all_event_classes:
            prefix = "handle"
            handler_name = f"{prefix}_{event_class.get_snake_case_name()}"
            handler_method = getattr(self, handler_name, None)
            if handler_method:
                self._event_bus.register(event_class, handler_method)

    def get_event_bus(self) -> EventBus:
        """Gets the event manager.

        Returns:
            Event manager.
        """
        return self._event_bus

    def dispatch_event(self, event: Event) -> None:
        """Dispatches the event.

        Args:
            event: Event to dispatch.
        """
        self._event_bus.dispatch(event)

    def request_resource(self, request_event: RequestResourceEvent) -> Any:
        """Requests a resource.

        Args:
            action: Action to request.

        Returns:
            Event.
        """
        resource = self._event_bus.dispatch_with_response(request_event)
        return cast(request_event.return_class, resource)
