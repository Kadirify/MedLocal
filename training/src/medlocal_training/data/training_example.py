from dataclasses import dataclass

from medlocal_training.data.chat_format import ChatMessage


@dataclass(frozen=True)
class TrainingExample:
    prompt: list[ChatMessage]
    answer: str
