#!/bin/bash
print_help() {
  echo "Usage: $(basename "$0") <MEDS_ROOT_DIR> <MEDS_DATASET_NAME> <MEDS_TASK_NAME> [additional parameters]"
  echo
  echo "Arguments:"
  echo "  MEDS_ROOT_DIR       The root directory of the MEDS dataset to be used."
  echo "  MEDS_DATASET_NAME   The name of the dataset to be used."
  echo "  MEDS_TASK_NAME      The name of the task to be executed."
  echo
  echo "Additional parameters can be passed to the aces-cli command."
  echo
  echo "Example:"
  echo "  $(basename "$0") /path/to/meds/root dataset_name task_name --some-parameter=value"
}

if [[ "$1" == "--help" || "$1" == "-h" ]]; then
  print_help
  exit 0
fi

if [[ $# -lt 3 ]]; then
  echo "Error: Missing required arguments. See --help for usage."
  exit 1
fi

export MEDS_ROOT_DIR=$1
export MEDS_DATASET_NAME=$2
export MEDS_TASK_NAME=$3

shift 3

MEDS_DEV_REPO_DIR=$(python -c "from importlib.resources import files; print(files(\"MEDS_DEV\"))")
export MEDS_DEV_REPO_DIR

SHARDS=$(expand_shards "$MEDS_ROOT_DIR"/data)

echo "Running task $MEDS_TASK_NAME on dataset $MEDS_DATASET_NAME with MEDS_ROOT_DIR=$MEDS_ROOT_DIR and SHARDS=$SHARDS"

aces-cli --config-path="$MEDS_DEV_REPO_DIR"/configs --config-name="_ACES_MD" \
  "hydra.searchpath=[pkg://aces.configs]" "data.shard=$SHARDS" -m "$@"
