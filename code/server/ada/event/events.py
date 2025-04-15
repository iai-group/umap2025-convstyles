from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Event(ABC):
    @classmethod
    def get_snake_case_name(cls) -> str:
        return "event"


@dataclass
class ChangeStyleEvent(Event):
    style: str = "default"

    @classmethod
    def get_snake_case_name(cls) -> str:
        return "change_style"


@dataclass
class LogEvent(Event):
    data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def get_snake_case_name(cls) -> str:
        return "log"
