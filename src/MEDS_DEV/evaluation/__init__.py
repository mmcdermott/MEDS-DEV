from importlib.resources import files

CFG_YAML = files("MEDS_DEV.configs") / "_evaluate_predictions.yaml"

__all__ = ["CFG_YAML"]
