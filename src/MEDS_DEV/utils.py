import contextlib
import hashlib
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from omegaconf import DictConfig

logger = logging.getLogger(__name__)


def get_venv_bin_path(venv_dir: str | Path) -> Path:
    """Get the bin/Scripts directory of the virtual environment.

    Args:
        venv_dir: Path to the virtual environment's root directory.

    Returns:
        Path to the bin/Scripts directory of the virtual environment, depending on the operating system.

    Examples:
        >>> get_venv_bin_path("path/to/venv")
        PosixPath('path/to/venv/bin')
    """
    # Windows uses "Scripts" instead of "bin"
    # TODO(mmd): Test this properly across operating systems
    if os.name == "nt":  # pragma: no cover
        return Path(venv_dir) / "Scripts"
    else:
        return Path(venv_dir) / "bin"


@contextlib.contextmanager
def tempdir_ctx(cfg: DictConfig) -> Path:
    """Provides a context manager that either yields a temporary directory or a specified directory.

    If a temporary directory is used, it is removed after the context manager exits. Pre-specified directories
    are not removed. The utility of this function is largely to normalize the interface through which
    directory contexts are used when running commands.

    Args:
        cfg: Configuration dictionary that may contain a "temp_dir" key. If the key is present, the specified
             directory is used as the temporary directory. If the key is not present or has a `None` value, a
             temporary directory is created.

    Yields:
        Path to the temporary directory. The returned directory is guaranteed to exist.

    Examples:
        >>> with tempdir_ctx({"temp_dir": None}) as temp_dir:
        ...     print(temp_dir)
        /tmp/...

    We can also specify a directory to use as the temporary directory (in this test, that directory is
    likewise specified within a temporary directory, just to ensure the test cleans up after itself; the
    specified directory can be anything):
        >>> with tempfile.TemporaryDirectory() as root:
        ...     temp_dir = Path(root) / "temp_dir"
        ...     assert not temp_dir.exists()
        ...     with tempdir_ctx({"temp_dir": str(temp_dir)}) as temp_dir:
        ...         print(str(temp_dir.relative_to(Path(root))))
        ...         assert temp_dir.exists()
        ...     assert temp_dir.exists()
        temp_dir
    """
    temp_dir = cfg.get("temp_dir", None)
    if temp_dir is None:
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    else:
        temp_dir = Path(temp_dir)
        temp_dir.mkdir(exist_ok=True, parents=True)
        yield temp_dir


def install_venv(venv_dir: Path, requirements: str | Path) -> Path:
    logger.info(f"Installing requirements from {requirements} into virtual environment.")
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

    venv_bin_path = get_venv_bin_path(venv_dir)
    venv_python = venv_bin_path / "python"
    if not venv_python.exists():
        raise RuntimeError(f"Virtual environment python {venv_python} does not exist!")

    subprocess.run(
        [str(venv_python), "-m", "pip", "install", "-r", str(requirements)],
        check=True,
    )

    logger.info(f"Installed requirements from {requirements} into virtual environment.")
    return venv_bin_path


def file_hash(filepath, algorithm="sha256", chunk_size=4096):
    hash_func = hashlib.new(algorithm)
    with open(filepath, "rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()


@contextlib.contextmanager
def temp_env(cfg: DictConfig, requirements: str | Path | None) -> tuple[Path, dict]:
    with tempdir_ctx(cfg) as build_temp_dir:
        env = os.environ.copy()
        if requirements is not None:
            if cfg.get("venv_dir", None) is not None:
                venv_dir = Path(cfg.venv_dir)
            else:
                venv_dir = build_temp_dir / ".venv"

            check_fp = venv_dir / f".installed.{file_hash(requirements)}.txt"
            venv_bin_path = get_venv_bin_path(venv_dir)

            if check_fp.exists():
                logger.info(f"Requirements already installed in {venv_dir}.")
            elif venv_bin_path.exists():
                any_check_fp = any(venv_dir.glob(".installed.*.txt"))
                if any_check_fp:
                    logger.warning(
                        f"Virtual environment {venv_dir} exists, but requirements check files differ! "
                        "Overwriting."
                    )
                else:
                    logger.warning(f"{venv_dir} exists but no requirements check files found. Overwriting.")
                shutil.rmtree(venv_dir)

            if not check_fp.exists():
                install_venv(venv_dir, requirements)
                check_fp.touch()

            env["VIRTUAL_ENV"] = str(venv_dir.resolve())
            env["PATH"] = f"{str(venv_bin_path.resolve())}{os.pathsep}{env['PATH']}"

        yield build_temp_dir, env


def run_in_env(
    cmd: str,
    output_dir: Path | str,
    env: dict[str, str] | None = None,
    do_overwrite: bool = False,
    cwd: Path | str | None = None,
    run_as_script: bool = True,
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

    if env is None:
        env = os.environ.copy()

    runner_kwargs = {"env": env, "capture_output": True}

    if run_as_script:
        script_file = output_dir / "cmd.sh"
        script_lines = ["#!/bin/bash", "set -e"]

        script_lines.append(cmd)
        script = "\n".join(script_lines)

        if env.get("VIRTUAL_ENV", None) is not None:
            script_lines.append(f"source {env['VIRTUAL_ENV']}/bin/activate")

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

        cmd = ["bash", str(script_file.resolve())]
        cmd_contents_error = script
        runner_kwargs["shell"] = False
    else:
        logger.info(f"Running command:\n{cmd}")
        cmd_contents_error = cmd
        runner_kwargs["shell"] = True

    if cwd is not None:
        runner_kwargs["cwd"] = cwd

    command_out = subprocess.run(cmd, **runner_kwargs)

    command_errored = command_out.returncode != 0
    if command_errored:
        raise RuntimeError(
            f"Command failed with exit code "
            f"{command_out.returncode}:\n"
            f"SCRIPT:\n{cmd_contents_error}\n"
            f"STDERR:\n{command_out.stderr.decode()}\n"
            f"STDOUT:\n{command_out.stdout.decode()}"
        )
    else:
        done_file.touch()

    return command_out
