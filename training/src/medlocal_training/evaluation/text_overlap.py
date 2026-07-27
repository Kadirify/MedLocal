import re
from collections.abc import Sequence

_WORD = re.compile(r"[a-z0-9]+")


def rouge_l(reference: str, candidate: str) -> float:
    """F1 over the longest common subsequence of words, ignoring case and punctuation."""
    reference_words, candidate_words = _words(reference), _words(candidate)
    common = _longest_common_subsequence(reference_words, candidate_words)
    if common == 0:
        return 0.0

    precision = common / len(candidate_words)
    recall = common / len(reference_words)
    return 2 * precision * recall / (precision + recall)


def _words(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def _longest_common_subsequence(a: Sequence[str], b: Sequence[str]) -> int:
    previous = [0] * (len(b) + 1)
    for item in a:
        current = [0]
        for index, other in enumerate(b, start=1):
            if item == other:
                current.append(previous[index - 1] + 1)
            else:
                current.append(max(previous[index], current[-1]))
        previous = current
    return previous[-1]
