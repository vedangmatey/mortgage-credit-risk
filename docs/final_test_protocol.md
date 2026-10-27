# Final Model Evaluation Protocol

[← Back to Project Overview](../README.md)

**Project:** Mortgage Credit Risk — Model Development, Validation & Governance\
**Status:** Final held-out evaluation completed\
**Evaluation Cohort:** 2007 Q4\
**Production Recommendation:** Not recommended

## 1. Evaluation Objective

Evaluate the selected mortgage credit risk models on a reserved test population to assess discrimination, probability calibration, and generalization to a later 2007 origination cohort.

The protocol separates model-selection decisions made before testing from the performance findings obtained afterward.

The evaluation is intended for research and methodological assessment, not production model approval.

## 2. Data Partitioning and Target Definition

### 2.1 Data Partitioning

| Dataset | Cohort | Mortgages | Purpose |
|---|---|---:|---|
| Training | 2007 Q1–Q2 | 488,486 | Model fitting |
| Validation | 2007 Q3 | 188,212 | Model selection and configuration |
| Final Test | 2007 Q4 | 211,425 | Held-out evaluation |

The cohorts were separated chronologically by mortgage origination quarter.

Because all mortgages originated in 2007, the test does not establish generalization across different origination years or economic environments.

### 2.2 Primary Target Definition

The primary evaluation used the original provisional 24-month serious-delinquency outcome.

- **Event:** An observed qualifying numeric delinquency status (03–98) within the first 24 scheduled payment months.
- **Complete non-event:** Complete eligible observation history without a qualifying event.
- **Unresolved outcome:** Excluded from the primary modeling population.
- **Special-status review:** Excluded pending further assessment.

This target is a research proxy for mortgage default, not an established production probability-of-default definition.

### 2.3 Target Limitations

The original population excludes mortgages with incomplete observation histories, including eligible early payoffs.

Alternative early-payoff treatment was investigated during validation, but it was not substituted into the primary final-test definition.

The two approaches represent different target and population assumptions and should not be directly mixed when interpreting their performance.

Detailed sensitivity findings are maintained in [Model Validation](model_validation.md).

## 3. Pre-Test Model Selection

The following candidate specifications and evaluation criteria were established before examining the reserved Q4 test results.

### 3.1 Candidate A — XGBoost

| Parameter | Specification |
|---|---|
| Algorithm | XGBoost Classifier |
| Input Features | Six origination-time characteristics |
| Training Population | 2007 Q1–Q2 |
| Missing Data | Training-fitted median imputation |
| Maximum Tree Depth | 4 |
| Learning Rate | 0.05 |
| Minimum Child Weight | 20 |
| Subsample | 0.80 |
| Column Subsample | 0.90 |
| L2 Regularization | 5 |
| Boosting Rounds for Final Evaluation | 213 |
| Random Seed | 42 |

The boosting-round count was selected using Q3 validation evidence before the final Q4 evaluation.

### 3.2 Candidate B — Logistic Regression

| Parameter | Specification |
|---|---|
| Algorithm | Logistic Regression |
| Input Features | Five origination-time characteristics |
| Excluded Feature | Original CLTV |
| Training Population | 2007 Q1–Q2 |
| Missing Data | Training-fitted median imputation |
| Scaling | Training-fitted StandardScaler |
| Solver | `lbfgs` |
| Maximum Iterations | 1,000 |

The reduced five-feature specification was selected for its interpretability and performance comparable to the original six-feature baseline.

The original six-feature Logistic Regression and Random Forest remained development benchmarks rather than prioritized final-test candidates.

## 4. Pre-Test Evaluation Criteria

Final assessment was designed to consider the following measures.

| Evaluation Area | Metric or Assessment |
|---|---|
| Discrimination | ROC-AUC |
| Event Identification | Average Precision |
| Probability Accuracy | Brier Score |
| Portfolio Calibration | Average predicted versus observed event rate |
| Risk-Segment Calibration | Predicted versus observed rates across risk deciles |
| Interpretability | Model complexity and explanatory transparency |
| Robustness | Previously documented sensitivity and stability findings |
| Governance | Material limitations and unresolved validation findings |

No single metric would automatically establish model superiority or production suitability.

### 4.1 Evaluation Controls

The protocol required that:

1. Candidate model specifications be frozen before Q4 testing.
2. Both candidates use the same primary Q4 evaluation population.
3. Preprocessing transformations be fitted using training data only.
4. Q4 data not be used for feature selection, hyperparameter tuning, or early stopping.
5. Material performance weaknesses be reported.
6. Q4 results not be used to recalibrate or optimize the evaluated models.
7. The final research assessment consider performance and unresolved model risks together.

## 5. Final Q4 Evaluation Population

The frozen candidate models were evaluated on eligible mortgages from the 2007 Q4 origination cohort.

| Measure | Value |
|---|---:|
| Test Mortgages | 211,425 |
| Observed Serious-Delinquency Events | 20,176 |
| Observed Event Rate | 9.54% |

The two models were evaluated on the same primary test population.

## 6. Final Model Performance

| Metric | Five-Feature Logistic Regression | XGBoost |
|---|---:|---:|
| ROC-AUC | 0.7906 | **0.7956** |
| Average Precision | 0.2910 | **0.3073** |
| Brier Score | 0.0783 | **0.0774** |
| Average Predicted Event Rate | 6.39% | 6.39% |
| Observed Event Rate | 9.54% | 9.54% |

### 6.1 Discrimination

XGBoost achieved higher ROC-AUC and Average Precision than the five-feature Logistic Regression model.

This indicates stronger discrimination on the Q4 test population.

However, the differences alone do not establish statistical superiority or suitability for operational credit risk estimation.

### 6.2 Probability Calibration

Both models predicted an average event probability of approximately 6.39%, compared with an observed event rate of 9.54%.

The portfolio-level underprediction was approximately **3.15 percentage points**.

Although XGBoost achieved a slightly lower Brier Score, both models showed material calibration deficiencies.

## 7. Risk-Decile Calibration Assessment

The final assessment compared predicted and observed event rates across ten equally sized risk groups for each model.

Risk deciles were constructed independently based on each model's predicted probabilities.

### 7.1 Calibration Error by Decile

Errors are measured in percentage points as:

**Calibration Error = Predicted Event Rate − Observed Event Rate**

Negative values indicate underprediction.

| Risk Decile | Logistic Regression Error (pp) | XGBoost Error (pp) |
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

### 7.2 Highest-Risk Decile

| Measure | Logistic Regression | XGBoost |
|---|---:|---:|
| Observed Event Rate | 32.63% | 33.76% |
| Average Predicted Event Rate | 25.68% | 25.31% |
| Underprediction | 6.95 pp | 8.45 pp |

Both models underestimated observed risk across every decile.

The absolute calibration discrepancies were generally larger in the higher-risk segments.

XGBoost had stronger overall discrimination but a larger underprediction in its highest-risk decile.

These results highlight the distinction between the ability to rank mortgages by risk and the ability to estimate reliable event probabilities.

Complete calibration evidence is documented in [Model Validation](model_validation.md).

## 8. Final Evaluation Findings

The evaluation established three central conclusions.

**First, XGBoost demonstrated stronger discrimination.**

XGBoost achieved the highest Q4 ROC-AUC and Average Precision among the two frozen candidate models.

**Second, probability calibration was materially deficient.**

Both models underestimated the observed Q4 portfolio event rate and showed underprediction throughout their risk-decile distributions.

**Third, predictive performance must be evaluated alongside model assumptions.**

The target definition, early-payoff treatment, population eligibility, feature stability, and temporal generalizability remain important limitations.

The final-test evidence supports validation finding **MV-005 — Systematic Q4 Probability Underprediction**, which remains open.

No model specification, feature, or calibration adjustment was made using Q4 results.

## 9. Final Research-Model Assessment

### 9.1 Comparative Assessment

**XGBoost:** Stronger research candidate for ranking mortgages by observed serious-delinquency risk.

**Five-feature Logistic Regression:** Interpretable benchmark with relatively similar discrimination.

Neither model demonstrated sufficiently reliable absolute probabilities for production credit risk estimation.

### 9.2 Validation and Governance Status

| Assessment Item | Status |
|---|---|
| Final held-out evaluation | Completed |
| Q4 discrimination analysis | Completed |
| Q4 portfolio calibration analysis | Completed |
| Q4 risk-decile calibration analysis | Completed |
| Post-test model tuning | Not performed |
| Outstanding validation findings | Five open |
| Production recommendation | Not recommended |
| Formal production approval | Not granted |

### 9.3 Final Disposition

**Final research assessment: Completed with material limitations.**

**Production recommendation: Not recommended for production probability estimation.**

Future model development should address target-definition assumptions, early-payoff treatment, population-selection risks, probability calibration, and generalization across different economic periods.

Any revised models should be assessed using an appropriately designed development process and new independent evaluation data.

The Q4 results will remain final held-out evaluation evidence for the frozen specifications and will not be used to optimize those evaluated models.

The detailed disposition and proposed remediation plan are documented in [Model Governance](model_governance.md).

---

*This protocol documents an individual research evaluation. It does not constitute organizationally independent model validation, formal model approval, or regulatory compliance certification.*