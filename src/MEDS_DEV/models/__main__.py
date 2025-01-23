import contextlib
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

from enum import StrEnum

import hydra
from omegaconf import DictConfig

from ..utils import temp_env
from . import CFG_YAML, MODELS


class RunMode(StrEnum):


def get_model_command(cfg: DictConfig, commands: dict[str, dict[str, str]], temp_dir: Path) -> str:
    """Gets the appropriate model command for the given run mode and commands dictionary.

    Args:
        cfg: The configuration dictionary for the model run. See `_run_model.yaml` for details.
        commands: The dictionary of commands for the model. These are stored in the model folder in
            `model.yaml` in the `commands` key and are loaded for the correct model from the MODELS
            dictionary.
        temp_dir: The temporary directory to use for the model run.

    Returns:
        The command to run the model.

    Examples:
        >>> TODO
    """
    raise NotImplementedError("TODO")  # TODO

@hydra.main(version_base=None, config_path=str(CFG_YAML.parent), config_name=CFG_YAML.stem)
def main(cfg: DictConfig):
    if cfg.model not in MODELS:
        raise ValueError(f"Model {cfg.model} not found in available models: {MODELS.keys()}")

    commands = MODELS[cfg.model]["commands"]
    requirements = MODELS[cfg.model]["requirements"]

    with temp_env(cfg, requirements) as (temp_dir, env):
        cmd = get_model_command(cfg, commands, temp_dir)

        logger.info(f"Running model command: {cmd}")
        command_out = subprocess.run(
            cmd, shell=True, env=env, cwd=temp_dir, capture_output=True
        )

        command_errored = command_out.returncode != 0
        if command_errored:
            raise RuntimeError(
                f"{cfg.model} command {cmd} failed with exit code "
                f"{command_out.returncode}:\n{command_out.stderr.decode()}"
            )
