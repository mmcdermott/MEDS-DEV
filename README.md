# The MEDS Dynamic Extensible Validation (MEDS-DEV) Benchmark: Re-thinking Reproducibility and Validation in ML for Health

This repository contains the dataset, task, model training recipes, and results for the MEDS-DEV benchmarking
effort for EHR machine learning.

Note that this repository is _not_ a place where functional code is stored. Rather, this repository stores
configuration files, training recipes, results, etc. for the MEDS-DEV benchmarking effort -- runnable code will
often come from other repositories, with suitable permalinks being present in the various configuration files
or commit messages for associated contributions to this repository.

## Contributing to MEDS-DEV

### To Add a Model

TODO

### To Add a Dataset

TODO

### To Add a Task

TODO

### To Add Results

TODO

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
