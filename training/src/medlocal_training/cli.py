import argparse
import sys
from collections.abc import Callable

from medlocal_training.device import CudaUnavailableError, require_cuda


def _doctor() -> int:
    try:
        gpu = require_cuda()
    except CudaUnavailableError as error:
        print(error, file=sys.stderr)
        return 1

    major, minor = gpu.compute_capability
    print(f"gpu      {gpu.name}")
    print(f"vram     {gpu.total_vram_gb} GB")
    print(f"compute  sm_{major}{minor}")
    print(f"torch    {gpu.torch_version} (cuda {gpu.cuda_version})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="medlocal")
    commands = parser.add_subparsers(dest="command", required=True)
    doctor = commands.add_parser("doctor", help="check that the GPU is usable for training")
    doctor.set_defaults(handler=_doctor)

    args = parser.parse_args()
    handler: Callable[[], int] = args.handler
    return handler()


if __name__ == "__main__":
    raise SystemExit(main())
