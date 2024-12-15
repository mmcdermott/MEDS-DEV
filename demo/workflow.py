#%%
# MEDS_DEV_DEMO_CONDA_ENV = "meds-dev-demo"
MEDS_DEV_DEMO_CONDA_ENV = "meds-dev"

#%%
# !conda init bash
# !conda create -n {MEDS_DEV_DEMO_CONDA_ENV} python=3.12
# !conda activate {MEDS_DEV_DEMO_CONDA_ENV}

#%% [markdown]
# Install MEDS-DEV and dependencies

#%%
!pwd
#%%
!git clone https://github.com/mmcdermott/MEDS-DEV.git
!cd ./MEDS-DEV && pip install -e .

#%% [markdown]
# TODO Install any model-related dependencies.

#%% [markdown]
# TODO Install MEDS Evaluation
#%%
# !git clone https://github.com/kamilest/meds-evaluation.git
# !cd ./meds-evaluation && pip install -e .

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

# %% [markdown]
# ## Training MEDS-TAB

# %%
!pip uninstall es-aces -y # TODO ???
!pip install meds-tab

# %%
MIMICIV_MEDS_DIR = "./content/meds/"
OUTPUT_TABULARIZATION_DIR="./content/tabularized/"
TASK_DIR="./content/tasks/"
TASK_NAME="in_hospital_3d_los_after_48h"
OUTPUT_MODEL_DIR="./content/output/meds_tab/"

# %%
!meds-tab-describe input_dir={MIMICIV_MEDS_DIR}/data output_dir={OUTPUT_TABULARIZATION_DIR}
