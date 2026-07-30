from collections.abc import Sequence

from medlocal_training.data.chat_format import to_prompt_messages
from medlocal_training.data.pubmedqa import PubMedQaSource
from medlocal_training.data.source import SplitName
from medlocal_training.data.splits import SplitIds
from medlocal_training.data.training_example import TrainingExample
from medlocal_training.labs.analyte import AnalyteCatalog
from medlocal_training.labs.dataset import read_examples
from medlocal_training.labs.prompt import to_explanation_messages
from medlocal_training.trainers.config import LabExplanationData, PubMedQaData


def load_training_examples(
    data: PubMedQaData | LabExplanationData, split: SplitName, seed: int
) -> Sequence[TrainingExample]:
    if isinstance(data, PubMedQaData):
        return _pubmedqa(data, split, seed)
    return _lab_explanations(data, split)


def _pubmedqa(data: PubMedQaData, split: SplitName, seed: int) -> list[TrainingExample]:
    source = PubMedQaSource(SplitIds.read(data.splits_file), data.artificial_train_samples, seed)
    return [
        TrainingExample(to_prompt_messages(sample, source.labels), sample.answer)
        for sample in source.load(split)
    ]


def _lab_explanations(data: LabExplanationData, split: SplitName) -> list[TrainingExample]:
    catalog = AnalyteCatalog.read(data.catalog_file)
    return [
        TrainingExample(to_explanation_messages(example.to_report(catalog)), example.explanation)
        for example in read_examples(data.examples_file)
        if example.split == split
    ]
