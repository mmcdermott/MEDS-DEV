# MEDS-Tab Model

This is a tiny model that uses the MEDS-Tab library to tabularize data and then uses an xgboost classifier to make
predictions. Only the top 100 most prevalent codes are used, and time windows of 7 days and 30 days are used. Three aggregation methods are used in tabularization: checking for static presence of values, counting code occurrences, and summing numeric values.
