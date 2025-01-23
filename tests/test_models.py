from pathlib import Path
from tempfile import TemporaryDirectory

from MEDS_DEV import MODELS
from tests.utils import run_command


def test_non_model_breaks():
    non_model = "_not_supported"
    while non_model in MODELS:
        non_model = f"_{non_model}"

    with TemporaryDirectory() as root_dir:
        output_dir = Path(root_dir) / "output"
        run_command(
            "meds-dev-model",
            test_name="Non-model should error",
            hydra_kwargs={"model": non_model, "output_dir": str(output_dir.resolve())},
            should_error=True,
            want_err_msg=f"Model {non_model} not currently configured",
        )


@pytest.mark.parametrize("model", MODELS)
def test_model_runs(demo_dataset_with_task_labels):
    dataset_name, dataset_dir, task_name, task_labels_dir = demo_dataset_with_task_labels
