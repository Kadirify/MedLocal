from collections.abc import Sequence
from typing import Any

from medlocal_training.data.report_sample import ReportSample
from medlocal_training.data.sample import QaSample

ChatMessage = dict[str, str]
VisionChatMessage = dict[str, Any]

_REPORT_SYSTEM = (
    "You are a radiology assistant drafting chest X-ray reports. "
    "Write only the findings section as a few plain sentences. "
    "Describe what is visible and do not give a diagnosis or recommendations."
)
_REPORT_REQUEST = "Write the findings section for this chest X-ray study."


def to_prompt_messages(sample: QaSample, labels: Sequence[str]) -> list[ChatMessage]:
    system = (
        "You answer biomedical research questions using only the given context. "
        f"Reply with exactly one of: {', '.join(labels)}."
    )
    user = f"Context:\n{sample.context}\n\nQuestion: {sample.question}"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def to_training_messages(sample: QaSample, labels: Sequence[str]) -> list[ChatMessage]:
    return [*to_prompt_messages(sample, labels), {"role": "assistant", "content": sample.answer}]


def to_report_prompt_messages(sample: ReportSample) -> list[VisionChatMessage]:
    images = [{"type": "image", "image": image} for image in sample.images]
    return [
        {"role": "system", "content": [{"type": "text", "text": _REPORT_SYSTEM}]},
        {"role": "user", "content": [*images, {"type": "text", "text": _REPORT_REQUEST}]},
    ]
