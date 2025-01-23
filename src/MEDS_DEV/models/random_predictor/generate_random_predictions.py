import logging
from importlib.resources import files
from pathlib import Path

import hydra
import numpy as np
import polars as pl
from omegaconf import DictConfig

logger = logging.getLogger(__name__)

SUBJECT_ID = "subject_id"
PREDICTION_TIME = "prediction_time"

BOOLEAN_VALUE_COLUMN = "boolean_value"
PREDICTED_BOOLEAN_VALUE_COLUMN = "predicted_boolean_value"
PREDICTED_BOOLEAN_PROBABILITY_COLUMN = "predicted_boolean_probability"

CONFIG = files("MEDS_DEV") / "models" / "random_predictor" / "_config.yaml"


@hydra.main(version_base=None, config_path=str(CONFIG.parent.resolve()), config_name=CONFIG.stem)
def main(cfg: DictConfig) -> None:
    labels_dir = Path(cfg.labels_dir)
    predictions_fp = Path(cfg.predictions_fp)
    seed = cfg.seed

    # Labels can live in any parquet file within the labels directory:
    labels_files = list(labels_dir.rglob("*.parquet"))
    if not labels_files:
        logger.warning(f"No labels found in {labels_dir}. Exiting without writing.")
        return

    labels = []
    if any(labels_dir.glob("**/*.parquet")):
        labels.append(pl.read_parquet(labels_dir / "**/*.parquet", use_pyarrow=True))
    if any(labels_dir.glob("*.parquet")):
        labels.append(pl.read_parquet(labels_dir / "*.parquet", use_pyarrow=True))

    labels = pl.concat(labels, how="vertical_relaxed")

    rng = np.random.default_rng(seed)
    probabilities = rng.uniform(0, 1, len(labels))

    labels[PREDICTED_BOOLEAN_PROBABILITY_COLUMN] = pl.Series(probabilities)
    labels[PREDICTED_BOOLEAN_VALUE_COLUMN] = pl.Series(probabilities > 0.5).cast(pl.Boolean)
    labels.write_parquet(predictions_fp, use_pyarrow=True)


if __name__ == "__main__":
    main()
