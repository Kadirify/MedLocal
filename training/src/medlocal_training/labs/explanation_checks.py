import re
from collections.abc import Callable

from medlocal_training.labs.report import Flag, LabReport, LabResult

_MIN_WORDS = 50
_MAX_WORDS = 280

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
_MARKDOWN = re.compile(r"[*#`]|^\s*[-•]\s", re.MULTILINE)
# the input marks results as LOW/HIGH/NORMAL; a reader should never see those tokens
_FLAG_TOKEN = re.compile(r"\b(LOW|HIGH|NORMAL)\b")
_DOCTOR = re.compile(r"\b(doctor|physician|healthcare (provider|professional)|clinician)\b")
_DIAGNOSIS = re.compile(
    r"\byou (have|are suffering from|suffer from|are diagnosed with)\b"
    r"|\b(means|confirms|shows|indicates|proves) (that )?you (have|are)\b"
)
# a recommending cue has to come first: "can be seen if you take water tablets" is background
_MEDICATION_ADVICE = re.compile(
    r"\b(should|need to|must|consider|recommend\w*|try to|advis\w+ to|may want to)\b[^.]{0,40}"
    r"\b(start|stop|begin|increase|reduce|lower|raise|take|taking|adjust)\b[^.]{0,40}"
    r"\b(medication|medicine|dose|dosage|supplement|tablet|pill)s?\b"
)
_DIRECTION_WORDS = {
    Flag.LOW: re.compile(r"\b(low|lower|below|reduced|decreased|under)\b"),
    Flag.HIGH: re.compile(r"\b(high|higher|above|elevated|raised|increased|over)\b"),
}

Check = Callable[[LabReport, str], bool]


def failed_checks(report: LabReport, explanation: str) -> list[str]:
    text = explanation.lower()
    failures = [name for name, passes in _CHECKS.items() if not passes(report, text)]
    if _FLAG_TOKEN.search(explanation):
        failures.append("no_flag_tokens")
    return failures


def _has_reasonable_length(_: LabReport, text: str) -> bool:
    return _MIN_WORDS <= len(text.split()) <= _MAX_WORDS


def _is_plain_text(_: LabReport, text: str) -> bool:
    return _MARKDOWN.search(text) is None


def _refers_to_a_doctor(_: LabReport, text: str) -> bool:
    return _DOCTOR.search(text) is not None


def _makes_no_diagnosis(_: LabReport, text: str) -> bool:
    return _DIAGNOSIS.search(text) is None


def _gives_no_medication_advice(_: LabReport, text: str) -> bool:
    return _MEDICATION_ADVICE.search(text) is None


def _mentions_every_flagged_result(report: LabReport, text: str) -> bool:
    return all(_sentences_about(result, text) for result in report.flagged())


def _keeps_the_given_direction(report: LabReport, text: str) -> bool:
    return all(_direction_is_kept(result, text) for result in report.flagged())


def _direction_is_kept(result: LabResult, text: str) -> bool:
    given = _DIRECTION_WORDS[result.flag]
    opposite = _DIRECTION_WORDS[Flag.HIGH if result.flag is Flag.LOW else Flag.LOW]

    sentences = _sentences_about(result, text)
    if not sentences:
        return True

    contradicted = any(opposite.search(s) and not given.search(s) for s in sentences)
    stated = any(given.search(p) for p in _sentences_about(result, text, include_next=True))
    return stated and not contradicted


def _sentences_about(result: LabResult, text: str, *, include_next: bool = False) -> list[str]:
    """Sentences naming the analyte; the direction often follows in the next one ("A low level")."""
    terms = result.analyte.search_terms()
    sentences = _SENTENCE_END.split(text)
    return [
        f"{sentence} {following}" if include_next else sentence
        for sentence, following in zip(sentences, [*sentences[1:], ""], strict=True)
        if any(term in sentence for term in terms)
    ]


_CHECKS: dict[str, Check] = {
    "length": _has_reasonable_length,
    "plain_text": _is_plain_text,
    "doctor_referral": _refers_to_a_doctor,
    "no_diagnosis": _makes_no_diagnosis,
    "no_medication_advice": _gives_no_medication_advice,
    "mentions_flagged": _mentions_every_flagged_result,
    "direction": _keeps_the_given_direction,
}
