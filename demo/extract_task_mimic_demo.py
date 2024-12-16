#%% [markdown]
# Install MEDS-DEV and dependencies

#%%
!git clone https://github.com/mmcdermott/MEDS-DEV.git
!cd ./MEDS-DEV && pip install -e .

#%% [markdown]
# TODO Install any model-related dependencies.

# %%
import os
ROOT_DIR=f"{os.getcwd()}/work_dir/mimiciv_demo"
TUTORIAL_DIR = f"{ROOT_DIR}/MIMIC-IV_Example"

MIMICIV_DEMO_MEDS_DATA_DIR = f"{ROOT_DIR}/meds"
DATASET_NAME = "MIMIC-IV"
TASK_NAME = "mortality/in_icu/first_24h"

# %% [markdown]
# ## Extracting a MEDS-DEV task through ACES
# This step prepares the MEDS dataset for a task by extracting a cohort using inclusion/exclusion criteria and
# processing the data to create the label files.

# %%
!./MEDS-DEV/src/MEDS_DEV/helpers/extract_task.sh {MIMICIV_DEMO_MEDS_DATA_DIR} {DATASET_NAME} {TASK_NAME}
# %%
