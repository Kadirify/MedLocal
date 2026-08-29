import json
from typing import Protocol
from urllib.request import Request, urlopen

from medlocal_training.labs.analyte import Language
from medlocal_training.labs.prompt import to_teacher_messages
from medlocal_training.labs.report import LabReport

_MAX_TOKENS = 900
_CONTEXT_TOKENS = 4096


class ExplanationWriter(Protocol):
    def write(self, report: LabReport, language: Language, attempt: int) -> str: ...


class OllamaExplanationWriter:
    """Teacher model behind Ollama. The attempt number is the sampling seed, so retries differ."""

    def __init__(
        self, base_url: str, model: str, temperature: float, timeout_seconds: float
    ) -> None:
        self._chat_url = f"{base_url.rstrip('/')}/api/chat"
        self._model = model
        self._temperature = temperature
        self._timeout_seconds = timeout_seconds

    def write(self, report: LabReport, language: Language, attempt: int) -> str:
        body = {
            "model": self._model,
            "messages": to_teacher_messages(report, language),
            "stream": False,
            "think": False,
            "options": {
                "temperature": self._temperature,
                "seed": attempt,
                "num_predict": _MAX_TOKENS,
                "num_ctx": _CONTEXT_TOKENS,
            },
        }
        request = Request(
            self._chat_url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=self._timeout_seconds) as response:
            reply = json.load(response)
        return str(reply["message"]["content"]).strip()
