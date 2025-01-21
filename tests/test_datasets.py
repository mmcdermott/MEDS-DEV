import pytest

from MEDS_DEV import DATASETS
from tests.utils import run_command


@pytest.mark.parametrize("dataset", DATASETS)
def test_dataset(dataset: str):
    run_command(f"meds-dev-dataset dataset={dataset}")
