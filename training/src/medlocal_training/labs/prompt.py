from dataclasses import dataclass

from medlocal_training.data.chat_format import ChatMessage
from medlocal_training.labs.analyte import Language, ReferenceRange, Sex
from medlocal_training.labs.report import Flag, LabReport, LabResult

_RESULT_LINE = "- {name}: {value} {unit} ({reference} {range}) {flag}"


@dataclass(frozen=True)
class _Wording:
    system: str
    patient: str
    sexes: dict[Sex, str]
    flags: dict[Flag, str]
    reference: str
    up_to: str
    at_least: str
    between: str
    background_header: str
    background_line: str
    sides: dict[Flag, str]
    style_reminder: str


_WORDING = {
    Language.ENGLISH: _Wording(
        system=(
            "You explain laboratory results to patients in plain language, speaking to the "
            'patient directly as "you". '
            "Each result below has already been compared with its reference range, so never "
            "re-judge a value. Start with a one-sentence overview. For every result marked LOW "
            "or HIGH, say what the test measures and what a result in that direction can be "
            "associated with in general, without stating that this patient has a condition. "
            "Cover the results marked NORMAL together in one sentence, and when every result "
            "is normal keep the whole answer to a few sentences. Do not recommend "
            "starting, stopping or changing any medicine or supplement, and do not comment on "
            "the patient's overall health. End by advising the "
            "patient to discuss the results with their doctor. Use short sentences, avoid "
            "jargon, and write plain text without markdown."
        ),
        patient="Patient: {sex}, {age} years old\nResults:",
        sexes={Sex.MALE: "male", Sex.FEMALE: "female"},
        flags={Flag.LOW: "LOW", Flag.NORMAL: "NORMAL", Flag.HIGH: "HIGH"},
        reference="reference",
        up_to="up to {high}",
        at_least="{low} or higher",
        between="{low} to {high}",
        background_header="Background you may rely on (do not quote it):",
        background_line="- {name} measures {measures}. A {side} result {context}.",
        sides={Flag.LOW: "low", Flag.HIGH: "high"},
        style_reminder="Write flowing paragraphs. No bullet points, headings or bold text.",
    ),
    Language.TURKISH: _Wording(
        system=(
            "Laboratuvar sonuçlarını hastalara sade bir Türkçeyle açıklıyorsun; hastaya "
            'doğrudan ve "siz" diye hitap et. '
            "Aşağıdaki her sonuç referans aralığıyla zaten karşılaştırıldı; bir değeri asla "
            "yeniden değerlendirme. Tek cümlelik bir genel özetle başla. DÜŞÜK veya YÜKSEK "
            "işaretli her sonuç için testin neyi ölçtüğünü ve o yöndeki bir sonucun genel "
            "olarak nelerle ilişkili olabileceğini söyle; hastada bir hastalık olduğunu "
            "söyleme. NORMAL işaretli sonuçları tek cümlede topla; bütün sonuçlar normalse "
            "yanıtın tamamını birkaç cümleyle sınırla. Herhangi bir ilaca veya "
            "takviyeye başlamayı, bırakmayı ya da dozunu değiştirmeyi önerme; hastanın genel "
            "sağlık durumu hakkında yorum yapma. Hastaya "
            "sonuçları doktoruyla konuşmasını önererek bitir. Kısa cümleler kur, tıbbi jargon "
            "kullanma ve markdown içermeyen düz metin yaz."
        ),
        patient="Hasta: {sex}, {age} yaşında\nSonuçlar:",
        sexes={Sex.MALE: "erkek", Sex.FEMALE: "kadın"},
        flags={Flag.LOW: "DÜŞÜK", Flag.NORMAL: "NORMAL", Flag.HIGH: "YÜKSEK"},
        reference="referans",
        up_to="en fazla {high}",
        at_least="en az {low}",
        between="{low} - {high}",
        background_header="Güvenebileceğin arka plan bilgisi (alıntılama):",
        background_line="- {name}, {measures} ölçer. {side} bir sonuç {context}.",
        sides={Flag.LOW: "Düşük", Flag.HIGH: "Yüksek"},
        style_reminder=(
            "Akıcı paragraflar halinde yaz. Madde işareti, başlık veya kalın yazı kullanma."
        ),
    ),
}


def explainer_system(language: Language) -> str:
    return _WORDING[language].system


def rendering_templates(language: Language) -> dict[str, object]:
    """Everything another implementation needs to render a report exactly as this module does."""
    wording = _WORDING[language]
    return {
        "patient": wording.patient,
        "sexes": {sex.value: text for sex, text in wording.sexes.items()},
        "flags": {flag.value: text for flag, text in wording.flags.items()},
        "result": _RESULT_LINE,
        "reference": wording.reference,
        "up_to": wording.up_to,
        "at_least": wording.at_least,
        "between": wording.between,
    }


def flag_tokens(language: Language) -> tuple[str, ...]:
    return tuple(_WORDING[language].flags.values())


def to_explanation_messages(report: LabReport, language: Language) -> list[ChatMessage]:
    return [
        {"role": "system", "content": explainer_system(language)},
        {"role": "user", "content": render_report(report, language)},
    ]


def to_teacher_messages(report: LabReport, language: Language) -> list[ChatMessage]:
    """Same task, plus vetted background so the teacher does not write from memory alone."""
    wording = _WORDING[language]
    user = render_report(report, language)

    notes = [_background(result, language) for result in report.flagged()]
    if notes:
        user += f"\n\n{wording.background_header}\n" + "\n".join(notes)
    user += f"\n\n{wording.style_reminder}"

    return [
        {"role": "system", "content": wording.system},
        {"role": "user", "content": user},
    ]


def render_report(report: LabReport, language: Language) -> str:
    wording = _WORDING[language]
    header = wording.patient.format(sex=wording.sexes[report.sex], age=report.age)
    lines = [_render(result, language) for result in report.results]
    return header + "\n" + "\n".join(lines)


def _render(result: LabResult, language: Language) -> str:
    wording = _WORDING[language]
    analyte = result.analyte
    value = f"{result.value:.{analyte.decimals}f}"
    reference = _describe(result.reference, analyte.decimals, wording)
    return _RESULT_LINE.format(
        name=analyte.display_name(language),
        value=value,
        unit=analyte.unit,
        reference=wording.reference,
        range=reference,
        flag=wording.flags[result.flag],
    )


def _describe(reference: ReferenceRange, decimals: int, wording: _Wording) -> str:
    low = None if reference.low is None else f"{reference.low:.{decimals}f}"
    high = None if reference.high is None else f"{reference.high:.{decimals}f}"
    if low is None:
        return wording.up_to.format(high=high)
    if high is None:
        return wording.at_least.format(low=low)
    return wording.between.format(low=low, high=high)


def _background(result: LabResult, language: Language) -> str:
    wording = _WORDING[language]
    analyte = result.analyte
    side = "low" if result.flag is Flag.LOW else "high"
    return wording.background_line.format(
        name=analyte.display_name(language),
        measures=analyte.measured_thing(language),
        side=wording.sides[result.flag],
        context=analyte.context(side, language),
    )
