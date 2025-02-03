import logging
import subprocess
from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf

logger = logging.getLogger(__name__)

CONFIG = Path(__file__).parent / "_config.yaml"
pretraining_yaml_template = Path(__file__).parent / "cehrbert_pretrain_template.yaml"


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
    meds_reader_dir.mkdir(exist_ok=True, parents=True)
    logger.info(f"Creating the meds reader now at {meds_reader_dir}")
    run_subprocess(
        cmd=f"meds_reader_convert {cfg.dataset_dir} {meds_reader_dir} --num_threads {cfg.num_threads}",
        temp_work_dir=str(output_dir),
        out_dir=output_dir / "meds_reader",
    )
    # model output
    logger.info(f"Creating the model output at {meds_reader_dir}")
    model_output_dir = get_pretrain_model_dir(output_dir)
    model_output_dir.mkdir(exist_ok=True, parents=True)

    # dataset_prepared_path
    dataset_prepared_path = output_dir / "dataset_prepared_path"
    logger.info(f"Creating the dataset_prepared output at {dataset_prepared_path}")
    dataset_prepared_path.mkdir(exist_ok=True, parents=True)

    # Open the YAML file
    pretraining_yaml_file = output_dir / "cehrbert_pretraining.yaml"
    logger.info(f"Writing the pretraining yaml file to {pretraining_yaml_file}")
    pretraining_yaml = OmegaConf.load(str(pretraining_yaml_template))
    pretraining_yaml["model_name_or_path"] = str(model_output_dir.resolve())
    pretraining_yaml["tokenizer_name_or_path"] = str(model_output_dir.resolve())
    pretraining_yaml["output_dir"] = str(model_output_dir.resolve())
    pretraining_yaml["data_folder"] = str(meds_reader_dir.resolve())
    pretraining_yaml["dataset_prepared_path"] = str(dataset_prepared_path.resolve())
    pretraining_yaml["dataloader_num_workers"] = cfg.num_threads
    pretraining_yaml["seed"] = cfg.seed

    if cfg.get("demo", False):
        pretraining_yaml["max_position_embeddings"] = 512
        pretraining_yaml["hidden_size"] = 128
        pretraining_yaml["evaluation_strategy"] = "steps"
        pretraining_yaml["save_strategy"] = "steps"
        pretraining_yaml["max_steps"] = 10
        pretraining_yaml["per_device_train_batch_size"] = 1

    # Assuming 'pretraining_yaml' is a DictConfig object
    pretraining_yaml_string = OmegaConf.to_yaml(pretraining_yaml)
    # Now write this string to a file
    with open(pretraining_yaml_file, "w") as file:
        file.write(pretraining_yaml_string)

    logger.info("Starting the cehrbert pretraining runner")
    run_subprocess(
        cmd=f"python -u -m cehrbert.runners.hf_cehrbert_pretrain_runner {pretraining_yaml_file}",
        temp_work_dir=str(output_dir),
        out_dir=model_output_dir,
    )


if __name__ == "__main__":
    main()
