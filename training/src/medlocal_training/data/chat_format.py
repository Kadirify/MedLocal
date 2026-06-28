from collections.abc import Sequence

from medlocal_training.data.sample import QaSample

ChatMessage = dict[str, str]


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
