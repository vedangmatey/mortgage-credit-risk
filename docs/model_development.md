# Model Development

[← Back to Project Overview](../README.md)

## 1. Modeling Objective

Develop a mortgage credit risk model to estimate the probability of observed serious delinquency (90+ days past due) within a 24-month observation horizon.

**Status:** In progress — preliminary model development.

## 2. Modeling Population

| Dataset | Mortgages | Events | Event Rate |
|---|---:|---:|---:|
| Training (2007 Q1–Q2) | 488,486 | 23,891 | 4.89% |
| Validation (2007 Q3) | 188,212 | 15,718 | 8.35% |
| Test (2007 Q4) | 211,425 | 20,176 | 9.54% |

A chronological quarterly cohort split was selected to assess performance on later mortgage cohorts.

The test set is reserved for final model evaluation. This is not an independent out-of-time test across origination years.

**Limitation:** The target currently excludes mortgages with incomplete outcomes and treats early terminations conservatively. Target sensitivity and selection bias require further validation.

## 3. Feature Selection

The baseline model uses six origination-time characteristics:

- Credit Score
- Original Loan-to-Value Ratio (LTV)
- Original Combined LTV (CLTV)
- Original Debt-to-Income Ratio (DTI)
- Original Interest Rate
- Original Loan Amount

Post-origination performance information is excluded from predictive features to avoid forward-looking data leakage.

## 4. Missing Data Treatment

### Approach: Median Imputation

Missing numeric values are replaced using medians calculated from the training dataset only.

| Feature | Missing Training Values | Training Median |
|---|---:|---:|
| Credit Score | 410 | 726 |
| Original LTV | 43 | 77 |
| Original CLTV | 45 | 80 |
| Original DTI | 9,635 | 37 |
| Interest Rate | 0 | 6.25 |
| Loan Amount | 0 | 158,000 |

### Why Median Imputation?

Median imputation was selected as a simple, reproducible baseline approach because it is less sensitive to extreme observations than mean imputation.

The imputer is fitted only on the training population, then applied unchanged to validation and test populations.

This prevents preprocessing statistics from being learned using future evaluation cohorts.

### Limitations and Planned Validation

Median imputation does not preserve the full distribution of missing values and may hide informative missingness.

Future checks will investigate missingness patterns, alternative imputation methods, and the potential predictive value of missingness indicators.

## 5. Planned Model Development

Three models will be evaluated:

1. Logistic Regression — interpretable baseline
2. Random Forest — nonlinear challenger
3. XGBoost — gradient-boosting challenger

Model comparison will include discrimination, calibration, stability, and interpretability.

**Current status:** Imputation completed; scaling and baseline model training are next.

## 6. Logistic Regression — Baseline Results

### Model Configuration

- Algorithm: Logistic Regression
- Solver: `lbfgs`
- Maximum iterations: 1,000
- Input features: 6 origination-time characteristics
- Missing data: Median imputation, fitted on training data only
- Feature scaling: StandardScaler, fitted on training data only
- Training cohort: 2007 Q1–Q2
- Validation cohort: 2007 Q3

### Validation Performance

| Metric | Result |
|---|---:|
| ROC-AUC | 0.7810 |
| Average Precision | 0.2488 |
| Brier Score | 0.0696 |
| Actual Event Rate | 8.35% |
| Average Predicted PD | 8.25% |

### Model Interpretability

The standardized logistic regression coefficients indicate that higher credit scores are associated with lower serious-delinquency odds, while higher interest rates, loan amounts, CLTV, DTI, and LTV are associated with higher odds, holding the other variables constant.

These associations should not be interpreted as causal relationships. Correlation between LTV and CLTV may also affect individual coefficient stability.

### Calibration Assessment

The validation population was divided into ten equally sized groups based on predicted risk.

Observed serious-delinquency rates increased consistently from 0.53% in the lowest-risk decile to 27.82% in the highest-risk decile.

The model showed modest calibration differences across deciles, with the largest absolute discrepancy of 1.70 percentage points in the highest-risk decile.

Although the overall predicted event rate (8.25%) was close to the observed rate (8.35%), further calibration testing is required.

### Preliminary Assessment

The baseline model demonstrates useful discriminatory ability on the validation population. It also exhibits broadly reasonable probability calibration, with differences that warrant additional investigation.

**Outstanding limitations:**
- Preliminary 24-month target definition
- Exclusion of mortgages with unresolved observation histories
- Potential selection bias from early payoff treatment
- Correlation among explanatory variables
- No completed independent model validation
- Final test cohort not yet evaluated

This assessment is preliminary and does not constitute production model approval.