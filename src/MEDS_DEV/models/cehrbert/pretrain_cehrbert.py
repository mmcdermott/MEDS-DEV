import logging
import subprocess
from importlib.resources import files
from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf

logger = logging.getLogger(__name__)

CONFIG = files("MEDS_DEV") / "models" / "cehrbert" / "_config.yaml"
pretraining_yaml_template = files("MEDS_DEV") / "models" / "cehrbert" / "cehrbert_pretrain_template.yaml"


def run_subprocess(cmd: str, temp_work_dir: str, out_dir: Path) -> None:
    done_file = out_dir / ".done"
    if done_file.exists():
        logger.info(f"Skipping {cmd} because {done_file} exists.")
        return

    logger.info(f"Running model command: {cmd}")
    command_out = subprocess.run(cmd, shell=True, cwd=temp_work_dir, capture_output=True)
    command_errored = command_out.returncode != 0
    if command_errored:
        raise RuntimeError(
            f"{cmd} failed with exit code "
            f"{command_out.returncode}:\n"
            f"STDERR:\n{command_out.stderr.decode()}\n"
            f"STDOUT:\n{command_out.stdout.decode()}"
        )
    elif not out_dir.is_dir():
        raise RuntimeError(
            f"{cmd} failed to create output directory {out_dir}.\n"
            f"STDERR:\n{command_out.stderr.decode()}\n"
            f"STDOUT:\n{command_out.stdout.decode()}"
        )
    else:
        done_file.touch()


def get_pretrain_model_dir(output_dir: Path) -> Path:
    return output_dir / "pretrained_cehrbert"


@hydra.main(version_base=None, config_path=str(CONFIG.parent.resolve()), config_name=CONFIG.stem)
def main(cfg: DictConfig) -> None:
    output_dir = Path(cfg.output_dir)
    # Create the meds_reader database
    meds_reader_dir = output_dir / "meds_reader"
    meds_reader_dir.mkdir(exist_ok=True)
    run_subprocess(
        cmd=f"meds_reader_convert {cfg.dataset_dir} {meds_reader_dir} --num_threads {cfg.num_threads}",
        temp_work_dir=str(output_dir),
        out_dir=output_dir / "meds_reader",
    )
    # model output
    model_output_dir = get_pretrain_model_dir(output_dir)
    model_output_dir.mkdir(exist_ok=True)

    # Open the YAML file
    pretraining_yaml_file = output_dir / "cehrbert_pretraining.yaml"
    pretraining_yaml = OmegaConf.load(str(pretraining_yaml_template))
    pretraining_yaml["model_name_or_path"] = model_output_dir
    pretraining_yaml["tokenizer_name_or_path"] = model_output_dir
    pretraining_yaml["output_dir"] = model_output_dir
    pretraining_yaml["data_folder"] = meds_reader_dir
    pretraining_yaml["dataset_prepared_path"] = output_dir / "dataset_prepared_path"
    pretraining_yaml["dataloader_num_workers"] = cfg.num_threads
    pretraining_yaml["seed"] = cfg.seed
    pretraining_yaml.to_yaml(pretraining_yaml_file)

    run_subprocess(
        cmd=f"python -u -m cehrbert.runners.hf_cehrbert_pretrain_runner {pretraining_yaml_file}",
        temp_work_dir=str(output_dir),
        out_dir=model_output_dir,
    )
