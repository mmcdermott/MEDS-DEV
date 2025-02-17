import meds_reader
import femr.splits
import femr.models.tokenizer
import pickle
import femr.models.tasks
import femr.models.processor
import femr.models.tasks
import logging
import subprocess
from pathlib import Path
import transformers
import femr.models.transformer
import hydra
from omegaconf import DictConfig, OmegaConf

logger = logging.getLogger(__name__)

CONFIG = Path(__file__).parent / "_config.yaml"
pretraining_yaml_template = Path(__file__).parent / "motor_pretrain_template.yaml"


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
    return output_dir / "pretrained_motor"


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
    pretraining_yaml_file = output_dir / "motor_pretraining.yaml"
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
        pretraining_yaml["vocab_size"] = 128 # TODO
        pretraining_yaml["num_tasks"] = 64
        pretraining_yaml["num_bins"] = 4
        pretraining_yaml["final_layer_size"] = 32
        pretraining_yaml["tokens_per_batch"] = 32
        pretraining_yaml["num_proc"] = 4

    # Assuming 'pretraining_yaml' is a DictConfig object
    pretraining_yaml_string = OmegaConf.to_yaml(pretraining_yaml)
    # Now write this string to a file
    with open(pretraining_yaml_file, "w") as file:
        file.write(pretraining_yaml_string)
        
    # First, we want to split our dataset into train, valid, and test
    # We do this by calling our split functionality twice
    logger.info("Loading MEDS reader database")
    database = meds_reader.SubjectDatabase(meds_reader_dir)
    main_split = femr.splits.generate_hash_split(list(database), 97, frac_test=0.15)
    main_database = database.filter(main_split.train_subject_ids)
    train_database = main_database.filter(train_split.train_subject_ids)
    val_database = main_database.filter(train_split.test_subject_ids)

    # Second, train the tokenizer
    logger.info("Training MOTOR tokenizer")
    with open('input/ontology.pkl', 'rb') as f:
        ontology = pickle.load(f)
    tokenizer = femr.models.tokenizer.train_tokenizer(
        train_database, 
        vocab_size=pretraining_yaml["vocab_size"], 
        is_hierarchical=True, # Note, we need to use a hierarchical tokenizer for MOTOR
        ontology=ontology
    )
    tokenizer.save_pretrained(os.path.join(TARGET_DIR, "motor_model"))

    # Third, prefit the MOTOR model. This is necessary because piecewise exponential models are unstable without an initial fit
    logger.info("Prefitting MOTOR model")
    motor_task = femr.models.tasks.MOTORTask.fit_pretraining_task_info(
        train_database, 
        tokenizer, 
        num_tasks=pretraining_yaml["num_tasks"], 
        num_bins=pretraining_yaml["num_bins"], 
        final_layer_size=pretraining_yaml["final_layer_size"]
    )
    # It's recommended to save this with pickle to avoid recomputing since it's an expensive operation
    # TODO
    
    # Fourth, create batches. 
    logger.info("Creating batches")
    processor = femr.models.processor.FEMRBatchProcessor(tokenizer, motor_task)
    train_batches = processor.convert_dataset(train_database, 
                                              tokens_per_batch=pretraining_yaml["tokens_per_batch"], 
                                              num_proc=pretraining_yaml["num_proc"])
    val_batches = processor.convert_dataset(val_database, 
                                            tokens_per_batch=pretraining_yaml["tokens_per_batch"], 
                                            num_proc=pretraining_yaml["num_proc"])
    train_batches.set_format("pt")
    val_batches.set_format("pt")
    
    # Fifth, train MOTOR using Huggingface's Trainer.
    logger.info("Setting up MOTOR configs")
    transformer_config = femr.models.config.FEMRTransformerConfig(
        vocab_size=tokenizer.vocab_size, 
        is_hierarchical=tokenizer.is_hierarchical, 
        n_layers=2,
        hidden_size=64, 
        intermediate_size=64*2,
        n_heads=8,
    )
    config = femr.models.config.FEMRModelConfig.from_transformer_task_configs(transformer_config, motor_task.get_task_config())
    model = femr.models.transformer.FEMRModel(config)
    collator = processor.collate

    trainer_config = transformers.TrainingArguments(
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        output_dir='tmp_trainer',
        remove_unused_columns=False,
        num_train_epochs=100,
        eval_steps=20,
        evaluation_strategy="steps",
        logging_steps=20,
        logging_strategy='steps',
        prediction_loss_only=True,
    )

    trainer = transformers.Trainer(
        model=model,
        data_collator=processor.collate,
        train_dataset=train_batches,
        eval_dataset=val_batches,
        args=trainer_config,
    )
    logger.info("Training MOTOR model")
    trainer.train()
    logger.info("Saving MOTOR model")
    model.save_pretrained(os.path.join(TARGET_DIR, 'motor_model'))
    logger.info("Done!")


if __name__ == "__main__":
    main()
