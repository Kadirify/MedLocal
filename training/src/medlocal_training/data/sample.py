from dataclasses import dataclass


@dataclass(frozen=True)
class QaSample:
    id: str
    question: str
    context: str
    answer: str
