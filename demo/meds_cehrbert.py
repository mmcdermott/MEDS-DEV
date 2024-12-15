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

# %% [markdown]
# ## Install dependencies

# %%
!pip -q install meds_etl==0.3.6 meds_transforms==0.0.7

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
# Download MIMIC IV metadata
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
# Convert to MEDS
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
!echo $TASK_NAME
!echo $TASK_CONFIG_FP

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

# %% [markdown]
# ## Switch Colab to python 3.11 for cehrbert
# %%
# %%capture
# !sudo apt-get install python3.11 python3.11-venv
# import sys
# !python3.11 -m venv cehrbert
# import os
# os.environ['PATH'] = './content/cehrbert/bin:' + os.environ['PATH']
# !pip install --upgrade pip

# %%
# import sys
# sys.executable = './content/cehrbert/bin/python'

# %% [markdown]
# ## Install cehrbert and its dependencies

# %%
!pip install meds_reader==0.1.9
!pip install setuptools
!pip install cehrbert==1.3.1

# %%
MIMICIV_MEDS_DIR = "./content/meds/"
MIMICIV_MEDS_READER_DIR = "./content/meds_reader/"
TASK_DIR="./content/tasks/"
TASK_NAME="in_hospital_3d_los_after_48h"
OUTPUT_PRETRAIN_MODEL_DIR="./content/output/cehrbert/"
# TODO this variable has an identical name?
OUTPUT_PRETRAIN_MODEL_DIR="./content/output/cehrbert_finetuned/"

# %% [markdown]
# Run meds_reader on the MEDS data

# %%
!meds_reader_convert $MIMICIV_MEDS_DIR $MIMICIV_MEDS_READER_DIR

# %%
!mkdir -p ./content/output/cehrbert/
!mkdir -p ./content/output/cehrbert_dataset_prepared/
!mkdir -p ./content/output/cehrbert_finetuned/

# %%
# !mkdir ./content/github_repo;cd ./content/github_repo;git clone https://github.com/cumc-dbmi/cehrbert.git;cd cehrbert;git checkout fix/meds_evaluation;pip install .;

# %% [markdown]
# Create the cehrbert pretraining configuration yaml file

# %%
cehrbert_pretrain_config = """
#Model arguments
model_name_or_path: "./content/output/cehrbert/"
tokenizer_name_or_path: "./content/output/cehrbert/"
num_hidden_layers: 6
max_position_embeddings: 1024
hidden_size: 768
vocab_size: 100000
min_frequency: 50
include_value_prediction: false # additional CEHR-BERT learning objective

#Data arguments
data_folder: "./content/meds_reader/"
dataset_prepared_path: "./content/output/cehrbert_dataset_prepared/"

# Below is a list of Med-to-CehrBert related arguments
preprocessing_num_workers: 2
preprocessing_batch_size: 128
# if is_data_in_med is false, it assumes the data is in the cehrbert format
is_data_in_meds: true
att_function_type: "cehr_bert"
inpatient_att_function_type: "mix"
include_auxiliary_token: true
include_demographic_prompt: false
# if the data is in the meds format, the validation split will be omitted
# as the meds already provide train/tuning/held_out splits
validation_split_percentage: 0.05

# Huggingface Arguments
dataloader_num_workers: 2
dataloader_prefetch_factor: 2

overwrite_output_dir: false
resume_from_checkpoint: # automatically infer the latest checkpoint from the output folder
seed: 42

output_dir: "./content/output/cehrbert/"
evaluation_strategy: "epoch"
save_strategy: "epoch"
eval_accumulation_steps: 10

learning_rate: 0.00005
per_device_train_batch_size: 8
per_device_eval_batch_size: 8
gradient_accumulation_steps: 2

num_train_epochs: 50 # for large datasets, 5-10 epochs should suffice
warmup_steps: 10
weight_decay: 0.01
logging_dir: "./logs"
logging_steps: 10

save_total_limit:
load_best_model_at_end: true
metric_for_best_model: "eval_loss"
greater_is_better: false

report_to: "none"
"""
PRETRAIN_CONFIG_FP = f"./content/output/cehrbert/cehrbert_pretrain_config.yaml"
with open(PRETRAIN_CONFIG_FP, 'w') as f:
    f.write(cehrbert_pretrain_config)

# %% [markdown]
# ## Pretrain cehrbert using MLM
!python3.11 -m cehrbert.runners.hf_cehrbert_pretrain_runner ./content/output/cehrbert/cehrbert_pretrain_config.yaml

# %% [markdown]
# ## Create the cehrbert finetuning configuration yaml file
cehrbert_finetune_config = f"""
#Model arguments
model_name_or_path: "./content/output/cehrbert/"
tokenizer_name_or_path: "./content/output/cehrbert/"
num_hidden_layers: 6
max_position_embeddings: 1024
hidden_size: 768
vocab_size: 100000
min_frequency: 50
include_value_prediction: false # additional CEHR-BERT learning objective

#Data arguments
cohort_folder: "./content/tasks/{TASK_NAME}/"
data_folder: "./content/meds_reader/"
dataset_prepared_path: "./content/output/cehrbert_dataset_prepared/"

#LORA
use_lora: True
lora_rank: 64
lora_alpha: 16
target_modules: [ "query", "value" ]
lora_dropout: 0.1

# Below is a list of Med-to-CehrBert related arguments
preprocessing_num_workers: 2
preprocessing_batch_size: 128
# if is_data_in_med is false, it assumes the data is in the cehrbert format
is_data_in_meds: true
att_function_type: "cehr_bert"
inpatient_att_function_type: "mix"
include_auxiliary_token: true
include_demographic_prompt: false
# if the data is in the meds format, the validation split will be omitted
# as the meds already provide train/tuning/held_out splits
validation_split_percentage: 0.05

# Huggingface Arguments
dataloader_num_workers: 2
dataloader_prefetch_factor: 2

overwrite_output_dir: false
resume_from_checkpoint: # automatically infer the latest checkpoint from the output folder
seed: 42

output_dir: "./content/output/cehrbert_finetuned"
evaluation_strategy: "epoch"
save_strategy: "epoch"
eval_accumulation_steps: 10

do_train: True
do_predict: True

learning_rate: 0.00005
per_device_train_batch_size: 8
per_device_eval_batch_size: 8
gradient_accumulation_steps: 2

num_train_epochs: 10
warmup_steps: 10
weight_decay: 0.01
logging_dir: "./logs"
logging_steps: 10

save_total_limit:
load_best_model_at_end: true
metric_for_best_model: "eval_loss"
greater_is_better: false

report_to: "none"
"""
FINETUNE_CONFIG_FP = f"./content/output/cehrbert/cehrbert_finetune_config.yaml"
with open(FINETUNE_CONFIG_FP, 'w') as f:
    f.write(cehrbert_finetune_config)

# %%
# ## Finetune cehrbert for the downstream task
!python3.11 -m cehrbert.runners.hf_cehrbert_finetune_runner ./content/output/cehrbert/cehrbert_finetune_config.yaml

# %%
import pandas as pd

pd.read_parquet("./content/output/cehrbert_finetuned/test_predictions")

# %%
!cat ./content/output/cehrbert_finetuned/test_results.json
