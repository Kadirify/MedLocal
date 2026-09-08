import json
from pathlib import Path

from medlocal_training.labs.analyte import AnalyteCatalog, Language, Sex
from medlocal_training.labs.prompt import explainer_system, render_report, rendering_templates
from medlocal_training.labs.report import LabReport, LabResult

_VERSION = 3

# one result of every rendering kind: two-sided, upper-only and lower-only ranges, each flag,
# sex-specific ranges and the different numbers of decimals
_EXAMPLE_SEX = Sex.FEMALE
_EXAMPLE_AGE = 34
_EXAMPLE_VALUES = {
    "hemoglobin": 10.8,
    "mcv": 74.0,
    "white_blood_cells": 6.21,
    "ferritin": 8,
    "hdl_cholesterol": 62,
    "ldl_cholesterol": 131,
    "tsh": 2.1,
}


def write_prompt_contract(catalog: AnalyteCatalog, path: Path) -> None:
    """Writes the prompt the explainer is trained on; the API loads it and is tested against it."""
    results = tuple(
        LabResult(key, analyte, value, analyte.range_for(_EXAMPLE_SEX))
        for key, value in _EXAMPLE_VALUES.items()
        for analyte in [catalog.analytes[key]]
    )
    report = LabReport(_EXAMPLE_SEX, _EXAMPLE_AGE, results)

    contract = {
        "version": _VERSION,
        "example": {
            "sex": _EXAMPLE_SEX.value,
            "age": _EXAMPLE_AGE,
            "results": [{"analyte": k, "value": v} for k, v in _EXAMPLE_VALUES.items()],
        },
        "languages": {
            language.value: {
                "system": explainer_system(language),
                "templates": rendering_templates(language),
                "user": render_report(report, language),
            }
            for language in Language
        },
    }
    path.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
