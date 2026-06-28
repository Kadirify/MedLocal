from collections.abc import Sequence
from itertools import batched

import torch
from transformers import PreTrainedModel, PreTrainedTokenizerBase

from medlocal_training.data.chat_format import to_prompt_messages
from medlocal_training.data.sample import QaSample


class LabelLogitPredictor:
    """Picks the label whose first token is most likely as the next token of the reply."""

    def __init__(
        self, model: PreTrainedModel, tokenizer: PreTrainedTokenizerBase, batch_size: int
    ) -> None:
        self._model = model
        self._tokenizer = tokenizer
        self._batch_size = batch_size
        # the last position of every row must be the end of the prompt
        self._tokenizer.padding_side = "left"

    @torch.inference_mode()
    def predict(self, samples: Sequence[QaSample], labels: Sequence[str]) -> list[str]:
        label_token_ids = self._first_token_ids(labels)
        predictions: list[str] = []

        for batch in batched(samples, self._batch_size):
            prompts = [
                self._tokenizer.apply_chat_template(
                    to_prompt_messages(sample, labels),
                    tokenize=False,
                    add_generation_prompt=True,
                )
                for sample in batch
            ]
            encoded = self._tokenizer(prompts, return_tensors="pt", padding=True)
            encoded = encoded.to(self._model.device)

            next_token_logits = self._model(**encoded, logits_to_keep=1).logits[:, -1, :]
            best = next_token_logits[:, label_token_ids].argmax(dim=-1)
            predictions.extend(labels[index] for index in best.tolist())

        return predictions

    def _first_token_ids(self, labels: Sequence[str]) -> list[int]:
        ids = [self._tokenizer.encode(label, add_special_tokens=False)[0] for label in labels]
        if len(set(ids)) != len(ids):
            raise ValueError(f"labels {list(labels)} do not start with distinct tokens")
        return ids
