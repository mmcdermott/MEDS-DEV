from importlib.resources import files

dataset_files = files("MEDS_DEV.datasets")

DATASETS = []
for path in dataset_files.iterdir():
    if path.is_dir() and (path / "commands.yaml").exists():
        DATASETS.append(path.name)

__all__ = ["DATASETS"]
