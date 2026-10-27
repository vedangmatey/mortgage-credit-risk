
# Final Model Evaluation Protocol

[← Back to Project Overview](../README.md)

**Status:** Defined before Q4 evaluation

## 1. Objective

Evaluate the selected mortgage credit risk models on
the reserved 2007 Q4 test cohort without modifying
model specifications based on test results.

This is a research evaluation, not production approval.

## 2. Primary Target Definition

The primary evaluation uses the original
24-month serious-delinquency target.

- Event: Observed numeric delinquency status 03–98
  within 24 scheduled payment months.
- Non-event: Complete 24-month reporting with no
  qualifying serious-delinquency or flagged special status.
- Unresolved outcomes: Excluded.

This target remains provisional. In particular,
sample selection and early-payoff treatment may affect
the interpretation of predicted probabilities.

## 3. Frozen Model Specifications

### Candidate A: XGBoost

- Six origination-time features
- Training population: 2007 Q1–Q2
- Median imputation fitted on training only
- Max depth: 4
- Learning rate: 0.05
- Min child weight: 20
- Subsample: 0.8
- Column sample: 0.9
- L2 regularization: 5
- Best boosting round selected on Q3: 213
- Random seed: 42

### Candidate B: Logistic Regression

- Five origination-time features
- CLTV excluded
- Median imputation fitted on training only
- Standardization fitted on training only
- Solver: lbfgs
- Maximum iterations: 1000

The original six-feature Logistic Regression remains
available as a reference model.

## 4. Final Test Population

- Origination cohort: 2007 Q4
- Preliminary eligible mortgages: 211,425
- Observed serious-delinquency events: 20,176

Q4 has not been used for model training, feature
selection, hyperparameter tuning, or early stopping.

## 5. Evaluation Metrics

The following will be reported for each candidate:

- ROC-AUC
- Average Precision
- Brier Score
- Actual event rate
- Average predicted probability
- Calibration across risk deciles
- Material segment-level performance differences

All models will be assessed on the same primary
Q4 population.

## 6. Decision Rules

Model selection will consider discrimination,
calibration, stability, complexity, interpretability,
and unresolved validation findings.

Small metric differences alone will not establish
superiority.

No hyperparameters, features, target rules, or
preprocessing methods will be changed based on Q4
results.

If material issues emerge, they will be documented
as limitations rather than tuned away on the test set.

## 7. Separate Sensitivity Analysis

The payoff-inclusive alternative target will be
evaluated separately, if warranted.

Its results must be clearly distinguished from the
primary evaluation because its eligible population
and outcome interpretation differ.

## 8. Approval Status

No production deployment or regulatory use is intended.

The final research assessment will report model
performance, open findings, limitations, and
recommendations without implying production approval.


## 9. Final Q4 Evaluation Results

The frozen model specifications were evaluated on
the reserved 2007 Q4 cohort.

### Evaluation Population

| Metric | Value |
|---|---:|
| Test Mortgages | 211,425 |
| Observed Events | 20,176 |
| Observed Event Rate | 9.54% |

### Model Performance

| Metric | Logistic Regression | XGBoost |
|---|---:|---:|
| ROC-AUC | 0.7906 | 0.7956 |
| Average Precision | 0.2910 | 0.3073 |
| Brier Score | 0.0783 | 0.0774 |
| Average Predicted Event Probability | 6.39% | 6.39% |

### Evaluation Findings

XGBoost demonstrated stronger discrimination and a
lower Brier Score than the five-feature Logistic
Regression model.

However, both models materially underestimated
the observed portfolio-level event rate.

The observed event rate was 9.54%, compared with
average predicted probabilities of approximately
6.39% for both models.

This represents an underestimation of approximately
3.15 percentage points.

### Preliminary Validation Conclusion

XGBoost is the stronger candidate based on final
discrimination and Brier Score.

However, the substantial underprediction raises a
material calibration concern.

The models are not considered suitable for
production use based on these results.

No tuning, feature changes, or calibration
adjustments were performed using Q4.

Further descriptive analysis will examine whether
underprediction occurs consistently across risk
deciles or is concentrated in particular segments.

**Final research-model assessment: Pending.**
