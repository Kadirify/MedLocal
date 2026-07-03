from dataclasses import dataclass

from PIL.Image import Image


@dataclass(frozen=True)
class ReportSample:
    id: str
    images: tuple[Image, ...]
    findings: str
