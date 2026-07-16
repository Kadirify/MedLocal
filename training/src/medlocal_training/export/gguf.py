import os
import subprocess
import sys
from pathlib import Path

_CONVERT_SCRIPT = "convert_hf_to_gguf.py"


class LlamaCppNotFoundError(FileNotFoundError):
    pass


def convert_to_gguf(model_dir: Path, llama_cpp_dir: Path, output_file: Path, outtype: str) -> None:
    script = llama_cpp_dir / _CONVERT_SCRIPT
    if not script.is_file():
        raise LlamaCppNotFoundError(
            f"{script} is missing; clone https://github.com/ggml-org/llama.cpp into {llama_cpp_dir}"
        )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    # the script has to run against the gguf package of the same checkout
    environment = {**os.environ, "PYTHONPATH": str(llama_cpp_dir / "gguf-py")}
    command = [sys.executable, str(script), str(model_dir)]
    command += ["--outfile", str(output_file), "--outtype", outtype]
    subprocess.run(command, env=environment, check=True)
