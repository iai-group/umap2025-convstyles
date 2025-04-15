from abc import ABC
from typing import Optional


class LLM(ABC):
    def query(self, prompt: str) -> Optional[str]:
        raise NotImplementedError
