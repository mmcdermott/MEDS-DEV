from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from MEDS_DEV import DATASETS, MODELS, TASKS
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

    task_metadata = TASKS[task_name].get("metadata", None)
    if (
        task_metadata is None
        or "test_datasets" not in task_metadata
        or dataset_name not in task_metadata["test_datasets"]
    ):
        pytest.skip(f"Dataset {dataset_name} not supported for testing {task_name}.")

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


@pytest.fixture(scope="session", params=MODELS)
def demo_model(request, demo_dataset_with_task_labels):
    model = request.param
    dataset_name, dataset_dir, task_name, task_labels_dir = demo_dataset_with_task_labels

    with TemporaryDirectory() as root_dir:
        run_command(
            "meds-dev-model",
            test_name=f"Model {model} should run on {dataset_name} and {task_name}",
            hydra_kwargs={
                "model": model,
                "dataset_type": "full",
                "mode": "full",
                "dataset_dir": str(dataset_dir.resolve()),
                "labels_dir": str(task_labels_dir.resolve()),
                "dataset_name": dataset_name,
                "task_name": task_name,
                "output_dir": str(root_dir),
                "demo": True,
            },
        )

        final_out_dir = Path(root_dir) / dataset_name / task_name / "predict"
        yield model, final_out_dir, dataset_name, dataset_dir, task_name, task_labels_dir


@pytest.fixture(scope="session")
def evaluated_model(demo_model):
    model, final_out_dir = demo_model[:2]

    with TemporaryDirectory() as root_dir:
        run_command(
            "meds-dev-evaluation",
            test_name=f"Evaluate {model}",
            hydra_kwargs={
                "output_dir": str(root_dir),
                "predictions_dir": str(final_out_dir),
            },
        )

        yield Path(root_dir), demo_model
