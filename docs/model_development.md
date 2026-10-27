# Model Development

[← Back to Project Overview](../README.md)

**Project:** Mortgage Credit Risk — Model Development, Validation & Governance\
**Status:** Research model development and final evaluation completed

## 1. Modeling Objective

Develop and compare statistical and machine learning models to estimate the likelihood of observed serious mortgage delinquency (90+ days past due) within a 24-month observation horizon.

The outcome serves as a research proxy for mortgage default. Its definition remains provisional because of unresolved early-payoff treatment and observation-history limitations.

The project is not intended for production lending decisions or regulatory credit risk estimation.

## 2. Dataset and Modeling Population

The project uses Freddie Mac's 2007 single-family mortgage loan-level data.

| Dataset | Records |
|---|---:|
| Mortgage origination records | 1,238,192 |
| Monthly performance records | 74,478,724 |
| Primary modeling population | 888,123 |
| Observed serious-delinquency events | 59,785 |

### Data Partitioning

| Dataset | Cohort | Mortgages | Events | Event Rate |
|---|---|---:|---:|---:|
| Training | 2007 Q1–Q2 | 488,486 | 23,891 | 4.89% |
| Validation | 2007 Q3 | 188,212 | 15,718 | 8.35% |
| Final Test | 2007 Q4 | 211,425 | 20,176 | 9.54% |

The chronological origination-cohort split was used to separate model training, model selection, and final held-out evaluation.

This is not an independent out-of-time evaluation across different origination years or economic conditions.

### Modeling Population Limitations

The original target definition excludes mortgages with unresolved 24-month observation histories.

A total of 350,069 mortgages were excluded from the primary modeling population.

These exclusions may introduce selection bias. Separate validation analyses investigated population representativeness and alternative early-payoff assumptions.

See [Model Validation](model_validation.md).

## 3. Target Development

The primary outcome identifies observed serious delinquency during the first 24 scheduled payment months.

The provisional classification framework distinguishes:

- **Event:** An observed qualifying numeric serious-delinquency status (03–98) within the observation window.
- **Complete non-event:** A mortgage with complete eligible observation history and no qualifying event.
- **Incomplete history:** A mortgage without sufficient eligible observation history.
- **Special-status review:** A mortgage requiring additional treatment of nonstandard performance statuses.

Only eligible events and complete non-events were included in the primary modeling population.

### Target Definition Limitation

Mortgage payoff and other termination events may occur before the full 24-month horizon.

Excluding these mortgages changes the eligible population and potentially affects estimated event probabilities.

An alternative target incorporating eligible early-payoff mortgages as non-events was evaluated separately as a sensitivity analysis.

Neither target definition has been established as a production-ready default definition.

## 4. Feature Selection

The initial models use six characteristics available at mortgage origination.

| Feature | Description |
|---|---|
| Credit Score | Borrower creditworthiness indicator |
| Original LTV | Original loan amount relative to property value |
| Original CLTV | Combined loan exposure relative to property value |
| Original DTI | Borrower debt-to-income ratio |
| Interest Rate | Original mortgage interest rate |
| Loan Amount | Original mortgage principal amount |

Post-origination performance information was excluded from the predictive features to reduce the risk of forward-looking data leakage.

### Feature Reduction

Validation identified substantial correlation between LTV and CLTV:

| Diagnostic | Result |
|---|---:|
| LTV–CLTV correlation | 0.9166 |
| LTV VIF | 6.44 |
| CLTV VIF | 6.32 |

A reduced Logistic Regression specification excluding CLTV was evaluated on the original Q3 validation population.

| Metric | Six Features | Five Features |
|---|---:|---:|
| ROC-AUC | 0.7810 | 0.7813 |
| Average Precision | 0.2488 | 0.2491 |
| Brier Score | 0.0696 | 0.0695 |
| Average Predicted Event Rate | 8.2518% | 8.3176% |

The five-feature model demonstrated similar predictive performance with a simpler specification.

It was retained as the interpretable benchmark for final Q4 evaluation. The original six-feature baseline remains available for comparison.

Removing CLTV may discard information about additional mortgage liens, so the related validation finding remains open.

## 5. Missing Data and Preprocessing

### Median Imputation

Missing numeric values were replaced using medians calculated exclusively from the training population.

| Feature | Missing Training Values | Training Median |
|---|---:|---:|
| Credit Score | 410 | 726 |
| Original LTV | 43 | 77 |
| Original CLTV | 45 | 80 |
| Original DTI | 9,635 | 37 |
| Interest Rate | 0 | 6.25 |
| Loan Amount | 0 | 158,000 |

Median imputation was selected as a straightforward, reproducible baseline approach that is less sensitive to extreme observations than mean imputation.

### Feature Scaling

Logistic Regression used standardization fitted on the training dataset only.

The same fitted preprocessing transformations were subsequently applied to validation and test data.

### Limitations

Median imputation may conceal informative missingness and does not preserve the original distribution of missing values.

Alternative imputation strategies and missingness indicators were not established as superior within this project.

## 6. Logistic Regression — Original Baseline

### Model Configuration

| Parameter | Specification |
|---|---|
| Algorithm | Logistic Regression |
| Solver | `lbfgs` |
| Maximum Iterations | 1,000 |
| Features | Six origination-time characteristics |
| Missing Data | Training-fitted median imputation |
| Scaling | Training-fitted StandardScaler |
| Training Cohort | 2007 Q1–Q2 |
| Validation Cohort | 2007 Q3 |

### Q3 Validation Performance

| Metric | Result |
|---|---:|
| ROC-AUC | 0.7810 |
| Average Precision | 0.2488 |
| Brier Score | 0.0696 |
| Observed Event Rate | 8.35% |
| Average Predicted Event Rate | 8.25% |

### Coefficient Interpretation

Standardized Logistic Regression coefficients were:

| Feature | Coefficient |
|---|---:|
| Credit Score | -0.7345 |
| Original LTV | 0.1371 |
| Original CLTV | 0.2588 |
| Original DTI | 0.2231 |
| Interest Rate | 0.4531 |
| Loan Amount | 0.3083 |

Higher credit scores were associated with lower estimated serious-delinquency odds.

Higher values of the other included variables were associated with higher estimated odds, holding the remaining features constant.

These relationships are not causal estimates. The strong correlation between LTV and CLTV also limits confidence in interpreting their individual coefficients.

### Calibration Assessment

On the Q3 validation population, observed event rates increased from 0.53% in the lowest predicted-risk decile to 27.82% in the highest.

The highest-risk decile had an average predicted event rate of 29.52%, representing an overprediction of approximately 1.70 percentage points.

Although aggregate Q3 calibration was relatively close, this did not establish reliability across later cohorts.

## 7. Challenger Model Development

Random Forest and XGBoost were developed as nonlinear alternatives to Logistic Regression.

### Q3 Validation Comparison

All three models were compared on the same original Q3 validation population of 188,212 mortgages.

| Metric | Logistic Regression | Random Forest | XGBoost |
|---|---:|---:|---:|
| ROC-AUC | 0.7810 | 0.7816 | **0.7843** |
| Average Precision | 0.2488 | 0.2518 | **0.2579** |
| Brier Score | 0.0696 | 0.0693 | **0.0691** |
| Average Predicted Event Rate | 8.25% | 8.40% | 8.73% |

The observed Q3 event rate was 8.35%.

### Random Forest

The Random Forest challenger used:

- 100 trees.
- Maximum depth of 10.
- Minimum leaf size of 100.

It produced modest improvements over the original Logistic Regression baseline but did not materially outperform it.

### XGBoost

The XGBoost challenger used gradient-boosted decision trees with regularization and validation-based early stopping.

| Parameter | Value |
|---|---:|
| Maximum Boosting Rounds | 400 |
| Selected Boosting Round | 213 |
| Maximum Tree Depth | 4 |
| Learning Rate | 0.05 |
| Minimum Child Weight | 20 |
| Subsample | 0.80 |
| Column Subsample | 0.90 |
| L2 Regularization | 5 |

XGBoost achieved the strongest Q3 validation discrimination and the lowest Brier Score among the three algorithms.

### Overfitting Assessment

| Metric | XGBoost ROC-AUC |
|---|---:|
| Training | 0.8054 |
| Validation | 0.7843 |
| Difference | 0.0211 |

The observed difference does not by itself establish overfitting.

Differences between mortgage origination cohorts may also contribute to the performance gap.

### XGBoost Calibration

Within the highest-risk Q3 validation decile:

- Observed event rate: 28.44%.
- Average predicted event rate: 30.53%.
- Overprediction: 2.09 percentage points.

These results supported further evaluation of XGBoost but did not establish production-quality probability estimates.

## 8. Final Model Selection for Testing

Before examining the reserved Q4 test cohort, the following specifications were identified for final evaluation.

**Candidate A — XGBoost**

Six origination-time features, with the boosting-round selection and other model parameters fixed using prior validation evidence.

**Candidate B — Five-feature Logistic Regression**

Original six-feature specification excluding CLTV, using training-fitted median imputation and standardization.

Random Forest was retained as an additional development challenger but was not prioritized for final Q4 evaluation.

The selection criteria considered discrimination, calibration, robustness, interpretability, and complexity.

The documented testing protocol is available in [Final Model Evaluation Protocol](final_test_protocol.md).

## 9. Final Q4 Held-Out Evaluation

The frozen candidate specifications were evaluated on 211,425 eligible mortgages originated in 2007 Q4.

The population contained 20,176 observed serious-delinquency events, corresponding to an event rate of 9.54%.

### Final Results

| Metric | Five-Feature Logistic Regression | XGBoost |
|---|---:|---:|
| ROC-AUC | 0.7906 | **0.7956** |
| Average Precision | 0.2910 | **0.3073** |
| Brier Score | 0.0783 | **0.0774** |
| Average Predicted Event Rate | 6.39% | 6.39% |
| Observed Event Rate | 9.54% | 9.54% |

### Performance Interpretation

XGBoost demonstrated stronger discrimination and a slightly lower Brier Score than the five-feature Logistic Regression model.

However, both models underestimated the observed portfolio-level event rate by approximately 3.15 percentage points.

The underprediction was observed across all ten risk deciles for both models and was more pronounced in higher-risk segments.

For the highest predicted-risk decile:

| Measure | Logistic Regression | XGBoost |
|---|---:|---:|
| Observed Event Rate | 32.63% | 33.76% |
| Average Predicted Event Rate | 25.68% | 25.31% |
| Underprediction | 6.95 pp | 8.45 pp |

Each model's deciles were constructed independently, so corresponding deciles may contain different mortgages.

No post-test tuning or calibration adjustments were performed using Q4 results.

## 10. Final Model Development Assessment

The project successfully developed and compared three mortgage credit risk modeling approaches.

**XGBoost is the strongest research candidate for ranking mortgages by the observed serious-delinquency outcome.**

The five-feature Logistic Regression remains an interpretable benchmark with relatively similar discriminatory performance.

However, neither model has demonstrated sufficiently reliable probability calibration for production credit risk estimation.

Outstanding limitations include:

- The provisional 24-month target definition and early-payoff treatment.
- Potential population-selection bias.
- Interest-rate distribution shifts across cohorts.
- Correlated leverage-related predictors.
- Material probability underprediction in Q4.
- Limited generalizability beyond the 2007 origination cohorts.

**Development status:** Research development and held-out evaluation completed.

**Production recommendation:** Not recommended for production probability estimation.

For detailed validation findings and remediation recommendations, see [Model Validation](model_validation.md) and [Model Governance](model_governance.md).

---

*This project is intended for research, educational purposes, and portfolio demonstration. It does not represent a production-approved mortgage credit risk model.*