from pathlib import Path

import pytest

from medlocal_training.labs.analyte import Analyte, AnalyteCatalog, ReferenceRange, Sex

CATALOG_FILE = Path(__file__).parents[3] / "reference" / "analytes.yaml"


def test_the_shipped_catalog_is_valid() -> None:
    catalog = AnalyteCatalog.read(CATALOG_FILE)

    assert len(catalog.analytes) >= 55
    assert all(catalog.panels.values())


def test_critical_limits_lie_outside_the_reference_range() -> None:
    catalog = AnalyteCatalog.read(CATALOG_FILE)

    for analyte in catalog.analytes.values():
        for reference in analyte.ranges.values():
            if analyte.critical.low is not None and reference.low is not None:
                assert analyte.critical.low < reference.low, analyte.name
            if analyte.critical.high is not None and reference.high is not None:
                assert analyte.critical.high > reference.high, analyte.name


def test_sex_specific_ranges_are_picked_by_sex() -> None:
    catalog = AnalyteCatalog.read(CATALOG_FILE)
    hemoglobin = catalog.analytes["hemoglobin"]

    assert hemoglobin.range_for(Sex.FEMALE) != hemoglobin.range_for(Sex.MALE)


def test_a_bound_without_context_is_rejected() -> None:
    with pytest.raises(ValueError, match="needs low_context"):
        Analyte(
            name="X",
            name_tr="X",
            unit="u",
            decimals=0,
            measures="x",
            measures_tr="x",
            mentions=("x",),
            mentions_tr=("x",),
            ranges={"any": ReferenceRange(low=1, high=2)},
            high_context="h",
            high_context_tr="h",
        )
