#!/bin/bash

export MEDS_ROOT_DIR=$1
export MEDS_DATASET_NAME=$2
export MEDS_TASK_NAME=$3

shift 3

MEDS_DEV_REPO_DIR=$(python -c "from importlib.resources import files; print(files(\"MEDS_DEV\"))")
export MEDS_DEV_REPO_DIR

DATA_DIR="$MEDS_ROOT_DIR"/"$MEDS_DATASET_NAME"/data
SHARDS=$(expand_shards "$DATA_DIR")

aces-cli --config-name="_ACES_MD" "hydra.searchpath=[pkg://MEDS_DEV.configs,pkg://aces.configs]" \
  "data.shard=$SHARDS" -m "$@"
