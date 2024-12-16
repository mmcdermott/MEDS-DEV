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
# # Downloading MIMIC-IV demo and converting it to MEDS format
# ### Install dependencies

#%% 
!pip -q install meds_etl==0.3.6 meds_transforms==0.0.9 es-aces==0.6.1


#%% [markdown]
# ### Download the MIMIC-IV demo dataset

import tempfile
import os
from pathlib import Path
temp_dir = tempfile.TemporaryDirectory()
MEDS_DEV_PROJECT_ROOT = os.getcwd()

ROOT_DIR=f"{MEDS_DEV_PROJECT_ROOT}/work_dir/mimiciv_demo"
Path(ROOT_DIR).mkdir(parents=True, exist_ok=True)

# %%
# macOS users should install wget (e.g. through brew)
!wget -q -r -N -c --no-host-directories --cut-dirs=1 -np -P {ROOT_DIR}/raw_data https://physionet.org/files/mimic-iv-demo/2.2/

# %%
# Download the pre-MEDS script, event config (defining how raw data is converted to MEDS data), and meds-transforms config
!mkdir {ROOT_DIR}/meds-transforms/
!git clone --depth 1 https://github.com/mmcdermott/MEDS_transforms.git {ROOT_DIR}/tmp/
!mv {ROOT_DIR}/tmp/MIMIC-IV_Example {ROOT_DIR}/MIMIC-IV_Example

# %%
# Download MIMIC-IV metadata
MIMICIV_RAW_DIR = "https://raw.githubusercontent.com/MIT-LCP/mimic-code/v2.4.0/mimic-iv/concepts/concept_map"
MIMICIV_PRE_MEDS_DIR = f"{ROOT_DIR}/pre_meds"
!mkdir {MIMICIV_PRE_MEDS_DIR}

OUTPUT_DIR = f"{ROOT_DIR}/raw_data/mimic-iv-demo/2.2"

files = [
    'd_labitems_to_loinc.csv',
    'inputevents_to_rxnorm.csv',
    'lab_itemid_to_loinc.csv',
    'meas_chartevents_main.csv',
    'meas_chartevents_value.csv',
    'numerics-summary.csv',
    'outputevents_to_loinc.csv',
    'proc_datetimeevents.csv',
    'proc_itemid.csv',
    'waveforms-summary.csv'
]

for file in files:
    !wget -O {OUTPUT_DIR}/{file} {MIMICIV_RAW_DIR}/{file}
    !wget -O {MIMICIV_PRE_MEDS_DIR}/{file} {MIMICIV_RAW_DIR}/{file}

# %%
!cp {MEDS_DEV_PROJECT_ROOT}/configs/extract_MIMIC.yaml {ROOT_DIR}/MIMIC-IV_Example/configs/

# %%
# Convert to MEDS
TUTORIAL_DIR = f"{ROOT_DIR}/MIMIC-IV_Example"
MIMICIV_RAW_DIR = f"{ROOT_DIR}/raw_data/mimic-iv-demo/2.2"
MIMICIV_PRE_MEDS_DIR = f"{ROOT_DIR}/pre_meds/"
MIMICIV_MEDS_DIR = f"{ROOT_DIR}/meds/"

EVENT_CONVERSION_CONFIG_FP=f"{ROOT_DIR}/MIMIC-IV_Example/configs/event_config.yaml"
PIPELINE_CONFIG_PATH=f"{ROOT_DIR}/MIMIC-IV_Example/configs/pipeline_config.yaml"
!cd {TUTORIAL_DIR} && bash {TUTORIAL_DIR}/run.sh {MIMICIV_RAW_DIR} {MIMICIV_PRE_MEDS_DIR} {MIMICIV_MEDS_DIR} do_unzip=true

# %%
# Move the data to demo/data/ as per MEDS-DEV
MIMICIV_DEMO_MEDS_DATA_DIR = f"{ROOT_DIR}/meds/data"
!cp -r {MIMICIV_DEMO_MEDS_DATA_DIR} .

# %% [markdown]
# ### Examine MEDS data
# %%
import polars as pl
data = pl.read_parquet(f'{MEDS_DEV_PROJECT_ROOT}/data/**/*.parquet')

data[['subject_id', 'time', 'code', 'numeric_value']]

# %% [markdown]
# A simple Polars analysis

# %%
icd10_events = data.filter(pl.col('code').str.starts_with('DIAGNOSIS//ICD//10//'))
icd10_events.group_by('code').count().sort('count', descending=True)

# %%
df = pl.read_parquet(f"{ROOT_DIR}/meds/metadata/codes.parquet")
df
# %%
