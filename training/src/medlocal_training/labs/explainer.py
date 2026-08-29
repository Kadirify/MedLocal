import json
from collections.abc import Sequence
from itertools import batched
from typing import Protocol
from urllib.request import Request, urlopen

import torch
from transformers import PreTrainedModel, PreTrainedTokenizerBase

from medlocal_training.labs.analyte import Language
from medlocal_training.labs.prompt import to_explanation_messages
from medlocal_training.labs.report import LabReport


class Explainer(Protocol):
    def explain(self, reports: Sequence[tuple[LabReport, Language]]) -> list[str]: ...


class CausalLmExplainer:
    def __init__(
        self,
        model: PreTrainedModel,
        tokenizer: PreTrainedTokenizerBase,
        batch_size: int,
        max_new_tokens: int,
    ) -> None:
        self._model = model
        self._tokenizer = tokenizer
        self._batch_size = batch_size
        self._max_new_tokens = max_new_tokens
        # generation continues from the last position, so padding has to go on the left
        self._tokenizer.padding_side = "left"

    @torch.inference_mode()
    def explain(self, reports: Sequence[tuple[LabReport, Language]]) -> list[str]:
        explanations: list[str] = []

        for batch in batched(reports, self._batch_size):
            prompts = [
                self._tokenizer.apply_chat_template(
                    to_explanation_messages(report, language),
                    tokenize=False,
                    add_generation_prompt=True,
                )
                for report, language in batch
            ]
            encoded = self._tokenizer(prompts, return_tensors="pt", padding=True)
            encoded = encoded.to(self._model.device)

            output = self._model.generate(
                **encoded, max_new_tokens=self._max_new_tokens, do_sample=False
            )
            replies = output[:, encoded["input_ids"].shape[1] :]
            decoded = self._tokenizer.batch_decode(replies, skip_special_tokens=True)
            explanations.extend(text.strip() for text in decoded)

        return explanations


class OllamaExplainer:
    def __init__(
        self, base_url: str, model: str, max_new_tokens: int, timeout_seconds: float
    ) -> None:
        self._chat_url = f"{base_url.rstrip('/')}/api/chat"
        self._model = model
        self._max_new_tokens = max_new_tokens
        self._timeout_seconds = timeout_seconds

    def explain(self, reports: Sequence[tuple[LabReport, Language]]) -> list[str]:
        return [self._explain(report, language) for report, language in reports]

    def _explain(self, report: LabReport, language: Language) -> str:
        body = {
            "model": self._model,
            "messages": to_explanation_messages(report, language),
            "stream": False,
            "think": False,
            "options": {"temperature": 0, "num_predict": self._max_new_tokens},
        }
        request = Request(
            self._chat_url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=self._timeout_seconds) as response:
            reply = json.load(response)
        return str(reply["message"]["content"]).strip()
