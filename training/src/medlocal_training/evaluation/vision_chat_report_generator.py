from collections.abc import Sequence
from itertools import batched

import torch
from transformers import PreTrainedModel, ProcessorMixin

from medlocal_training.data.chat_format import to_report_prompt_messages
from medlocal_training.data.report_sample import ReportSample


class VisionChatReportGenerator:
    def __init__(
        self,
        model: PreTrainedModel,
        processor: ProcessorMixin,
        batch_size: int,
        max_new_tokens: int,
    ) -> None:
        self._model = model
        self._processor = processor
        self._batch_size = batch_size
        self._max_new_tokens = max_new_tokens
        # generation continues from the last position, so padding has to go on the left
        self._processor.tokenizer.padding_side = "left"

    @torch.inference_mode()
    def generate(self, samples: Sequence[ReportSample]) -> list[str]:
        reports: list[str] = []

        for batch in batched(samples, self._batch_size):
            inputs = self._processor.apply_chat_template(
                [to_report_prompt_messages(sample) for sample in batch],
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                return_tensors="pt",
                processor_kwargs={"padding": True},
            ).to(self._model.device, dtype=torch.bfloat16)

            output = self._model.generate(
                **inputs, max_new_tokens=self._max_new_tokens, do_sample=False
            )
            replies = output[:, inputs["input_ids"].shape[1] :]
            decoded = self._processor.batch_decode(replies, skip_special_tokens=True)
            reports.extend(text.strip() for text in decoded)

        return reports
