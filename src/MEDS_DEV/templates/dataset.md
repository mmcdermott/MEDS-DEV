# \[New dataset\] \*\*Add your dataset name here\*\*

This is a template for supporting a new dataset in MEDS-DEV. Please edit the information on the template as appropriate, and commit this information in a `README.md` file in a directory named after your dataset in `src/MEDS_DEV/datasets` (e.g. `src/MEDS_DEV/datasets/MIMIC-IV/README.md`).

## Description

Provide a brief description of your dataset, including:

- Aggregate statistics
- Cohort description (inclusion criteria and censoring)

## Supported tasks

Provide the list of the existing tasks already present in MEDS-DEV that are covered, and note any exceptions for tasks that **cannot** be run on your dataset (e.g. due to censoring limitations, incompatible inclusion criteria, etc.)

For supported tasks, provide the predicate definitions in a `predicates.yaml` file in `src/MEDS_DEV/datasets/$YOUR_DATASET_NAME` (e.g. `src/MEDS_DEV/datasets/MIMIC-IV/predicates.yaml`).

### Future tasks

If there are any currently undefined tasks that your dataset would be particularly suitable for, describe them here.

## Resources and links

Please provide the following:

- (Permanent) link to the dataset's webpage and/or documentation
- If the dataset is a combination of multiple sources, list of sources with links
- Any relevant research papers or articles
- Any additional resources that would be helpful for users

## Access requirements

Describe any access requirements for the dataset (e.g, human species research). If the dataset is publicly available, state that here. If the dataset is not publicly available, describe the process for obtaining access. We recommend the following topics be covered:

- **Access Policy**: Describe the access policy for the dataset, including any restrictions or permissions required.
- **License (for files)**: Specify the license under which the dataset files are distributed.
- **Data Use Agreement**: Specify any data use agreement that must be signed to access the dataset.
- **Required training**: Specify any training or certification required to access the dataset.

## MEDS compatibility

Shortly specify the process of transforming this dataset into the MEDS format. If the dataset is already in the MEDS format when downloaded, specify that here.

Provide any other instructions for how to prepare the dataset for use with MEDS models and tasks.

## Checklist

Please ensure your model conforms to the MEDS-DEV API by checking the following:

- [ ] I filled out the above template and committed it as a `README.md` file in a directory named after the dataset in `src/MEDS_DEV/datasets`.
- [ ] I included the predicates yaml file, defining all predictates required for the supported tasks.
