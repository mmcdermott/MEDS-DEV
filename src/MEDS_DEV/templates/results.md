Users are expected to submit one pull request for each (meds_dev_version $\\times$ model $\\times$ dataset $\\times$ task) combination.

In this pull request one file should be added with the following structure:

```yaml
model: ???
dataset: ???
meds_dev_version: ???
task_name: ???
metrics:
  auc: ???
  ... # Any other task-specific metrics
```

The directory of this file should be: `results/${meds_dev_version}/${task}/${dataset}/${model}.yaml`

> \[!Warning\]
> We should add a github action that runs a script that confirms the validity of the results yaml:
>
> 1. Check existence of (meds_dev_version $\\times$ model $\\times$ dataset $\\times$ task) in MES-DEV
> 2. Are they compatible? I.e. does the dataset support the task?
> 3. Are all task metrics included?
> 4. Does the yaml include all expected fields.

To retract a result the user is expected to submit a pull request that removes it and explain why.
