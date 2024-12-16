#%%
# MEDS_DEV_DEMO_CONDA_ENV = "meds-dev-demo"
# MEDS_DEV_DEMO_CONDA_ENV = "meds-dev"

#%%
# !conda init bash
# !conda create -n {MEDS_DEV_DEMO_CONDA_ENV} python=3.12
# !conda activate {MEDS_DEV_DEMO_CONDA_ENV}

#%% [markdown]
# Install MEDS-DEV and dependencies

#%%
!git clone https://github.com/mmcdermott/MEDS-DEV.git
!cd ./MEDS-DEV && pip install -e .

#%% [markdown]
# TODO Install any model-related dependencies.

# %%
MEDS_DEV_PROJECT_ROOT = "."
DATASET_NAME = "MIMIC-IV"
TASK_NAME = "mortality/in_icu/first_24h"

# %% [markdown]
# ## Extracting a MEDS-DEV task through ACES
# This step prepares the MEDS dataset for a task by extracting a cohort using inclusion/exclusion criteria and
# processing the data to create the label files.

# %%
!./MEDS-DEV/src/MEDS_DEV/helpers/extract_task.sh {MEDS_DEV_PROJECT_ROOT} {DATASET_NAME} {TASK_NAME}
