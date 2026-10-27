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


### Feature Stability and Interest-Rate Calibration

#### Population Stability Assessment

Feature distributions were compared between the
2007 Q1-Q2 training and Q3 validation cohorts using
Population Stability Index (PSI).

| Feature | PSI |
|---|---:|
| Credit Score | 0.0060 |
| Original LTV | 0.0655 |
| Original CLTV | 0.0238 |
| Original DTI | 0.0077 |
| Interest Rate | 1.2899 |
| Loan Amount | 0.0164 |

Interest rate exhibited the largest distribution shift.

Median mortgage interest rates increased from 6.25%
in training to 6.75% in validation.

PSI is a population-shift diagnostic and does not
independently establish model failure.

#### Interest-Rate Segment Calibration

The original Logistic Regression model was evaluated
on the Q3 validation population.

| Interest Rate | Actual Rate | Predicted PD | Error (pp) |
|---|---:|---:|---:|
| <= 5.875% | 3.03% | 1.86% | -1.17 |
| 5.875-6.25% | 4.22% | 3.50% | -0.72 |
| 6.25-6.50% | 5.53% | 5.14% | -0.39 |
| 6.50-6.75% | 6.69% | 7.21% | +0.53 |
| > 6.75% | 13.34% | 13.28% | -0.06 |

#### Validation Findings

- Interest-rate distributions changed substantially
  between the training and validation cohorts.
- The model underpredicted risk in the lowest-rate group
  by 1.17 percentage points.
- The highest-rate group exhibited a small calibration
  difference of -0.06 percentage points.
- Distribution shift did not result in uniformly poor
  calibration across interest-rate segments.

**Finding MV-003: Open**

Further investigation is needed to assess segment
stability, potential confounding risk characteristics,
and the reliability of predictions across cohorts.

The reserved Q4 test population remains untouched.


### Multicollinearity and Coefficient Robustness

#### Validation Objective

Assess whether correlated explanatory variables create
coefficient interpretability concerns in the baseline
Logistic Regression model.

#### Variance Inflation Factor Analysis

| Feature | VIF |
|---|---:|
| Original LTV | 6.44 |
| Original CLTV | 6.32 |
| Interest Rate | 1.16 |
| Loan Amount | 1.12 |
| Credit Score | 1.10 |
| Original DTI | 1.06 |

LTV and CLTV exhibited a Pearson correlation of 0.9166.

The two variables contain substantial overlapping
information, which may affect coefficient interpretation
and statistical stability.

#### Reduced-Feature Model Comparison

A five-feature Logistic Regression model excluding CLTV
was trained using the original training population and
evaluated on the same Q3 validation population.

| Metric | Original Model | Without CLTV |
|---|---:|---:|
| ROC-AUC | 0.7810 | 0.7813 |
| Standardized LTV Coefficient | 0.1371 | 0.3615 |
| Number of Features | 6 | 5 |

Removing CLTV changed the estimated LTV coefficient
substantially but produced a negligible change in ROC-AUC.

#### Validation Assessment

The analysis identifies meaningful multicollinearity
between LTV and CLTV, creating potential concerns for
individual coefficient interpretation.

The six-feature baseline is retained for comparison.
The reduced model remains a candidate for simplification,
subject to calibration and robustness testing.

**Finding MV-004: Open — Multicollinearity and coefficient
interpretability.**

No final feature-removal decision has been made.


#### Feature Removal — Probability Calibration

The original six-feature Logistic Regression model
was compared against a simplified five-feature model
excluding CLTV.

Both models were evaluated on the same 2007 Q3
validation population of 188,212 mortgages.

| Metric | 6 Features | 5 Features |
|---|---:|---:|
| ROC-AUC | 0.7810 | 0.7813 |
| Average Precision | 0.2488 | 0.2491 |
| Brier Score | 0.0696 | 0.0695 |
| Average Predicted PD | 8.2518% | 8.3176% |
| Observed Event Rate | 8.35% | 8.35% |

##### Validation Assessment

Removing CLTV produced negligible improvements in
discrimination, Average Precision, and Brier Score.

The simplified model also demonstrated a smaller
portfolio-level calibration difference.

Given the strong correlation between LTV and CLTV,
the five-feature specification is recommended as a
preferred simplified Logistic Regression candidate.

However, the improvement is small, and removing
CLTV may discard information about additional liens.

Finding MV-004 remains open pending coefficient
stability analysis and segment-level calibration.

The original six-feature model is preserved for
comparison. No final model selection has been approved.


### Final Q4 Calibration Assessment

#### Objective

Assess the calibration of frozen model predictions on
the reserved 2007 Q4 test population.

#### Test Population

- Mortgages: 211,425
- Observed serious-delinquency events: 20,176
- Observed event rate: 9.54%

#### Portfolio-Level Results

| Metric | Logistic Regression | XGBoost |
|---|---:|---:|
| ROC-AUC | 0.7906 | 0.7956 |
| Average Precision | 0.2910 | 0.3073 |
| Brier Score | 0.0783 | 0.0774 |
| Average Predicted Probability | 6.39% | 6.39% |
| Observed Event Rate | 9.54% | 9.54% |

Both models underestimated the observed portfolio-level
event rate by approximately 3.15 percentage points.

#### Risk-Decile Calibration

| Decile | Logistic Error (pp) | XGBoost Error (pp) |
|---|---:|---:|
| 1 | -0.04 | -0.22 |
| 2 | -0.29 | -0.63 |
| 3 | -0.68 | -1.07 |
| 4 | -1.21 | -1.41 |
| 5 | -2.09 | -1.94 |
| 6 | -3.39 | -3.08 |
| 7 | -4.29 | -3.71 |
| 8 | -5.51 | -4.66 |
| 9 | -7.07 | -6.36 |
| 10 | -6.95 | -8.45 |

Negative errors indicate underprediction.

Risk deciles were constructed independently for each
model, so corresponding deciles do not necessarily
contain the same mortgages.

#### Validation Finding MV-005

**Title:** Systematic underprediction in final Q4 testing

**Status:** Open

Both models underestimated observed serious-delinquency
rates across all ten risk deciles.

The calibration deficiencies were more pronounced in
higher-risk segments.

Although XGBoost demonstrated stronger discrimination
and a lower Brier Score, its highest-risk decile showed
an 8.45 percentage-point underprediction.

#### Validation Assessment

The models demonstrate useful risk-ranking ability,
but their predicted probabilities are insufficiently
calibrated on the reserved Q4 population.

This finding presents a material limitation for uses
requiring accurate absolute event probabilities.

Potential contributors include cohort differences,
model specification, and the provisional target and
population-selection assumptions.

These explanations have not been established as causes.

No recalibration, hyperparameter tuning, or feature
changes will be performed using the Q4 test results.

**Recommendation:** Do not approve either model for
production probability estimation. Retain Q4 results
as final held-out evaluation evidence and document
the calibration limitation.


## 4. Validation Findings Register

| ID | Finding | Status |
|---|---|---|
| MV-001 | Model predictions are sensitive to early-payoff target treatment | Open |
| MV-002 | Modeling population may be subject to selection bias | Open |
| MV-003 | Interest-rate distribution shift and segment-level calibration differences | Open |
| MV-004 | LTV/CLTV multicollinearity and coefficient interpretability | Open |
| MV-005 | Systematic Q4 underprediction across risk deciles | Open |

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


---

## 5. Final Model Validation Assessment

### 5.1 Validation Scope

The project evaluated mortgage credit risk models using
Freddie Mac 2007 loan-level mortgage data.

Validation covered:

- Data integrity and reconciliation
- Outcome definition and population selection
- Model discrimination and probability calibration
- Feature distribution stability
- Multicollinearity and model simplification
- Sensitivity to alternative early-payoff assumptions
- Performance on a reserved origination-cohort test set

This is a self-conducted research validation exercise,
not an organizationally independent model validation.

### 5.2 Final Model Performance

The selected model candidates were evaluated using
211,425 mortgages originated in 2007 Q4.

| Metric | Logistic Regression | XGBoost |
|---|---:|---:|
| ROC-AUC | 0.7906 | 0.7956 |
| Average Precision | 0.2910 | 0.3073 |
| Brier Score | 0.0783 | 0.0774 |
| Average Predicted Event Rate | 6.39% | 6.39% |
| Observed Event Rate | 9.54% | 9.54% |

XGBoost demonstrated better discrimination and a
slightly lower Brier Score.

However, both models underestimated observed
serious-delinquency rates by approximately
3.15 percentage points.

Underprediction occurred across all ten risk deciles
for both models.

### 5.3 Outstanding Validation Findings

| Finding | Description | Status |
|---|---|---|
| MV-001 | Early-payoff treatment sensitivity | Open |
| MV-002 | Potential population selection bias | Open |
| MV-003 | Interest-rate distribution shift | Open |
| MV-004 | LTV/CLTV multicollinearity | Open |
| MV-005 | Systematic Q4 underprediction | Open |

The findings remain open because identifying and
documenting a model risk does not resolve it.

### 5.4 Overall Validation Conclusion

The models demonstrate useful discriminatory power
for ranking mortgages by the observed
serious-delinquency outcome.

However, the evidence does not establish that their
predicted probabilities are sufficiently reliable
for production credit risk estimation.

Material limitations include:

1. Provisional target definition and treatment of
   early mortgage payoffs.
2. Potential selection bias from excluding incomplete
   observation histories.
3. Meaningful interest-rate distribution differences
   between development and validation cohorts.
4. Coefficient interpretability concerns associated
   with correlated LTV and CLTV variables.
5. Systematic probability underprediction in the
   reserved Q4 test population.
6. Limited temporal generalizability because all
   mortgages originated during 2007.

### 5.5 Final Validation Recommendation

**Validation disposition: Not recommended for
production probability estimation.**

XGBoost is identified as the stronger research
candidate for risk ranking based on final
discrimination and Brier Score.

The five-feature Logistic Regression model remains
an interpretable benchmark.

Neither model is approved for production deployment.

The reserved Q4 results must not be used to tune
the evaluated model specifications.

Any future model revisions should use a documented
development process and new independent evaluation
data before making stronger performance claims.

### 5.6 Research Project Status

**Technical validation assessment: Completed**

**Outstanding findings: 5 Open**

**Production approval: Not granted**

The next project phase is to document the final
governance disposition, ownership, monitoring
requirements, and recommended remediation actions.
