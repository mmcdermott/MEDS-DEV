import logging
import subprocess
from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf

logger = logging.getLogger(__name__)

CONFIG = Path(__file__).parent / "_config.yaml"
pretraining_yaml_template = Path(__file__).parent / "cehrbert_pretrain_template.yaml"
DEMO_DEFAULT_STEPS = 10
STEPS_STRATEGY = "steps"
EPOCH_STRATEGY = "epoch"


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

    # Logic for handling streaming
    demo = cfg.get("demo", False)
    streaming = cfg.get("streaming", demo)
    max_steps = cfg.get("max_steps", None) if not demo else DEMO_DEFAULT_STEPS
    save_steps = cfg.get("save_steps", None) if not demo else DEMO_DEFAULT_STEPS
    eval_steps = cfg.get("eval_steps", None)
    save_strategy = cfg.get("save_strategy", STEPS_STRATEGY)
    evaluation_strategy = cfg.get("evaluation_strategy", STEPS_STRATEGY)
    logging_steps = cfg.get("logging_steps", DEMO_DEFAULT_STEPS if demo else None)
    load_best_model_at_end = cfg.get("load_best_model_at_end", False)

    if streaming and max_steps is None:
        raise RuntimeError(
            f"When streaming is set to True, max_steps must be a non-negative integer. "
            f"Current max_steps: {max_steps}"
        )
    if save_strategy == STEPS_STRATEGY and save_steps is None:
        raise RuntimeError(
            f"When streaming is set to True, save_steps must be a non-negative integer. "
            f"Current max_steps: {save_steps}"
        )
    # eval_steps defaults to logging_steps if not provided, we should set it to the same as save_steps
    if evaluation_strategy == STEPS_STRATEGY and eval_steps is None:
        logging.warning(
            "The current eval_steps is None and will default to logging_steps: %s. "
            "This will result in frequent evaluation, we set eval_steps to save_steps: %s",
            logging_steps,
            save_steps,
        )
        eval_steps = save_steps

    pretraining_yaml["streaming"] = streaming
    pretraining_yaml["max_steps"] = max_steps
    pretraining_yaml["save_steps"] = save_steps
    pretraining_yaml["eval_steps"] = eval_steps
    pretraining_yaml["evaluation_strategy"] = evaluation_strategy
    pretraining_yaml["save_strategy"] = save_strategy
    pretraining_yaml["load_best_model_at_end"] = load_best_model_at_end

    # Demo specific setting to speed up the test
    if demo:
        pretraining_yaml["hidden_size"] = 64
        pretraining_yaml["max_position_embeddings"] = 128
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
