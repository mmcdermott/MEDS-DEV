from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from MEDS_DEV import DATASETS, TASKS
from tests.utils import run_command


@pytest.fixture(scope="session", params=DATASETS)
def demo_dataset(request) -> Path:
    dataset_name = request.param
    with TemporaryDirectory() as root_dir:
        root_dir = Path(root_dir)
        output_dir = root_dir / "output"

        run_command(
            "meds-dev-dataset",
            test_name=f"Build {dataset_name}",
            hydra_kwargs={"dataset": dataset_name, "output_dir": str(output_dir.resolve()), "demo": True},
        )

        yield dataset_name, output_dir


@pytest.fixture(scope="session", params=TASKS)
def demo_dataset_with_task_labels(request, demo_dataset):
    task_name = request.param
    (dataset_name, dataset_dir) = demo_dataset

    task_labels_dir = dataset_dir / "task_labels"

    run_command(
        "meds-dev-task",
        test_name=f"Extract {task_name}",
        hydra_kwargs={
            "task": task_name,
            "dataset": dataset_name,
            "dataset_dir": str(dataset_dir.resolve()),
            "output_dir": str(task_labels_dir.resolve()),
        },
    )

    return dataset_name, dataset_dir, task_name, task_labels_dir
