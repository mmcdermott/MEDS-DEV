import os
from importlib.resources import files
from pathlib import Path

import hydra
import numpy as np
import polars as pl
from omegaconf import DictConfig

SUBJECT_ID = "subject_id"
PREDICTION_TIME = "prediction_time"

BOOLEAN_VALUE_COLUMN = "boolean_value"
PREDICTED_BOOLEAN_VALUE_COLUMN = "predicted_boolean_value"
PREDICTED_BOOLEAN_PROBABILITY_COLUMN = "predicted_boolean_probability"

CONFIG = files("MEDS_DEV").joinpath("configs/predictions.yaml")


@hydra.main(version_base=None, config_path=str(CONFIG.parent.resolve()), config_name=CONFIG.stem)
def generate_random_predictions(cfg: DictConfig) -> None:
    cohort_dir = cfg.cohort_dir  # cohort_dir: "${oc.env:MEDS_ROOT_DIR}/task_labels"
    cohort_name = cfg.cohort_name  # cohort_name: ${task_name}; task_name: ${oc.env:MEDS_TASK_NAME}

    cohort_dir = Path(cohort_dir) / cohort_name
    cohort_predictions_dir = (
        cfg.cohort_predictions_dir
    )  # cohort_predictions_dir: "${oc.env:MEDS_ROOT_DIR}/task_predictions"

    # TODO: use expand_shards helper from the script to access sharded dataframes directly
    for split in cohort_dir.iterdir():
        if split.is_dir() and split.name in {"train", "tuning", "held_out"}:  # train | tuning | held_out
            for file in split.iterdir():
                if file.is_file():
                    dataframe = pl.read_parquet(file)
                    predictions = _generate_random_predictions(dataframe)  # sharded dataframes

                    # $MEDS_ROOT_DIR/task_predictions/$TASK_NAME/<split>/<file>.parquet
                    predictions_path = Path(cohort_predictions_dir) / cohort_name / split.name
                    os.makedirs(predictions_path, exist_ok=True)

                    predictions.write_parquet(predictions_path / file.name)
        elif split.is_file():
            dataframe = pl.read_parquet(split)
            predictions = _generate_random_predictions(dataframe)

            predictions_path = Path(cohort_predictions_dir) / cohort_name
            os.makedirs(predictions_path, exist_ok=True)

            predictions.write_parquet(predictions_path / split.name)


def _generate_random_predictions(dataframe: pl.DataFrame) -> pl.DataFrame:
    """Creates a new dataframe with the same subject_id and boolean_value columns as in the input dataframe,
    along with predictions."""

    output = dataframe.select([SUBJECT_ID, PREDICTION_TIME, BOOLEAN_VALUE_COLUMN])
    probabilities = np.random.uniform(0, 1, len(dataframe))
    # TODO: meds-evaluation currently cares about the order of columns and types, so the new columns have to
    #  be inserted at the correct position and cast to the correct type
    output.insert_column(3, pl.Series(PREDICTED_BOOLEAN_VALUE_COLUMN, probabilities.round()).cast(pl.Boolean))
    output.insert_column(4, pl.Series(PREDICTED_BOOLEAN_PROBABILITY_COLUMN, probabilities))

    return output


if __name__ == "__main__":
    generate_random_predictions()
