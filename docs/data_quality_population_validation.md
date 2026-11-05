# Data Quality Validation – Järfälla Population

## Objective

Validate that the sum of population across all DeSO areas in Järfälla Municipality approximately equals the official municipality population.

\[
\sum Population_{DeSO} \approx Population_{Municipality}
\]

The purpose is to verify that the DeSO aggregation does not appear to omit or duplicate population data.

## Data Sources

| Source | Geographic level | Reference period |
|---|---|---|
| SCB TAB638 | Municipality | 2010–2024 |
| SCB TAB6471 | Municipality | December 2025 |
| SCB TAB6574 – DeSO 2018 | DeSO | 2010–2023 |
| SCB TAB6574 – DeSO 2025 | DeSO | 2024–2025 |

## Validation Results

| Period | Comparison | Difference | Result |
|---|---|---:|---|
| 2010–2023 | TAB638 vs DeSO 2018 | 0 | PASS |
| 2024 | TAB638 vs DeSO 2025 | 0 | PASS |
| 2025 | TAB6471 vs DeSO 2025 | -4 (-0.0044%) | PASS – within tolerance |

## Conclusion

The aggregated DeSO population matches the official municipality population exactly for 2010–2024.

For 2025, the difference is only four people, equivalent to approximately -0.0044%.

SCB documents controlled statistical uncertainty (CKM) from reference year 2025. This may contribute to differences between published totals and aggregated components.

The validation provides strong evidence that the DeSO aggregation is consistent with the municipality-level population figures for the periods tested.

## Limitations

- Matching totals do not independently prove that every individual DeSO record is correct.
- Small differences may occur due to statistical uncertainty and source methodology.
- DeSO 2018 and DeSO 2025 represent different geographical versions and should not be combined into one historical time series without geographical harmonization.

## Status

Population aggregation validation completed. The data can proceed to the next stage: database loading and transformation with dbt.