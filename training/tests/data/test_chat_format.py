from medlocal_training.data.chat_format import ChatMessage, render_training_text, to_prompt_messages
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


class ThinkingTemplateTokenizer:
    """Mimics Qwen3: assistant turns get a think block, the generation prompt does not."""

    eos_token = "<eos>"

    def apply_chat_template(
        self, conversation: list[ChatMessage], *, tokenize: bool, add_generation_prompt: bool
    ) -> str:
        turns = "".join(
            f"<{m['role']}>{'<think></think>' if m['role'] == 'assistant' else ''}{m['content']}"
            for m in conversation
        )
        return turns + ("<assistant>" if add_generation_prompt else "")


def test_training_text_is_the_inference_prompt_followed_by_the_answer() -> None:
    tokenizer = ThinkingTemplateTokenizer()
    labels = ("yes", "no", "maybe")

    text = render_training_text(tokenizer, SAMPLE, labels)

    prompt = tokenizer.apply_chat_template(
        to_prompt_messages(SAMPLE, labels), tokenize=False, add_generation_prompt=True
    )
    assert text == f"{prompt}yes<eos>"
    assert "<think>" not in text
