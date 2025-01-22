import logging

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

    logger.info(f"Running task {cfg.task} on dataset {cfg.dataset}")
    raise NotImplementedError("Function not yet implemented")
