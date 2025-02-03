import logging
from pathlib import Path

import hydra
import polars as pl
from meds_evaluation.schema import validate_binary_classification_schema
from omegaconf import DictConfig

logger = logging.getLogger(__name__)

CONFIG = Path(__file__).parent / "_config.yaml"


@hydra.main(version_base=None, config_path=str(CONFIG.parent.resolve()), config_name=CONFIG.stem)
def main(cfg: DictConfig) -> None:
    predictions_fp = Path(cfg.predictions_fp)
    predictions_fp.parent.mkdir(parents=True, exist_ok=True)
    # Get the output dir
    model_finetuned_dir = Path(cfg.model_initialization_dir)
    # Infer the task label
    task_label_name = Path(cfg.labels_dir).name
    # Fine-tuned model dir
    test_prediction_output_dir = model_finetuned_dir / task_label_name / "test_predictions"
    if not test_prediction_output_dir.exists():
        raise RuntimeError(
            "The previous fine-tuning step did not generate the predictions for the held-out set."
        )

    predictions = pl.read_parquet(list(test_prediction_output_dir.rglob("*.parquet")))
    # TODO: calibrate the classifier and generate better boolean predictions
    predictions = predictions.with_columns(
        predictions["predicted_boolean_probability"].cast(pl.Float64).alias("predicted_boolean_probability"),
        (predictions["predicted_boolean_probability"] > 0.5).alias("predicted_boolean_value"),
    )

    # Check the schema output:
    validate_binary_classification_schema(predictions)
    predictions.write_parquet(predictions_fp, use_pyarrow=True)


if __name__ == "__main__":
    main()
