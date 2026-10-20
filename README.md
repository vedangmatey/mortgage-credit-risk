# Mortgage Credit Risk Modeling

End-to-end mortgage credit risk model development, independent validation, and model governance using Freddie Mac's Single-Family Loan-Level Dataset.

## Project Objective

Develop and validate a Probability of Default (PD) model that estimates mortgage delinquency risk using historical borrower and loan characteristics.

**Initial modeling target:** 90+ days delinquent within 24 months of mortgage origination. The precise target definition and observation rules will be finalized during data preparation.

## Project Scope

1. **Data Engineering:** Ingest, clean, and transform mortgage origination and monthly performance data.
2. **Exploratory Data Analysis:** Investigate borrower characteristics, credit risk drivers, and historical delinquency patterns.
3. **Model Development:** Build and evaluate mortgage default prediction models.
4. **Independent Model Validation:** Assess discrimination, calibration, stability, data quality, and model limitations.
5. **Model Governance:** Develop model documentation, risk controls, monitoring requirements, and governance procedures.

## Technology Stack

- Python
- SQL and DuckDB
- Apache Parquet
- pandas, NumPy, and scikit-learn
- Jupyter Notebooks
- Git and GitHub

## Dataset

**Source:** Freddie Mac Single-Family Loan-Level Dataset.

Initial analysis will use the full 2007 mortgage origination cohort and associated monthly performance records. Additional cohorts may be introduced for out-of-time validation.

Raw data is stored locally and excluded from version control.

## Project Status

**Phase 1: Environment setup and data acquisition**

## Regulatory and Model Risk Framework

The project will incorporate applicable U.S. supervisory model risk management guidance, including SR 11-7 and relevant subsequent developments, with the precise framework reviewed during the governance phase.

## Disclaimer

This is an independent educational portfolio project, not an approved production banking risk model. Any independence of validation is simulated for educational purposes.