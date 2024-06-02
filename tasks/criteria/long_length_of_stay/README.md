# Long length-of-stay (LOS) prediction

This folder contains tasks for predicting whether or not a patient's stay will be longer than a certain
target. Understanding the likely ranges of a patient's length of stay can be useful for a variety of clinical
operational tasks, in particular optimizing patient flow and resource allocation.

We sub-divide these tasks into hospital LOS and ICU LOS currently, but may add more varieties of this task
in the future. 

Note that in our setting, the task is not to predict the exact length of stay, but rather to predict whether
or not (in a binary setting) the length of stay will exceed some pre-specified, constant threshold. This is a
a simplification that is often useful in practice, but may not be suitable to all use-cases or deployment
targets.

Note that there is overlap between LOS tasks, mortality tasks, and discharge tasks, and users should carefully
consider which task is most suited to their situation. In particular, a model that predicts mortality within
some time range is implicitly also predicting a length of stay. Relatedly, a model that predicts a patient is
unlikely to have a long length of stay may be implicitly predicting either that the patient is likely to be
discharged or that the patient is likely to die (or both), so a prediction of a likely short length of stay is
*not* a good proxy for the patient being in good health.

TODO: References
