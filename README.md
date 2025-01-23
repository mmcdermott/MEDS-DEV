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

## To add a model

To add a model, create a new subdirectory of `src/MEDS_DEV/models/` with the name of the model. Then, within
this subdirectory, create a `requirements.txt`, `README.md`, and `model.yaml` file. The `requirements.txt`
contains the necessary Python packages to install to run the model, similar to dataset creation, the
`README.md` contains a description of the model, and the `model.yaml` file contains some programmatic
information about the model, including most critically a `commands` key with a dictionary of commands needed
to run to train the model from scratch on a MEDS dataset.

A full description of these commands is coming soon, but for now, note that:

1. Commands can use the template variables `{output_dir}`, `{dataset_dir}`, `{labels_dir}`, and `{demo}`.
2. Commands should be added in a nested manner for running either over `unsupervised` or `supervised`
    datasets, in either `train` or `predict` modes. See the random predictors example for an example.

See the help string for `meds-dev-model` for more information. Note the final output predictions should be
stored as a set of parquet files in the final output directory specified by the `output_dir` variable in the
format expected by `meds-evaluation`.

### Evaluate the model

You can use the `meds-evaluation` package by running `meds-evaluation-cli` and providing the path to
predictions dataframe as well as the output directory. For example,

```bash
meds-evaluation-cli \
  predictions_path="./$MEDS_ROOT_DIR/task_predictions/$DATASET_NAME/$TASK_NAME/$MODEL_NAME/.../*.parquet" \
  output_dir="./$MEDS_ROOT_DIR/task_evaluation/$DATASET_NAME/$TASK_NAME/$MODEL_NAME/.../"
```

This will create a JSON file with the results in the directory provided by the `output_dir` argument.
