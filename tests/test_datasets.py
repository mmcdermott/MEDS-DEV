import pytest

from MEDS_DEV import DATASETS
from tests.utils import run_command


def test_non_dataset_breaks():
    non_dataset = "_not_supported"
    while non_dataset in DATASETS:
        non_dataset = f"_{non_dataset}"

    run_command(
        "meds-dev-dataset",
        test_name="Non-dataset should error",
        hydra_kwargs={"dataset": non_dataset},
        should_error=True,
    )


@pytest.mark.parametrize("dataset", DATASETS)
def test_datasets_configured(dataset: str):
    run_command(
        "meds-dev-dataset", test_name=f"Build {dataset}", hydra_kwargs={"dataset": dataset, "demo": True}
    )
