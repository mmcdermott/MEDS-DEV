import contextlib
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from MEDS_DEV import DATASETS
from tests.utils import run_command


@contextlib.contextmanager
def dataset_context():
    with TemporaryDirectory() as root_dir:
        root_dir = Path(root_dir)
        output_dir = root_dir / "output"
        temp_dir = root_dir / "temp"

        yield str(output_dir.resolve()), str(temp_dir.resolve())


def test_non_dataset_breaks():
    non_dataset = "_not_supported"
    while non_dataset in DATASETS:
        non_dataset = f"_{non_dataset}"

    with dataset_context() as (output_dir, _):
        run_command(
            "meds-dev-dataset",
            test_name="Non-dataset should error",
            hydra_kwargs={"dataset": non_dataset, "output_dir": output_dir},
            should_error=True,
            want_err_msg=f"Dataset {non_dataset} not currently configured",
        )


@pytest.mark.parametrize("dataset", DATASETS)
def test_datasets_configured(dataset: str):
    with dataset_context() as (output_dir, _):
        run_command(
            "meds-dev-dataset",
            test_name=f"Build {dataset}",
            hydra_kwargs={"dataset": dataset, "output_dir": output_dir, "demo": True},
        )
