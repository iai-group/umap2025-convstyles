from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Response:
    event: str
    data: Any


@dataclass
class SystemMessage:
    text: str
    intent: Optional[str] = None
    info: Optional[Dict[str, Any]] = None


@dataclass
class UserMessage:
    message: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Option:
    id: int
    short_text: str
    text: Optional[str] = None
