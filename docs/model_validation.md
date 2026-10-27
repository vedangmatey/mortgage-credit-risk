# Independent-Style Model Validation

[← Back to Project Overview](../README.md)

## 1. Validation Objective

Assess the reliability, limitations, and robustness of the mortgage Probability of Default models developed using Freddie Mac's 2007 loan-level dataset.

**Status:** In Progress

Validation is maintained as a separate workstream from model development. Because this is an individual research project, it is not organizationally independent validation.

## 2. Population Representativeness

The preliminary modeling population contains 888,123 mortgages out of 1,238,192 original mortgages.

**350,069 mortgages (28.3%) were excluded**, primarily because of incomplete 24-month observation histories.

Exclusion rates differed across origination cohorts:

| Cohort | Exclusion Rate |
|---|---:|
| 2007 Q1 | 24.14% |
| 2007 Q2 | 26.81% |
| 2007 Q3 | 33.96% |
| 2007 Q4 | 28.77% |

Excluded mortgages generally had higher average credit scores and lower LTV and DTI values than included mortgages.

**Validation concern:** The modeling sample may not represent the full originating mortgage portfolio.

## 3. Early-Payoff Sensitivity Analysis

### Objective

Determine whether including mortgages with verified continuous reporting through early payoff materially changes model predictions.

### Alternative Target Assumption

- Original approach: Exclude mortgages with incomplete 24-month histories.
- Sensitivity approach: Include 256,875 eligible clean early-payoff mortgages as non-events.
- Preserve all original observed serious-delinquency events.
- Exclude mortgages with unresolved reporting histories and special-status concerns.

The sensitivity target increased the available modeling population from 888,123 to 1,144,998 mortgages.

### Common-Population Model Comparison

Two Logistic Regression models were trained separately and evaluated on the same 188,212 original Q3 validation mortgages.

| Metric | Original | Payoff Sensitivity |
|---|---:|---:|
| Training Mortgages | 488,486 | 591,932 |
| ROC-AUC | 0.7810 | 0.7793 |
| Average Precision | 0.2488 | 0.2446 |
| Brier Score | 0.0696 | 0.0701 |
| Average Predicted PD | 8.25% | 6.73% |
| Actual Event Rate | 8.35% | 8.35% |

### Findings

Adding 103,446 eligible early-payoff mortgages to the training population reduced average predicted risk by 1.52 percentage points on the common validation population.

The sensitivity model underpredicted the observed validation event rate by 1.62 percentage points.

Discriminatory performance changed relatively little, with a ROC-AUC reduction of 0.0017.

### Interpretation

Model probability estimates are materially sensitive to the treatment of early mortgage payoffs.

The results demonstrate the importance of distinguishing discriminatory performance from probability calibration.

This does not establish that either target definition is definitively preferable. Early payoff is a competing outcome, and the comparison uses the original validation population rather than an expanded payoff-inclusive validation population.

### Expanded Validation Population Assessment

A second evaluation included 79,556 eligible clean
early-payoff mortgages in the 2007 Q3 validation population.

The expanded validation sample contained 267,768
mortgages and 15,718 serious-delinquency events,
resulting in an observed event rate of 5.87%.

| Metric | Original Model | Sensitivity Model |
|---|---:|---:|
| ROC-AUC | 0.7998 | 0.8000 |
| Average Precision | 0.2055 | 0.2037 |
| Brier Score | 0.0512 | 0.0508 |
| Average Predicted PD | 7.49% | 6.06% |
| Observed Event Rate | 5.87% | 5.87% |

#### Validation Interpretation

Including eligible early-payoff mortgages in training
and validation reduced portfolio-level overprediction
from 1.62 to 0.19 percentage points.

Discriminatory performance remained similar, while
the Brier Score improved modestly.

This demonstrates sensitivity of estimated PDs to
population eligibility and early-payoff assumptions.

The expanded-population results are conditional on
the alternative target definition and do not establish
that early payoffs should automatically be classified
as 24-month non-events.

#### Validation Conclusion

**Finding MV-001: Remains open.**

The alternative target definition improves aggregate
calibration on the expanded Q3 population. However,
further investigation of competing events, decile-level
calibration, and portfolio representativeness is required.

The reserved Q4 test population remains untouched.


### Risk-Decile Calibration Assessment

Both Logistic Regression models were evaluated across ten
common risk groups in the expanded 2007 Q3 validation
population of 267,768 mortgages.

Risk deciles were defined using the original model's
predicted probabilities to ensure identical group membership.

| Decile | Actual Rate | Original PD | Sensitivity PD |
|---|---:|---:|---:|
| 1 | 0.30% | 0.60% | 0.43% |
| 2 | 0.56% | 1.31% | 0.97% |
| 3 | 1.00% | 2.02% | 1.53% |
| 4 | 1.89% | 2.86% | 2.19% |
| 5 | 2.68% | 3.90% | 3.03% |
| 6 | 3.91% | 5.26% | 4.12% |
| 7 | 6.01% | 7.12% | 5.64% |
| 8 | 8.43% | 9.82% | 7.89% |
| 9 | 12.01% | 14.33% | 11.65% |
| 10 | 21.92% | 27.71% | 23.11% |

#### Key Findings

- The sensitivity model had smaller absolute calibration
  errors in all ten risk deciles.
- In the highest-risk decile, overprediction decreased
  from 5.79 to 1.19 percentage points.
- The sensitivity model slightly underpredicted risk
  in deciles 7 through 9.
- Improvement in calibration is conditional on the
  expanded early-payoff target definition.

#### Validation Assessment

The early-payoff sensitivity model demonstrates improved
probability calibration across the expanded validation
population, with little change in discriminatory performance.

Finding MV-001 remains open pending target-definition
review, competing-risk assessment, and additional
robustness testing.

The reserved Q4 test cohort has not been evaluated.


## 4. Validation Findings Register

| ID | Finding | Status |
|---|---|---|
| MV-001 | Model predictions are sensitive to early-payoff target treatment | Open |
| MV-002 | Modeling population may be subject to selection bias | Open |

## 5. Further Validation Required

- Target definition and reporting-history review
- Early payoff as a competing event
- Calibration under a common and expanded evaluation population
- Stability across mortgage origination cohorts
- Model complexity and interpretability
- Robustness of explanatory variables
- Final reserved Q4 test evaluation
- Model limitations and recommended governance controls

No production model approval or final validation conclusion has been issued.