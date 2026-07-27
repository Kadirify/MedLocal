from collections.abc import Sequence
from typing import Protocol

from medlocal_training.data.sample import QaSample

ChatMessage = dict[str, str]


class ChatTemplateTokenizer(Protocol):
    eos_token: str

    def apply_chat_template(
        self, conversation: list[ChatMessage], *, tokenize: bool, add_generation_prompt: bool
    ) -> str: ...


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


def render_training_text(
    tokenizer: ChatTemplateTokenizer, sample: QaSample, labels: Sequence[str]
) -> str:
    """The exact inference prompt followed by the answer.

    Rendering the answer as an assistant message is not equivalent: Qwen3 templates put an
    empty think block in front of it, so the model would learn a prefix it never sees later.
    """
    prompt = tokenizer.apply_chat_template(
        to_prompt_messages(sample, labels), tokenize=False, add_generation_prompt=True
    )
    return f"{prompt}{sample.answer}{tokenizer.eos_token}"
