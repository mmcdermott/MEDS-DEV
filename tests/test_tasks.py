from MEDS_DEV import TASKS
from tests.utils import run_command


def test_non_task_breaks(demo_dataset):
    (dataset_name, dataset_dir) = demo_dataset

    non_task = "_not_supported"
    while non_task in TASKS:
        non_task = f"_{non_task}"

    task_labels_dir = dataset_dir / "task_labels"

    run_command(
        "meds-dev-task",
        test_name="Non-task should error",
        hydra_kwargs={
            "task": non_task,
            "dataset": dataset_name,
            "dataset_dir": str(dataset_dir.resolve()),
            "output_dir": str(task_labels_dir.resolve()),
        },
        should_error=True,
        want_err_msg=f"Task {non_task} not currently configured",
    )


def test_tasks_configured(demo_dataset_with_task_labels):
    dataset_name, dataset_dir, task_name, task_labels_dir = demo_dataset_with_task_labels

    files = list(task_labels_dir.glob("**/*.parquet"))
    assert files, f"No files found for task {task_name} in dataset {dataset_name}"
