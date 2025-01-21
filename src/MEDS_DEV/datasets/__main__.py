import hydra
from omegaconf import DictConfig

from . import CFG_YAML, DATASETS


@hydra.main(version_base=None, config_path=str(CFG_YAML.parent), config_name=CFG_YAML.stem)
def main(cfg: DictConfig):
    if cfg.dataset not in DATASETS:
        raise ValueError(f"Dataset {cfg.dataset} not currently configured!")

    raise NotImplementedError("This is a placeholder function. Please implement the functionality.")
