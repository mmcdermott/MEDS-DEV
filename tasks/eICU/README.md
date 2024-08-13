# eICU Tasks
This folder contains tasks for the [eICU Collaborative Research Database](https://eicu-crd.mit.edu/). The eICU
Collaborative Research Database is a multi-center database comprising deidentified health data associated with
over 200,000 admissions to ICUs across the United States between 2014-2015. The database is an open access
resource, and is ideal for use in a wide range of projects including data mining of electronic health records,
outcomes research, and development of predictive models.

Due to the make-up of this dataset, it is only appropriate to model things at the level of an individual
hospital stay---_not_ at the level of an individual patient, which you can do to some extent with, for
example, MIMIC-IV. As such, tasks that cross hospitalization boundaries, such as post-discharge mortality or
readmission risk prediction, would be inappropriate. However, in-hospital or in-ICU mortality prediction and
length of stay prediction are appropriate tasks.
