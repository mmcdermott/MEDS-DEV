import logging
from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf

from .pretrain_cehrbert import get_pretrain_model_dir, run_subprocess

logger = logging.getLogger(__name__)

CONFIG = Path(__file__).parent / "_config.yaml"
finetune_yaml_template = Path(__file__).parent / "cehrbert_finetune_template.yaml"


@hydra.main(version_base=None, config_path=str(CONFIG.parent.resolve()), config_name=CONFIG.stem)
def main(cfg: DictConfig) -> None:
    # Get the output dir
    output_dir = Path(cfg.output_dir)
    # Infer the task label
    task_label_name = Path(cfg.labels_dir).name
    # meds_reader dir
    meds_reader_dir = output_dir / "meds_reader"
    # Pretrained model dir
    pretrained_model_dir = get_pretrain_model_dir(output_dir)
    # Fine-tuned model dir
    finetuned_output_dir = output_dir / task_label_name
    finetuned_output_dir.mkdir(exist_ok=True, parents=True)
    # Open the YAML file
    finetune_yaml_file = output_dir / f"cehrbert_finetune_{task_label_name}.yaml"
    finetune_yaml = OmegaConf.load(str(finetune_yaml_template))
    finetune_yaml["model_name_or_path"] = pretrained_model_dir
    finetune_yaml["tokenizer_name_or_path"] = pretrained_model_dir
    finetune_yaml["output_dir"] = finetuned_output_dir
    finetune_yaml["data_folder"] = meds_reader_dir
    finetune_yaml["cohort_folder"] = cfg.labels_dir
    finetune_yaml["dataset_prepared_path"] = output_dir / "dataset_prepared_path"
    finetune_yaml["dataloader_num_workers"] = cfg.num_threads
    finetune_yaml["seed"] = cfg.seed
    finetune_yaml["do_train"] = True
    finetune_yaml["do_predict"] = True
    finetune_yaml.to_yaml(finetune_yaml_file)

    run_subprocess(
        cmd=f"python -u -m cehrbert.runners.hf_cehrbert_finetune_runner {finetune_yaml_file}",
        temp_work_dir=str(output_dir),
        out_dir=finetuned_output_dir,
    )
