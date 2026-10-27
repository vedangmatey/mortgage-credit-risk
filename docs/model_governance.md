# Model Governance Framework

[← Back to Project Overview](../README.md)

**Project:** Mortgage Credit Risk — Model Development, Validation & Governance
**Status:** In Development — Not Approved for Production

## 1. Model Overview and Intended Use

The project develops statistical and machine learning models using Freddie Mac's 2007 single-family mortgage data to estimate the likelihood of serious delinquency (90+ days past due) within a 24-month horizon.

The models are intended for research, methodology evaluation, and demonstration of model risk management practices.

**Out-of-scope uses:** Actual lending decisions, borrower eligibility determination, regulatory capital calculations, and production credit risk reporting.

## 2. Model Inventory

| Attribute | Description |
|---|---|
| Model Category | Mortgage Credit Risk |
| Target | Observed 90+ day delinquency within 24 scheduled payment months |
| Modeling Population | Freddie Mac 2007 mortgage cohort |
| Baseline Model | Logistic Regression |
| Challenger Models | Random Forest, XGBoost |
| Development Environment | Python, DuckDB, scikit-learn, XGBoost |
| Model Owner | Individual research project |
| Model Status | Development and validation in progress |
| Production Approval | Not granted |

The outcome is a serious-delinquency proxy for default. The definition and treatment of early payoffs require further review before interpreting estimates as production-ready probabilities of default.

## 3. Model Risk Assessment

| Risk Area | Identified Concern | Current Treatment |
|---|---|---|
| Data Quality | Incorrect or unmatched loan records | Automated integrity checks |
| Target Definition | Early payoff and incomplete histories | Alternative target sensitivity analysis |
| Population Risk | Nonrepresentative modeling sample | Exclusion and representativeness analysis |
| Model Risk | Overfitting and inaccurate probabilities | Validation and calibration testing |
| Feature Risk | Distribution shifts and correlated inputs | PSI, segment analysis, VIF |
| Implementation Risk | Incorrect transformations or inconsistent preprocessing | Reproducible scripts and training-only preprocessing |

Risks remain subject to further assessment. Completion of a diagnostic does not imply the related risk has been resolved.

## 4. Model Validation Findings

| Finding | Description | Status |
|---|---|---|
| MV-001 | Sensitivity to early-payoff treatment | Open |
| MV-002 | Potential population selection bias | Open |
| MV-003 | Interest-rate distribution shift and calibration differences | Open |
| MV-004 | LTV/CLTV multicollinearity and interpretability | Open |

Detailed evidence and recommendations are maintained in [Model Validation](model_validation.md).

## 5. Model Selection and Approval Controls

The final candidate model will be selected using evidence covering:

- Discrimination: ROC-AUC and Average Precision
- Probability accuracy: Brier Score and calibration
- Stability across mortgage cohorts and risk segments
- Interpretability and model complexity
- Sensitivity to target and feature assumptions
- Implementation reproducibility and documented limitations

**Current decision:** No final model selected.

XGBoost is the leading challenger on preliminary validation metrics. Five-feature Logistic Regression is a promising interpretable alternative.

Model selection must be documented before the reserved Q4 test dataset is evaluated.


### Pre-Test Model Selection Framework

The following decision framework was established before
evaluating the reserved 2007 Q4 test cohort.

#### Selection Criteria

| Area | Evaluation Standard |
|---|---|
| Discrimination | Compare ROC-AUC and Average Precision |
| Calibration | Assess Brier Score and predicted vs. observed event rates |
| Stability | Review performance across mortgage cohorts and risk segments |
| Interpretability | Evaluate coefficient or feature-level explanations |
| Robustness | Assess sensitivity to target and feature assumptions |
| Complexity | Consider whether additional complexity is justified |

No single metric automatically determines model selection.

#### Provisional Candidate Models

**Primary candidate: XGBoost**

Selected for further evaluation because it achieved the
strongest preliminary validation discrimination and
Brier Score among the three developed algorithms.

**Interpretable benchmark: Five-feature Logistic Regression**

Retained because removing CLTV produced similar
discrimination and calibration with a simpler specification.

**Additional challenger: Random Forest**

Retained as comparative evidence but not prioritized
for final model selection.

#### Final Evaluation Protocol

1. Resolve or explicitly document material target-definition limitations.
2. Freeze candidate specifications and preprocessing procedures.
3. Evaluate the selected candidates on the reserved Q4 population.
4. Report discrimination, calibration, and segment-level performance.
5. Compare results against validation expectations.
6. Document any unresolved findings and limitations.
7. Issue a final research-model assessment.

The Q4 test dataset must not be used for parameter tuning,
feature selection, or repeated model optimization.

If final evaluation identifies material deficiencies,
the project will document them rather than claim approval.

**Current decision: Provisional candidates identified;
final research-model assessment pending.**


## 6. Model Monitoring Framework

A future monitoring framework will address:

| Monitoring Area | Proposed Measure |
|---|---|
| Data Integrity | Missing fields, invalid values, duplicate loan identifiers |
| Population Stability | Feature distributions and PSI |
| Discrimination | ROC-AUC and Average Precision |
| Calibration | Predicted versus observed event rates |
| Segment Performance | Performance by borrower-risk and interest-rate groups |
| Model Changes | Recorded changes to data, features, parameters, and code |

Monitoring thresholds, escalation procedures, and retraining triggers will be developed as proposals, not represented as operational controls currently in force.

## 7. Governance Decisions and Limitations

The following decisions remain unresolved:

1. Final 24-month outcome definition, including early-payoff treatment.
2. Acceptable modeling-population exclusions.
3. Whether to retain CLTV in the interpretable baseline.
4. Final model selection among the candidate approaches.
5. Acceptance criteria for final testing and material validation findings.

The project does not have an independent validation department, formal approval committee, or operational monitoring system. Governance documentation illustrates a proposed process rather than claiming these organizational controls exist.

## 8. Final Model Review Status

**Decision: Pending**

A final research-model assessment will require a documented target policy, completed validation analysis, a selected candidate specification, reserved Q4 evaluation, and explicit discussion of unresolved limitations.

No production approval or regulatory compliance certification is implied.


---

## 9. Final Governance Assessment

### 9.1 Final Model Evaluation

The final evaluation was conducted using the reserved
2007 Q4 mortgage cohort.

| Metric | Logistic Regression | XGBoost |
|---|---:|---:|
| ROC-AUC | 0.7906 | 0.7956 |
| Average Precision | 0.2910 | 0.3073 |
| Brier Score | 0.0783 | 0.0774 |
| Average Predicted Event Rate | 6.39% | 6.39% |
| Observed Event Rate | 9.54% | 9.54% |

XGBoost demonstrated stronger discrimination and
a slightly lower Brier Score.

However, both models materially underestimated
observed delinquency risk across all Q4 risk deciles.

### 9.2 Governance Disposition

**Research assessment: Completed with material limitations**

**Production recommendation: Not recommended**

**Formal production approval: Not granted**

The models demonstrate useful research-level
risk-ranking capability but have not demonstrated
sufficient probability calibration for production
credit risk estimation.

This disposition represents the conclusion of an
individual research project, not a decision by an
independent bank model validation or approval function.

### 9.3 Remediation Action Plan

| Finding | Proposed Remediation | Priority |
|---|---|---|
| MV-001 | Review competing-risk treatment of early mortgage payoffs and finalize the target definition | High |
| MV-002 | Investigate excluded loan populations and quantify selection bias | High |
| MV-003 | Analyze interest-rate distribution shifts and assess performance across cohorts | Medium |
| MV-004 | Evaluate coefficient stability and document the final LTV/CLTV feature decision | Medium |
| MV-005 | Investigate calibration drift and develop a calibration improvement strategy using new development data | High |

### 9.4 Conditions for Reconsideration

Before a future model could be considered for
production probability estimation, the following
activities would be required:

1. Establish a defensible outcome definition,
   including early-payoff treatment.
2. Resolve or formally assess population-selection risks.
3. Reassess model development with broader
   origination vintages and economic conditions.
4. Demonstrate acceptable discrimination and
   probability calibration on independent data.
5. Document feature selection and model stability.
6. Define monitoring thresholds, escalation procedures,
   and model-change controls.
7. Obtain independent validation and appropriate
   organizational approval.

The reserved Q4 test results will remain historical
evaluation evidence and will not be used to optimize
the existing models.

### 9.5 Governance Conclusion

The project demonstrates an end-to-end model risk
management workflow covering:

- Model development and challenger comparison
- Data quality and target-definition controls
- Quantitative validation and sensitivity analysis
- Identification and tracking of validation findings
- Model-selection and testing protocols
- Governance disposition and remediation planning

The most important conclusion is that satisfactory
discrimination does not necessarily imply reliable
probability estimates.

The research models are retained for educational
and methodological purposes only.

**Final governance status: Research assessment completed;
five findings remain open; production use not recommended.**
