# Mortgage Credit Risk | Model Development, Validation & Governance

## Project Overview

An end-to-end mortgage credit risk modeling project using Freddie Mac's historical single-family loan-level data.

The objective is to develop a **Probability of Default (PD) model**, perform independent model validation, and establish a model governance framework demonstrating sound model risk management practices.

**Project Status:** In Progress — Data ingestion and initial integrity validation completed.


## Explore the Project


| Section | Description |
|---|---|
| [Model Development](docs/model_development.md) | Data preparation, feature engineering, model training, and performance |
| [Model Validation](docs/model_validation.md) | Population analysis, sensitivity testing, calibration, and validation findings |
| Model Governance | Coming soon |


## Baseline Model — Logistic Regression

**Status:** Preliminary validation completed

The baseline model uses six mortgage origination
characteristics to predict serious delinquency
within a 24-month observation horizon.

### Validation Results

| Metric | Result |
|---|---:|
| ROC-AUC | 0.7810 |
| Average Precision | 0.2488 |
| Brier Score | 0.0696 |
| Actual Event Rate | 8.35% |
| Average Predicted PD | 8.25% |

### Model Performance

**ROC Curve — Discriminatory Power**

![Logistic Regression ROC Curve](reports/figures/logistic_roc.png)

**Calibration — Predicted vs. Observed Risk**

![Logistic Regression Calibration](reports/figures/logistic_calibration.png)

For preprocessing decisions, coefficient interpretation,
and model limitations, see the
[Model Development Documentation](docs/model_development.md).

> **Research limitation:** These results are based on
> a preliminary target definition and the 2007 Q3
> validation cohort. Independent validation and
> final model testing are not yet complete.


## Business Objective

Estimate the likelihood that a mortgage becomes seriously delinquent (90+ days past due) within a defined 24-month observation horizon.

The project will address data quality, outcome definitions, early mortgage termination, predictive performance, model limitations, and governance considerations.

## Dataset

**Source:** Freddie Mac Single-Family Loan-Level Dataset  
**Cohort:** 2007  
**Mortgage Origination Records:** 1,238,192  
**Monthly Performance Records:** 74,478,724

The original data and generated datasets are excluded from this repository. Users must obtain the source data through Freddie Mac.

## Methodology

| Phase | Scope | Status |
|---|---|---|
| 1. Data Engineering | Ingestion, Parquet conversion, data integrity checks | Completed |
| 2. Target Development | Define serious delinquency outcomes and observation eligibility | In Progress |
| 3. Model Development | Feature engineering, logistic regression, model evaluation | Planned |
| 4. Model Validation | Independent testing, discrimination, calibration, sensitivity analysis | Planned |
| 5. Model Governance | Model documentation, risk assessment, monitoring framework | Planned |

## Technology Stack

- **Python:** Automated data processing and modeling
- **DuckDB and SQL:** Large-scale mortgage data analysis
- **Parquet:** Efficient columnar data storage
- **Git and GitHub:** Version control and reproducibility

Additional dependencies will be documented as they are introduced.

## Data Quality Controls

Initial validation of the complete 2007 cohort confirmed:

| Control | Result |
|---|---|
| Unique origination loan identifiers | Passed |
| Origination-to-performance identifier reconciliation | Passed |
| Monthly reporting-date format validation | Passed |
| Duplicate loan-month checks within quarterly files | Passed |
| Quarterly record-count and schema checks | Passed |

These controls establish initial data integrity; they do not constitute full model validation.

## Preliminary Research Findings

The initial investigation identified **59,785 mortgages with an observed numeric serious-delinquency status (03–98) during the first 24 scheduled payment months**.

This is not yet a finalized model default rate. Observation gaps, mortgage payoffs, special delinquency statuses, and target-definition limitations require further analysis.

## Model Risk Management Considerations

The project will document model assumptions, input data limitations, target construction, potential selection bias, validation results, and ongoing monitoring requirements.

The project is intended for research, education, and portfolio demonstration. It is not a production lending decision system.

## References

Freddie Mac — [Single-Family Loan-Level Dataset](https://www.freddiemac.com/research/datasets/sf-loanlevel-dataset)

Freddie Mac — [General User Guide](https://www.freddiemac.com/fmac-resources/research/pdf/user_guide.pdf)