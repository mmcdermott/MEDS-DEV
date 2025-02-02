# MEDS-Tab Model

MEDS-Tab is a tool for tabularizing and modeling complex medical time-series data. It works by:

- Leveraging sparse representations during tabularization
- Utilizing parallelism over shards
- Computing aggregations over various time windows and codes

This approach significantly reduces the computation required to generate high-quality tree-based baseline models for any supervised learning task, while leveraging as many features as possible.

## Feature Generation

MEDS-Tab generates features by computing the cross product of three elements:

1. A MEDS `code`
2. User-defined time windows (e.g., 1 day, 1 year, full patient history)
3. The following aggregation functions for the subset of observations that fall within the time window:

- `code/count`: Number of times a `code` was observed
- `value/count`: Number of times a `code` had a `numeric_value`
- `value/sum`: Sum of `numeric_value` for a `code`
- `value/sum_sqd`: Sum of squared `numeric_value` for a `code`
- `value/min`: Minimum `numeric_value` for a `code`
- `value/max`: Maximum `numeric_value` for a `code`
- `static/present`: Binary indicator for presence of a `code` with null `time`
- `static/first`: `numeric_value` of a `code` with null `time`

## Citation

If you use MEDS-Tab in your research, please cite:

```bibtex
@misc{oufattole2024medstabautomatedtabularizationbaseline,
      title={MEDS-Tab: Automated tabularization and baseline methods for MEDS datasets},
      author={Nassim Oufattole and Teya Bergamaschi and Aleksia Kolo and Hyewon Jeong and Hanna Gaggin and Collin M. Stultz and Matthew B. A. McDermott},
      year={2024},
      eprint={2411.00200},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2411.00200},
}
```
