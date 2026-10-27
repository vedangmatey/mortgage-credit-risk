
import duckdb
import pandas as pd

from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

# Step 126 — Multicollinearity sensitivity test

features = [
    "credit_score",
    "original_ltv",
    "original_cltv",
    "original_dti",
    "interest_rate",
    "loan_amount"
]

# Alternative model excludes CLTV
reduced_features = [
    f for f in features if f != "original_cltv"
]

con = duckdb.connect()
con.execute("SET memory_limit='3GB'")
con.execute("SET threads=2")

df = con.execute("""
    SELECT *
    FROM read_parquet(
        'data/processed/modeling_split.parquet'
    )
    WHERE data_split IN ('TRAIN', 'VALIDATION')
""").df()

con.close()

train = df[df["data_split"] == "TRAIN"]
validation = df[df["data_split"] == "VALIDATION"]

y_train = train["target"].astype(int)
y_validation = validation["target"].astype(int)

# Check correlation between LTV and CLTV
correlation = train[
    ["original_ltv", "original_cltv"]
].corr().iloc[0, 1]

print("========== MULTICOLLINEARITY CHECK ==========")
print(f"LTV / CLTV correlation: {correlation:.4f}")


def test_model(selected_features):

    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(
            max_iter=1000,
            solver="lbfgs"
        )
    )

    model.fit(train[selected_features], y_train)

    predictions = model.predict_proba(
        validation[selected_features]
    )[:, 1]

    coefficients = dict(zip(
        selected_features,
        model.named_steps["logisticregression"].coef_[0]
    ))

    return (
        roc_auc_score(y_validation, predictions),
        coefficients["original_ltv"]
    )


# Original model: LTV + CLTV
original_auc, original_ltv_coef = test_model(features)

# Reduced model: LTV only
reduced_auc, reduced_ltv_coef = test_model(reduced_features)

print("\n========== MODEL COMPARISON ==========")

print(f"{'Metric':<24}{'Original':>12}{'Without CLTV':>16}")

print(
    f"{'Validation ROC-AUC':<24}"
    f"{original_auc:>12.4f}"
    f"{reduced_auc:>16.4f}"
)

print(
    f"{'LTV Coefficient':<24}"
    f"{original_ltv_coef:>12.4f}"
    f"{reduced_ltv_coef:>16.4f}"
)

print("\nMulticollinearity diagnostic: COMPLETED")


# Step 127 — Variance Inflation Factor (VIF)

import numpy as np
from sklearn.linear_model import LinearRegression

# Use training data only
imputer = SimpleImputer(strategy="median")
X = imputer.fit_transform(train[features])

vif_results = []

for i, feature in enumerate(features):

    # Predict this feature using all other features
    y = X[:, i]
    X_others = np.delete(X, i, axis=1)

    regression = LinearRegression()
    regression.fit(X_others, y)

    r_squared = regression.score(X_others, y)

    vif = (
        1 / (1 - r_squared)
        if r_squared < 1
        else float("inf")
    )

    vif_results.append((feature, vif))

print("\n========== VARIANCE INFLATION FACTOR ==========")

for feature, vif in sorted(
    vif_results,
    key=lambda x: x[1],
    reverse=True
):
    print(f"{feature:<20}: {vif:.2f}")

print("\nVIF diagnostic: COMPLETED")


# Step 129 — Calibration comparison with and without CLTV

from sklearn.metrics import brier_score_loss, average_precision_score

def evaluate_calibration(selected_features):
    pipeline = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(
            max_iter=1000,
            solver="lbfgs"
        )
    )

    pipeline.fit(
        train[selected_features],
        y_train
    )

    predicted = pipeline.predict_proba(
        validation[selected_features]
    )[:, 1]

    return (
        roc_auc_score(y_validation, predicted),
        average_precision_score(y_validation, predicted),
        brier_score_loss(y_validation, predicted),
        predicted.mean() * 100
    )


full_results = evaluate_calibration(features)
reduced_results = evaluate_calibration(reduced_features)

print("\n========== FEATURE REMOVAL VALIDATION ==========")

metrics = [
    "ROC-AUC",
    "Average Precision",
    "Brier Score",
    "Average Predicted PD (%)"
]

print(f"{'Metric':<28}{'6 Features':>14}{'5 Features':>14}")

for name, full, reduced in zip(
    metrics, full_results, reduced_results
):
    print(f"{name:<28}{full:>14.4f}{reduced:>14.4f}")

print(f"\nActual Q3 Event Rate: {y_validation.mean():.2%}")
print("Feature removal comparison: COMPLETED")
