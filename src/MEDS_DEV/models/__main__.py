import itertools
import logging
import shutil
import subprocess
from collections.abc import Generator
from pathlib import Path

import meds

logger = logging.getLogger(__name__)

from enum import StrEnum, auto

import hydra
from omegaconf import DictConfig

from ..utils import temp_env
from . import CFG_YAML, MODELS


class RunMode(StrEnum):
    """The different run modes supported.

    Args:
        TRAIN: Train a model.
        PREDICT: Predict with a model.
        FULL: Perform all viable stages for a model.
    """

    TRAIN = auto()
    PREDICT = auto()
    FULL = auto()


ALL_RUN_MODES = [RunMode.TRAIN, RunMode.PREDICT]


class DatasetType(StrEnum):
    """The different dataset types supported.

    Args:
        UNSUPERVISED: Unsupervised dataset.
        SUPERVISED: Supervised dataset.
        FULL: Run the model across both the unsupervised and supervised datasets.
    """

    UNSUPERVISED = auto()
    SUPERVISED = auto()
    FULL = auto()


ALL_DATASET_TYPES = [DatasetType.UNSUPERVISED, DatasetType.SUPERVISED]

COMMANDS_DICT_T = dict[str, dict[str, str]]


def fmt_command(
    commands: COMMANDS_DICT_T, dataset_type: DatasetType, run_mode: RunMode, **format_kwargs
) -> str:
    """Gets the appropriate model command for the given run mode and commands dictionary.

    Args:
        commands: The dictionary of commands for the model. These are stored in the model folder in
            `model.yaml` in the `commands` key and are loaded for the correct model from the MODELS
            dictionary.
        dataset_type: The dataset type to use.
        run_mode: The run mode to use.

    Returns:
        The command to run the model.

    Examples:
        >>> TODO
    """

    if dataset_type not in commands:
        raise RuntimeError(f"Model does not support dataset type {dataset_type}.")

    dataset_commands = commands[dataset_type]
    if run_mode not in dataset_commands:
        raise RuntimeError(f"Model does not support run mode {run_mode}.")

    return commands[dataset_type][run_mode].format(**format_kwargs)


def model_commands(
    cfg: DictConfig, commands: dict[str, dict[str, str]], model_dir: Path
) -> Generator[tuple[str, Path]]:
    """Yields the sequence of appropriate dataset, run mode pairs for the given config and commands.

    Args:
        cfg: TODO
        commands: TODO

    Yields:
        The sequence of base commands (un-formatted) to run for the given model run.

    Examples:
        >>> TODO
    """

    run_modes = ALL_RUN_MODES if cfg.mode == RunMode.FULL else [cfg.mode]
    dataset_types = ALL_DATASET_TYPES if cfg.dataset_type == DatasetType.FULL else [cfg.dataset_type]

    do_set_split = cfg.mode == RunMode.FULL

    output_dir = Path(cfg.output_dir)

    format_kwargs = {
        "dataset_dir": str(cfg.dataset_dir),
        "model_dir": str(model_dir),
    }
    if cfg.get("model_initialization_dir", None):
        format_kwargs["model_initialization_dir"] = cfg.model_initialization_dir
    if cfg.get("demo", False):
        format_kwargs["demo"] = True
    if cfg.get("split", None):
        if do_set_split:
            raise ValueError(f"Cannot set split manually when mode is {cfg.mode}.")
        format_kwargs["split"] = cfg.split

    if len(run_modes) == 1 and len(dataset_types) == 1:
        run_mode = run_modes[0]
        dataset_type = dataset_types[0]
        format_kwargs["output_dir"] = str(output_dir)

        yield fmt_command(commands, dataset_type, run_mode, **format_kwargs), output_dir
        return

    all_modes = itertools.product(run_modes, dataset_types)
    for run_mode, dataset_type in all_modes:
        dataset_commands = commands.get(dataset_type, None)
        if dataset_commands is None:
            continue

        run_command = dataset_commands.get(run_mode, None)
        if not run_command:
            continue

        run_output_dir = output_dir / cfg.dataset_name
        if dataset_type == DatasetType.SUPERVISED:
            run_output_dir = run_output_dir / cfg.task_name
            format_kwargs["labels_dir"] = str(cfg.labels_dir)
        else:
            run_output_dir = run_output_dir / dataset_type

        run_output_dir = run_output_dir / run_mode

        format_kwargs["output_dir"] = str(run_output_dir)

        if do_set_split:
            if run_mode == RunMode.PREDICT:
                format_kwargs["split"] = meds.held_out_split
            else:
                # We don't set the split in anything but predict mode.
                format_kwargs.pop("split", None)

        yield (fmt_command(commands, dataset_type, run_mode, **format_kwargs), run_output_dir)

        if run_mode != RunMode.PREDICT:
            format_kwargs["model_initialization_dir"] = str(run_output_dir)


@hydra.main(version_base=None, config_path=str(CFG_YAML.parent), config_name=CFG_YAML.stem)
def main(cfg: DictConfig):
    if cfg.model not in MODELS:
        raise ValueError(f"Model {cfg.model} not currently configured")

    commands = MODELS[cfg.model]["commands"]
    model_dir = MODELS[cfg.model]["model_dir"]
    requirements = MODELS[cfg.model]["requirements"]

    output_dir = Path(cfg.output_dir)
    if cfg.get("do_overwrite", False) and output_dir.exists():  # pragma: no cover
        logger.info(f"Removing existing output directory: {output_dir}")
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    with temp_env(cfg, requirements) as (temp_dir, env):
        for cmd, out_dir in model_commands(cfg, commands, model_dir):
            done_file = out_dir / ".done"
            if done_file.exists():
                logger.info(f"Skipping {cmd} because {done_file} exists.")
                continue

            logger.info(f"Running model command: {cmd}")
            command_out = subprocess.run(cmd, shell=True, env=env, cwd=temp_dir, capture_output=True)

            command_errored = command_out.returncode != 0
            if command_errored:
                raise RuntimeError(
                    f"{cfg.model} command {cmd} failed with exit code "
                    f"{command_out.returncode}:\n"
                    f"STDERR:\n{command_out.stderr.decode()}\n"
                    f"STDOUT:\n{command_out.stdout.decode()}"
                )
            elif not out_dir.is_dir():
                raise RuntimeError(
                    f"{cfg.model} command {cmd} failed to create output directory {out_dir}.\n"
                    f"STDERR:\n{command_out.stderr.decode()}\n"
                    f"STDOUT:\n{command_out.stdout.decode()}"
                )
            else:
                done_file.touch()
    logger.info(f"Model {cfg.model} finished successfully.")
