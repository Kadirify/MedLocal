import re
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache

from medlocal_training.labs.analyte import Language
from medlocal_training.labs.prompt import flag_tokens
from medlocal_training.labs.report import Flag, LabReport, LabResult

_MIN_WORDS = 40
_MAX_WORDS = 420
# characters after an analyte's name within which a direction word is taken to describe it
_SAID_OF_WINDOW = 60

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
_MARKDOWN = re.compile(r"[*#`]|^\s*[-•]\s", re.MULTILINE)


@dataclass(frozen=True)
class _Patterns:
    doctor: re.Pattern[str]
    diagnosis: re.Pattern[str]
    medication_advice: re.Pattern[str]
    direction: dict[Flag, re.Pattern[str]]
    normal: re.Pattern[str]
    # a handful of lab values says nothing about a person's health as a whole
    health_verdict: re.Pattern[str]
    # conditions an explanation may only name when the catalog's own context for a flagged
    # result names them; group 1 is the stem looked up in that context
    condition: re.Pattern[str]
    # Turkish is agglutinative: "hemoglobininiz" still names hemoglobin
    names_take_suffixes: bool


_PATTERNS = {
    Language.ENGLISH: _Patterns(
        doctor=re.compile(
            r"\b(doctor|physician|healthcare (provider|professional)|clinician)\b", re.I
        ),
        diagnosis=re.compile(
            r"\byou (have|are suffering from|suffer from|are diagnosed with)\b"
            r"|\b(means|confirms|shows|indicates|proves) (that )?you (have|are)\b",
            re.I,
        ),
        # a recommending cue has to come first:
        # "can be seen if you take water tablets" is background, not advice
        medication_advice=re.compile(
            r"\b(should|need to|must|consider|recommend\w*|try to|advis\w+ to|may want to)\b"
            r"[^.]{0,40}\b(start|stop|begin|increase|reduce|lower|raise|take|taking|adjust)\b"
            r"[^.]{0,40}\b(medication|medicine|dose|dosage|supplement|tablet|pill)s?\b",
            re.I,
        ),
        direction={
            Flag.LOW: re.compile(r"\b(low|lower|below|reduced|decreased|under)\b", re.I),
            Flag.HIGH: re.compile(r"\b(high|higher|above|elevated|raised|increased|over)\b", re.I),
        },
        normal=re.compile(r"\b(normal|within|expected range|in range)\b", re.I),
        health_verdict=re.compile(
            r"\b(overall|general) health\b|\byou are (perfectly |completely )?healthy\b"
            r"|\bnothing to worry\b|\bno (cause|reason) for concern\b|\bgood health\b",
            re.I,
        ),
        condition=re.compile(
            r"\b(hyperthyroid|hypothyroid|anemi|anaemi|diabet|leukemi|leukaemi|lymphoma|cancer"
            r"|tumou?r|cirrhos|hepatit|kidney failure|renal failure|gout|lupus|arthritis"
            r"|heart attack|heart disease|stroke)\w*",
            re.I,
        ),
        names_take_suffixes=False,
    ),
    Language.TURKISH: _Patterns(
        doctor=re.compile(r"\b(doktor|hekim)\w*", re.I),
        diagnosis=re.compile(
            r"\bsizde\b[^.]{0,60}\b(var|bulunuyor|mevcut)\b"
            r"|\b\w+(hastasısınız|hastalığınız var)\b"
            r"|\bolduğunuzu (gösterir|gösteriyor|kanıtlar)\b"
            r"|\btanısı (konur|konulur|koyar)\b",
            re.I,
        ),
        medication_advice=re.compile(
            r"\b(ilaç|ilac|takviye|hap|tablet|doz)\w*[^.]{0,50}"
            r"\b(almalısınız|almanız gerek\w*|kullanmalısınız|kullanmanız gerek\w*|başlamalısınız"
            r"|başlayın|bırakmalısınız|bırakın|artırın|azaltın|alın|kullanın)\b",
            re.I,
        ),
        direction={
            Flag.LOW: re.compile(r"\b(düşü\w*|altında\w*|azalmış\w*)\b", re.I),
            Flag.HIGH: re.compile(r"\b(yükse\w*|üstünde\w*|üzerinde\w*|artmış\w*)\b", re.I),
        },
        normal=re.compile(r"\b(normal\w*|aralı\w+ içinde\w*|aralığında\w*)\b", re.I),
        health_verdict=re.compile(
            r"\bgenel sağlı\w*|\bsağlıklısınız\b|\bsağlığınız (iyi|yerinde)\b"
            r"|\bendişe\w* (gerek|bir şey) yok\b|\bendişelenme\w* gerek yok\b",
            re.I,
        ),
        condition=re.compile(
            r"\b(hipertiroid|hipotiroid|anemi|kansızlı|diyabet|lösemi|lenfoma|kanser|tümör"
            r"|siroz|hepatit|böbrek yetmezli|gut|lupus|romatizma|kalp krizi|kalp hastalı|inme)\w*",
            re.I,
        ),
        names_take_suffixes=True,
    ),
}

Check = Callable[[LabReport, str, Language], bool]


def failed_checks(report: LabReport, explanation: str, language: Language) -> list[str]:
    return [name for name, passes in _CHECKS.items() if not passes(report, explanation, language)]


def _has_reasonable_length(_: LabReport, text: str, __: Language) -> bool:
    return _MIN_WORDS <= len(text.split()) <= _MAX_WORDS


def _is_plain_text(_: LabReport, text: str, __: Language) -> bool:
    return _MARKDOWN.search(text) is None


def _copies_no_flag_tokens(_: LabReport, text: str, language: Language) -> bool:
    # the input marks results as LOW/HIGH/NORMAL; a reader should never see those tokens
    return not any(re.search(rf"\b{re.escape(token)}\b", text) for token in flag_tokens(language))


def _refers_to_a_doctor(_: LabReport, text: str, language: Language) -> bool:
    return _PATTERNS[language].doctor.search(text) is not None


def _makes_no_diagnosis(_: LabReport, text: str, language: Language) -> bool:
    return _PATTERNS[language].diagnosis.search(text) is None


def _gives_no_medication_advice(_: LabReport, text: str, language: Language) -> bool:
    return _PATTERNS[language].medication_advice.search(text) is None


def _passes_no_verdict_on_health(_: LabReport, text: str, language: Language) -> bool:
    return _PATTERNS[language].health_verdict.search(text) is None


def _names_only_conditions_from_the_catalog(
    report: LabReport, text: str, language: Language
) -> bool:
    allowed = " ".join(
        result.analyte.context("low" if result.flag is Flag.LOW else "high", language)
        for result in report.flagged()
    ).lower()
    named = _PATTERNS[language].condition.finditer(text)
    return all(match.group(1).lower() in allowed for match in named)


def _mentions_every_flagged_result(report: LabReport, text: str, language: Language) -> bool:
    return all(_sentences_about(result, text, language) for result in report.flagged())


def _keeps_the_given_direction(report: LabReport, text: str, language: Language) -> bool:
    return all(_direction_is_kept(result, text, language) for result in report.flagged())


def _direction_is_kept(result: LabResult, text: str, language: Language) -> bool:
    directions = _PATTERNS[language].direction
    given = directions[result.flag]
    opposite = directions[Flag.HIGH if result.flag is Flag.LOW else Flag.LOW]

    sentences = _sentences_about(result, text, language)
    if not sentences:
        return True

    names = _names(result, language)
    contradicted = any(
        _said_of(names, opposite, s) and not _said_of(names, given, s) for s in sentences
    )
    passages = _sentences_about(result, text, language, include_next=True)
    return any(given.search(p) for p in passages) and not contradicted


def _said_of(names: re.Pattern[str], direction: re.Pattern[str], sentence: str) -> bool:
    """Whether a direction word follows the analyte's name closely.

    In "low phosphorus can be linked to low vitamin D" nothing is said about vitamin D itself;
    in "your vitamin D is low" and in the Turkish "D vitamininiz düşük" the word comes after.
    """
    return any(
        direction.search(sentence, match.end(), match.end() + _SAID_OF_WINDOW)
        for match in names.finditer(sentence)
    )


def _raises_no_false_alarm(report: LabReport, text: str, language: Language) -> bool:
    """A normal result must not be described as low or high.

    Only sentences that name no flagged result are judged; a sentence such as "ferritin is low
    while B12 is normal" legitimately carries both.
    """
    patterns = _PATTERNS[language]
    flagged = report.flagged()

    for result in report.results:
        if result.flag is not Flag.NORMAL:
            continue
        for sentence in _sentences_about(result, text, language):
            if any(_names(other, language).search(sentence) for other in flagged):
                continue
            names = _names(result, language)
            alarmed = any(_said_of(names, p, sentence) for p in patterns.direction.values())
            if alarmed and not patterns.normal.search(sentence):
                return False
    return True


def _sentences_about(
    result: LabResult, text: str, language: Language, *, include_next: bool = False
) -> list[str]:
    """Sentences naming the analyte; the direction often follows in the next one ("A low level")."""
    names = _names(result, language)
    sentences = _SENTENCE_END.split(text)
    return [
        f"{sentence} {following}" if include_next else sentence
        for sentence, following in zip(sentences, [*sentences[1:], ""], strict=True)
        if names.search(sentence)
    ]


def _names(result: LabResult, language: Language) -> re.Pattern[str]:
    suffixes = _PATTERNS[language].names_take_suffixes
    return _name_pattern(result.analyte.search_terms(language), suffixes)


@cache
def _name_pattern(terms: tuple[str, ...], take_suffixes: bool) -> re.Pattern[str]:
    """Whole words only: "ast" must not match inside "fasting".

    Acronyms are matched case-sensitively so that "ALT" is not found in the Turkish "altında".
    """
    tail = r"(?:['’]?\w*)" if take_suffixes else r"s?"
    parts = [
        rf"\b{re.escape(term)}{tail}\b" if term.isupper() else rf"(?i:\b{re.escape(term)}{tail}\b)"
        for term in terms
    ]
    return re.compile("|".join(parts))


_CHECKS: dict[str, Check] = {
    "length": _has_reasonable_length,
    "plain_text": _is_plain_text,
    "no_flag_tokens": _copies_no_flag_tokens,
    "doctor_referral": _refers_to_a_doctor,
    "no_diagnosis": _makes_no_diagnosis,
    "no_medication_advice": _gives_no_medication_advice,
    "no_health_verdict": _passes_no_verdict_on_health,
    "no_unlisted_condition": _names_only_conditions_from_the_catalog,
    "mentions_flagged": _mentions_every_flagged_result,
    "direction": _keeps_the_given_direction,
    "no_false_alarm": _raises_no_false_alarm,
}
