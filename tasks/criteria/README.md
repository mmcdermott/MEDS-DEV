# Task Criteria Files
This folder contains the dataset-agnostic criteria files for a collection of pre-defined tasks. These tasks
are nested, and the overall "task name" should reflect that nesting -- e.g., the file
`mortality/in_hospital/first_24h.yaml` is the configuration for the `mortality/in_hospital/first_24h` task.

Each directory in this structure should contain a `README.md` file that describes that sub-collection of
tasks.

All task criteria files are [ACES](https://github.com/justin13601/ACES) task-configuration `yaml` files.
Currently, all tasks should be interpreted as _binary classification_ tasks, where the output label (indicated
in the configuration file) should be interperted as a `False` or `0` label if the ACES derived task dataframe
has a `label` column with a value of `0`, and a `True` or `1` label if the ACES derived task dataframe has a
label column with any value greater than `0`.

Task criteria files should each contain a free-text `description` key describing the task.
