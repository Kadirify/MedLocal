from medlocal_training.data.chat_format import ChatMessage
from medlocal_training.labs.analyte import ReferenceRange
from medlocal_training.labs.report import Flag, LabReport, LabResult

EXPLAINER_SYSTEM = (
    "You explain laboratory results to patients in plain language. "
    "Each result below has already been compared with its reference range, so never re-judge "
    "a value. Start with a one-sentence overview. For every result marked LOW or HIGH, say "
    "what the test measures and what a result in that direction can be associated with in "
    "general, without stating that this patient has a condition. Cover the results marked "
    "NORMAL together in one sentence. Do not recommend starting, stopping or changing any "
    "medicine or supplement. End by advising the patient to discuss the results with their "
    "doctor. Use short sentences, avoid jargon, and write plain text without markdown."
)


def to_explanation_messages(report: LabReport) -> list[ChatMessage]:
    return [
        {"role": "system", "content": EXPLAINER_SYSTEM},
        {"role": "user", "content": render_report(report)},
    ]


def to_teacher_messages(report: LabReport) -> list[ChatMessage]:
    """Same task, plus vetted background so the teacher does not write from memory alone."""
    notes = "\n".join(_background(result) for result in report.flagged())
    user = render_report(report)
    if notes:
        user += f"\n\nBackground you may rely on (do not quote it):\n{notes}"
    return [
        {"role": "system", "content": EXPLAINER_SYSTEM},
        {"role": "user", "content": user},
    ]


def render_report(report: LabReport) -> str:
    lines = [_render(result) for result in report.results]
    return f"Patient: {report.sex.value}, {report.age} years old\nResults:\n" + "\n".join(lines)


def _render(result: LabResult) -> str:
    analyte = result.analyte
    value = f"{result.value:.{analyte.decimals}f}"
    reference = _describe(result.reference, analyte.decimals)
    return f"- {analyte.name}: {value} {analyte.unit} (reference {reference}) {result.flag.value}"


def _describe(reference: ReferenceRange, decimals: int) -> str:
    if reference.low is None:
        return f"up to {reference.high:.{decimals}f}"
    if reference.high is None:
        return f"{reference.low:.{decimals}f} or higher"
    return f"{reference.low:.{decimals}f} to {reference.high:.{decimals}f}"


def _background(result: LabResult) -> str:
    analyte = result.analyte
    context = analyte.low_context if result.flag is Flag.LOW else analyte.high_context
    return f"- {analyte.name} measures {analyte.measures}. A {result.flag.value} result {context}."
