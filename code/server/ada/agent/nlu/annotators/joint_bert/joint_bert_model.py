"""Joint BERT model for intent classification and slot annotation."""

from __future__ import annotations

import os
from typing import List, Optional, Tuple

import torch
import torch.nn as nn
from transformers import BertModel

_BERT_BASE_MODEL = "allenai/scibert_scivocab_uncased"


class JointBERTModel(nn.Module):
    def __init__(
        self,
        intent_label_count: int,
        slot_label_count: int,
    ) -> None:
        """Initializes the JointBERT model.

        Args:
            intent_label_count: The number of intent labels.
            slot_label_count: The number of slot labels.
        """
        super(JointBERTModel, self).__init__()

        self.slot_label_count = slot_label_count
        self.intent_label_count = intent_label_count

        self.bert = BertModel.from_pretrained(_BERT_BASE_MODEL)
        self.intent_classifier = nn.Linear(
            self.bert.config.hidden_size, intent_label_count
        )
        self.slot_classifier = nn.Linear(
            self.bert.config.hidden_size, slot_label_count
        )
        self._last_hidden_state_cache = None

    def pop_last_hidden_state_cache(self) -> Optional[torch.Tensor]:
        """Returns the last hidden state of the model.

        Returns:
            The last hidden state of the model.
        """
        last_hidden_state = self._last_hidden_state_cache
        self._last_hidden_state_cache = None
        return last_hidden_state

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        use_pooler: bool = False,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass of the model.

        Args:
            input_ids: The input token IDs.
            attention_mask: The attention mask.

        Returns:
            Tuple of intent and slot logits.
        """
        outputs = self.bert(input_ids, attention_mask=attention_mask)
        self._last_hidden_state_cache = outputs.last_hidden_state.detach().numpy()
        embedding = (
            outputs.pooler_output
            if use_pooler
            else outputs.last_hidden_state[:, 0, :]
        )

        intent_logits = self.intent_classifier(embedding)
        slot_logits = self.slot_classifier(outputs.last_hidden_state)
        return intent_logits, slot_logits

    def predict(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[List[int], List[int]]:
        """Predicts the intent and slot annotations for the given input.

        Args:
            input_ids: The input token IDs.
            attention_mask (optional): The attention mask. Defaults to None.

        Returns:
            A tuple of the predicted intent and slot annotations.
        """
        with torch.no_grad():
            if attention_mask is None:
                attention_mask = torch.ones(input_ids.shape)

            intent_logits, slot_logits = self(input_ids, attention_mask)

            sorted_intents = torch.argsort(
                intent_logits, descending=True, dim=1
            )
            sorted_intent_indices = sorted_intents[0].tolist()
            predicted_slots = slot_logits.argmax(dim=2).squeeze().tolist()

        return (sorted_intent_indices, predicted_slots)

    @classmethod
    def from_pretrained(cls, path: str) -> JointBERTModel:
        """Loads the model and tokenizer from the specified directory.

        Args:
            path: The path to the directory containing the model and tokenizer.

        Returns:
            The loaded model.
        """

        # Load the state dictionary
        model_path = os.path.join(path, "joint_bert_model.pth")
        state_dict = torch.load(model_path)

        # Infer label counts from the state dictionary
        intent_label_count = state_dict["intent_classifier.weight"].shape[0]
        slot_label_count = state_dict["slot_classifier.weight"].shape[0]

        # Create the model with inferred label counts
        model = cls(intent_label_count, slot_label_count)
        model.load_state_dict(state_dict)
        return model
