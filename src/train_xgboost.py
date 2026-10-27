
import duckdb

from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss
)

from xgboost import XGBClassifier


# ----------------------------------------
# 1. Load training and validation data
# ----------------------------------------

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


features = [
    "credit_score",
    "original_ltv",
    "original_cltv",
    "original_dti",
    "interest_rate",
    "loan_amount"
]

train = df[df["data_split"] == "TRAIN"]
validation = df[df["data_split"] == "VALIDATION"]


# ----------------------------------------
# 2. Prepare model inputs
# ----------------------------------------

imputer = SimpleImputer(strategy="median")

X_train = imputer.fit_transform(train[features])
X_validation = imputer.transform(validation[features])

y_train = train["target"].astype(int)
y_validation = validation["target"].astype(int)


# ----------------------------------------
# 3. Configure XGBoost
# ----------------------------------------

model = XGBClassifier(
    n_estimators=400,
    max_depth=4,
    learning_rate=0.05,
    min_child_weight=20,
    subsample=0.8,
    colsample_bytree=0.9,
    reg_lambda=5,
    objective="binary:logistic",
    eval_metric="logloss",
    tree_method="hist",
    early_stopping_rounds=30,
    n_jobs=2,
    random_state=42
)


# ----------------------------------------
# 4. Train the model
# ----------------------------------------

print("Training XGBoost...", flush=True)

model.fit(
    X_train,
    y_train,
    eval_set=[(X_validation, y_validation)],
    verbose=False
)

print("Model training: COMPLETED")


# ----------------------------------------
# 5. Evaluate validation performance
# ----------------------------------------

predictions = model.predict_proba(
    X_validation
)[:, 1]

print("\n========== XGBOOST RESULTS ==========")

print(f"Training mortgages   : {len(train):,}")
print(f"Validation mortgages : {len(validation):,}")

print(
    f"ROC-AUC              : "
    f"{roc_auc_score(y_validation, predictions):.4f}"
)

print(
    f"Average Precision    : "
    f"{average_precision_score(y_validation, predictions):.4f}"
)

print(
    f"Brier Score          : "
    f"{brier_score_loss(y_validation, predictions):.4f}"
)

print(
    f"Actual Event Rate    : "
    f"{y_validation.mean():.2%}"
)

print(
    f"Average Predicted PD : "
    f"{predictions.mean():.2%}"
)

print(f"Best Boosting Round  : {model.best_iteration + 1}")

print("\nXGBoost validation: COMPLETED")


# Step 101 — XGBoost calibration analysis

import pandas as pd

calibration = pd.DataFrame({
    "actual": y_validation.to_numpy(),
    "predicted": predictions
})

# Divide mortgages into 10 groups by predicted risk
calibration["risk_decile"] = pd.qcut(
    calibration["predicted"],
    q=10,
    labels=False,
    duplicates="raise"
) + 1

# Calculate actual and predicted risk in each group
summary = (
    calibration.groupby("risk_decile")
    .agg(
        mortgages=("actual", "size"),
        actual_event_rate=("actual", "mean"),
        average_predicted_pd=("predicted", "mean")
    )
    .reset_index()
)

# Convert decimals to percentages
summary["actual_event_rate"] *= 100
summary["average_predicted_pd"] *= 100

# Difference in percentage points
summary["difference_pp"] = (
    summary["average_predicted_pd"]
    - summary["actual_event_rate"]
)

print("\n========== XGBOOST CALIBRATION ==========")

print(
    summary.to_string(
        index=False,
        float_format=lambda x: f"{x:.2f}"
    )
)

assert summary["mortgages"].sum() == len(validation)

print("\nCalibration reconciliation: PASSED")


# Step 102 — Check training vs. validation performance

train_predictions = model.predict_proba(X_train)[:, 1]

train_auc = roc_auc_score(y_train, train_predictions)
validation_auc = roc_auc_score(y_validation, predictions)

print("\n========== OVERFITTING CHECK ==========")

print(f"Training ROC-AUC   : {train_auc:.4f}")
print(f"Validation ROC-AUC : {validation_auc:.4f}")
print(f"AUC Difference     : {train_auc - validation_auc:.4f}")

print("\nOverfitting diagnostic: COMPLETED")
