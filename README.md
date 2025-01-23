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

## To add a dataset

To add a dataset, you will need to create a new directory under `src/MEDS_DEV/datasets/` with the name of the
dataset, containing the following files:

1. `README.md`: This file should contain a description of the dataset. See the templates for examples.
2. `requirements.txt`: This file should be a valid `pip` specification for what is needed to install the ETL
    to build the environment. _The ETL must be runnable on Python 3.11_.
3. `commands.yaml`: This file must have two shell command strings under the keys `build_full` and
    `build_demo` that, if run in an environment with the requirements installed, with the specified
    placeholder variables (indicated in python syntax, include `temp_dir` for intermediate files and
    `output_dir` for where you want the final MEDS cohort to live) will produce the desired MEDS cohort.
4. `predicates.yaml` contains ACES syntax predicates to realize the target tasks.

If all of these are defined, then you can, after installing `MEDS-DEV` via `pip install -e .`, run the command
`meds-dev-dataset dataset=DATASET_NAME output_dir=OUTPUT_DIR` to generate the MEDS cohort for that dataset
(with `demo=True` if you want the demo version).

## To add a task

To add a task, simply create a new task configuration file under `src/MEDS_DEV/tasks` with the desired
(slash-separated) task name. The task configuration file should be a valid ACES configuration file, with the
predicates left as placeholders to-be-overwritten by dataset-specific predicates. In addition, in the same
series of folders leading to the task configuration file, you should have `README.md` files that describe what
those "categories" of tasks mean.

Once a task is defined, then you can, after installing `MEDS-DEV` via `pip install -e .`, run the command
`meds-dev-task task=TASK_NAME dataset=DATASET_NAME output_dir=OUTPUT_DIR dataset_dir=DATASET_DIR` to generate
the labels for task `TASK_NAME` over dataset `DATASET_NAME` stored in the directory `DATASET_DIR` in the
output directory `OUTPUT_DIR`.

For testing purposes, _e.g., to ensure your task is correctly defined and supported by the expected datasets_,
you should also include the following information in a `metadata` block in your task config:

```
metadata:
  test_datasets:
    - MIMIC-IV
    - ...
```

where the list of datasets in `metadata.test_datasets` will be used to test the task automatically by the test
set-up (against the _demo_ version of that dataset only!)

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

TODO -- see command above.

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
