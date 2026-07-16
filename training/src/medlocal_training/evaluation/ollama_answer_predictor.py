import json
from collections.abc import Sequence
from urllib.request import Request, urlopen

from medlocal_training.data.chat_format import to_prompt_messages
from medlocal_training.data.sample import QaSample

_MAX_ANSWER_TOKENS = 4


class OllamaAnswerPredictor:
    """Asks a model served by Ollama, so the exported and quantized artefact is what gets scored."""

    def __init__(self, base_url: str, model: str, timeout_seconds: float) -> None:
        self._chat_url = f"{base_url.rstrip('/')}/api/chat"
        self._model = model
        self._timeout_seconds = timeout_seconds

    def predict(self, samples: Sequence[QaSample], labels: Sequence[str]) -> list[str]:
        return [self._answer(sample, labels) for sample in samples]

    def _answer(self, sample: QaSample, labels: Sequence[str]) -> str:
        body = {
            "model": self._model,
            "messages": to_prompt_messages(sample, labels),
            "stream": False,
            "options": {"temperature": 0, "num_predict": _MAX_ANSWER_TOKENS},
        }
        request = Request(
            self._chat_url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=self._timeout_seconds) as response:
            reply = json.load(response)

        # anything outside the label set stays as is and is scored as a wrong answer
        return str(reply["message"]["content"]).strip().lower()
