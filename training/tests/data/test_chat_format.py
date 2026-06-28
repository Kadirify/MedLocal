from medlocal_training.data.chat_format import to_prompt_messages
from medlocal_training.data.sample import QaSample

SAMPLE = QaSample(id="1", question="Does X reduce Y?", context="X reduced Y.", answer="yes")


def test_system_message_lists_the_allowed_labels() -> None:
    system, _ = to_prompt_messages(SAMPLE, ("yes", "no", "maybe"))

    assert system["role"] == "system"
    assert "yes, no, maybe" in system["content"]


def test_prompt_never_contains_the_answer_field() -> None:
    sample = QaSample(id="1", question="Q?", context="C.", answer="SECRET")

    messages = to_prompt_messages(sample, ("yes", "no"))

    assert all("SECRET" not in message["content"] for message in messages)
