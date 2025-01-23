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
    predictions_fp.parent.mkdir(parents=True, exist_ok=True)
    seed = cfg.seed

    # Labels can live in any parquet file within the labels directory:
    labels_files = list(labels_dir.rglob("*.parquet"))
    if not labels_files:
        logger.warning(f"No labels found in {labels_dir}. Exiting without writing.")
        return

    labels = []
    try:
        labels = pl.concat(
            [pl.read_parquet(f, use_pyarrow=True) for f in labels_files], how="vertical_relaxed"
        )
    except Exception as e:
        err_lines = [f"Error reading labels: {e}", "Labels dir contents:"]
        for file in labels_dir.rglob("*.parquet"):
            err_lines.append(f"  - {file.relative_to(labels_dir)}")
        err_str = "\n".join(err_lines)
        logger.error(err_str)
        raise ValueError(err_str) from e

    rng = np.random.default_rng(seed)
    probabilities = rng.uniform(0, 1, len(labels))

    labels = labels.with_columns(
        pl.Series(probabilities).alias(PREDICTED_BOOLEAN_PROBABILITY_COLUMN),
    )
    labels = labels.with_columns(
        (pl.col(PREDICTED_BOOLEAN_PROBABILITY_COLUMN) > 0.5).alias(PREDICTED_BOOLEAN_VALUE_COLUMN),
    )
    labels.write_parquet(predictions_fp, use_pyarrow=True)


if __name__ == "__main__":
    main()
