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

__all__ = ["MODELS", "CFG_YAML"]
