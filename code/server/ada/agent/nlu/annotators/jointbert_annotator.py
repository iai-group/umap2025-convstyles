import re
from typing import Dict, List, Optional, Tuple

import spacy
import torch
from dialoguekit.core.annotation import Annotation
from dialoguekit.core.utterance import Utterance
from dialoguekit.nlu.intent_classifier import IntentClassifier
from dialoguekit.nlu.slot_annotator import SlotAnnotator
from dialoguekit.participant import DialogueParticipant
from spacy.tokens import Doc as SpacyDoc
from spacy.tokens import Span as SpacySpan
from transformers import BertTokenizerFast

from ada.agent.nlu.annotators.joint_bert.joint_bert_model import JointBERTModel
from ada.agent.nlu.annotators.joint_bert.mappings import JointBERTSlot
from ada.core.dialogue_act import DialogueAct
from ada.core.intents import UserIntent
from ada.core.span import Span
from ada.core.span_annotation import SpanAnnotation

_MODEL_PATH = "models/joint_bert"


class JointBERTAnnotator(SlotAnnotator, IntentClassifier):
    """JointBERT annotator."""

    def __init__(self, path: str = _MODEL_PATH) -> None:
        """Initializes the annotator.

        Args:
            path: Path to the model.
        """
        self._nlp = spacy.load("en_core_web_sm")
        self.annotations_cache: Dict[Utterance, DialogueAct] = {}
        self.load_model(path)

    def classify_intent(self, utterance: Utterance) -> UserIntent:
        if utterance not in self.annotations_cache:
            self.annotate_utterance(utterance)

        return self.annotations_cache[utterance].intent

    def get_annotations(self, utterance: Utterance) -> List[Annotation]:
        if utterance not in self.annotations_cache:
            self.annotate_utterance(utterance)

        return self.annotations_cache[utterance].annotations

    def annotate_text(self, text: str) -> List[SpanAnnotation]:
        text = text.strip().lower()
        tokens = self.tokenize(text)
        _, slots = self._get_predictions(tokens)
        embeddings = self._model.pop_last_hidden_state_cache()[0, 1:-1, :]
        return self._get_keyphrases_from_slots(text, tokens, slots, embeddings)

    def annotate_utterance(self, utterance: Utterance) -> None:
        """Annotates the utterance.

        Args:
            utterance: Utterance.

        Returns:
            List of annotations.
        """
        text = utterance.text.strip().lower()
        tokens = self.tokenize(text)
        intent, slots = self._get_predictions(tokens)
        keyphrases = self._get_keyphrases_from_slots(text, tokens, slots)

        # annotations = [
        #     Annotation(keyphrase.slot, " ".join(keyphrase.value.text.split()))
        #     for keyphrase in keyphrases
        # ]
        self.annotations_cache[utterance] = DialogueAct(
            intent=UserIntent(intent + 1),
            annotations=[
                Annotation(phrase.slot, phrase.value.text)
                for phrase in keyphrases
            ],
        )

    def _get_predictions(
        self, tokens: List[str]
    ) -> Tuple[List[int], List[int]]:
        token_ids = self._tokenizer.convert_tokens_to_ids(
            ["[CLS]"] + tokens + ["[SEP]"]
        )

        intents, slots = self._model.predict(torch.tensor([token_ids]))
        return intents[0], slots[1:-1]

    def _get_keyphrases_from_slots(
        self,
        text: str,
        tokens: List[str],
        slots: List[int],
        embeddings: Optional[torch.Tensor] = None,
    ) -> List[SpanAnnotation]:
        doc = self._nlp(text)
        keyphrases: List[SpanAnnotation] = []
        current_keyphrase: Span = None
        current_slot = None
        end = 0
        for i, (token, slot) in enumerate(zip(tokens, slots)):
            if token.startswith("##"):
                if current_keyphrase:
                    start = text.find(token[2:], end)
                    end = start + len(token[2:])
                    current_keyphrase += Span(
                        text[start:end],
                        text,
                        start,
                        end,
                        lemma=(
                            doc.char_span(start, end).lemma_
                            if doc.char_span(start, end)
                            else None
                        ),
                    )
                continue

            slot_parts = JointBERTSlot(slot).name.lower().split("_")
            slot_type = slot_parts[0]
            slot_name = "_".join(slot_parts[1:])
            start = text.find(token, end)
            end = start + len(token)
            if current_keyphrase and (
                slot_name != current_slot or slot_type == "b"
            ):
                keyphrases.extend(
                    SpanAnnotation(
                        current_slot,
                        cleaned_phrase,
                    )
                    for cleaned_phrase in self._clean_keyphrase(
                        current_keyphrase, doc
                    )
                )
                current_keyphrase = None

            if slot_name != "out":
                emb = embeddings[i] if embeddings is not None else None
                token = Span(
                    text[start:end],
                    text,
                    start,
                    end,
                    embedding=emb,
                    lemma=(
                        doc.char_span(start, end).lemma_
                        if doc.char_span(start, end)
                        else None
                    ),
                )
                current_keyphrase = (
                    current_keyphrase + token if current_keyphrase else token
                )
            current_slot = slot_name

        if current_keyphrase:
            keyphrases.extend(
                SpanAnnotation(
                    current_slot,
                    cleaned_phrase,
                )
                for cleaned_phrase in self._clean_keyphrase(
                    current_keyphrase, doc
                )
            )
        return keyphrases

    def _is_phrase_meaningful(
        self, phrase: SpacySpan, full_doc: SpacyDoc
    ) -> bool:
        # A single-word phrase can be meaningful if it's a noun or a proper noun
        if len(phrase.text.split()) == 1:
            token = full_doc[phrase.start]
            return token.pos_ in {"NOUN", "PROPN"}
        # For multi-word phrases, ensure it's not entirely composed of stopwords
        return not all(token.is_stop for token in phrase)

    def _trim_trailing_words(self, phrase: SpacySpan) -> SpacySpan:
        # Create a Doc object from the phrase
        last_index = len(phrase)
        first_index = 0

        # Iterate through the tokens in reverse order
        for token in phrase:
            if token.pos_ in {"VERB", "NOUN", "PROPN", "ADJ", "NUM"}:
                break
            else:
                first_index += 1

        # Iterate through the tokens in reverse order
        for token in reversed(phrase):
            # Adjective was added as it is applicable in some cases
            # We dont want "Feynman path integral" -> "Feynman path"
            if token.pos_ in {"NOUN", "PROPN", "ADJ", "NUM"}:
                break
            else:
                last_index -= 1

        if first_index >= last_index:
            return self._nlp("")
        return phrase[first_index:last_index]

    def _clean_keyphrase(self, keyphrase: Span, doc: SpacyDoc) -> List[Span]:
        cleaned_phrases = []

        for subphrase in re.split(r"[().,]", keyphrase.text):
            subphrase = subphrase.strip()
            # keyphrase should be at least 3 characters long. E.g., LLM
            # Changing to 2 characters because of AI. TODO: Validate
            if len(subphrase) <= 1:
                continue

            start = doc.text.find(subphrase, keyphrase.start)
            spacy_span = doc.char_span(start, start + len(subphrase))
            if spacy_span and self._is_phrase_meaningful(spacy_span, doc):
                cleaned_phrase = self._trim_trailing_words(spacy_span)
                if len(cleaned_phrase) > 0:
                    start = doc.text.find(cleaned_phrase.text, start)
                    cleaned_phrases.append(
                        keyphrase[start : start + len(cleaned_phrase.text)]
                    )

        return cleaned_phrases

    def load_model(self, path: str) -> None:
        """Loads the model.

        Args:
            path: Path to the model.
        """
        self._model = JointBERTModel.from_pretrained(path)
        self._tokenizer: BertTokenizerFast = BertTokenizerFast.from_pretrained(
            path
        )

    def tokenize(self, text: str) -> List[str]:
        """Tokenizes the text.

        Args:
            text: Text.

        Returns:
            List of tokens.
        """
        # TODO add special tokens here?
        return self._tokenizer.tokenize(
            text, truncation=True, max_length=510, add_special_tokens=False
        )

    def save_model(self, file_path: str) -> None:
        pass

    def train_model(
        self, utterances: List[Utterance], labels: List[UserIntent]
    ) -> None:
        pass


if __name__ == "__main__":
    annotator = JointBERTAnnotator()
    utterance = Utterance(
        "I want to talk about the weather in London.", DialogueParticipant.USER
    )
    print(annotator.get_annotations(utterance))
    print(annotator.classify_intent(utterance))
    utterance = Utterance(
        "I am interested in photosyntheses.", DialogueParticipant.USER
    )
    print(annotator.get_annotations(utterance))
    print(annotator.classify_intent(utterance))
    utterance = Utterance(
        "I would like to know more about quantum computing.",
        DialogueParticipant.USER,
    )
    print(annotator.get_annotations(utterance))
    print(annotator.classify_intent(utterance))
    utterance = Utterance("Lets start over.", DialogueParticipant.USER)
    print(annotator.get_annotations(utterance))
    print(annotator.classify_intent(utterance))
    utterance = Utterance(
        "Not interested in quantum computing.",
        DialogueParticipant.USER,
    )
    print(annotator.get_annotations(utterance))
    print(annotator.classify_intent(utterance))
    utterance = Utterance(
        "Conversational recommender systems",
        DialogueParticipant.USER,
    )
    print(annotator.get_annotations(utterance))
    print(annotator.classify_intent(utterance))
