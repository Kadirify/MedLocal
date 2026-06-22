import pytest
import torch

from medlocal_training.device import CudaUnavailableError, require_cuda


def test_raises_when_cuda_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)

    with pytest.raises(CudaUnavailableError):
        require_cuda()


@pytest.mark.skipif(not torch.cuda.is_available(), reason="needs a CUDA device")
def test_reports_the_installed_gpu() -> None:
    gpu = require_cuda()

    assert gpu.name
    assert gpu.total_vram_gb > 0
