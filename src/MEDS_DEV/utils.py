import contextlib
import logging
import os
import shutil
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
            env["VIRTUAL_ENV"] = str(venv_path.resolve())
            env["PATH"] = f"{str(venv_bin_path.resolve())}{os.pathsep}{env['PATH']}"

        yield build_temp_dir, env


def run_in_env(
    cmd: str,
    env: dict[str, str],
    output_dir: Path | str,
    do_overwrite: bool = False,
    cwd: Path | str | None = None,
) -> subprocess.CompletedProcess:
    if type(output_dir) is str:
        output_dir = Path(output_dir)

    if do_overwrite and output_dir.exists():
        logger.info(f"Removing existing output directory: {output_dir}")
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    done_file = output_dir / ".done"
    if done_file.is_file():
        logger.info(f"Skipping {cmd} because {done_file} exists.")
        return

    script_file = output_dir / "cmd.sh"
    script_lines = ["#!/bin/bash"]

    if env.get("VIRTUAL_ENV", None) is not None:
        script_lines.append(f"source {env['VIRTUAL_ENV']}/bin/activate")

    script_lines.append(cmd)
    script = "\n".join(script_lines)

    if script_file.is_file():
        if script_file.read_text() != script:
            raise RuntimeError(
                f"Script file {script_file} already exists and is different from the current script. "
                f"Existing file:\n{script_file.read_text()}\n"
                f"New script:\n{script}"
                "Consider running with do_overwrite=True."
            )
        else:
            logger.info(f"(Matching) script file already exists: {script_file}")
    else:
        script_file.write_text(script)

    script_file.chmod(0o755)

    logger.info(f"Running command in {script_file}:\n{script}")

    runner_kwargs = {"shell": False, "env": env, "capture_output": True}
    if cwd is not None:
        runner_kwargs["cwd"] = cwd

    command_out = subprocess.run(["bash", str(script_file.resolve())], **runner_kwargs)

    command_errored = command_out.returncode != 0
    if command_errored:
        raise RuntimeError(
            f"Command failed with exit code "
            f"{command_out.returncode}:\n"
            f"SCRIPT:\n{script}\n"
            f"STDERR:\n{command_out.stderr.decode()}\n"
            f"STDOUT:\n{command_out.stdout.decode()}"
        )
    else:
        done_file.touch()

    return command_out
