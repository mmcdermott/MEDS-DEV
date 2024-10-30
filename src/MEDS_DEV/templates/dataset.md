# \[New dataset\] \*\*Add your dataset name here\*\*

This is a template for creating a new dataset in MEDS-DEV. The dataset should be stored in a directory named after the dataset in the `src/MEDS-DEV/datasets` directory.

## Description

Provide a brief description of your dataset, including:

- Aggregate statistics (e.g., number of patients, time range, demographic distributions)
- Cohort description:
  - Inclusion/exclusion criteria
  - Censoring rules
  - Key demographic characteristics

## Supported tasks

Describe the existing tasks already present in MEDS-DEV that are covered. If there are new tasks that can be added, describe them here. Also note the `predicates.yaml` file that specifies the dataset's predicates.

## Resources and links

Please provide the following:

Link to the dataset's webpage and/or documentation (e.g., institutional repository, GitHub)
Relevant research papers or articles:
  - Original dataset publication
  - Key studies using this dataset
  - Methodology papers
Additional resources:
  - Data dictionaries
  - Code repositories
  - Usage examples

## Access requirements

Describe any access requirements for the dataset (e.g, human species research). If the dataset is publicly available, state that here. If the dataset is not publicly available, describe the process for obtaining access. We recommend the following topics be covered:

- **Access Policy**: Describe the access policy for the dataset, including any restrictions or permissions required.
- **License (for files)**: Specify the license under which the dataset files are distributed.
- **Data Use Agreement**: Specify any data use agreement that must be signed to access the dataset.
- **Required training**: Specify any training or certification required to access the dataset.

## Sources

Summarize the sources of the dataset. If the dataset is a combination of multiple sources, list them here.

1. https://link-to-dataset.org

## MEDS compatibility

Shortly specify the process of transforming this dataset to the MEDS format. If the dataset is already in the MEDS format when downloaded, specify that here.

## Checklist

Please ensure your model conforms to the MEDS-DEV API by checking the following:

- [ ] I filled out the above template.
- [ ] I included the predicates yaml file, defining all predictates required for the supported tasks.
