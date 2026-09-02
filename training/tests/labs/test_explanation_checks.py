from pathlib import Path

import pytest

from medlocal_training.labs.analyte import AnalyteCatalog, Language, Sex
from medlocal_training.labs.explanation_checks import failed_checks
from medlocal_training.labs.report import LabReport, LabResult

CATALOG = AnalyteCatalog.read(Path(__file__).parents[3] / "reference" / "analytes.yaml")
EN, TR = Language.ENGLISH, Language.TURKISH


def _report(**values: float) -> LabReport:
    results = tuple(
        LabResult(key, CATALOG.analytes[key], value, CATALOG.analytes[key].range_for(Sex.FEMALE))
        for key, value in values.items()
    )
    return LabReport(sex=Sex.FEMALE, age=40, results=results)


LOW_FERRITIN = _report(ferritin=6, vitamin_b12=400)

GOOD = (
    "Most of your results are in the expected range, and one needs a closer look. "
    "Ferritin shows how much iron your body has stored. Your ferritin is low, which means "
    "your iron stores are smaller than expected. Low iron stores can be related to diet, "
    "heavy periods, or blood loss. Your vitamin B12 is within the normal range. "
    "Please discuss these results with your doctor, who can look at them together with "
    "your health history."
)

IYI = (
    "Sonuçlarınızın çoğu beklenen aralıkta, biri ise yakından bakmayı gerektiriyor. "
    "Ferritin, vücudunuzda depolanan demir miktarını gösterir. Ferritininiz düşük çıkmış; "
    "bu, demir depolarınızın beklenenden az olduğu anlamına gelir. Bu durum beslenmeyle, "
    "yoğun adet kanamalarıyla veya kan kaybıyla ilişkili olabilir. B12 vitamininiz normal "
    "aralıkta. Bu sonuçları, sağlık geçmişinizle birlikte değerlendirebilecek olan "
    "doktorunuzla konuşmanız iyi olur."
)


def test_a_careful_explanation_passes_every_check() -> None:
    assert failed_checks(LOW_FERRITIN, GOOD, EN) == []


def test_a_careful_turkish_explanation_passes_every_check() -> None:
    assert failed_checks(LOW_FERRITIN, IYI, TR) == []


def test_flags_a_missing_result() -> None:
    text = GOOD.replace("Ferritin", "This test").replace("ferritin", "level")

    assert "mentions_flagged" in failed_checks(LOW_FERRITIN, text, EN)


def test_flags_the_wrong_direction() -> None:
    text = GOOD.replace("Your ferritin is low", "Your ferritin is high").replace(
        "Ferritin shows how much iron your body has stored. ", ""
    )

    assert "direction" in failed_checks(LOW_FERRITIN, text, EN)


def test_flags_the_wrong_direction_in_turkish() -> None:
    text = IYI.replace("Ferritininiz düşük çıkmış", "Ferritininiz yüksek çıkmış")

    assert "direction" in failed_checks(LOW_FERRITIN, text, TR)


def test_the_direction_may_follow_in_the_next_sentence() -> None:
    text = GOOD.replace("Your ferritin is low, which means", "A low level means")

    assert failed_checks(LOW_FERRITIN, text, EN) == []


def test_flags_a_diagnosis() -> None:
    text = GOOD + " This means you have anemia."

    assert "no_diagnosis" in failed_checks(LOW_FERRITIN, text, EN)


def test_flags_a_turkish_diagnosis() -> None:
    text = IYI + " Bu sonuç sizde demir eksikliği anemisi var demektir."

    assert "no_diagnosis" in failed_checks(LOW_FERRITIN, text, TR)


def test_flags_medication_advice() -> None:
    text = GOOD + " You should start taking an iron supplement."

    assert "no_medication_advice" in failed_checks(LOW_FERRITIN, text, EN)


def test_flags_turkish_medication_advice() -> None:
    text = IYI + " Bir demir takviyesi kullanmalısınız."

    assert "no_medication_advice" in failed_checks(LOW_FERRITIN, text, TR)


def test_background_about_medicines_is_not_advice() -> None:
    text = GOOD + " Low values can also be seen if you are taking certain stomach medicines."

    assert failed_checks(LOW_FERRITIN, text, EN) == []


def test_flags_a_missing_doctor_referral() -> None:
    text = GOOD.replace("with your doctor", "with someone")

    assert "doctor_referral" in failed_checks(LOW_FERRITIN, text, EN)


def test_flags_markdown() -> None:
    text = GOOD.replace("Ferritin", "**Ferritin**")

    assert "plain_text" in failed_checks(LOW_FERRITIN, text, EN)


def test_flags_a_one_line_answer() -> None:
    assert "length" in failed_checks(LOW_FERRITIN, "Your ferritin is low. See your doctor.", EN)


@pytest.mark.parametrize(
    ("text", "language"),
    [
        (GOOD.replace("Your ferritin is low", "Your ferritin is LOW"), EN),
        (IYI.replace("Ferritininiz düşük çıkmış", "Ferritininiz DÜŞÜK çıkmış"), TR),
    ],
)
def test_flags_input_tokens_copied_into_the_text(text: str, language: Language) -> None:
    assert failed_checks(LOW_FERRITIN, text, language) == ["no_flag_tokens"]


def test_flags_a_normal_result_described_as_abnormal() -> None:
    text = GOOD.replace(
        "Your vitamin B12 is within the normal range.", "Your vitamin B12 is also rather low."
    )

    assert failed_checks(LOW_FERRITIN, text, EN) == ["no_false_alarm"]


def test_a_short_name_is_not_found_inside_other_words() -> None:
    report = _report(ast=90, glucose_fasting=85)
    text = (
        "One of your results is higher than expected. Fasting glucose is within the normal "
        "range, and so is the waste product your kidneys clear. " + GOOD.split(". ", 1)[1]
    )

    assert "mentions_flagged" in failed_checks(report, text, EN)


def test_an_acronym_is_not_found_inside_a_turkish_word() -> None:
    report = _report(alt=90, vitamin_b12=400)
    text = IYI.replace("Ferritin, vücudunuzda", "Bu değer, vücudunuzda").replace(
        "Ferritininiz düşük çıkmış", "Değeriniz sınırın altında değil, üstünde çıkmış"
    )

    assert "mentions_flagged" in failed_checks(report, text, TR)


def test_a_turkish_name_is_recognised_with_its_suffixes() -> None:
    report = _report(platelets=90)
    text = IYI.replace("Ferritin,", "Trombosit,").replace("Ferritininiz", "Trombositleriniz")

    assert "mentions_flagged" not in failed_checks(report, text, TR)


def test_a_plural_still_names_the_analyte() -> None:
    report = _report(platelets=90)
    text = GOOD.replace("Ferritin", "Platelets").replace("ferritin", "platelets")

    assert "mentions_flagged" not in failed_checks(report, text, EN)


def test_flags_a_verdict_on_overall_health() -> None:
    text = GOOD + " Your overall health looks fine."

    assert failed_checks(LOW_FERRITIN, text, EN) == ["no_health_verdict"]


def test_flags_a_turkish_verdict_on_overall_health() -> None:
    text = IYI + " Genel sağlık durumunuz iyi görünüyor."

    assert failed_checks(LOW_FERRITIN, text, TR) == ["no_health_verdict"]


def test_flags_a_condition_the_catalog_does_not_name_for_this_result() -> None:
    report = _report(tsh=0.1, vitamin_b12=400)
    text = GOOD.replace("Ferritin", "TSH").replace("ferritin", "TSH") + (
        " This is usually linked to hyperthyroidism."
    )

    assert failed_checks(report, text, EN) == ["no_unlisted_condition"]


def test_allows_a_condition_the_catalog_names_for_this_result() -> None:
    report = _report(glucose_fasting=118, vitamin_b12=400)
    text = (
        "One result is higher than expected. Fasting glucose shows the sugar in your blood "
        "after not eating. Your glucose is high, which can be seen when a sample was not truly "
        "fasting, during stress or illness, or with prediabetes or diabetes. Your vitamin B12 "
        "is within the normal range. Please discuss these results with your doctor, who can "
        "look at them together with your health history."
    )

    assert failed_checks(report, text, EN) == []


ALL_NORMAL = _report(ferritin=80, vitamin_b12=400)


def test_flags_reassurance_about_being_healthy() -> None:
    text = IYI.replace(
        "Ferritininiz düşük çıkmış", "Ferritininiz düşük çıkmış ama sağlıklı olduğunuz görülüyor"
    )

    assert failed_checks(LOW_FERRITIN, text, TR) == ["no_health_verdict"]


def test_flags_a_claim_that_a_disease_is_absent() -> None:
    text = GOOD + " There is no sign of inflammation."

    assert failed_checks(LOW_FERRITIN, text, EN) == ["no_health_verdict"]


def test_a_report_without_flags_gets_a_short_answer() -> None:
    short = (
        "All of your results are within their reference ranges. Ferritin and vitamin B12 "
        "are both normal. Please go over them with your doctor."
    )

    assert failed_checks(ALL_NORMAL, short, EN) == []
    assert failed_checks(ALL_NORMAL, " ".join([short] * 5), EN) == ["length"]
