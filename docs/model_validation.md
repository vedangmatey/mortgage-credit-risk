# Model Validation

[← Back to Project Overview](../README.md)

**Project:** Mortgage Credit Risk — Model Development, Validation & Governance\
**Status:** Research validation assessment completed\
**Outstanding Findings:** Five open\
**Production Recommendation:** Not recommended for production probability estimation

## 1. Validation Objective and Scope

Assess the reliability, robustness, predictive performance, and limitations of mortgage credit risk models developed using Freddie Mac's 2007 single-family loan-level dataset.

The evaluation focuses on estimating observed serious mortgage delinquency (90+ days past due) within a provisional 24-month observation horizon.

Validation activities include:

- Data integrity and modeling-population assessment.
- Outcome definition and early-payoff sensitivity.
- Probability calibration and discriminatory performance.
- Population and feature stability.
- Multicollinearity and feature selection.
- Frozen-model performance on a reserved test cohort.
- Documentation of model limitations and remediation recommendations.

**Independence limitation:** Validation was conducted as a separate workstream within an individual research project. It is not organizationally independent model validation performed by a financial institution.

The outcome is a serious-delinquency proxy for default, not a production-validated Probability of Default (PD) measure.

## 2. Data Quality and Population Representativeness

### 2.1 Data Integrity

The source dataset contains:

| Description | Records |
|---|---:|
| Mortgage originations | 1,238,192 |
| Monthly performance observations | 74,478,724 |

Automated controls covered origination identifier uniqueness, loan matching between origination and performance records, reporting-date validity, duplicate loan-month observations, and quarterly record reconciliation.

These checks support initial data integrity but do not establish full model reliability.

### 2.2 Modeling Population

The primary modeling population includes 888,123 eligible mortgages.

| Population Classification | Mortgages |
|---|---:|
| Observed serious-delinquency events | 59,785 |
| Complete non-events | 828,338 |
| Incomplete observation histories | 350,057 |
| Special-status review | 12 |
| **Total mortgage originations** | **1,238,192** |

**350,069 mortgages, or approximately 28.3% of the original population, were excluded** from the primary modeling population.

### 2.3 Cohort-Level Exclusions

| Origination Cohort | Exclusion Rate |
|---|---:|
| 2007 Q1 | 24.14% |
| 2007 Q2 | 26.81% |
| 2007 Q3 | 33.96% |
| 2007 Q4 | 28.77% |

Excluded mortgages generally had higher average credit scores and lower LTV and DTI values than included mortgages.

This indicates that the eligible modeling sample may differ systematically from the full mortgage-origination portfolio.

### 2.4 Validation Finding MV-002

**Title:** Potential modeling-population selection bias\
**Status:** Open

Exclusion of mortgages without complete eligible observation histories may affect population representativeness and estimated event probabilities.

**Recommendation:** Review excluded populations, establish defensible eligibility criteria, and investigate methods for handling incomplete histories and early termination.

The available evidence identifies a selection-bias concern but does not quantify the causal contribution of exclusions to the final Q4 calibration error.

## 3. Target Definition and Early-Payoff Sensitivity

### 3.1 Primary Target Assumption

The original target uses the first 24 scheduled payment months.

- **Event:** An observed qualifying numeric delinquency status (03–98) within the observation horizon.
- **Complete non-event:** Complete eligible reporting history without a qualifying event.
- **Incomplete history:** Insufficient eligible reporting observations.
- **Special-status review:** Nonstandard performance statuses requiring further investigation.

Only events and complete non-events are included in the primary modeling population.

The definition remains provisional, especially because mortgage payoff and other termination events may prevent observation through the entire horizon.

### 3.2 Alternative Early-Payoff Assumption

The sensitivity analysis treated eligible mortgages with verified continuous reporting through early payoff as non-events.

| Measure | Value |
|---|---:|
| Original eligible population | 888,123 |
| Additional eligible early-payoff mortgages | 256,875 |
| Alternative eligible population | 1,144,998 |
| Observed serious-delinquency events | 59,785 |

The original target and modeling datasets were preserved.

The alternative assumption is a sensitivity scenario, not evidence that every early payoff should be classified as a 24-month non-event.

### 3.3 Common-Population Validation

Two Logistic Regression models were trained under different target and population assumptions.

Both were evaluated on the same original Q3 validation population of 188,212 mortgages.

| Metric | Original Model | Payoff Sensitivity Model |
|---|---:|---:|
| Training Mortgages | 488,486 | 591,932 |
| ROC-AUC | 0.7810 | 0.7793 |
| Average Precision | 0.2488 | 0.2446 |
| Brier Score | 0.0696 | 0.0701 |
| Average Predicted Event Rate | 8.25% | 6.73% |
| Observed Event Rate | 8.35% | 8.35% |

Including eligible early-payoff mortgages in training reduced average predicted risk by approximately 1.52 percentage points on the common validation population.

The sensitivity model underestimated the observed rate by approximately 1.62 percentage points.

Discriminatory performance changed relatively little.

### 3.4 Expanded-Population Validation

A separate evaluation added 79,556 eligible early-payoff mortgages to the original Q3 validation population.

| Measure | Value |
|---|---:|
| Expanded Validation Mortgages | 267,768 |
| Serious-Delinquency Events | 15,718 |
| Observed Event Rate | 5.87% |

| Metric | Original Model | Sensitivity Model |
|---|---:|---:|
| ROC-AUC | 0.7998 | 0.8000 |
| Average Precision | 0.2055 | 0.2037 |
| Brier Score | 0.0512 | 0.0508 |
| Average Predicted Event Rate | 7.49% | 6.06% |
| Observed Event Rate | 5.87% | 5.87% |

The original model overpredicted the observed rate by approximately 1.62 percentage points.

The sensitivity model overpredicted it by approximately 0.19 percentage points.

The improvement was conditional on the alternative target assumption and expanded evaluation population.

### 3.5 Common Risk-Decile Comparison

Risk deciles were constructed using the original model's predictions so that both models were compared on identical mortgage groups.

| Decile | Observed Rate | Original Predicted Rate | Sensitivity Predicted Rate |
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

The sensitivity model demonstrated smaller absolute calibration errors in all ten deciles.

In the highest-risk decile, overprediction decreased from 5.79 to 1.19 percentage points.

### 3.6 Validation Finding MV-001

**Title:** Sensitivity to early-payoff target treatment\
**Status:** Open

Model probability estimates are materially sensitive to early-payoff treatment and associated population eligibility.

**Recommendation:** Finalize the intended estimand, investigate early payoff as a competing event, and establish a defensible target and eligibility methodology.

Neither target definition has been established as definitively preferable.

## 4. Feature Stability and Interest-Rate Calibration

### 4.1 Population Stability Assessment

Feature distributions were compared between the Q1–Q2 training and Q3 validation populations using Population Stability Index (PSI).

| Feature | PSI |
|---|---:|
| Credit Score | 0.0060 |
| Original LTV | 0.0655 |
| Original CLTV | 0.0238 |
| Original DTI | 0.0077 |
| Interest Rate | **1.2899** |
| Loan Amount | 0.0164 |

Interest rate exhibited the largest distribution shift.

The median original interest rate increased from **6.25% in training to 6.75% in validation**.

PSI identifies differences between distributions; it does not independently establish model failure or the causes of those differences.

### 4.2 Interest-Rate Segment Calibration

The original six-feature Logistic Regression model was evaluated across Q3 validation interest-rate segments.

| Interest Rate Segment | Observed Rate | Predicted Rate | Error (pp) |
|---|---:|---:|---:|
| ≤ 5.875% | 3.03% | 1.86% | -1.17 |
| 5.875–6.25% | 4.22% | 3.50% | -0.72 |
| 6.25–6.50% | 5.53% | 5.14% | -0.39 |
| 6.50–6.75% | 6.69% | 7.21% | +0.53 |
| Greater than 6.75% | 13.34% | 13.28% | -0.06 |

Error is calculated as the predicted rate minus the observed rate.

The lowest-rate segment exhibited the largest absolute calibration discrepancy, while the highest-rate segment showed a relatively small difference.

The distribution shift did not produce uniformly poor calibration across interest-rate segments.

### 4.3 Validation Finding MV-003

**Title:** Interest-rate distribution shift and segment-level calibration differences\
**Status:** Open

The interest-rate distribution changed substantially between training and validation cohorts.

**Recommendation:** Investigate cohort differences, assess possible confounding factors, and evaluate performance across broader economic environments.

## 5. Multicollinearity and Feature Robustness

### 5.1 Correlation and VIF Analysis

The original Logistic Regression model included both LTV and CLTV.

The Pearson correlation between these variables was **0.9166**.

Variance Inflation Factor (VIF) results were:

| Feature | VIF |
|---|---:|
| Original LTV | 6.44 |
| Original CLTV | 6.32 |
| Interest Rate | 1.16 |
| Loan Amount | 1.12 |
| Credit Score | 1.10 |
| Original DTI | 1.06 |

The elevated LTV and CLTV values indicate meaningful overlapping linear information, which can complicate individual coefficient interpretation.

### 5.2 Reduced-Feature Logistic Regression

A five-feature Logistic Regression model excluding CLTV was trained and evaluated on the original Q3 validation population.

| Metric | Six Features | Five Features |
|---|---:|---:|
| ROC-AUC | 0.7810 | 0.7813 |
| Average Precision | 0.2488 | 0.2491 |
| Brier Score | 0.0696 | 0.0695 |
| Average Predicted Event Rate | 8.2518% | 8.3176% |
| Observed Event Rate | 8.35% | 8.35% |
| Standardized LTV Coefficient | 0.1371 | 0.3615 |

Removing CLTV substantially changed the LTV coefficient but produced negligible changes in discrimination and probability accuracy.

The five-feature specification was retained as an interpretable benchmark for final Q4 testing.

The numerical improvements are too small to establish statistical superiority, and removing CLTV may discard useful information concerning additional mortgage liens.

### 5.3 Validation Finding MV-004

**Title:** LTV/CLTV multicollinearity and coefficient interpretability\
**Status:** Open

**Recommendation:** Document the final feature-selection rationale, investigate coefficient stability, and assess whether removal of CLTV materially affects segment-level performance.

## 6. Final Held-Out Q4 Evaluation

### 6.1 Evaluation Design

The final evaluation used mortgage originations from 2007 Q4.

| Measure | Value |
|---|---:|
| Test Mortgages | 211,425 |
| Observed Serious-Delinquency Events | 20,176 |
| Observed Event Rate | 9.54% |

The evaluation compared two model specifications selected using earlier development and Q3 validation evidence:

- **Five-feature Logistic Regression:** Excludes CLTV.
- **XGBoost:** Uses six origination-time features.

The model specifications were frozen before final evaluation.

No feature changes, parameter tuning, or calibration adjustments were made using Q4 results.

See [Final Test Protocol](final_test_protocol.md).

### 6.2 Final Model Performance

| Metric | Logistic Regression | XGBoost |
|---|---:|---:|
| ROC-AUC | 0.7906 | **0.7956** |
| Average Precision | 0.2910 | **0.3073** |
| Brier Score | 0.0783 | **0.0774** |
| Average Predicted Event Rate | 6.39% | 6.39% |
| Observed Event Rate | 9.54% | 9.54% |

XGBoost demonstrated stronger discrimination and a slightly lower Brier Score.

However, both models underestimated the portfolio-level observed event rate by approximately **3.15 percentage points**.

The gap represents a material calibration concern for applications requiring accurate absolute probabilities.

### 6.3 Logistic Regression — Q4 Decile Calibration

| Decile | Observed Rate | Predicted Rate | Error (pp) |
|---|---:|---:|---:|
| 1 | 0.47% | 0.43% | -0.04 |
| 2 | 1.24% | 0.96% | -0.29 |
| 3 | 2.20% | 1.52% | -0.68 |
| 4 | 3.41% | 2.19% | -1.21 |
| 5 | 5.14% | 3.05% | -2.09 |
| 6 | 7.57% | 4.18% | -3.39 |
| 7 | 10.02% | 5.73% | -4.29 |
| 8 | 13.56% | 8.05% | -5.51 |
| 9 | 19.18% | 12.11% | -7.07 |
| 10 | 32.63% | 25.68% | -6.95 |

### 6.4 XGBoost — Q4 Decile Calibration

| Decile | Observed Rate | Predicted Rate | Error (pp) |
|---|---:|---:|---:|
| 1 | 0.46% | 0.24% | -0.22 |
| 2 | 1.25% | 0.63% | -0.63 |
| 3 | 2.25% | 1.18% | -1.07 |
| 4 | 3.36% | 1.95% | -1.41 |
| 5 | 4.90% | 2.96% | -1.94 |
| 6 | 7.33% | 4.26% | -3.08 |
| 7 | 9.70% | 5.98% | -3.71 |
| 8 | 13.19% | 8.53% | -4.66 |
| 9 | 19.22% | 12.86% | -6.36 |
| 10 | 33.76% | 25.31% | -8.45 |

Risk deciles were constructed independently for each model. Corresponding deciles do not necessarily contain identical mortgages.

### 6.5 Calibration Assessment

Both models underestimated observed serious-delinquency rates in all ten Q4 risk deciles.

The calibration deficiency generally became larger in higher-risk groups.

In the highest-risk decile:

| Measure | Logistic Regression | XGBoost |
|---|---:|---:|
| Observed Event Rate | 32.63% | 33.76% |
| Predicted Event Rate | 25.68% | 25.31% |
| Underprediction | 6.95 pp | 8.45 pp |

XGBoost maintained stronger overall discrimination, but its highest-risk decile exhibited a larger absolute calibration error than Logistic Regression.

These findings distinguish risk-ranking ability from the reliability of absolute predicted probabilities.

### 6.6 Validation Finding MV-005

**Title:** Systematic Q4 probability underprediction\
**Status:** Open\
**Priority:** High

Both models materially underestimated observed Q4 serious-delinquency rates across all risk deciles.

Possible contributors include differences between origination cohorts, model specification, target-definition assumptions, and population selection.

The analysis does not establish which factors caused the calibration deficiency.

**Recommendation:** Investigate calibration and target-design weaknesses using a revised development framework and new independent evaluation data.

The reserved Q4 results should remain historical held-out evaluation evidence and must not be used to optimize the evaluated specifications.

## 7. Validation Findings Register

| ID | Finding | Priority | Status |
|---|---|---|---|
| MV-001 | Sensitivity to early-payoff treatment | High | Open |
| MV-002 | Potential modeling-population selection bias | High | Open |
| MV-003 | Interest-rate distribution shift and segment-level calibration differences | Medium | Open |
| MV-004 | LTV/CLTV multicollinearity and coefficient interpretability | Medium | Open |
| MV-005 | Systematic Q4 probability underprediction | High | Open |

Priorities reflect the proposed remediation plan documented in [Model Governance](model_governance.md).

The findings remain open because identifying, measuring, and documenting a risk does not establish that it has been resolved.

## 8. Final Model Validation Assessment

### 8.1 Summary of Evidence

The project completed quantitative research validation covering:

- Mortgage data integrity.
- Population eligibility and representativeness.
- Target-definition sensitivity to early payoff.
- Model discrimination and probability calibration.
- Input-feature distribution stability.
- Multicollinearity and reduced-feature modeling.
- Final held-out Q4 evaluation.

The technical assessment identified meaningful model weaknesses despite useful discriminatory performance.

### 8.2 Model Comparison and Interpretation

**XGBoost** demonstrated the strongest Q4 discrimination and a slightly lower Brier Score than the five-feature Logistic Regression benchmark.

**Five-feature Logistic Regression** offered a simpler, more interpretable alternative with relatively similar discrimination.

However, neither model demonstrated sufficiently reliable probability calibration for production probability estimation.

Model selection based solely on ROC-AUC or Brier Score would not adequately address the observed weaknesses.

### 8.3 Material Limitations

1. The 24-month outcome definition and early-payoff treatment remain provisional.
2. Excluding incomplete observation histories may create selection bias.
3. Interest-rate distributions changed significantly between training and validation cohorts.
4. Correlated LTV and CLTV variables complicate interpretation of the original Logistic Regression coefficients.
5. Both final candidate models systematically underestimated Q4 event rates.
6. All mortgages originated in 2007, limiting evidence of generalizability across origination vintages and economic environments.
7. The validation was self-conducted rather than organizationally independent.

### 8.4 Final Validation Recommendation

**Validation disposition: Not recommended for production probability estimation.**

XGBoost is retained as the stronger research candidate for ranking mortgages by observed serious-delinquency risk.

Five-feature Logistic Regression remains the interpretable benchmark.

Neither model is production-approved.

Future development should address target definition, population selection, probability calibration, temporal robustness, and independent validation before any production-use consideration.

### 8.5 Research Assessment Status

| Item | Final Status |
|---|---|
| Quantitative research validation | Completed |
| Final reserved Q4 evaluation | Completed |
| Validation findings | Five open |
| Remediation activities | Proposed, not completed |
| Organizationally independent validation | Not performed |
| Production recommendation | Not recommended |
| Formal production approval | Not granted |

This disposition represents an individual research assessment, not an approval or rejection by a financial institution's model risk management function.

The associated governance assessment and proposed remediation actions are documented in [Model Governance](model_governance.md).

---

*This validation report is intended for research, education, and portfolio demonstration. It does not certify regulatory compliance or production model suitability.*