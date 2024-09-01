#!/bin/bash

export MEDS_ROOT_DIR=$1
export MEDS_DATASET_NAME=$2
export MEDS_TASK_NAME=$3

shift 3

MEDS_DEV_REPO_DIR=$(python -c "from importlib.resources import files; print(files(\"MEDS_DEV\"))")
export MEDS_DEV_REPO_DIR

SHARDS=$(expand_shards "$MEDS_ROOT_DIR"/data)

aces-cli --config-path="$MEDS_DEV_REPO_DIR"/configs --config-name="_ACES_MD" \
  "hydra.searchpath=[pkg://aces.configs]" "data.shard=$SHARDS" -m "$@"
