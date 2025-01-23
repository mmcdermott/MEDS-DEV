import logging
import subprocess

logger = logging.getLogger(__name__)

import hydra
from omegaconf import DictConfig

from ..utils import temp_env
from . import CFG_YAML, DATASETS


@hydra.main(version_base=None, config_path=str(CFG_YAML.parent), config_name=CFG_YAML.stem)
def main(cfg: DictConfig):
    if cfg.dataset not in DATASETS:
        raise ValueError(f"Dataset {cfg.dataset} not currently configured!")

    commands = DATASETS[cfg.dataset]["commands"]
    requirements = DATASETS[cfg.dataset]["requirements"]

    build_cmd = commands["build_demo"] if cfg.demo else commands["build_full"]

    with temp_env(cfg, requirements) as (build_temp_dir, env):
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
