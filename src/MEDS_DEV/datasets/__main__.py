import contextlib
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

import hydra
from omegaconf import DictConfig

from . import CFG_YAML, DATASETS


def get_venv_bin_path(venv_path):
    """Get the bin/Scripts directory of the virtual environment."""
    if os.name == "nt":  # Windows
        return Path(venv_path) / "Scripts"
    else:  # Unix-like systems
        return Path(venv_path) / "bin"


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
    requirements = DATASETS[cfg.dataset]["requirements"]

    build_cmd = commands["build_demo"] if cfg.demo else commands["build_full"]

    with build_environment(cfg) as build_temp_dir:
        if requirements is not None:
            logger.info(f"Installing requirements from {requirements} into virtual environment.")
            venv_path = build_temp_dir / ".venv"
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)

            venv_bin_path = get_venv_bin_path(venv_path)
            venv_python = venv_bin_path / "python"
            if not venv_python.exists():
                raise RuntimeError(f"Virtual environment python {venv_python} does not exist!")

            subprocess.run(
                [str(venv_python), "-m", "pip", "install", "-r", str(requirements)],
                check=True,
            )

            logger.info(f"Installed requirements from {requirements} into virtual environment.")
            env = os.environ.copy()
            env["PATH"] = f"{str(venv_bin_path)}{os.pathsep}{env['PATH']}"
        else:
            env = os.environ.copy()

        build_cmd = build_cmd.format(output_dir=cfg.output_dir, temp_dir=str(build_temp_dir.resolve()))

        logger.info(f"Running build command: {build_cmd}")
        build_command_out = subprocess.run(
            build_cmd, shell=True, env=env, cwd=build_temp_dir, capture_output=True
        )

        command_errored = build_command_out.returncode != 0
        if command_errored:
            raise RuntimeError(
                f"Build {cfg.dataset} command {build_cmd} failed with exit code "
                f"{build_command_out.returncode}:\n{build_command_out.stderr.decode()}"
            )
