from __future__ import annotations

from collections import defaultdict
from typing import Callable, Dict, List, Type

from ada.event.events import Event
from ada.event.resources import RequestResourceEvent


class EventBus:
    def __init__(self) -> None:
        self._listeners: Dict[Type[Event], List[Callable]] = defaultdict(list)

    def register(
        self,
        event_class: Type[Event],
        listener: Callable,
    ) -> None:
        self._listeners[event_class].append(listener)

    def dispatch(self, event: Event) -> None:
        for listener in self._listeners.get(type(event), []):
            listener(event)

    def dispatch_with_response(
        self,
        request_event: RequestResourceEvent,
    ) -> Event:
        output = None
        for listener in self._listeners.get(type(request_event), []):
            response = listener(data=request_event.data)
            if response is not None:
                if output is not None:
                    raise ValueError(
                        "Multiple listeners returned a response for the same "
                        f"request {request_event}"
                    )
                if type(response) is not request_event.return_class:
                    raise ValueError(
                        "Listener returned an invalid response for the request "
                        f"event {request_event}"
                    )
                output = response
        if output is None:
            raise ValueError(
                "No listener returned a response for request event "
                f"{request_event}"
            )

        return output
