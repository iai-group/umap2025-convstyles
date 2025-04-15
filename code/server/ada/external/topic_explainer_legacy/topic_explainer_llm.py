import json
from dataclasses import asdict, dataclass, field
from typing import Optional

import requests

from ada.external.topic_explainer_legacy.topic_explainer_llm import (
    TopicExplainer,
)

PROMPT = "What is {topic} in one short sentence? Be concise! \n\n"
# PROMPT = (
#     "What are {topic1} and {topic2} in one short sentence? Be concise! \n\n"
# )
_DEFAULT_LLM_ENDPOINT = "http://gustav1.ux.uis.no:8888/completion"


@dataclass
class DefaultLLMParams:
    max_tokens: int = 64
    temperature: float = 0.0
    top_p: float = 0.9
    n: int = 1
    stream: bool = False
    logprobs: int = 10
    stop: list = field(default_factory=lambda: ["\n"])


class LLMTopicExplainer(TopicExplainer):
    def __init__(
        self, llm_endpoint: str = _DEFAULT_LLM_ENDPOINT, prompt: str = PROMPT
    ) -> None:
        self._llm_endpoint = llm_endpoint
        self._headers = {"Content-Type": "application/json"}
        self._params = asdict(DefaultLLMParams())
        self._prompt = prompt

    def get_topic_explanation(self, topic: str) -> Optional[str]:
        response = requests.post(
            self._llm_endpoint,
            headers=self._headers,
            json={
                "prompt": self._prompt.format(topic=topic),
                **self._params,
            },
        )
        output_sentence = json.loads(response.text)["content"]
        return output_sentence

    def get_multi_topic_explanation(
        self, topic1: str, topic2: str
    ) -> Optional[str]:
        response = requests.post(
            self._llm_endpoint,
            headers=self._headers,
            json={
                "prompt": self._prompt.format(topic1=topic1, topic2=topic2),
                **self._params,
            },
        )
        output_sentence = json.loads(response.text)["content"]
        return output_sentence


if __name__ == "__main__":
    # prompts = [
    #     "Define {keyphrase}:\n\n",
    #     "Concisely, define {keyphrase} in one sentence:\n\n",
    #     "What is {keyphrase}?\n\n",
    #     "What is {keyphrase} in one sentence? Be concise! \n\n",
    #     "What is {keyphrase} in one short sentence? Be concise! \n\n",
    #     "Explain {keyphrase}:\n\n",
    #     "Concisely, explain {keyphrase} in one sentence:\n\n",
    #     "{keyphrase} is:\n\n",
    #     "Concisely, {keyphrase} in one sentence is:\n\n",
    #     "Explain to me like i'm five what {keyphrase} is:\n\n",
    #     "Explain to me like i'm five what {keyphrase} is in one sentence:\n\n",
    #     "Explain to me like i'm five what {keyphrase} is in one sentence in formal tone:\n\n",
    # ]

    while True:
        topic = input("Enter topic: ")
        if topic == "exit":
            break
        explainer = LLMTopicExplainer()
        explanation = explainer.get_topic_explanation(*topic.split(","))
        print(f"\n{explanation}\n")
