from enum import StrEnum
from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, ConfigDict, NonNegativeInt, model_validator


class Sex(StrEnum):
    MALE = "male"
    FEMALE = "female"


class Language(StrEnum):
    ENGLISH = "en"
    TURKISH = "tr"


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ReferenceRange(_Frozen):
    low: float | None
    high: float | None

    @model_validator(mode="after")
    def _has_ordered_bounds(self) -> Self:
        if self.low is None and self.high is None:
            raise ValueError("a reference range needs at least one bound")
        if self.low is not None and self.high is not None and self.low >= self.high:
            raise ValueError(f"low {self.low} is not below high {self.high}")
        return self


class CriticalLimits(_Frozen):
    low: float | None = None
    high: float | None = None


class Analyte(_Frozen):
    name: str
    name_tr: str
    unit: str
    decimals: NonNegativeInt
    measures: str
    measures_tr: str
    ranges: dict[str, ReferenceRange]
    critical: CriticalLimits = CriticalLimits()
    aliases: tuple[str, ...] = ()
    mentions: tuple[str, ...]
    mentions_tr: tuple[str, ...]
    low_context: str | None = None
    low_context_tr: str | None = None
    high_context: str | None = None
    high_context_tr: str | None = None

    @model_validator(mode="after")
    def _is_consistent(self) -> Self:
        keys = set(self.ranges)
        if keys != {"any"} and keys != {Sex.MALE.value, Sex.FEMALE.value}:
            raise ValueError(f"{self.name}: ranges must be 'any' or both sexes, got {sorted(keys)}")

        for side in ("low", "high"):
            bounded = any(getattr(r, side) is not None for r in self.ranges.values())
            for field in (f"{side}_context", f"{side}_context_tr"):
                if bounded and getattr(self, field) is None:
                    raise ValueError(f"{self.name}: a {side} bound needs {field}")
        return self

    def range_for(self, sex: Sex) -> ReferenceRange:
        return self.ranges.get("any") or self.ranges[sex.value]

    def display_name(self, language: Language) -> str:
        return self.name_tr if language is Language.TURKISH else self.name

    def measured_thing(self, language: Language) -> str:
        return self.measures_tr if language is Language.TURKISH else self.measures

    def search_terms(self, language: Language) -> tuple[str, ...]:
        return self.mentions_tr if language is Language.TURKISH else self.mentions

    def context(self, side: str, language: Language) -> str:
        suffix = "_tr" if language is Language.TURKISH else ""
        text: str | None = getattr(self, f"{side}_context{suffix}")
        if text is None:
            raise ValueError(f"{self.name} has no {side} context")
        return text


class AnalyteCatalog(_Frozen):
    panels: dict[str, tuple[str, ...]]
    analytes: dict[str, Analyte]

    @model_validator(mode="after")
    def _panels_use_known_analytes(self) -> Self:
        unknown = {key for keys in self.panels.values() for key in keys} - set(self.analytes)
        if unknown:
            raise ValueError(f"panels reference unknown analytes: {sorted(unknown)}")
        return self

    @classmethod
    def read(cls, path: Path) -> "AnalyteCatalog":
        return cls.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
