import itertools
import logging
import shutil
from collections.abc import Generator
from pathlib import Path

import meds

logger = logging.getLogger(__name__)

from enum import StrEnum, auto

import hydra
from omegaconf import DictConfig

from ..utils import run_in_env, temp_env
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
        format_kwargs: The remaining template variables to format the command.

    Returns:
        The command to run the model.

    Raises:
        RuntimeError: If the model does not support the given dataset type or run mode.

    Examples:
        >>> commands = {
        ...     "unsupervised": {"train": "train {dataset_dir} {output_dir}"}
        ...     "supervised": {
        ...         "train": "FT data={dataset_dir} labels={labels_dir} output={output_dir}",
        ...         "predict": "predict model_initialization_dir={model_dir} labels={labels_dir}",
        ...     }
        ... }
        >>> fmt_command(commands, "unsupervised", "train", dataset_dir="data", output_dir="output")
        "train data output"
        >>> fmt_command(commands, "supervised", "predict", model_dir="model", labels="labels")
        "predict model_initialization_dir=model labels=labels"

    You can also use the constants in the enumeration objects:
        >>> fmt_command(
        ...     commands, DATASET_TYPE.UNSUPERVISED, RunMode.TRAIN, dataset_dir="data2", output_dir="output2"
        ... )
        "train data2 output2"

    Extra format variables are ignored:
        >>> fmt_command(commands, "supervised", "predict", model_dir="model", labels="labels", out="foo")
        "predict model_initialization_dir=model labels=labels"

    Unsupported commands cause errors:
        >>> fmt_command(commands, "semi-supervised", "predict")
        Traceback (most recent call last):
            ...
        RuntimeError: Model does not support dataset type semi-supervised.
        >>> fmt_command(commands, "supervised", "full")
        Traceback (most recent call last):
            ...
        RuntimeError: Model does not support run mode full.
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

    For a given model run, the configuration may specify to either run a single command or a sequence of
    commands that span multiple (supported) dataset types and run modes. This function yields the appropriate
    sequence of commands to use for the given configuration and model. This sequence may be a single command
    or multiple, and is returned as a generator of tuples of the individual commands and command-specific
    output directories. If the configuration dictates a single run, the output directory will be the specified
    model directory (passed as input via `model_dir`), but if the configuration specifies multiple runs, the
    command-specific output directories will be subdirectories of `model_dir` based on which command is being
    run. In particular, if a command reflects running over dataset type `DATASET_TYPE` and run mode
    `RUN_MODE`, the output directory will be `f"model_dir/{DATASET_TYPE}/{RUN_MODE}"`.

    The configuration indicates that a sequence of commands should be run if either or both of the `cfg.mode`
    and `cfg.dataset_type` are set to `RunMode.FULL` (`"full"`) and `DatasetType.FULL` (`"full"`),
    respectively. Otherwise, only the single specified combination of run mode and dataset type will be run.
    If dataset type is set to `DatasetType.FULL`, the model will be run over both the unsupervised and
    supervised dataset types, in that order (or whichever of those are supported by the model), for the
    specified run mode (or sequence therein). If the run mode is set to full, the model will be run over both
    the "train" and "predict" run modes, in that order (or whichever of those are supported by the model),
    within all specified dataset types.

    Args:
        cfg: The configuration for the model run.
        commands: The dictionary of commands for the model. These are stored in the model folder in the
            `model.yaml` in the `commands` key and are loaded for the correct model from the MODELS variable.
        model_dir: The run-directory of the given model.

    Yields:
        The sequence of base commands (un-formatted) to run for the given model run.

    Raises:
        ValueError: If the configuration specifies a split while the run mode is `RunMode.FULL`. This
        constitutes and error because the split must be set dynamically in run model `RunMode.FULL` as it
        varies across the individual commands.

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
        "demo": cfg.get("demo", False),
    }
    if cfg.get("model_initialization_dir", None):
        format_kwargs["model_initialization_dir"] = cfg.model_initialization_dir
    if cfg.get("split", None):
        if do_set_split:
            raise ValueError(f"Cannot set split manually when mode is {cfg.mode}.")
        format_kwargs["split"] = cfg.split

    if len(run_modes) == 1 and len(dataset_types) == 1:
        run_mode = run_modes[0]
        dataset_type = dataset_types[0]
        format_kwargs["output_dir"] = str(output_dir)
        if dataset_type == DatasetType.SUPERVISED:
            format_kwargs["labels_dir"] = str(cfg.labels_dir)
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
        raise ValueError(f"Model {cfg.model} not currently configured. Available models: {MODELS.keys()}")

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
            logger.info(f"Considering running model command: {cmd}")
            try:
                run_in_env(cmd, out_dir, env=env, do_overwrite=cfg.do_overwrite)
            except Exception as e:  # pragma: no cover
                raise ValueError(f"Failed to run {cfg.model} command {cmd}") from e

    logger.info(f"Model {cfg.model} finished successfully.")
