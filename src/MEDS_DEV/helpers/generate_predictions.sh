#!/bin/bash

export MEDS_ROOT_DIR=$1
export MEDS_DATASET_NAME=$2
export MEDS_TASK_NAME=$3

shift 3

MEDS_DEV_REPO_DIR=$(python -c "from importlib.resources import files; print(files(\"MEDS_DEV\"))")
export MEDS_DEV_REPO_DIR

# TODO improve efficiency of prediction generator by using this
# SHARDS=$(expand_shards "$MEDS_ROOT_DIR"/data)

python -m MEDS_DEV.helpers.generate_random_predictions  --config-path="$MEDS_DEV_REPO_DIR"/configs \
--config-name="predictions" "hydra.searchpath=[pkg://aces.configs]" "$@"
