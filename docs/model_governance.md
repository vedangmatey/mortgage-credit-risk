# Model Governance Framework

[← Back to Project Overview](../README.md)

**Project:** Mortgage Credit Risk — Model Development, Validation & Governance\
**Status:** Final research governance assessment completed\
**Production Recommendation:** Not recommended\
**Outstanding Validation Findings:** Five open

## 1. Governance Objective

Establish and document a research-oriented model governance framework for mortgage credit risk models developed using Freddie Mac's 2007 single-family mortgage data.

The framework addresses:

- Model inventory and intended use.
- Model ownership and accountability.
- Model risk identification and assessment.
- Model development and validation controls.
- Model selection and testing decisions.
- Validation findings and remediation planning.
- Proposed monitoring and model-change controls.
- Final model governance disposition.

This framework demonstrates model risk management principles within an individual research project. It does not represent an operational governance program at a financial institution.

## 2. Model Overview and Intended Use

### 2.1 Model Inventory

| Attribute | Description |
|---|---|
| Model Category | Mortgage Credit Risk |
| Outcome | Observed serious delinquency (90+ days past due) |
| Observation Horizon | First 24 scheduled payment months |
| Data Source | Freddie Mac Single-Family Loan-Level Dataset |
| Origination Cohorts | 2007 Q1–Q4 |
| Primary Modeling Population | 888,123 mortgages |
| Original Baseline | Six-feature Logistic Regression |
| Final Interpretable Benchmark | Five-feature Logistic Regression |
| Leading Research Candidate | XGBoost |
| Additional Challenger | Random Forest |
| Technology | Python, DuckDB, pandas, scikit-learn, XGBoost |
| Project Ownership | Individual research project |
| Production Status | Not approved |

The outcome serves as a serious-delinquency proxy for default.

The target definition remains provisional because early-payoff treatment, observation-history requirements, and population eligibility have not been fully resolved.

### 2.2 Intended Use

The models are intended for:

- Research and methodology evaluation.
- Comparative statistical and machine learning analysis.
- Quantitative model validation demonstrations.
- Model risk management documentation.
- Educational and professional portfolio presentation.

### 2.3 Prohibited or Unsupported Uses

The models are not suitable for:

- Production lending or underwriting decisions.
- Borrower eligibility determination.
- Regulatory capital calculations.
- Production probability-of-default estimation.
- Operational credit risk reporting.

No production approval or regulatory compliance certification is implied.

## 3. Model Ownership and Governance Responsibilities

In a financial institution, effective model governance would ordinarily require clearly assigned responsibilities for development, validation, approval, implementation, and ongoing monitoring.

The following responsibilities are proposed for a hypothetical operational framework.

| Function | Proposed Responsibility |
|---|---|
| Model Development | Develop methodology, maintain code, document assumptions and limitations |
| Model Owner | Define intended use, oversee performance, coordinate remediation |
| Independent Model Validation | Challenge model assumptions, assess performance and implementation |
| Model Risk Management | Track material findings, assess model risk, advise on use restrictions |
| Approval Authority | Decide whether model use is permissible under organizational policy |
| Model Monitoring | Track performance, population changes, and potential deterioration |

**Research-project limitation:** These are illustrative organizational responsibilities.

The project was completed by an individual. It does not have an independent validation department, formal approval committee, or operational monitoring function.

Validation was conducted as a separate analytical workstream but was not organizationally independent.

## 4. Model Risk Assessment

The development and validation processes identified several sources of model risk.

| Risk Area | Identified Concern | Evidence or Control |
|---|---|---|
| Data Quality | Invalid, unmatched, or duplicated mortgage records | Automated data integrity and reconciliation checks |
| Target Definition | Early payoffs and incomplete observation histories | Alternative target sensitivity analysis |
| Population Selection | Eligible modeling sample may be unrepresentative | Exclusion and representativeness analysis |
| Model Specification | Overfitting or inappropriate assumptions | Challenger comparison and validation metrics |
| Calibration | Predicted probabilities may differ materially from observed rates | Portfolio-level and decile-level calibration |
| Feature Stability | Input distributions may shift between cohorts | Population Stability Index analysis |
| Multicollinearity | Correlated predictors affect coefficient interpretation | Correlation, VIF, and feature-removal analysis |
| Temporal Generalizability | Evidence is limited to 2007 origination cohorts | Explicit limitation in the validation assessment |
| Implementation | Incorrect preprocessing or inconsistent transformations | Reproducible scripts and training-only preprocessing |

Completion of a diagnostic does not mean the underlying risk has been eliminated.

Material unresolved risks are documented in the validation findings register.

## 5. Model Development and Validation Controls

### 5.1 Development Controls

The research workflow applied the following controls:

- Consistent source-data ingestion and schema handling.
- Automated data-integrity checks.
- Documented target and population eligibility assumptions.
- Mortgage origination-time predictor selection.
- Training-only fitting of preprocessing transformations.
- Chronological separation of training, validation, and test cohorts.
- Comparison of interpretable and nonlinear modeling approaches.
- Version-controlled Python scripts and documentation.

### 5.2 Validation Controls

Model validation included:

- Population representativeness assessment.
- Early-payoff sensitivity testing.
- Model discrimination and probability calibration.
- Feature distribution stability.
- Multicollinearity and feature-reduction analysis.
- Comparison of challenger models.
- Frozen-model evaluation on a reserved test population.
- Formal documentation of unresolved findings.

### 5.3 Independence Limitation

The validation workstream was separate from the development documentation, but both were conducted within the same individual research project.

Consequently, the assessment does not satisfy the organizational independence expected of a formal independent model validation function.

## 6. Model Selection and Final Testing

### 6.1 Pre-Test Selection Framework

Before evaluating the reserved Q4 cohort, model selection criteria were documented across six areas.

| Criterion | Evaluation Consideration |
|---|---|
| Discrimination | ROC-AUC and Average Precision |
| Calibration | Brier Score and predicted versus observed event rates |
| Stability | Cohort and risk-segment performance |
| Interpretability | Transparency of model outputs and risk factors |
| Robustness | Sensitivity to assumptions and feature selection |
| Complexity | Whether incremental performance justifies complexity |

No single performance metric was designated as sufficient for model approval.

### 6.2 Frozen Candidate Specifications

Two models were selected for final held-out evaluation.

**Candidate A — XGBoost**

Selected as the leading research challenger based on Q3 validation performance.

The final specification used six origination-time predictors, training-fitted median imputation, and boosting rounds selected using Q3 validation evidence.

**Candidate B — Five-Feature Logistic Regression**

Selected as the interpretable benchmark after feature-reduction testing showed similar validation performance without CLTV.

The original six-feature baseline and Random Forest challenger remained available as development comparisons.

### 6.3 Final Evaluation Protocol

The evaluation protocol established that:

1. Candidate specifications would be fixed before Q4 testing.
2. Both candidates would be evaluated on the same eligible Q4 population.
3. Discrimination and calibration metrics would be reported.
4. Material weaknesses would be documented.
5. Q4 results would not be used to retune model specifications.

The methodology and results are recorded in [Final Test Protocol](final_test_protocol.md).

## 7. Final Held-Out Evaluation

### 7.1 Test Population

| Measure | Value |
|---|---:|
| Origination Cohort | 2007 Q4 |
| Eligible Mortgages | 211,425 |
| Observed Serious-Delinquency Events | 20,176 |
| Observed Event Rate | 9.54% |

### 7.2 Model Performance

| Metric | Five-Feature Logistic Regression | XGBoost |
|---|---:|---:|
| ROC-AUC | 0.7906 | **0.7956** |
| Average Precision | 0.2910 | **0.3073** |
| Brier Score | 0.0783 | **0.0774** |
| Average Predicted Event Rate | 6.39% | 6.39% |
| Observed Event Rate | 9.54% | 9.54% |

XGBoost achieved stronger discrimination and a slightly lower Brier Score.

However, both models underestimated the observed event rate by approximately **3.15 percentage points**.

Underprediction occurred across all ten risk deciles for both models, including material errors in higher-risk groups.

### 7.3 Governance Interpretation

The evaluation supports the conclusion that XGBoost is the stronger research candidate for ranking mortgages by observed serious-delinquency risk.

It does not establish that XGBoost or Logistic Regression produces sufficiently reliable absolute probabilities for production credit risk estimation.

Good discrimination does not eliminate the need for acceptable calibration, defensible target assumptions, population representativeness, and appropriate model governance.

No tuning or calibration adjustments were made using the reserved Q4 results.


## 8. Validation Findings and Issue Tracking

Five model validation findings remain open.

### 8.1 Findings Register

| ID | Finding | Priority | Proposed Responsible Function | Target Date | Status |
|---|---|---|---|---|---|
| MV-001 | Early-payoff target sensitivity | High | Model Development | TBD | Open |
| MV-002 | Modeling-population selection bias | High | Model Development / Data Management | TBD | Open |
| MV-003 | Interest-rate distribution shift | Medium | Model Development / Model Monitoring | TBD | Open |
| MV-004 | LTV/CLTV multicollinearity | Medium | Model Development | TBD | Open |
| MV-005 | Systematic Q4 probability underprediction | High | Model Development / Model Owner | TBD | Open |

### 8.2 Remediation and Closure Evidence

The following evidence would be required to support
closure consideration for each finding.

| ID | Proposed Remediation | Required Closure Evidence |
|---|---|---|
| MV-001 | Finalize early-payoff treatment and target methodology | Documented target definition, competing-risk assessment, and sensitivity results |
| MV-002 | Investigate exclusions and population representativeness | Population analysis, eligibility rationale, and quantified impact assessment |
| MV-003 | Assess interest-rate shifts and cohort stability | Distribution diagnostics, segment-performance analysis, and robustness results |
| MV-004 | Review correlated features and coefficient stability | Feature-selection rationale, coefficient sensitivity results, and segment calibration |
| MV-005 | Investigate systematic underprediction and revise calibration methodology | Documented root-cause assessment and satisfactory independent calibration evidence |

### 8.3 Issue Management Principles

- Findings remain open until supported by appropriate
  remediation and review evidence.
- Proposed responsible functions represent hypothetical
  organizational roles, not actual assigned owners.
- Target dates remain TBD because remediation work has
  not been scheduled.
- Closure should require documented evidence that the
  underlying issue has been adequately addressed.
- High-priority findings should receive greater attention
  in any future remediation plan.
- Material model-use limitations should remain documented
  until the relevant concerns are satisfactorily addressed.

### 8.4 Current Findings Status

**Total Findings:** 5

**High Priority:** 3

**Medium Priority:** 2

**Open:** 5

**Closed:** 0

**Remediation Completed:** None

Priorities are proposed research remediation priorities,
not institutionally assigned risk ratings.

No formal issue ownership, deadline, approval, or closure
decision has been established in this individual project.

Detailed quantitative evidence is available in
[Model Validation](model_validation.md).

Proposed corrective actions are summarized in
Section 9 — Remediation Action Plan.


## 9. Remediation Action Plan

The following actions are recommended before future consideration of production probability estimation.

| Finding | Proposed Remediation | Priority |
|---|---|---|
| MV-001 | Review early payoff as a competing event and finalize the outcome definition | High |
| MV-002 | Assess excluded mortgage populations and establish defensible eligibility criteria | High |
| MV-003 | Investigate interest-rate shifts and test model stability across broader origination cohorts | Medium |
| MV-004 | Assess coefficient stability and document the final LTV/CLTV feature decision | Medium |
| MV-005 | Investigate systematic underprediction and develop a calibration improvement strategy using new development data | High |

### 9.1 Remediation Principles

Future remediation should:

- Address the underlying modeling issue rather than merely improve a reported metric.
- Preserve evidence of the original validation findings.
- Document methodology and specification changes.
- Distinguish development data from independent evaluation data.
- Reassess performance using new, appropriate evaluation data.
- Obtain independent review before any organizational production-use decision.

The reserved Q4 cohort should remain historical final-test evidence for the frozen models rather than become an optimization dataset.

### 9.2 Remediation Status

**Remediation actions are proposed but not completed.**

The findings register therefore remains open.

## 10. Proposed Model Monitoring Framework

The following framework describes how a future production model could be monitored if it were remediated, independently validated, and approved.

| Monitoring Area | Proposed Measure | Purpose |
|---|---|---|
| Data Quality | Missingness, invalid values, duplicate identifiers | Detect input-data defects |
| Population Stability | PSI and feature-distribution comparisons | Detect shifts in the modeled population |
| Discrimination | ROC-AUC and Average Precision | Monitor risk-ranking ability |
| Calibration | Predicted versus observed event rates | Assess probability reliability |
| Segment Performance | Performance across borrower-risk and loan-characteristic groups | Identify concentrated model weaknesses |
| Model Changes | Version and specification change logs | Maintain traceability |
| Findings Management | Finding status, remediation evidence, and review outcomes | Track unresolved model risk |

### 10.1 Monitoring Thresholds and Escalation

Before operational deployment, an institution would need to define:

- Monitoring frequency.
- Metric-specific thresholds.
- Materiality standards.
- Escalation responsibilities.
- Model-use restrictions.
- Retraining or redevelopment triggers.
- Documentation and approval requirements for model changes.

These controls have not been implemented as operational monitoring processes in this research project.

No specific thresholds are represented as approved or institutionally adopted.

## 11. Final Governance Disposition

### 11.1 Research Assessment

The development and validation workstreams have completed their documented research assessment.

The final evaluation demonstrated useful discriminatory performance but identified material calibration deficiencies.

Five validation findings remain unresolved, including high-priority concerns involving target definition, population selection, and probability calibration.

### 11.2 Final Recommendation

**Research assessment:** Completed with material limitations.

**Production recommendation:** Not recommended for production probability estimation.

**Formal production approval:** Not granted.

**Outstanding findings:** Five open.

XGBoost remains the leading research candidate for risk ranking.

The five-feature Logistic Regression remains the interpretable benchmark.

Neither model should be represented as suitable for operational lending decisions, regulatory calculations, or production probability-of-default estimation.

### 11.3 Conditions for Future Reconsideration

Any future reconsideration would require:

1. A defensible target definition and early-payoff methodology.
2. Further assessment of population-selection and incomplete-history risks.
3. Development and evaluation across broader origination vintages and economic environments.
4. Evidence of acceptable probability calibration and discrimination.
5. Documented feature-selection and model stability assessments.
6. Defined monitoring, escalation, and model-change procedures.
7. Organizationally independent validation and appropriate approval.

These requirements describe a prospective governance process, not activities already completed by this project.

## 12. Governance Conclusion

The project demonstrates an end-to-end research workflow connecting:

**Model Development → Model Validation → Validation Findings → Governance Assessment → Remediation Planning**

Its central lesson is that **stronger discriminatory performance does not necessarily establish reliable probability estimation or justify model approval**.

A credible model risk management assessment must consider the complete evidence, document unresolved risks, and recommend appropriate restrictions when material limitations remain.

**Final governance status:** Research assessment completed; five validation findings open; production use not recommended.

---

*This framework is intended for research, education, and professional portfolio demonstration. It does not constitute a banking institution's formal governance approval, independent validation, or regulatory compliance certification.*