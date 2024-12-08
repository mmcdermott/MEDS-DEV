# The MEDS Decentralized Extensible Validation (MEDS-DEV) Benchmark: Establishing Reproducibility and Comparability in ML for Health

This repository contains the dataset, task, model training recipes, and results for the MEDS-DEV benchmarking
effort for EHR machine learning.

Note that this repository is _not_ a place where functional code is stored. Rather, this repository stores
configuration files, training recipes, results, etc. for the MEDS-DEV benchmarking effort -- runnable code
will
often come from other repositories, with suitable permalinks being present in the various configuration files
or commit messages for associated contributions to this repository.

> \[!NOTE\]
> MEDS-DEV currently only supports binary classification tasks.

## Example workflow

### (Optional) Set up the MEDS project with environment

```bash
# Create and enter a MEDS project directory
mkdir $MY_MEDS_PROJECT_ROOT
cd $MY_MEDS_PROJECT_ROOT

conda create -n $MY_MEDS_CONDA_ENV python=3.10
conda activate $MY_MEDS_CONDA_ENV
```

Additionally install any model-related dependencies.

### Install MEDS-DEV

Clone the MEDS-DEV GitHub repo and install it locally.
This will additionally install some MEDS data processing dependencies:

```bash
git clone https://github.com/mmcdermott/MEDS-DEV.git
cd ./MEDS-DEV
pip install -e .
```

Install the MEDS evaluation package:

```bash
git clone https://github.com/kamilest/meds-evaluation.git
pip install -e ./meds-evaluation
```

Additionally, make sure any model-related dependencies are installed.

### Extract a task from the MEDS dataset

This step prepares the MEDS dataset for a task by extracting a cohort using inclusion/exclusion criteria and
processing the data to create the label files.

### Find the task configuration file

Task-related information is stored in Hydra configuration files (in `.yaml` format) under
`MEDS-DEV/src/MEDS_DEV/tasks/criteria`.

Task names are defined in a way that corresponds to the path to their configuration,
starting from the `MEDS-DEV/src/MEDS_DEV/tasks/criteria` directory.
For example,
`MEDS-DEV/src/MEDS_DEV/tasks/criteria/mortality/in_icu/first_24h.yaml` directory corresponds to a `$TASK_NAME`
of
`mortality/in_icu/first_24h`.

**To add a task**

If your task is not supported, you will need to add a directory and define an appropriate configuration file
in a corresponding location.

### Dataset configuration file

Task configuration files are incomplete, because some concepts (predicates) have to be defined in a
dataset-specific
way (e.g. `icu_admission` in `mortality/in_icu/first_24h`).

These dataset-specific predicate definitions are found in
`MEDS-DEV/src/MEDS_DEV/datasets/$DATASET_NAME/predicates.yaml` Hydra configuration files.

In addition to `$DATASET_NAME` (e.g. `MIMIC-IV`), you will also need to have your MEDS dataset directory
ready (i.e.
`$MEDS_ROOT_DIR`).

**To add a dataset configuration file**

If your dataset is not supported, you will need to add a directory and define an appropriate configuration
file in a corresponding location.

### Run the MEDS task extraction helper

From your project directory (`$MY_MEDS_PROJECT_ROOT`) where `MEDS-DEV` is located, run

```bash
./MEDS-DEV/src/MEDS_DEV/helpers/extract_task.sh $MEDS_ROOT_DIR $DATASET_NAME $TASK_NAME
```

This will use information from task and dataset-specific predicate configs to extract cohorts and labels from
`$MEDS_ROOT_DIR/data`, and place them in `$MEDS_ROOT_DIR/task_labels/$TASK_NAME/` subdirectories, retaining
the same
sharded structure as the `$MEDS_ROOT_DIR/data` directory.

### Train the model

This step depends on the API of your particular model.

For example, the command below will call a helper script that will generate random outputs for binary
classification, in a format compatible with the evaluation step (see below):

```bash
./MEDS-DEV/src/MEDS_DEV/helpers/generate_predictions.sh $MEDS_ROOT_DIR $TASK_NAME
```

In order to work with MEDS-Evaluation (see the next section),
the model's outputs must contain the first three and at least one of the remaining fields from the following
`polars` schema:

```python
Schema(
    [
        ("subject_id", Int64),
        ("prediction_time", Datetime(time_unit="us")),
        ("boolean_value", Boolean),
        ("predicted_boolean_value", Boolean),
        ("predicted_boolean_probability", Float64),
    ]
)
```

where `boolean_value` represents the ground truth value, `predicted_boolean_value` is a binary prediction
(which for most methods depends on a decision threshold), and `predicted_boolean_probability` is an
uncertainty level in the range \[0, 1\].

When predicting the label, models are allowed to use all data about a subject up to and
including the `prediction_time`.

### Evaluate the model

You can use the `meds-evaluation` package by running `meds-evaluation-cli` and providing the path to
predictions dataframe as well as the output directory. For example,

```bash
meds-evaluation-cli \
	predictions_path="./$MEDS_ROOT_DIR/task_predictions/$DATASET_NAME/$TASK_NAME/$MODEL_NAME/.../*.parquet" \
	output_dir="./$MEDS_ROOT_DIR/task_evaluation/$DATASET_NAME/$TASK_NAME/$MODEL_NAME/.../"
```

This will create a JSON file with the results in the directory provided by the `output_dir` argument.

## Helpers

### To extract a task

First, clone the repo and install it locally with `pip install .` Then, make sure you have the desired task
criteria and dataset predicates yaml files in their respective locations in the repo.

Finally, run the following:

```bash
./src/MEDS_DEV/helpers/extract_task.sh $MEDS_ROOT_DIR $DATASET_NAME $TASK_NAME
```

E.g.,

```bash
./src/MEDS_DEV/helpers/extract_task.sh ../MEDS_TAB_COMPL_TEST/MIMIC-IV/ MIMIC-IV mortality/in_icu/first_24h
```

which will use the `datasets/MIMIC-IV/predicates.yaml` predicates file, the
`tasks/criteria/mortality/in_icu/first_24h.yaml` task criteria, and will run over the dataset in the root
directory at `../MEDS_TAB_COMPL_TEST/MIMIC-IV`, reading data from the `data` subdir of that root dir and
writing labels to the `task_labels` subdir of that root dir, in a name dependent manner.
