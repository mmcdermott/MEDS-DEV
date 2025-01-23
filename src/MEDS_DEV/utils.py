import contextlib
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from omegaconf import DictConfig

logger = logging.getLogger(__name__)


def get_venv_bin_path(venv_path: str | Path) -> Path:
    """Get the bin/Scripts directory of the virtual environment."""
    if os.name == "nt":  # Windows
        return Path(venv_path) / "Scripts"
    else:  # Unix-like systems
        return Path(venv_path) / "bin"


@contextlib.contextmanager
def tempdir_ctx(cfg: DictConfig) -> Path:
    temp_dir = cfg.get("temp_dir", None)
    if temp_dir is None:
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    else:
        temp_dir = Path(temp_dir)
        temp_dir.mkdir(exist_ok=True, parents=True)
        yield temp_dir


def install_venv(venv_path: Path, requirements: str | Path) -> Path:
    logger.info(f"Installing requirements from {requirements} into virtual environment.")
    subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)

    venv_bin_path = get_venv_bin_path(venv_path)
    venv_python = venv_bin_path / "python"
    if not venv_python.exists():
        raise RuntimeError(f"Virtual environment python {venv_python} does not exist!")

    subprocess.run(
        [str(venv_python), "-m", "pip", "install", "-r", str(requirements)],
        check=True,
    )

    logger.info(f"Installed requirements from {requirements} into virtual environment.")
    return venv_bin_path


@contextlib.contextmanager
def temp_env(cfg: DictConfig, requirements: str | Path | None) -> tuple[Path, dict]:
    with tempdir_ctx(cfg) as build_temp_dir:
        env = os.environ.copy()
        if requirements is not None:
            venv_path = build_temp_dir / ".venv"
            venv_bin_path = install_venv(venv_path, requirements)
            env["PATH"] = f"{str(venv_bin_path)}{os.pathsep}{env['PATH']}"

        yield build_temp_dir, env
