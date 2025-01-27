import logging
from importlib.resources import files
from pathlib import Path

import hydra
import meds
import numpy as np
import polars as pl
from meds_evaluation.schema import (
    PREDICTED_BOOLEAN_PROBABILITY_FIELD,
    PREDICTED_BOOLEAN_VALUE_FIELD,
    validate_binary_classification_schema,
)
from omegaconf import DictConfig

logger = logging.getLogger(__name__)

CONFIG = files("MEDS_DEV") / "models" / "random_predictor" / "_config.yaml"


@hydra.main(version_base=None, config_path=str(CONFIG.parent.resolve()), config_name=CONFIG.stem)
def main(cfg: DictConfig) -> None:
    dataset_dir = Path(cfg.dataset_dir)
    labels_dir = Path(cfg.labels_dir)
    predictions_fp = Path(cfg.predictions_fp)
    predictions_fp.parent.mkdir(parents=True, exist_ok=True)
    seed = cfg.seed

    if cfg.split != meds.held_out_split:
        raise ValueError(
            f"Split {cfg.split} does not match held out split {meds.held_out_split}; this model should "
            "only be used for predictions so this is likely an error!"
        )

    splits_file = dataset_dir / meds.subject_splits_filepath
    if not splits_file.is_file():
        raise FileNotFoundError(
            f"Could not find splits file {splits_file.relative_to(dataset_dir)} for dataset "
            f"{dataset_dir}."
        )

    splits = pl.read_parquet(splits_file, use_pyarrow=True)
    subjects = set(splits.filter(pl.col("split") == cfg.split)[meds.subject_id_field])

    # Labels can live in any parquet file within the labels directory:
    labels_files = list(labels_dir.rglob("*.parquet"))
    if not labels_files:
        logger.warning(f"No labels found in {labels_dir}. Exiting without writing.")
        return

    def read_split(fp: Path) -> pl.DataFrame:
        return pl.read_parquet(fp, use_pyarrow=True).filter(pl.col(meds.subject_id_field).is_in(subjects))

    try:
        labels = pl.concat([read_split(f) for f in labels_files], how="vertical_relaxed")
    except Exception as e:
        err_lines = [f"Error reading labels: {e}", "Labels dir contents:"]
        for file in labels_dir.rglob("*.parquet"):
            err_lines.append(f"  - {file.relative_to(labels_dir)}")
        err_str = "\n".join(err_lines)
        logger.error(err_str)
        raise ValueError(err_str) from e

    rng = np.random.default_rng(seed)
    probabilities = rng.uniform(0, 1, len(labels))

    predictions = labels.with_columns(
        pl.Series(probabilities).alias(PREDICTED_BOOLEAN_PROBABILITY_FIELD),
    )
    predictions = predictions.with_columns(
        (pl.col(PREDICTED_BOOLEAN_PROBABILITY_FIELD) > 0.5).alias(PREDICTED_BOOLEAN_VALUE_FIELD),
    )

    # Check the schema output:
    validate_binary_classification_schema(predictions)

    predictions.write_parquet(predictions_fp, use_pyarrow=True)


if __name__ == "__main__":
    main()
