# The MEDS Dynamic Extensible Validation (MEDS-DEV) Benchmark: Re-thinking Reproducibility and Validation in ML for Health

This repository contains the dataset, task, model training recipes, and results for the MEDS-DEV benchmarking
effort for EHR machine learning.

Note that this repository is _not_ a place where functional code is stored. Rather, this repository stores
configuration files, training recipes, results, etc. for the MEDS-DEV benchmarking effort -- runnable code will
often come from other repositories, with suitable permalinks being present in the various configuration files
or commit messages for associated contributions to this repository.

## Example workflow

```bash
# Create and enter a MEDS project directory 
mkdir <my-meds-project-root>
cd <my-meds-project-root>

# Locate the MEDS data root directory <my-meds-dataset-path> and <dataset-name> 

# Create a new python environment
conda create -n <my-meds-env> python=3.10
conda activate <my-meds-env>

# In <my-meds-project-root>, install MEDS-DEV files and dependencies
# TODO: this will be probably be replaced with `pip install MEDS-DEV` in the future
git clone https://github.com/mmcdermott/MEDS-DEV.git
pip install -e ./MEDS-DEV
# TODO: consider the other dependencies that have not been deployed yet and are not in MEDS-DEV dependencies yet, e.g.:
# git clone https://github.com/kamilest/meds-evaluation.git
# pip install -e ./meds-evaluation
# etc.

# Install any model-specific dependencies

# TODO: locate and process task predicates in ./MEDS-DEV/tasks/, defining the unknown codes using predicates in
#   ./MEDS-DEV/datasets/<dataset-name>

aces-cli data.path='<my-meds-dataset-path>', data.standard='meds', cohort_dir=TODO, cohort_name=TODO

# TODO Figure out how ACES processes the cohort and where is the output stored: <aces-output>

# TODO Train model on <aces-output>, place the outputs in the MEDS prediction format in 
#   <my-meds-project-root>/predictions

# Evaluate model
meds-evaluation-cli predictions_path='<my-meds-project-root>/predictions', \ 
  output_dir='<my-meds-project-root>/evaluation'
```

## Contributing to MEDS-DEV

### To Add a Model

TODO

### To Add a Dataset

TODO

### To Add a Task

TODO

### To Add Results

TODO
