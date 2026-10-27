
from pathlib import Path

import duckdb
import pandas as pd

from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
)

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed"

FEATURES = [
    "credit_score",
    "original_ltv",
    "original_cltv",
    "original_dti",
    "interest_rate",
    "loan_amount",
]

con = duckdb.connect()
con.execute("SET memory_limit='3GB'")
con.execute("SET threads=2")

try:
    # 1. Load the original TRAIN and VALIDATION cohorts
    original = con.execute("""
        SELECT *
        FROM read_parquet(?)
        WHERE data_split IN ('TRAIN', 'VALIDATION')
    """, [str(DATA / "modeling_split.parquet")]).df()

    train = original[original["data_split"] == "TRAIN"]
    validation = original[
        original["data_split"] == "VALIDATION"
    ]

    # 2. Load only additional eligible payoff mortgages
    #    from the TRAIN cohorts (2007 Q1 and Q2).
    payoffs = con.execute("""
        SELECT
            o.column19 AS loan_id,
            0 AS target,

            CASE
                WHEN TRY_CAST(o.column00 AS DOUBLE)
                    BETWEEN 300 AND 850
                THEN TRY_CAST(o.column00 AS DOUBLE)
            END AS credit_score,

            CASE
                WHEN TRY_CAST(o.column11 AS DOUBLE)
                    BETWEEN 1 AND 105
                THEN TRY_CAST(o.column11 AS DOUBLE)
            END AS original_ltv,

            CASE
                WHEN TRY_CAST(o.column08 AS DOUBLE)
                    BETWEEN 1 AND 200
                THEN TRY_CAST(o.column08 AS DOUBLE)
            END AS original_cltv,

            CASE
                WHEN TRY_CAST(o.column09 AS DOUBLE)
                    BETWEEN 1 AND 65
                THEN TRY_CAST(o.column09 AS DOUBLE)
            END AS original_dti,

            CASE
                WHEN TRY_CAST(o.column12 AS DOUBLE) > 0
                THEN TRY_CAST(o.column12 AS DOUBLE)
            END AS interest_rate,

            CASE
                WHEN TRY_CAST(o.column10 AS DOUBLE) > 0
                THEN TRY_CAST(o.column10 AS DOUBLE)
            END AS loan_amount

        FROM read_parquet(?) o

        INNER JOIN read_parquet(?) t
            ON o.column19 = t.loan_id

        WHERE t.sensitivity_payoff_flag = 1
          AND SUBSTR(o.column19, 1, 5)
              IN ('F07Q1', 'F07Q2')
    """, [
        str(DATA / "orig_2007Q*.parquet"),
        str(DATA / "target_payoff_sensitivity.parquet")
    ]).df()

finally:
    con.close()

# 3. Create sensitivity training population
sensitivity_train = pd.concat(
    [train, payoffs],
    ignore_index=True
)

assert len(payoffs) > 0
assert payoffs["target"].eq(0).all()
assert not sensitivity_train["loan_id"].duplicated().any()

print("========== POPULATION COMPARISON ==========")
print(f"Original training loans    : {len(train):,}")
print(f"Additional clean payoffs   : {len(payoffs):,}")
print(f"Sensitivity training loans : {len(sensitivity_train):,}")
print(f"Common validation loans    : {len(validation):,}")


# 4. Use exactly the same modeling procedure
def evaluate(training_data, validation_data):

    pipeline = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(
            max_iter=1000,
            solver="lbfgs"
        )
    )

    pipeline.fit(
        training_data[FEATURES],
        training_data["target"].astype(int)
    )

    actual = validation_data["target"].astype(int)

    predicted = pipeline.predict_proba(
        validation_data[FEATURES]
    )[:, 1]

    return {
        "roc_auc": roc_auc_score(actual, predicted),
        "average_precision": average_precision_score(
            actual, predicted
        ),
        "brier": brier_score_loss(actual, predicted),
        "average_pd": predicted.mean(),
    }


# 5. Compare both models on the SAME validation loans
baseline = evaluate(train, validation)

sensitivity = evaluate(
    sensitivity_train,
    validation
)

print("\n========== COMMON VALIDATION COMPARISON ==========")

print(
    f"{'Metric':<22}"
    f"{'Original':>12}"
    f"{'Sensitivity':>15}"
)

for key in baseline:
    print(
        f"{key:<22}"
        f"{baseline[key]:>12.4f}"
        f"{sensitivity[key]:>15.4f}"
    )

print(
    f"\nActual validation event rate: "
    f"{validation['target'].mean():.2%}"
)

print("\nSensitivity comparison: COMPLETED")

# Step 112 — Expanded Q3 validation population

with duckdb.connect() as audit_con:

    expanded_counts = audit_con.execute("""
        SELECT
            classification,
            COUNT(*) AS mortgages,
            COUNT(*) FILTER (
                WHERE target = 1
            ) AS events

        FROM read_parquet(?)

        WHERE SUBSTR(loan_id, 1, 5) = 'F07Q3'
          AND target IS NOT NULL

        GROUP BY classification
        ORDER BY mortgages DESC
    """, [
        str(DATA / "target_payoff_sensitivity.parquet")
    ]).fetchall()

print("\n========== EXPANDED Q3 VALIDATION ==========")

for classification, mortgages, events in expanded_counts:
    print(
        f"{classification:<25}: "
        f"{mortgages:>8,} mortgages | "
        f"{events:>6,} events"
    )

total_loans = sum(row[1] for row in expanded_counts)
total_events = sum(row[2] for row in expanded_counts)

print(f"\nTotal Q3 mortgages : {total_loans:,}")
print(f"Total Q3 events    : {total_events:,}")
print(f"Q3 event rate      : {total_events / total_loans:.2%}")

assert total_loans > 188_212
assert total_events == 15_718

print("\nExpanded population reconciliation: PASSED")


# Step 113 — Compare both models on expanded Q3

# Load the newly eligible Q3 payoff mortgages
with duckdb.connect() as audit_con:

    q3_payoffs = audit_con.execute("""
        SELECT
            o.column19 AS loan_id,
            0 AS target,

            CASE WHEN TRY_CAST(o.column00 AS DOUBLE)
                BETWEEN 300 AND 850
            THEN TRY_CAST(o.column00 AS DOUBLE)
            END AS credit_score,

            CASE WHEN TRY_CAST(o.column11 AS DOUBLE)
                BETWEEN 1 AND 105
            THEN TRY_CAST(o.column11 AS DOUBLE)
            END AS original_ltv,

            CASE WHEN TRY_CAST(o.column08 AS DOUBLE)
                BETWEEN 1 AND 200
            THEN TRY_CAST(o.column08 AS DOUBLE)
            END AS original_cltv,

            CASE WHEN TRY_CAST(o.column09 AS DOUBLE)
                BETWEEN 1 AND 65
            THEN TRY_CAST(o.column09 AS DOUBLE)
            END AS original_dti,

            CASE WHEN TRY_CAST(o.column12 AS DOUBLE) > 0
            THEN TRY_CAST(o.column12 AS DOUBLE)
            END AS interest_rate,

            CASE WHEN TRY_CAST(o.column10 AS DOUBLE) > 0
            THEN TRY_CAST(o.column10 AS DOUBLE)
            END AS loan_amount

        FROM read_parquet(?) o
        JOIN read_parquet(?) t
            ON o.column19 = t.loan_id

        WHERE t.classification = 'CLEAN_PAYOFF_NON_EVENT'
          AND SUBSTR(t.loan_id, 1, 5) = 'F07Q3'
    """, [
        str(DATA / "orig_2007Q3.parquet"),
        str(DATA / "target_payoff_sensitivity.parquet")
    ]).df()

# Add the payoffs to the original Q3 validation population
expanded_validation = pd.concat(
    [validation, q3_payoffs],
    ignore_index=True
)

# Verify the new population
assert len(q3_payoffs) == 79_556
assert len(expanded_validation) == 267_768
assert not expanded_validation["loan_id"].duplicated().any()
assert expanded_validation["target"].sum() == 15_718

print("\n========== EXPANDED VALIDATION ==========")
print(f"Original Q3 mortgages : {len(validation):,}")
print(f"Additional Q3 payoffs : {len(q3_payoffs):,}")
print(f"Expanded Q3 mortgages : {len(expanded_validation):,}")

# Use the same model configuration and evaluation function
original_expanded = evaluate(train, expanded_validation)

sensitivity_expanded = evaluate(
    sensitivity_train,
    expanded_validation
)

print("\n========== EXPANDED MODEL COMPARISON ==========")

print(
    f"{'Metric':<22}"
    f"{'Original':>12}"
    f"{'Sensitivity':>15}"
)

for key in original_expanded:
    print(
        f"{key:<22}"
        f"{original_expanded[key]:>12.4f}"
        f"{sensitivity_expanded[key]:>15.4f}"
    )

print(
    f"\nActual expanded event rate: "
    f"{expanded_validation['target'].mean():.2%}"
)

print("\nExpanded validation comparison: COMPLETED")


# Step 115 — Calibration comparison across risk deciles

def fit_model(training_data):
    pipeline = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(
            max_iter=1000,
            solver="lbfgs"
        )
    )

    pipeline.fit(
        training_data[FEATURES],
        training_data["target"].astype(int)
    )

    return pipeline


# Train both models using their respective populations
original_model = fit_model(train)
sensitivity_model = fit_model(sensitivity_train)

# Predict on the SAME expanded Q3 validation mortgages
original_pd = original_model.predict_proba(
    expanded_validation[FEATURES]
)[:, 1]

sensitivity_pd = sensitivity_model.predict_proba(
    expanded_validation[FEATURES]
)[:, 1]

# Build the calibration comparison
calibration = pd.DataFrame({
    "actual": expanded_validation["target"].to_numpy(),
    "original_pd": original_pd,
    "sensitivity_pd": sensitivity_pd
})

# Use common risk groups based on original model predictions
calibration["risk_decile"] = pd.qcut(
    calibration["original_pd"],
    q=10,
    labels=False,
    duplicates="raise"
) + 1

summary = (
    calibration.groupby("risk_decile")
    .agg(
        mortgages=("actual", "size"),
        actual_rate=("actual", "mean"),
        original_pd=("original_pd", "mean"),
        sensitivity_pd=("sensitivity_pd", "mean")
    )
    .reset_index()
)

# Convert to percentages
for column in ["actual_rate", "original_pd", "sensitivity_pd"]:
    summary[column] *= 100

# Prediction errors in percentage points
summary["original_error_pp"] = (
    summary["original_pd"] - summary["actual_rate"]
)

summary["sensitivity_error_pp"] = (
    summary["sensitivity_pd"] - summary["actual_rate"]
)

print("\n========== EXPANDED CALIBRATION BY DECILE ==========")

print(
    summary.to_string(
        index=False,
        float_format=lambda x: f"{x:.2f}"
    )
)

assert summary["mortgages"].sum() == 267_768

print("\nCalibration comparison: PASSED")
