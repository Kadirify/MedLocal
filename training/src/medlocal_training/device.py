from dataclasses import dataclass

import torch


class CudaUnavailableError(RuntimeError):
    pass


@dataclass(frozen=True)
class GpuInfo:
    name: str
    total_vram_gb: float
    compute_capability: tuple[int, int]
    torch_version: str
    cuda_version: str | None


def require_cuda() -> GpuInfo:
    if not torch.cuda.is_available():
        raise CudaUnavailableError(
            f"torch {torch.__version__} cannot see a CUDA device; "
            "check the driver and that torch was installed from the cu128 index"
        )

    props = torch.cuda.get_device_properties(0)
    return GpuInfo(
        name=props.name,
        total_vram_gb=round(props.total_memory / 1024**3, 1),
        compute_capability=(props.major, props.minor),
        torch_version=torch.__version__,
        cuda_version=torch.version.cuda,
    )
