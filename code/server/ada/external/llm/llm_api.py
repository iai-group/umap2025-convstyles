import json
from dataclasses import asdict, dataclass
from typing import Optional

import requests

from ada.external.llm.llm import LLM

_DEFAULT_LLM_ENDPOINT = "https://ollama.ux.uis.no"


@dataclass
class DefaultLLMParams:
    max_tokens: int = 64
    n: int = 1
    stream: bool = False


class LLMapi(LLM):
    def __init__(self, llm_endpoint: str = _DEFAULT_LLM_ENDPOINT) -> None:
        self._llm_endpoint = llm_endpoint
        self._headers = {"Content-Type": "application/json"}
        self._params = asdict(DefaultLLMParams())

    def query(self, prompt: str) -> Optional[str]:
        response = requests.post(
            f"{self._llm_endpoint}/chat/completions",
            headers=self._headers,
            json={
                "prompt": prompt,
                "model": "llama3.2:latest",
                **self._params,
            },
        )
        output_sentence = json.loads(response.text)["response"]
        return output_sentence
