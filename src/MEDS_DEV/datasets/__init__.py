from importlib.resources import files

from omegaconf import OmegaConf

dataset_files = files("MEDS_DEV.datasets")
CFG_YAML = files("MEDS_DEV.configs") / "_build_dataset.yaml"

DATASETS = {}
for path in dataset_files.iterdir():
    if not (path.is_dir() and (path / "commands.yaml").exists()):
        continue

    commands = OmegaConf.load(path / "commands.yaml")
    requirements_path = path / "requirements.txt"
    DATASETS[path.name] = {
        "commands": commands,
        "requirements": requirements_path if requirements_path.exists() else None,
    }

__all__ = ["DATASETS", "CFG_YAML"]
