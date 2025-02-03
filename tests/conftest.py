import contextlib
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from MEDS_DEV import DATASETS, MODELS, TASKS
from tests.utils import run_command


def pytest_addoption(parser):
    parser.addoption(
        "--persistent_cache_dir",
        default=None,
        help=(
            "Use this local (preserved) directory for persistent caching. Directory must exist. Use the "
            "options --cache_dataset, --cache_task, and --cache_model to enable or disable caching for "
            "specific datasets, tasks, and models."
        ),
    )

    def add_cache_opt(opt: str):
        cache_str_template = (
            "Cache the {opt} with the given name. Use 'all' to cache all {opt}s. Add specific {opt}s "
            "by repeating the option, e.g., --cache_{opt}={opt}1 --cache_{opt}={opt}2."
        )
        parser.addoption(f"--cache_{opt}", action="append", type=str, help=cache_str_template.format(opt=opt))

    add_cache_opt("dataset")
    add_cache_opt("task")
    add_cache_opt("model")

    def add_test_opt(opt: str):
        test_str_template = (
            "Test the {opt} with the given name. Use 'all' to select all {opt}s. Add specific {opt}s "
            "by repeating the option, e.g., --test_{opt}={opt}1 --test_{opt}={opt}2. Default is to run all. "
            "If any are added, then only those will be run, but if none are added, then all will be run."
        )
        parser.addoption(f"--test_{opt}", action="append", type=str, help=test_str_template.format(opt=opt))

    add_test_opt("dataset")
    add_test_opt("task")
    add_test_opt("model")


def get_and_validate_cache_settings(request) -> tuple[Path | None, tuple[set[str], set[str], set[str]]]:
    """A helper to check the pytest parser options for caching and return the appropriate options.

    Args:
        request: The pytest request object.

    Returns:
        A tuple with the persistent cache directory and a tuple with the sets for datasets, tasks, and models.
        If the persistent cache directory is None, the sets will be empty. If the persistent cache directory
        is not None and exists, the sets will be filled with the respective names. If any of the sets contain
        'all', they will be set to all valid options.

    Raises:
        pytest.UsageError: If the persistent cache directory is not set but any of the cache options are set.
        pytest.UsageError: If the persistent cache directory is set but not a valid, existing directory.

    Examples:
        >>> class MockRequest:
        ...     def __init__(self, persistent_cache_dir, cache_datasets, cache_tasks, cache_models):
        ...         self.opts = {
        ...             '--persistent_cache_dir': persistent_cache_dir,
        ...             '--cache_dataset': cache_datasets,
        ...             '--cache_task': cache_tasks,
        ...             '--cache_model': cache_models,
        ...         }
        ...         self.config = self
        ...     def getoption(self, opt):
        ...         return self.opts[opt]
        >>> get_and_validate_cache_settings(MockRequest(None, None, None, None))
        (None, (set(), set(), set()))
        >>> with TemporaryDirectory() as temp_dir:
        ...     cache_dir = Path(temp_dir) / "cache"
        ...     cache_dir.mkdir()
        ...     out = get_and_validate_cache_settings(MockRequest(cache_dir, None, None, None))
        ...     print(out[0].relative_to(Path(temp_dir)), out[1], len(out))
        cache (set(), set(), set()) 2
        >>> with TemporaryDirectory() as temp_dir:
        ...     cache_dir = Path(temp_dir) / "cache"
        ...     cache_dir.mkdir()
        ...     out = get_and_validate_cache_settings(MockRequest(cache_dir, ["d1", "d2"], ["t1"], []))
        ...     print(out[0].relative_to(Path(temp_dir)), tuple(sorted(x) for x in out[1]), len(out))
        cache (['d1', 'd2'], ['t1'], []) 2
        >>> with TemporaryDirectory() as temp_dir:
        ...     cache_dir = Path(temp_dir) / "cache_dir"
        ...     cache_dir.mkdir()
        ...     out = get_and_validate_cache_settings(MockRequest(cache_dir, ["d1", "d2", "all"], [], ["m1"]))
        ...     assert out[0] == cache_dir, f"Expected {cache_dir}, got {out[0]}"
        ...     assert len(out) == 2, f"Expected 2, got {len(out)}"
        ...     assert out[1] == (set(DATASETS), set(), {"m1"}), (
        ...         f"Want ({set(DATASETS)}, [], {{'m1'}}) got {out[1]}"
        ...     )
        >>> get_and_validate_cache_settings(MockRequest(None, ["d1", "d2", "all"], [], ["m1"]))
        Traceback (most recent call last):
            ...
        _pytest.config.exceptions.UsageError: Persistent cache directory must be set if any cache options are!
        >>> with TemporaryDirectory() as temp_dir:
        ...     cache_dir = Path(temp_dir) / "cache_dir"
        ...     get_and_validate_cache_settings(MockRequest(cache_dir, [], [], []))
        Traceback (most recent call last):
            ...
        _pytest.config.exceptions.UsageError: Persistent cache directory must be an existent directory!
    """
    persistent_cache_dir = request.config.getoption("--persistent_cache_dir")
    cache_datasets = request.config.getoption("--cache_dataset")
    cache_tasks = request.config.getoption("--cache_task")
    cache_models = request.config.getoption("--cache_model")
    if (cache_datasets or cache_tasks or cache_models) and not persistent_cache_dir:
        raise pytest.UsageError("Persistent cache directory must be set if any cache options are!")

    if not persistent_cache_dir:
        return None, (set(), set(), set())

    persistent_cache_dir = Path(persistent_cache_dir)
    if not persistent_cache_dir.is_dir():
        raise pytest.UsageError("Persistent cache directory must be an existent directory!")

    datasets_set = set(cache_datasets) if cache_datasets else set()
    if "all" in datasets_set:
        datasets_set = set(DATASETS)
    tasks_set = set(cache_tasks) if cache_tasks else set()
    if "all" in tasks_set:
        tasks_set = set(TASKS)
    models_set = set(cache_models) if cache_models else set()
    if "all" in models_set:
        models_set = set(MODELS)

    return persistent_cache_dir, (datasets_set, tasks_set, models_set)


@contextlib.contextmanager
def cache_dir(persistent_dir: Path | None):
    """A simple helper to yield either the persistent dir or a temporary directory.

    Args:
        persistent_dir (Path | None): A Path object to a persistent directory that should be used or None.

    Yields: Either the persistent directory if it is not None or a temporary directory.

    Examples:
        >>> with cache_dir(Path("my_dir")) as root_dir:
        ...     print(str(root_dir))
        my_dir
        >>> with cache_dir(None) as root_dir:
        ...     print(str(root_dir))
        /tmp/...
    """
    if persistent_dir:
        yield persistent_dir
    else:
        with TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)


def get_opts(config, opt: str) -> list[str]:
    """A helper to get the options from the config object, pulling from all supported where appropriate."""
    arg = config.getoption(f"--test_{opt}")
    allowed = {"dataset": DATASETS, "task": TASKS, "model": MODELS}

    if arg:
        return allowed[opt] if "all" in arg else arg
    else:
        return allowed[opt]


def pytest_generate_tests(metafunc):
    if "demo_dataset" in metafunc.fixturenames:
        metafunc.parametrize("demo_dataset", get_opts(metafunc.config, "dataset"), indirect=True)
    if "demo_dataset_with_task_labels" in metafunc.fixturenames:
        metafunc.parametrize(
            "demo_dataset_with_task_labels", get_opts(metafunc.config, "task"), indirect=True
        )
    if "demo_model" in metafunc.fixturenames:
        metafunc.parametrize("demo_model", get_opts(metafunc.config, "model"), indirect=True)


@pytest.fixture(scope="session")
def demo_dataset(request) -> tuple[str, Path]:
    dataset_name = request.param
    persistent_cache_dir, (cache_datasets, _, _) = get_and_validate_cache_settings(request)

    with cache_dir(persistent_cache_dir if dataset_name in cache_datasets else None) as root_dir:
        root_dir = Path(root_dir)
        output_dir = root_dir / dataset_name

        run_command(
            "meds-dev-dataset",
            test_name=f"Build {dataset_name}",
            hydra_kwargs={"dataset": dataset_name, "output_dir": str(output_dir.resolve()), "demo": True},
        )

        yield dataset_name, output_dir


@pytest.fixture(scope="session")
def demo_dataset_with_task_labels(request, demo_dataset) -> tuple[str, Path, str, Path]:
    task_name = request.param
    (dataset_name, dataset_dir) = demo_dataset

    task_metadata = TASKS[task_name].get("metadata", None)
    if (
        task_metadata is None
        or "test_datasets" not in task_metadata
        or dataset_name not in task_metadata["test_datasets"]
    ):
        pytest.skip(f"Dataset {dataset_name} not supported for testing {task_name}.")

    persistent_cache_dir, (_, cache_tasks, _) = get_and_validate_cache_settings(request)
    with cache_dir(persistent_cache_dir if task_name in cache_tasks else None) as root_dir:
        root_dir = Path(root_dir)
        task_labels_dir = root_dir / dataset_name / "task_labels" / task_name

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

        yield dataset_name, dataset_dir, task_name, task_labels_dir


@pytest.fixture(scope="session")
def demo_model(request, demo_dataset_with_task_labels) -> tuple[str, Path, str, Path, str, Path]:
    model = request.param
    dataset_name, dataset_dir, task_name, task_labels_dir = demo_dataset_with_task_labels

    persistent_cache_dir, (_, _, cache_models) = get_and_validate_cache_settings(request)

    with cache_dir(persistent_cache_dir if model in cache_models else None) as root_dir:
        model_dir = root_dir / model
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
                "output_dir": str(model_dir.resolve()),
                "demo": True,
            },
        )

        final_out_dir = model_dir / dataset_name / task_name / "predict"
        yield model, final_out_dir, dataset_name, dataset_dir, task_name, task_labels_dir


@pytest.fixture(scope="session")
def evaluated_model(demo_model) -> tuple[Path, tuple[str, Path, str, Path, str, Path]]:
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
