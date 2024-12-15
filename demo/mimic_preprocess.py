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
# ## Download the MIMIC-IV demo dataset and convert it to MEDS format

MEDS_DEV_PROJECT_ROOT = "."

# %%
!pwd

# %%
# macOS users should install wget (e.g. through brew)
!wget -q -r -N -c --no-host-directories --cut-dirs=1 -np -P ./content/download https://physionet.org/files/mimic-iv-demo/2.2/

# %%
# Download the pre-MEDS script, event config (defining how raw data is converted to MEDS data), and meds-transform config
!mkdir -p ./content/meds-transforms/
!git clone --depth 1 https://github.com/mmcdermott/MEDS_transforms.git ./content/tmp/
!mv ./content/tmp/MIMIC-IV_Example ./content/MIMIC-IV_Example

# %%
# Download MIMIC-IV metadata
MIMICIV_RAW_DIR = "https://raw.githubusercontent.com/MIT-LCP/mimic-code/v2.4.0/mimic-iv/concepts/concept_map"
MIMICIV_PRE_MEDS_DIR = "./content/pre_meds/"
!mkdir {MIMICIV_PRE_MEDS_DIR}

OUTPUT_DIR = "./content/download/mimic-iv-demo/2.2"

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
# Convert to MEDS
TUTORIAL_DIR = MEDS_DEV_PROJECT_ROOT + "/content/MIMIC-IV_Example"
MIMICIV_RAW_DIR = MEDS_DEV_PROJECT_ROOT + "/content/download/mimic-iv-demo/2.2"
MIMICIV_PRE_MEDS_DIR = MEDS_DEV_PROJECT_ROOT + "/content/pre_meds"
MIMICIV_MEDS_DIR = MEDS_DEV_PROJECT_ROOT + "/content/meds"

EVENT_CONVERSION_CONFIG_FP = MEDS_DEV_PROJECT_ROOT + "/content/MIMIC-IV_Example/configs/event_config.yaml"
PIPELINE_CONFIG_PATH = MEDS_DEV_PROJECT_ROOT + "/content/MIMIC-IV_Example/configs/pipeline_config.yaml"
!cd {TUTORIAL_DIR} && ./run.sh {MIMICIV_RAW_DIR} {MIMICIV_PRE_MEDS_DIR} {MIMICIV_MEDS_DIR} do_unzip=true

# %%
# Move the data to demo/data/ as per MEDS-DEV
MIMICIV_DEMO_MEDS_DATA_DIR = MEDS_DEV_PROJECT_ROOT + "/content/meds/data"
!mv {MIMICIV_DEMO_MEDS_DATA_DIR} .
# %%
