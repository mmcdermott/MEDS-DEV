import os
from importlib.resources import files

from omegaconf import OmegaConf

model_files = files("MEDS_DEV.models")
CFG_YAML = files("MEDS_DEV.configs") / "_run_model.yaml"

MODELS = {}

for path in model_files.rglob("*/model.yaml"):
    model_name = path.relative_to(model_files).parent.with_suffix("").as_posix()
    MODELS[model_name] = OmegaConf.to_object(OmegaConf.load(path))
    requirements_path = path.parent / "requirements.txt"
    MODELS[model_name]["requirements"] = requirements_path if requirements_path.exists() else None
    MODELS[model_name]["model_dir"] = path.parent

if os.environ.get("MEDS_DEV_MODEL_NAMES", None) is not None:
    valid_models = set(os.environ["MEDS_DEV_MODEL_NAMES"].split(","))
    MODELS = {model: MODELS[model] for model in MODELS if model in valid_models}

__all__ = ["MODELS", "CFG_YAML"]
