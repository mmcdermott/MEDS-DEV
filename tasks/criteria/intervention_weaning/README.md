# Intervention Weaning

This folder contains tasks for predicting the time to weaning of an intervention. This task can be used to forecast the optimal timing for reducing or discontinuing medical interventions, such as ventilators or medications, which is vital in practice to ensure patient safety and promote recovery. Accurate predictions can benefit patient outcomes, reduce hospital stays, and optimize healthcare resources.

ACES cannot currently directly extract a label for the time until weaning as the labels need to be framed as a binary classification problem. However, the time to weaning can be easily calculated by subtracting the start from end times for the `target` window for the cohort that was extracted.



TODO: References
- Ventilator weaning strategies: https://www.sciencedirect.com/science/article/abs/pii/S0883944123000242?via%3Dihub