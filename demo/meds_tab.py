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

# %% [Colab-only] Switch Colab to python 3.12
# !sudo apt-get install python3.12 python3.12-venv
# import sys
# !python3.12 -m venv meds_env
# import os
# os.environ['PATH'] = '/content/meds_env/bin:' + os.environ['PATH']
# !pip install --upgrade pip

# # Then in a new code cell:
# import sys
# sys.executable = '/content/meds_env/bin/python'

# # Confirm python version is 3.12
# !python --version

# %%
!pwd # Should be .../src/MEDS_DEV/demo

# %% [markdown]
# ## Install dependencies

# %%
!pip -q install meds_etl==0.3.6 meds_transforms==0.0.7

# TODO install meds-evaluation

# %% [markdown]
# # Download MIMIC-IV demo

# %%
# macOS users should install wget (e.g. through brew)
!wget -q -r -N -c --no-host-directories --cut-dirs=1 -np -P ./content/download https://physionet.org/files/mimic-iv-demo/2.2/

# %%
# Download pre-meds script, event config (defining how raw data is converted to meds data), and meds-transform config
!mkdir -p ./content/meds-transform/
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
CURRENT_DIR = !pwd
CURRENT_DIR = CURRENT_DIR[0]
# %%
TUTORIAL_DIR = CURRENT_DIR + "/content/MIMIC-IV_Example"
MIMICIV_RAW_DIR = CURRENT_DIR + "/content/download/mimic-iv-demo/2.2"
MIMICIV_PRE_MEDS_DIR = CURRENT_DIR + "/content/pre_meds"
MIMICIV_MEDS_DIR = CURRENT_DIR + "/content/meds"

EVENT_CONVERSION_CONFIG_FP = CURRENT_DIR + "/content/MIMIC-IV_Example/configs/event_config.yaml"
PIPELINE_CONFIG_PATH = CURRENT_DIR + "/content/MIMIC-IV_Example/configs/pipeline_config.yaml"
!cd {TUTORIAL_DIR} && ./run.sh {MIMICIV_RAW_DIR} {MIMICIV_PRE_MEDS_DIR} {MIMICIV_MEDS_DIR} do_unzip=true

# %% [markdown]
# # Examine MEDS data

# %%
import polars as pl

data = pl.read_parquet('./content/meds/data/**/*.parquet')

data[['subject_id', 'time', 'code', 'numeric_value']]

# %% [markdown]
# # A simple Polars analysis

# %%
icd10_events = data.filter(pl.col('code').str.starts_with('DIAGNOSIS//ICD//10//'))
icd10_events.group_by('code').count().sort('count', descending=True)

# %%
df = pl.read_parquet("./content/meds/metadata/codes.parquet")
df

# %% [markdown]
# ## Using an example MEDS tool, ACES for labeling

# %% [markdown]
# ## Install ACES

# %%
!pip install es-aces

# %%

# From ACES documentation
task_config = """
description: >-
  This file specifies the base configuration for the prediction of a hospital los being greater than 3days,
  leveraging only the first 48 hours of data after admission, with a 24 hour gap between the input window
  and the target window. Patients who die or are discharged in the gap window are excluded. Note that this
  task is in-**hospital** los, not in-**ICU** los which is a different task.

predicates:
  hospital_admission:
    code: {regex: "HOSPITAL_ADMISSION//.*"}
  hospital_discharge:
    code: {regex: "HOSPITAL_DISCHARGE//.*"}
  death:
    code: MEDS_DEATH
  discharge_or_death:
    expr: or(hospital_discharge, death)

trigger: hospital_admission

windows:
  input:
    start: NULL
    end: trigger + 48h
    start_inclusive: True
    end_inclusive: True
    index_timestamp: end
  gap:
    start: input.end
    end: start + 24h
    start_inclusive: False
    end_inclusive: True
    has:
      hospital_admission: (None, 0)
      discharge_or_death: (None, 0)
  target:
    start: trigger
    end: start + 3d
    start_inclusive: False
    end_inclusive: True
    label: discharge_or_death
"""

!mkdir ./content/tasks/ -p
TASK_NAME = "in_hospital_3d_los_after_48h"
TASK_CONFIG_FP = f"./content/tasks/{TASK_NAME}.yaml"
with open(TASK_CONFIG_FP, 'w') as f:
    f.write(task_config)

# %%
!pip install es-aces

# %%
!aces-cli --multirun data=sharded data.standard=meds data.root="$MIMICIV_MEDS_DIR/data" "data.shard=$(expand_shards  ./content/meds/data/)" cohort_dir=" ./content/tasks" cohort_name="$TASK_NAME" config_path="$TASK_CONFIG_FP"

# %%
# TODO: reimporting polars due to dependencies?
import polars as pl

# Execute query and get results
df = pl.read_parquet(f"./content/tasks/{TASK_NAME}/**/*.parquet")

print("train prevalence: " + str(round(pl.read_parquet(f"./content/tasks/{TASK_NAME}/train/*.parquet")['boolean_value'].mean(), 3)))
print("tuning prevalence: " + str(round(pl.read_parquet(f"./content/tasks/{TASK_NAME}/tuning/*.parquet")['boolean_value'].mean(), 3)))
print("held_out prevalence: " + str(round(pl.read_parquet(f"./content/tasks/{TASK_NAME}/held_out/*.parquet")['boolean_value'].mean(), 3)))


df.sort('boolean_value')

# %%
# ## Install meds-tab

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

# %%
# Define the window sizes and aggregations to generate features for
# TODO define this as system variables or make sure the shell
# commands can find these
WINDOW_SIZES = "tabularization.window_sizes=[1d,30d,365d]"
AGGREGATIONS = "tabularization.aggs=[static/present,code/count,value/count,value/sum,value/sum_sqd,value/min,value/max]"

# %%
!rm -rf ./content/tabularized/tabularize/

# %%
# TODO shell vs python variables
!echo {OUTPUT_TABULARIZATION_DIR}

# %%
# TODO shell vs python variables
!echo WINDOW_SIZES
# %%
# TODO shell vs python variables
!meds-tab-tabularize-static "input_dir=$MIMICIV_MEDS_DIR/data" "output_dir=$OUTPUT_TABULARIZATION_DIR" do_overwrite=False $WINDOW_SIZES $AGGREGATIONS

# %%
# TODO shell vs python variables
!meds-tab-tabularize-time-series --multirun "worker=range(0,2)" "hydra/launcher=joblib" "input_dir=$MIMICIV_MEDS_DIR/data" "output_dir=$OUTPUT_TABULARIZATION_DIR" do_overwrite=False $WINDOW_SIZES $AGGREGATIONS

# %%
# TODO shell vs python variables
!meds-tab-cache-task "input_dir={MIMICIV_MEDS_DIR}/data" "output_dir=$OUTPUT_TABULARIZATION_DIR" "input_label_dir=$TASK_DIR/$TASK_NAME/" "task_name=$TASK_NAME" do_overwrite=False $WINDOW_SIZES $AGGREGATIONS

# %%
# TODO shell vs python variables
!meds-tab-xgboost --multirun "input_dir=$MIMICIV_MEDS_DIR/data" "output_dir=$OUTPUT_TABULARIZATION_DIR" "output_model_dir=$OUTPUT_MODEL_DIR/$TASK_NAME/" "task_name=$TASK_NAME" do_overwrite=False "hydra.sweeper.n_trials=10" $WINDOW_SIZES $AGGREGATIONS "tabularization.min_code_inclusion_count=10"
