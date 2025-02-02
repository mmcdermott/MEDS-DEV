import logging
import shutil
import subprocess
from pathlib import Path

import hydra
from omegaconf import DictConfig

from .. import DATASETS
from . import CFG_YAML, TASKS

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path=str(CFG_YAML.parent), config_name=CFG_YAML.stem)
def main(cfg: DictConfig):
    if cfg.task not in TASKS:
        raise ValueError(f"Task {cfg.task} not currently configured")
    if cfg.dataset not in DATASETS:
        raise ValueError(f"Dataset {cfg.dataset} not currently configured")

    task_config_path = TASKS[cfg.task]["criteria_fp"]
    dataset_predicates_path = DATASETS[cfg.dataset]["predicates"]

    if dataset_predicates_path is None:
        raise ValueError(f"Predicates not found for dataset {cfg.dataset}")

    logger.info(f"Running task {cfg.task} on dataset {cfg.dataset}")

    output_dir = Path(cfg.output_dir)
    if cfg.get("do_overwrite", False) and output_dir.exists():  # pragma: no cover
        logger.info(f"Removing existing output directory: {output_dir}")
        shutil.rmtree(output_dir)

        output_dir.mkdir(parents=True, exist_ok=False)

    done_fp = output_dir / ".done"
    if done_fp.exists():  # pragma: no cover
        logger.info(f"Output directory {output_dir} already exists and is marked as done.")
        return

    # make the ACES command
    cmd = " ".join(
        [
            "aces-cli",
            "--multirun",
            f"cohort_name={cfg.task}",
            "data=sharded",
            "data.standard=meds",
            f"data.root={cfg.dataset_dir}/data",
            f"data.shard=$(expand_shards {cfg.dataset_dir}/data)",
            f"config_path={task_config_path}",
            f"predicates_path={dataset_predicates_path}",
            f"output_filepath={cfg.output_dir}" + r"/\$\{data._prefix\}.parquet",
            f"log_dir={cfg.output_dir}/.logs",
        ]
    )

    logger.info(f"Running ACES: {cmd}")
    aces_command_out = subprocess.run(cmd, shell=True, capture_output=True)

    command_errored = aces_command_out.returncode != 0
    if command_errored:
        raise RuntimeError(
            f"Extract {cfg.task} for {cfg.dataset} command {cmd} failed with exit code "
            f"{aces_command_out.returncode}:\n"
            f"STDERR:\n{aces_command_out.stderr.decode()}\n"
            f"STDOUT:\n{aces_command_out.stdout.decode()}"
        )
    logger.info(f"Extract {cfg.task} for {cfg.dataset} command {cmd} finished successfully.")
    done_fp.touch()
