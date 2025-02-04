from pathlib import Path
from tempfile import TemporaryDirectory

from MEDS_DEV import DATASETS
from tests.utils import run_command


def test_non_dataset_breaks():
    non_dataset = "_not_supported"
    while non_dataset in DATASETS:
        non_dataset = f"_{non_dataset}"

    with TemporaryDirectory() as root_dir:
        output_dir = Path(root_dir) / "output"
        run_command(
            "meds-dev-dataset",
            test_name="Non-dataset should error",
            hydra_kwargs={"dataset": non_dataset, "output_dir": str(output_dir.resolve())},
            should_error=True,
            want_err_msg=f"Dataset {non_dataset} not currently configured",
        )


def test_datasets_configured(demo_dataset):
    dataset_name, demo_dataset_dir = demo_dataset

    assert demo_dataset_dir.exists(), f"Output directory not found for {dataset_name}"
    data_subdir = demo_dataset_dir / "data"
    metadata_subdir = demo_dataset_dir / "metadata"

    if not data_subdir.is_dir() or not metadata_subdir.is_dir():
        err_str = [
            f"Either data/ or metadata/ is not a directory for {dataset_name}.",
            f"Demo dataset directory: {demo_dataset_dir}",
            "Directory contents:",
        ]
        for f in demo_dataset_dir.rglob("*"):
            err_str.append(f"  - {f}")
            if f.suffix == ".log":
                err_str.append("    Log contents:")
                err_str.append(f"    {f.read_text()}")

        raise AssertionError("\n".join(err_str))
