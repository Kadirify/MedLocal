import json
from pathlib import Path

import pytest

from medlocal_training.labs.analyte import AnalyteCatalog, Language, Sex
from medlocal_training.labs.prompt import explainer_system, render_report
from medlocal_training.labs.report import LabReport, LabResult

REFERENCE = Path(__file__).parents[3] / "reference"
CONTRACT = json.loads((REFERENCE / "explainer-prompt.json").read_text(encoding="utf-8"))
CATALOG = AnalyteCatalog.read(REFERENCE / "analytes.yaml")


def _example_report() -> LabReport:
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
    return LabReport(sex, example["age"], results)


def test_the_contract_covers_every_language() -> None:
    assert set(CONTRACT["languages"]) == {language.value for language in Language}


@pytest.mark.parametrize("language", list(Language))
def test_system_prompt_matches_the_contract_shared_with_the_api(language: Language) -> None:
    assert CONTRACT["languages"][language.value]["system"] == explainer_system(language)


@pytest.mark.parametrize("language", list(Language))
def test_report_rendering_matches_the_contract_shared_with_the_api(language: Language) -> None:
    expected = CONTRACT["languages"][language.value]["user"]

    assert render_report(_example_report(), language) == expected
