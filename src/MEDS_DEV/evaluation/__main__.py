import logging

import hydra
from omegaconf import DictConfig

from ..utils import run_in_env
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

    run_in_env(cmd=cmd, env=None, output_dir=cfg.output_dir, do_overwrite=cfg.get("do_overwrite", False))

    logger.info(f"Evaluation command {cmd} finished successfully.")
