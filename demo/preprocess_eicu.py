# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3
#     name: python3
# ---

#%% [markdown]
# # Downloading eICU dataset and converting it to MEDS format
# ### Install dependencies

#%% 
!pip -q install meds_etl==0.3.6 meds_transforms==0.0.9 es-aces==0.6.1


#%% [markdown]
# ### Download the eICU demo dataset

import os
from pathlib import Path
MEDS_DEV_PROJECT_ROOT = os.getcwd()

ROOT_DIR=f"{MEDS_DEV_PROJECT_ROOT}/work_dir/eicu_demo"
Path(ROOT_DIR).mkdir(parents=True, exist_ok=True)

# %%
# Download the pre-MEDS script, event config (defining how raw data is converted to MEDS data), and meds-transforms config
!mkdir {ROOT_DIR}/meds-transforms/
!git clone --depth 1 https://github.com/mmcdermott/MEDS_transforms.git {ROOT_DIR}/tmp/
!mv {ROOT_DIR}/tmp/eICU_Example {ROOT_DIR}/eICU_Example

# %%
# Override configs: we remove the column apneaparms and the whole infusionDrug table as they are not in the demo
!cp configs/extract_eICU.yaml {ROOT_DIR}/eICU_Example/configs/.
!cp configs/table_preprocessors.yaml {ROOT_DIR}/eICU_Example/configs/.
!cp configs/event_configs.yaml {ROOT_DIR}/eICU_Example/configs/.

# %%
# Downloading eICU demo
# macOS users should install wget (e.g. through brew)
!wget -q -r -N -c --no-host-directories --cut-dirs=1 -np -P {ROOT_DIR}/raw_data https://physionet.org/files/eicu-crd-demo/2.0.1/

# %%
# Converting to MEDS
TUTORIAL_DIR = f"{ROOT_DIR}/eICU_Example"
EICU_RAW_DIR = f"{ROOT_DIR}/raw_data/eicu-crd-demo/2.0.1"
EICU_PRE_MEDS_DIR = f"{ROOT_DIR}/pre_meds/"
EICU_MEDS_DIR = f"{ROOT_DIR}/meds/"

EVENT_CONVERSION_CONFIG_FP=f"{ROOT_DIR}/eICU_Example/configs/event_config.yaml"
PIPELINE_CONFIG_PATH=f"{ROOT_DIR}/eICU_Example/configs/pipeline_config.yaml"
!cd {TUTORIAL_DIR} && bash {TUTORIAL_DIR}/run.sh {EICU_RAW_DIR} {EICU_PRE_MEDS_DIR} {EICU_MEDS_DIR} do_unzip=true

# %%
# Move the data to demo/data/ as per MEDS-DEV main tutorial
# NOTE this will currently overwrite the current data folder
# EICU_DEMO_MEDS_DATA_DIR = f"{ROOT_DIR}/meds/data"
# !cp -r {EICU_DEMO_MEDS_DATA_DIR} .

# %% [markdown]
# ### Examine MEDS data
# %%
import polars as pl
data = pl.read_parquet(f'{ROOT_DIR}/meds/data/**/*.parquet')

data[['subject_id', 'time', 'code', 'numeric_value']]
# %%
