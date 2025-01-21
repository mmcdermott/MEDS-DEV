import contextlib
import subprocess
import tempfile
from pathlib import Path

import hydra
from omegaconf import DictConfig

from . import CFG_YAML, DATASETS


@contextlib.contextmanager
def build_environment(cfg: DictConfig) -> Path:
    if cfg.temp_dir is None:
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    else:
        temp_dir = Path(cfg.temp_dir)
        temp_dir.mkdir(exist_ok=True, parents=True)
        yield temp_dir


@hydra.main(version_base=None, config_path=str(CFG_YAML.parent), config_name=CFG_YAML.stem)
def main(cfg: DictConfig):
    if cfg.dataset not in DATASETS:
        raise ValueError(f"Dataset {cfg.dataset} not currently configured!")

    commands = DATASETS[cfg.dataset]["commands"]

    build_cmd = commands["build_demo"] if cfg.demo else commands["build_full"]

    with build_environment(cfg) as build_temp_dir:
        build_cmd = build_cmd.format(output_dir=cfg.output_dir, temp_dir=str(build_temp_dir.resolve()))
        build_command_out = subprocess.run(build_cmd, shell=True, cwd=build_temp_dir, capture_output=True)

        command_errored = build_command_out.returncode != 0
        if command_errored:
            raise RuntimeError(
                f"Build {cfg.dataset} command {build_cmd} failed with exit code "
                f"{build_command_out.returncode}:\n{build_command_out.stderr.decode()}"
            )
