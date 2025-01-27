import logging
import subprocess

import hydra
from omegaconf import DictConfig

from . import CFG_YAML

logger = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path=str(CFG_YAML.parent), config_name=CFG_YAML.stem)
def main(cfg: DictConfig):
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
