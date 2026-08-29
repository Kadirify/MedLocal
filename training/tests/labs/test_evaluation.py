from pathlib import Path

import pytest

from medlocal_training.labs.analyte import AnalyteCatalog, Language, Sex
from medlocal_training.labs.evaluation import score_explanations
from medlocal_training.labs.report import LabReport, LabResult

CATALOG = AnalyteCatalog.read(Path(__file__).parents[3] / "reference" / "analytes.yaml")
FERRITIN = CATALOG.analytes["ferritin"]
LAB_REPORT = LabReport(
    sex=Sex.FEMALE,
    age=30,
    results=(LabResult("ferritin", FERRITIN, 5, FERRITIN.range_for(Sex.FEMALE)),),
)
REPORT = (LAB_REPORT, Language.ENGLISH)
FILLER = " ".join(["This sentence only adds length to the text."] * 6)
CAREFUL = f"Here is an overview. Ferritin is low. {FILLER} Please talk to your doctor."
CARELESS = f"Here is an overview. Ferritin is low. {FILLER} You have anemia."


def test_counts_explanations_that_pass_every_check() -> None:
    metrics = score_explanations([REPORT, REPORT], [CAREFUL, CAREFUL], [CAREFUL, CARELESS])

    assert metrics.passed_every_check == 0.5
    assert metrics.failure_rate_per_check == {"doctor_referral": 0.5, "no_diagnosis": 0.5}


def test_an_explanation_identical_to_the_teacher_has_full_overlap() -> None:
    metrics = score_explanations([REPORT], [CAREFUL], [CAREFUL])

    assert metrics.rouge_l_to_teacher == 1.0


def test_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError, match="differ in length"):
        score_explanations([REPORT], [CAREFUL], [])
