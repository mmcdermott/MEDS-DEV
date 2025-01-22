from importlib.resources import files

task_files = files("MEDS_DEV.tasks")
CFG_YAML = files("MEDS_DEV.configs") / "_extract_task.yaml"
ACES_CFG_YAML = files("MEDS_DEV.configs") / "_ACES_MD.yaml"

TASKS = {}
for path in task_files.glob("**/*.yaml"):
    task = path.relative_to(task_files).with_suffix("").as_posix()
    TASKS[task] = path

__all__ = ["TASKS", "CFG_YAML", "ACES_CFG_YAML"]
