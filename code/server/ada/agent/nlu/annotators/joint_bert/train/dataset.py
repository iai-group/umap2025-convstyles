"""Dataset loading for training and evaluating the JointBERT model. """

import os
import re
import string
from typing import Dict, Generator, List, Tuple

import torch
import yaml
from torch.utils.data import Dataset
from transformers import BertTokenizer

from ada.agent.nlu.annotators.joint_bert.mappings import JointBERTSlot
from ada.core.intents import UserIntent

DataPoint = Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]

_IGNORE_INDEX = -100
_TOKENIZER_PATH = "allenai/scibert_scivocab_uncased"


def load_yaml(path: str) -> Dict[str, List[str]]:
    """Loads the YAML file at the given path.

    Args:
        path: The path to the YAML file.

    Raises:
        FileNotFoundError: If the file does not exist.

    Returns:
        The data in the YAML file.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    with open(path) as f:
        return yaml.safe_load(f)


def add_punctuation_if_missing(text: str) -> str:
    if text and text[-1] not in string.punctuation:
        return f"{text}."
    return text


def remove_end_punctuation(text: str) -> str:
    return re.sub(r"[{}]$".format(re.escape(string.punctuation)), "", text)


def remove_all_punctuation_and_lowercase(text: str) -> str:
    return re.sub(
        r"[{}]".format(re.escape(string.punctuation)), "", text
    ).lower()


def parse_example(example: str) -> Tuple[str, str, List[str]]:
    """Parses the example to extract intent, text, and slot annotations.

    Args:
        example: The example to parse.

    Returns:
        A tuple of the intent, text, and slot annotations.
    """
    # Extract slot information
    slot_annotations = re.findall(r"\[(.*?)\]\((.*?)\)", example)

    # Remove slot annotations from the text
    clean_text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", example)

    return clean_text, slot_annotations


def parse_data(
    data: Dict[str, List[str]]
) -> Generator[Tuple[str, str, str, List[str]], None, None]:
    """Parses the input data to extract intent, text, and slot annotations.

    Args:
        data: The input data.

    Yields:
        A tuple of the intent, text, and slot annotations.
    """
    for topic in topics():
        yield "REVEAL_PREFERENCE", "", topic, [(topic, "topic")]
    # for topic in topics():
    #     yield "REMOVE_PREFERENCE", "", topic, [(topic, "exclude_topic")]
    for intent in data.keys():
        for example_set in data[intent]:
            for example in example_set["user_utterances"]:
                system_utterance = example_set["system_utterance"]
                clean_text, slot_annotations = parse_example(example)
                clean_text_with_punctuation = add_punctuation_if_missing(
                    clean_text
                )
                yield intent, system_utterance, clean_text_with_punctuation, slot_annotations
                # if len(slot_annotations):
                #     print(
                #         intent,
                #         system_utterance,
                #         clean_text_with_punctuation,
                #         slot_annotations,
                #     )
                #     return
                clean_text_without_end_punctuation = remove_end_punctuation(
                    clean_text
                )
                yield intent, system_utterance, clean_text_without_end_punctuation, slot_annotations
                clean_text_no_punctuation_lowercase = (
                    remove_all_punctuation_and_lowercase(clean_text)
                )
                slot_annotations = [
                    (
                        remove_all_punctuation_and_lowercase(slot_text),
                        slot_label,
                    )
                    for slot_text, slot_label in slot_annotations
                ]
                yield intent, system_utterance, clean_text_no_punctuation_lowercase, slot_annotations


def topics() -> Generator[str, None, None]:
    with open("data/nlu/topics_updated.txt") as topics_file:
        for topic in topics_file:
            yield topic.strip()


class JointBERTDataset(Dataset):
    def __init__(self, path: str, max_length: int = 32) -> None:
        """Initializes the dataset.

        Args:
            path: The path to the YAML file containing the data.
            max_length: The maximum length of the input sequence. Defaults to
                32.
        """
        self.data = load_yaml(path)
        self.max_length = max_length

        self.intent_label_count = len(UserIntent)
        self.slot_label_count = len(JointBERTSlot)

        self.tokenizer = BertTokenizer.from_pretrained(_TOKENIZER_PATH)

        self.examples = []
        self._build_dataset()

    def _build_dataset(self) -> None:
        """Builds the dataset."""
        for intent, system_prompt, clean_text, slot_annotations in parse_data(
            self.data
        ):
            # print(intent, clean_text, slot_annotations)
            intent, tokens, labels = self._tokenize_and_label(
                intent, clean_text, slot_annotations
            )
            # print(intent, tokens, labels)
            # print()

            input_ids = self.tokenizer.encode(tokens, add_special_tokens=True)
            attention_mask = [1] * len(input_ids)

            # Add [CLS] and [SEP] tokens to labels
            cls_label = _IGNORE_INDEX
            sep_label = _IGNORE_INDEX
            labels = [cls_label] + labels + [sep_label]

            # Pad input_ids, attention_mask, and labels
            padding_length = self.max_length - len(input_ids)
            input_ids = input_ids + (
                [self.tokenizer.pad_token_id] * padding_length
            )
            attention_mask = attention_mask + ([0] * padding_length)
            labels = labels + ([_IGNORE_INDEX] * padding_length)
            self.examples.append((input_ids, attention_mask, intent, labels))

    def _num_inside_word_tokens(self, word: str) -> int:
        """Returns the number of inside word tokens in the input word.

        I.e The number of non-starting tokens in the word.

        Args:
            word: The input word.

        Returns:
            The number of word tokens in the input word.
        """
        return len(self.tokenizer.tokenize(word)) - 1

    def _tokenize_and_label(
        self, intent: str, text: str, slot_annotations: Tuple[str, str]
    ) -> Tuple[int, List[str], List[int]]:
        """Tokenizes the text and assigns labels based on slot annotations.

        The main purpose of this method is to convert the slot annotations into
        labels that can be used to train the model. The labels need to have the
        same length as the tokenized utterance.

        For example:

        Input: "I like scifi."
        Tokens: ["I", "like", "sci", "##fi", "."]
        Labels: ["OUT", "OUT", "B_GENRE", -100, "OUT"]
        Indexes: [0, 0, 3, -100, 0]

        Note that we put -100 to ignore evaluation of the loss function for
        tokens that are not beginning of a slot. This makes it easier to
        decode the labels later.

        Args:
            intent: The intent of the text.
            text: The text to tokenize.
            slot_annotations: A tuple of slot-value pairs in the text.

        Returns:
            A tuple of the intent, tokenized text, and labels.
        """
        tokens = self.tokenizer.tokenize(text)
        labels = []

        start_idx = 0
        for slot_text, slot_label in slot_annotations:
            index = text.find(slot_text)
            for word in text[start_idx:index].split():
                labels.append(JointBERTSlot["_OUT"].value)
                labels.extend(
                    [_IGNORE_INDEX] * self._num_inside_word_tokens(word)
                )

            for i, word in enumerate(slot_text.split()):
                slot = ("B_" if i == 0 else "I_") + slot_label.upper()

                labels.append(JointBERTSlot[slot].value)
                labels.extend(
                    [_IGNORE_INDEX] * self._num_inside_word_tokens(word)
                )
            start_idx = index + len(slot_text)

        for word in text[start_idx:].split():
            labels.append(JointBERTSlot["_OUT"].value)
            labels.extend([_IGNORE_INDEX] * self._num_inside_word_tokens(word))
        assert len(tokens) == len(labels)
        return UserIntent[intent.upper()].value - 1, tokens, labels

    def __len__(self):
        """Returns the number of examples in the dataset."""
        return len(self.examples)

    def __getitem__(self, idx: int) -> DataPoint:
        """Returns the example at the given index.

        Args:
            idx: The index of the example to return.

        Returns:
            A tuple of the input_ids, attention_mask, intent, and labels.
        """
        input_ids, attention_mask, intent, labels = self.examples[idx]

        return (
            torch.tensor(input_ids, dtype=torch.long),
            torch.tensor(attention_mask, dtype=torch.long),
            torch.tensor(intent, dtype=torch.long),
            torch.tensor(labels, dtype=torch.long),
        )


if __name__ == "__main__":
    # dataset = JointBERTDataset("data/nlu/annotated_examples.yaml")
    # print(dataset[0])
    # print(len(dataset))
    # print(
    [
        el
        for el in parse_data(
            load_yaml("data/nlu/annotated_examples_v1.1_clean.yaml")
        )
        if el is not None
    ]
    # )
