from importlib.metadata import PackageNotFoundError, version

from .datasets import DATASETS  # noqa: F401
from .models import MODELS  # noqa: F401
from .tasks import TASKS  # noqa: F401

__all__ = ["DATASETS", "TASKS", "MODELS"]

__package_name__ = "MEDS_DEV"
try:
    __version__ = version(__package_name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
