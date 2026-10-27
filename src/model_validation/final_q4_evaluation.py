
from pathlib import Path
import duckdb

from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss
)

from xgboost import XGBClassifier


# Step 135 — Frozen Q4 model evaluation

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "processed" / "modeling_split.parquet"

FEATURES = [
    "credit_score",
    "original_ltv",
    "original_cltv",
    "original_dti",
    "interest_rate",
    "loan_amount"
]

LOGISTIC_FEATURES = [
    feature for feature in FEATURES
    if feature != "original_cltv"
]


# 1. Load only training and final test populations
con = duckdb.connect()
con.execute("SET memory_limit='3GB'")
con.execute("SET threads=2")

try:
    df = con.execute("""
        SELECT *
        FROM read_parquet(?)
        WHERE data_split IN ('TRAIN', 'TEST')
    """, [str(DATA)]).df()
finally:
    con.close()

train = df[df["data_split"] == "TRAIN"]
test = df[df["data_split"] == "TEST"]

y_train = train["target"].astype(int)
y_test = test["target"].astype(int)

assert len(train) == 488_486
assert len(test) == 211_425
assert int(y_test.sum()) == 20_176

assert not set(train["loan_id"]).intersection(
    set(test["loan_id"])
)

print("========== FINAL TEST POPULATION ==========")
print(f"Training mortgages: {len(train):,}")
print(f"Q4 test mortgages : {len(test):,}")
print(f"Q4 events         : {y_test.sum():,}")
print(f"Q4 event rate     : {y_test.mean():.2%}")


# 2. Five-feature Logistic Regression
logistic = make_pipeline(
    SimpleImputer(strategy="median"),
    StandardScaler(),
    LogisticRegression(
        max_iter=1000,
        solver="lbfgs"
    )
)

print("\nTraining frozen Logistic Regression...", flush=True)

logistic.fit(
    train[LOGISTIC_FEATURES],
    y_train
)

logistic_pd = logistic.predict_proba(
    test[LOGISTIC_FEATURES]
)[:, 1]


# 3. Six-feature XGBoost
# Boosting rounds were selected on Q3, not Q4.
imputer = SimpleImputer(strategy="median")

X_train = imputer.fit_transform(train[FEATURES])
X_test = imputer.transform(test[FEATURES])

xgboost = XGBClassifier(
    n_estimators=213,
    max_depth=4,
    learning_rate=0.05,
    min_child_weight=20,
    subsample=0.8,
    colsample_bytree=0.9,
    reg_lambda=5,
    objective="binary:logistic",
    eval_metric="logloss",
    tree_method="hist",
    n_jobs=2,
    random_state=42
)

print("Training frozen XGBoost...", flush=True)

xgboost.fit(X_train, y_train)

xgboost_pd = xgboost.predict_proba(X_test)[:, 1]


# 4. Calculate final evaluation metrics
def evaluate(predicted):
    return {
        "ROC-AUC": roc_auc_score(y_test, predicted),
        "Average Precision": average_precision_score(
            y_test, predicted
        ),
        "Brier Score": brier_score_loss(
            y_test, predicted
        ),
        "Average Predicted PD": predicted.mean()
    }


logistic_results = evaluate(logistic_pd)
xgboost_results = evaluate(xgboost_pd)


# 5. Display comparison
print("\n========== FINAL Q4 MODEL EVALUATION ==========")

print(
    f"{'Metric':<24}"
    f"{'Logistic':>14}"
    f"{'XGBoost':>14}"
)

for metric in logistic_results:
    print(
        f"{metric:<24}"
        f"{logistic_results[metric]:>14.4f}"
        f"{xgboost_results[metric]:>14.4f}"
    )

print(f"\nActual Q4 event rate: {y_test.mean():.4f}")

print("\nFinal Q4 model evaluation: COMPLETED")


# Step 137 — Q4 Risk Decile Calibration

import pandas as pd
import numpy as np


def decile_calibration(model_name, predicted):

    results = pd.DataFrame({
        "actual": y_test.to_numpy(),
        "predicted": predicted
    })

    # Rank predictions into 10 equally sized risk groups
    results["decile"] = pd.qcut(
        results["predicted"].rank(method="first"),
        q=10,
        labels=range(1, 11)
    )

    summary = (
        results.groupby("decile", observed=True)
        .agg(
            mortgages=("actual", "size"),
            actual_rate=("actual", "mean"),
            predicted_rate=("predicted", "mean")
        )
    )

    summary["error_pp"] = (
        summary["predicted_rate"]
        - summary["actual_rate"]
    ) * 100

    print(f"\n========== {model_name} Q4 DECILE CALIBRATION ==========")

    print(
        f"{'Decile':<9}"
        f"{'Mortgages':>12}"
        f"{'Actual %':>12}"
        f"{'Predicted %':>14}"
        f"{'Error (pp)':>13}"
    )

    for decile, row in summary.iterrows():
        print(
            f"{int(decile):<9}"
            f"{int(row['mortgages']):>12,}"
            f"{row['actual_rate'] * 100:>12.2f}"
            f"{row['predicted_rate'] * 100:>14.2f}"
            f"{row['error_pp']:>13.2f}"
        )


decile_calibration("LOGISTIC REGRESSION", logistic_pd)
decile_calibration("XGBOOST", xgboost_pd)

print("\nQ4 decile calibration analysis: COMPLETED")
