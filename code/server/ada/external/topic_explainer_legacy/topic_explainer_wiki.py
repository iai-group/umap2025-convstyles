from pprint import pprint
from typing import Optional

import spacy
import wikipediaapi

from ada.external.topic_explainer_legacy.topic_explainer_wiki import (
    TopicExplainer,
)


class WikiTopicExplainer(TopicExplainer):
    def __init__(self) -> None:
        self._nlp = spacy.load("en_core_web_sm")
        self._wiki = wikipediaapi.Wikipedia("IAI MovieBot", "en")

    def get_first_sentence(self, text: str) -> Optional[str]:
        doc = self._nlp(text)
        pprint(doc.to_dict())
        sentences = [sent.text for sent in doc.sents]
        for sentence in sentences:
            return sentence
        return None

    def get_topic_explanation(self, topic: str) -> Optional[str]:
        page = self._wiki.page(topic.lower())

        if not page.exists():
            return None

        first_sentence = self.get_first_sentence(page.summary)
        return first_sentence


if __name__ == "__main__":
    topic = ""
    explainer = WikiTopicExplainer()
    while True:
        topic = input("Enter a topic: ")
        if topic == "exit":
            break
        print(explainer.get_topic_explanation(topic))
