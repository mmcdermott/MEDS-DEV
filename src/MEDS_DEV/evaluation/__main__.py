import logging
import shutil
import subprocess
from pathlib import Path

import hydra
from omegaconf import DictConfig

from . import CFG_YAML

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path=str(CFG_YAML.parent), config_name=CFG_YAML.stem)
def main(cfg: DictConfig):
    output_dir = Path(cfg.output_dir)
    if cfg.get("do_overwrite", False) and output_dir.exists():  # pragma: no cover
        logger.info(f"Removing existing output directory: {output_dir}")
        shutil.rmtree(output_dir)

        output_dir.mkdir(parents=True, exist_ok=False)

    done_fp = output_dir / ".done"
    if done_fp.exists():  # pragma: no cover
        logger.info(f"Output directory {output_dir} already exists and is marked as done.")
        return

    cmd_parts = [
        "meds-evaluation-cli",
        f'predictions_path="{cfg.predictions_path}"',
        f'output_dir="{cfg.output_dir}"',
    ]
    cmd = " ".join(cmd_parts)

    logger.info(f"Running MEDS-Evaluation: {cmd}")
    evaluation_command_out = subprocess.run(cmd, shell=True, capture_output=True)

    command_errored = evaluation_command_out.returncode != 0
    if command_errored:
        raise RuntimeError(
            f"Evaluation command {cmd} failed with exit code "
            f"{evaluation_command_out.returncode}:\n"
            f"STDERR:\n{evaluation_command_out.stderr.decode()}\n"
            f"STDOUT:\n{evaluation_command_out.stdout.decode()}"
        )
    logger.info(f"Evaluation command {cmd} finished successfully.")
    done_fp.touch()
