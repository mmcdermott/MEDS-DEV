from importlib.resources import files

from omegaconf import OmegaConf

dataset_files = files("MEDS_DEV.datasets")
CFG_YAML = files("MEDS_DEV.configs") / "_build_dataset.yaml"

DATASETS = {}
for path in dataset_files.rglob("*/dataset.yaml"):
    dataset_name = path.relative_to(dataset_files).parent.with_suffix("").as_posix()

    metadata = OmegaConf.to_object(OmegaConf.load(path))
    requirements_path = path.parent / "requirements.txt"
    predicates_path = path.parent / "predicates.yaml"
    DATASETS[dataset_name] = {
        "metadata": metadata,
        "predicates": predicates_path if predicates_path.exists() else None,
        "requirements": requirements_path if requirements_path.exists() else None,
    }

__all__ = ["DATASETS", "CFG_YAML"]
