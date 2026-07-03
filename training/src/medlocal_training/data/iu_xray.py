from collections.abc import Sequence
from typing import Any

from datasets import load_dataset

from medlocal_training.data.report_sample import ReportSample
from medlocal_training.data.source import SplitName

_REPO = "CAIR-M3LLM/IU-Xray"


class IuXraySource:
    """Indiana University chest X-ray studies with the R2Gen train/validation/test split."""

    def load(self, split: SplitName) -> Sequence[ReportSample]:
        return [_to_sample(row) for row in load_dataset(_REPO, split=split)]


def _to_sample(row: dict[str, Any]) -> ReportSample:
    # The mirror's user turn hints at the findings of each study, so only the reply is kept.
    findings = next(m["content"] for m in row["messages"] if m["role"] == "assistant")
    return ReportSample(id=row["id"], images=tuple(row["images"]), findings=findings)
