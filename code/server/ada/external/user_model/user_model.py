from abc import ABC
from typing import Dict, List

from dialoguekit.core import Annotation


class UserModel(ABC):
    def __init__(self, user_id: str, **kwargs):
        self._id = user_id
        self._preferences: Dict[str, List[Annotation]]
        super().__init__(**kwargs)

    def get_slot_preferences(self):
        return self._preferences
