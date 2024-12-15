# Demo Notebooks Guide

## Data Extraction
1. Run `extract_meds_data.ipynb` to convert datasets to MEDS format:
   - MIMIC-IV demo dataset
   - EICU dataset

Extracted data locations:
- EICU: `demo/work_dir/eicu_demo/meds`
- MIMIC-IV: `demo/work_dir/mimiciv_demo/meds`

## Task Label Generation
2. Run `aces.ipynb` to generate prediction task labels

## Model Experiments
3. Run any of these notebooks for model experiments and AUC results:
- `meds_cehrbert.ipynb` - CEHR-BERT implementation
- `meds_tab.ipynb` - Tabular models
- `meds_torch.ipynb` - PyTorch models
