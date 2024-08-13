# Readmission Prediction

This folder contains tasks for predicting readmission within some time-frame post discharge. This is
a common and actionable task in the U.S. healthcare system in particular due to the financial penalties
imposed on hospitals for admission of patients who are readmitted within a certain time-frame post discharge.
Currently, the focus here is on hospital readmission. However, within that scope, there are still important
nuances. For example, predicting hospital admission within 30 days of either:

1. A discharge from a hospital stay that was non-elective (i.e. the patient was admitted due to an emergency)
2. A discharge from a hospital stay that was elective (i.e. the patient was admitted for a planned procedure)
3. A "discharge" from an ED visit that did not result in a formal hospital stay.
4. A discharge from a hospital stay for patients who meet certain clinical criteria (e.g., who have heart
    failure or who were admitted to the ICU, etc.).

Are all different tasks with different cohorts, implications, and potentially different predictors. Some
datasets are only usable for a subset of these tasks. For example, the
[MIMIC-IV dataset](https://mimic.mit.edu) is only usable for predicting readmission for patients with
non-elective hospital stays or for patients who were admitted to the ICU. The
[eICU](https://eicu-crd.mit.edu/) dataset is not usable for this task at all as one cannot reliably link
patients across multiple admissions in this dataset.
