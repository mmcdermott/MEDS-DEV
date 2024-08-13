# Task Criteria Files

This folder contains the dataset-agnostic criteria files for a collection of pre-defined tasks. These tasks
are nested, and the overall "task name" should reflect that nesting -- e.g., the file
`mortality/in_hospital/first_24h.yaml` is the configuration for the `mortality/in_hospital/first_24h` task.

Each directory in this structure should contain a `README.md` file that describes that sub-collection of
tasks.

All task criteria files are [ACES](https://github.com/justin13601/ACES) task-configuration `yaml` files. The
current version of ACES supported by these files can be seen in the `pyproject.toml` file in the root of this
repository. Currently, all tasks should be interpreted as _binary classification_ tasks. When run through the
ACES-CLI tool in `meds` format, the output files will be in the `meds` `label` schema, with the label for the
task appearing in the `boolean_label` column. For the current version of `meds` supported, see the
`pyproject.toml` file in the root of this repository.

Task criteria files should each contain a free-text `description` key describing the task.
