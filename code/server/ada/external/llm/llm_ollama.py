from typing import Dict, List, Optional

from ollama import Client

from ada.external.llm.llm import LLM

_DEFAULT_LLM_ENDPOINT = "https://ollama.ux.uis.no"
_MODEL = "llama3.2:latest"


class LLMollama(LLM):
    def __init__(
        self,
        model: str = _MODEL,
        llm_endpoint: str = _DEFAULT_LLM_ENDPOINT,
        **kwargs,
    ) -> None:
        self._model = model
        self._client = Client(host=llm_endpoint)
        super().__init__(**kwargs)

    def query(self, prompt: str) -> Optional[str]:
        return self._query_generate(prompt)

    def _query_generate(self, prompt: str) -> Optional[str]:
        response = self._client.generate(
            model=self._model,
            prompt=prompt,
        )
        return response["response"]

    def _query_chat(self, prompt: str) -> Optional[str]:
        response = self._client.chat(
            model=self._model,
            messages=self._get_chat_prompt(prompt),
        )
        return response["message"]["content"]

    def _get_chat_prompt(self, prompt: str) -> List[Dict[str, str]]:
        return [{"content": prompt, "role": "user"}]

    def pull(self, model: str = None, **kwargs):
        return self._client.pull(model=model or self._model, **kwargs)
