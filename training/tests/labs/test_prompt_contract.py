import json
from pathlib import Path

from medlocal_training.labs.analyte import AnalyteCatalog, Sex
from medlocal_training.labs.prompt import EXPLAINER_SYSTEM, render_report
from medlocal_training.labs.report import LabReport, LabResult

REFERENCE = Path(__file__).parents[3] / "reference"
CONTRACT = json.loads((REFERENCE / "explainer-prompt.json").read_text(encoding="utf-8"))
CATALOG = AnalyteCatalog.read(REFERENCE / "analytes.yaml")


def test_system_prompt_matches_the_contract_shared_with_the_api() -> None:
    assert CONTRACT["system"] == EXPLAINER_SYSTEM


def test_report_rendering_matches_the_contract_shared_with_the_api() -> None:
    example = CONTRACT["example"]
    sex = Sex(example["sex"])
    results = tuple(
        LabResult(
            row["analyte"],
            CATALOG.analytes[row["analyte"]],
            row["value"],
            CATALOG.analytes[row["analyte"]].range_for(sex),
        )
        for row in example["results"]
    )

    assert render_report(LabReport(sex, example["age"], results)) == example["user"]
