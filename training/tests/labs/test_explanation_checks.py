from pathlib import Path

from medlocal_training.labs.analyte import AnalyteCatalog, Sex
from medlocal_training.labs.explanation_checks import failed_checks
from medlocal_training.labs.report import LabReport, LabResult

CATALOG = AnalyteCatalog.read(Path(__file__).parents[3] / "reference" / "analytes.yaml")


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


def test_a_careful_explanation_passes_every_check() -> None:
    assert failed_checks(LOW_FERRITIN, GOOD) == []


def test_flags_a_missing_result() -> None:
    text = GOOD.replace("Ferritin", "This test").replace("ferritin", "level")

    assert "mentions_flagged" in failed_checks(LOW_FERRITIN, text)


def test_flags_the_wrong_direction() -> None:
    text = GOOD.replace("Your ferritin is low", "Your ferritin is high").replace(
        "Ferritin shows how much iron your body has stored. ", ""
    )

    assert "direction" in failed_checks(LOW_FERRITIN, text)


def test_flags_a_diagnosis() -> None:
    assert "no_diagnosis" in failed_checks(LOW_FERRITIN, GOOD + " This means you have anemia.")


def test_flags_medication_advice() -> None:
    text = GOOD + " You should start taking an iron supplement."

    assert "no_medication_advice" in failed_checks(LOW_FERRITIN, text)


def test_background_about_medicines_is_not_advice() -> None:
    text = GOOD + " Low values can also be seen if you are taking certain stomach medicines."

    assert failed_checks(LOW_FERRITIN, text) == []


def test_the_direction_may_follow_in_the_next_sentence() -> None:
    text = GOOD.replace("Your ferritin is low, which means", "A low level means")

    assert failed_checks(LOW_FERRITIN, text) == []


def test_flags_a_missing_doctor_referral() -> None:
    text = GOOD.replace("with your doctor", "with someone")

    assert "doctor_referral" in failed_checks(LOW_FERRITIN, text)


def test_flags_markdown() -> None:
    assert "plain_text" in failed_checks(LOW_FERRITIN, GOOD.replace("Ferritin", "**Ferritin**"))


def test_flags_a_one_line_answer() -> None:
    assert "length" in failed_checks(LOW_FERRITIN, "Your ferritin is low. See your doctor.")


def test_flags_input_tokens_copied_into_the_text() -> None:
    text = GOOD.replace("Your ferritin is low", "Your ferritin is LOW")

    assert failed_checks(LOW_FERRITIN, text) == ["no_flag_tokens"]
