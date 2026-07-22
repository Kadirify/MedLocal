import pytest

from medlocal_training.labs.analyte import ReferenceRange
from medlocal_training.labs.report import Flag, flag_value

BOTH = ReferenceRange(low=3.6, high=5.2)


@pytest.mark.parametrize(
    ("value", "expected"),
    [(3.5, Flag.LOW), (3.6, Flag.NORMAL), (4.4, Flag.NORMAL), (5.2, Flag.NORMAL), (5.3, Flag.HIGH)],
)
def test_bounds_themselves_are_normal(value: float, expected: Flag) -> None:
    assert flag_value(value, BOTH) is expected


def test_a_range_without_a_low_bound_never_flags_low() -> None:
    assert flag_value(0.0, ReferenceRange(low=None, high=99)) is Flag.NORMAL


def test_a_range_without_a_high_bound_never_flags_high() -> None:
    assert flag_value(500.0, ReferenceRange(low=40, high=None)) is Flag.NORMAL


def test_a_range_needs_a_bound() -> None:
    with pytest.raises(ValueError, match="at least one bound"):
        ReferenceRange(low=None, high=None)


def test_a_range_needs_ordered_bounds() -> None:
    with pytest.raises(ValueError, match="not below"):
        ReferenceRange(low=5, high=5)
