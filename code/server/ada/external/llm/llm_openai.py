from dataclasses import asdict, dataclass, field
from typing import List, Optional

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
)

from ada.external.llm.llm import LLM


@dataclass
class DefaultLLMParams:
    max_tokens: int = 64
    n: int = 1
    stream: bool = False
    stop: list = field(default_factory=lambda: ["\n"])


class LLMopenai(LLM):
    def __init__(self, model: str = "llama3.2:latest") -> None:
        self._model = model
        self._client = OpenAI(
            api_key="ollama", base_url="https://ollama.ux.uis.no/"
        )
        self._params = asdict(DefaultLLMParams())

    def query(self, prompt: str) -> Optional[str]:
        chat_prompt = self._get_chat_prompt(prompt)
        response = self._client.chat.completions.create(
            model=self._model,
            messages=chat_prompt,
            **self._params,
        )
        print("************************")
        print(response)
        print("************************")
        return response.choices[0].message.content

    def _get_chat_prompt(self, prompt: str) -> List[ChatCompletionMessageParam]:
        return [ChatCompletionUserMessageParam(content=prompt, role="user")]
