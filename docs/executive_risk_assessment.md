# Executive Risk Assessment

**Mortgage Credit Risk — Model Development, Validation & Governance**

[← Back to Project Overview](../README.md)

**Assessment Type:** Research Model Risk Assessment
**Assessment Status:** Completed with Material Limitations
**Outstanding Findings:** 5 Open
**Production Recommendation:** Not Recommended

---

## 1. Executive Summary

An end-to-end research assessment was conducted on mortgage credit risk models developed using Freddie Mac's 2007 single-family loan-level dataset.

The assessment covered data quality, model performance, population stability, methodology assumptions, probability calibration, and governance considerations.

**Overall conclusion:** Although the models demonstrated useful risk-ranking capability, material weaknesses were identified in probability calibration, target definition, and population selection.

The research assessment therefore recommends **against production probability estimation** using the evaluated models.

This is an individual research assessment, not a decision issued by an independent bank model validation or approval function.

## 2. Key Risk Indicators

| Indicator | Result |
|---|---|
| Original Mortgage Population | 1,238,192 |
| Final Test Population | 211,425 |
| Leading Research Candidate | XGBoost |
| XGBoost Test ROC-AUC | 0.7956 |
| Observed Q4 Event Rate | 9.54% |
| Average Predicted Event Rate | 6.39% |
| Portfolio-Level Underprediction | Approximately 3.15 percentage points |
| Outstanding Validation Findings | 5 |

**Principal risk:** Both tested models materially underestimated observed serious-delinquency rates across all ten Q4 risk deciles.

This limits their reliability for applications requiring accurate absolute event probabilities.

## 3. Material Validation Findings

| ID | Risk Identified | Priority | Status |
|---|---|---|---|
| MV-001 | Model estimates are sensitive to early-payoff treatment | High | Open |
| MV-002 | Excluded mortgages may introduce population-selection bias | High | Open |
| MV-003 | Material interest-rate distribution shift between cohorts | Medium | Open |
| MV-004 | LTV/CLTV correlation affects coefficient interpretability | Medium | Open |
| MV-005 | Systematic underprediction in final Q4 evaluation | High | Open |

Priorities represent proposed research remediation priorities, not institutionally assigned risk ratings.

## 4. Risk Impact Assessment

**Probability estimation:** Systematic underprediction creates uncertainty about the reliability of model-generated absolute risk estimates.

**Model methodology:** Early-payoff treatment and incomplete observation histories may affect the modeled population and the interpretation of predicted probabilities.

**Model stability:** Input distribution shifts and the reliance on 2007 originations limit evidence of robustness across economic environments.

**Governance:** The outstanding findings would require further assessment and remediation before consideration of production probability estimation.

No actual production exposure, financial loss, regulatory breach, or operational reporting incident is claimed.

## 5. Recommended Actions

| Priority | Recommended Action |
|---|---|
| High | Establish a defensible outcome definition and early-payoff methodology |
| High | Investigate population-selection and incomplete-history risks |
| High | Address probability calibration using a revised development approach and new evaluation data |
| Medium | Assess stability across broader origination cohorts |
| Medium | Document feature-selection decisions and coefficient robustness |

Remediation actions remain proposed and have not been completed.

The reserved Q4 test results should remain historical held-out evaluation evidence and must not be used to optimize the evaluated models.

## 6. Governance Disposition

**Research assessment:** Completed with material limitations.

**Model-use recommendation:** Not recommended for production probability estimation.

**Open findings:** Five, including three with high proposed remediation priority.

**Required before reconsideration:** Defensible target methodology, further population assessment, satisfactory calibration, broader temporal validation, appropriate monitoring controls, and organizationally independent review and approval.

### Management Takeaway

**Strong discriminatory performance does not establish reliable probability estimation.**

The assessment demonstrates the importance of documented controls, evidence-based issue identification, formal findings tracking, and clear governance recommendations when model limitations are identified.

---

*Research and portfolio demonstration only. This report does not represent an actual bank committee decision, regulatory examination finding, or production model approval.*