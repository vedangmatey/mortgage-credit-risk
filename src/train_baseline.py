
import duckdb

# Connect to DuckDB
con = duckdb.connect()

# Our six model inputs
features = [
    "credit_score",
    "original_ltv",
    "original_cltv",
    "original_dti",
    "interest_rate",
    "loan_amount"
]

# Load our prepared mortgage dataset
df = con.execute("""
    SELECT *
    FROM read_parquet(
        'data/processed/modeling_split.parquet'
    )
""").df()

con.close()

# Separate training, validation and testing data
train = df[df["data_split"] == "TRAIN"].copy()
validation = df[df["data_split"] == "VALIDATION"].copy()
test = df[df["data_split"] == "TEST"].copy()

print("========== MODEL DATA ==========")
print(f"Training mortgages   : {len(train):,}")
print(f"Validation mortgages : {len(validation):,}")
print(f"Testing mortgages    : {len(test):,}")

print("\nMissing values in training data:")
print(train[features].isna().sum())


# Step 83 — Handle missing values

from sklearn.impute import SimpleImputer

imputer = SimpleImputer(strategy="median")

# Learn replacement values from training data only
imputer.fit(train[features])

# Display the learned replacement values
print("\n========== TRAINING MEDIANS ==========")

for feature, median in zip(features, imputer.statistics_):
    print(f"{feature:<20}: {median:.2f}")

# Apply the same trained imputer to each dataset
X_train = imputer.transform(train[features])
X_validation = imputer.transform(validation[features])
X_test = imputer.transform(test[features])

print("\nMissing-value imputation: PASSED")
print("Training shape:", X_train.shape)


# Step 85 — Standardize model features

from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()

# Learn scaling parameters from training data only
X_train_scaled = scaler.fit_transform(X_train)

# Apply the same scaling to validation and test
X_validation_scaled = scaler.transform(X_validation)
X_test_scaled = scaler.transform(X_test)

# Prepare the actual outcomes
y_train = train["target"].astype(int)
y_validation = validation["target"].astype(int)
y_test = test["target"].astype(int)

print("\n========== FEATURE SCALING ==========")

print("Training shape  :", X_train_scaled.shape)
print("Validation shape:", X_validation_scaled.shape)
print("Testing shape   :", X_test_scaled.shape)

print("\nTraining feature means after scaling:")
print(X_train_scaled.mean(axis=0).round(4))

print("\nTraining feature standard deviations:")
print(X_train_scaled.std(axis=0).round(4))

print("\nFeature scaling: PASSED")


# Step 86 — Train and evaluate baseline logistic regression

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss
)

# Create the logistic regression model
model = LogisticRegression(
    max_iter=1000,
    solver="lbfgs"
)

# Train using training data only
model.fit(X_train_scaled, y_train)

print("\n========== LOGISTIC REGRESSION ==========")
print("Model training: COMPLETED")

# Predict probabilities on validation data
validation_probabilities = model.predict_proba(
    X_validation_scaled
)[:, 1]

# Evaluate the model
roc_auc = roc_auc_score(
    y_validation,
    validation_probabilities
)

pr_auc = average_precision_score(
    y_validation,
    validation_probabilities
)

brier = brier_score_loss(
    y_validation,
    validation_probabilities
)

print("\n========== VALIDATION RESULTS ==========")
print(f"ROC-AUC              : {roc_auc:.4f}")
print(f"Average Precision    : {pr_auc:.4f}")
print(f"Brier Score          : {brier:.4f}")

print(
    f"Actual Event Rate    : {y_validation.mean():.2%}"
)

print(
    f"Average Predicted PD : "
    f"{validation_probabilities.mean():.2%}"
)

print("\nValidation evaluation: COMPLETED")


# Step 88 — Examine logistic regression coefficients

import pandas as pd

coefficients = pd.DataFrame({
    "Feature": features,
    "Coefficient": model.coef_[0]
})

coefficients["Odds_Ratio"] = (
    coefficients["Coefficient"].apply(
        lambda x: float(__import__("math").exp(x))
    )
)

coefficients = coefficients.sort_values(
    "Coefficient"
)

print("\n========== MODEL COEFFICIENTS ==========")

print(
    coefficients.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)

print("\nCoefficient analysis: COMPLETED")


# Step 89 — Validation calibration by risk decile

calibration = pd.DataFrame({
    "actual": y_validation.to_numpy(),
    "predicted": validation_probabilities
})

# Divide loans into ten groups by predicted risk
calibration["risk_decile"] = pd.qcut(
    calibration["predicted"],
    q=10,
    labels=False,
    duplicates="raise"
) + 1

# Compare predicted and actual event rates
calibration_summary = (
    calibration.groupby("risk_decile")
    .agg(
        mortgages=("actual", "size"),
        actual_event_rate=("actual", "mean"),
        average_predicted_pd=("predicted", "mean")
    )
    .reset_index()
)

# Express rates as percentages
calibration_summary["actual_event_rate"] *= 100
calibration_summary["average_predicted_pd"] *= 100

calibration_summary["difference_pp"] = (
    calibration_summary["average_predicted_pd"]
    - calibration_summary["actual_event_rate"]
)

print("\n========== VALIDATION CALIBRATION ==========")

print(
    calibration_summary.to_string(
        index=False,
        float_format=lambda x: f"{x:.2f}"
    )
)

assert calibration_summary["mortgages"].sum() == len(validation)

print("\nCalibration reconciliation: PASSED")


# Step 91 — Create model performance charts

from pathlib import Path
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve

# Folder for figures
ROOT = Path(__file__).resolve().parent.parent
FIGURES = ROOT / "reports" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

# ----------------------------------------
# Chart 1: ROC Curve
# ----------------------------------------

fpr, tpr, _ = roc_curve(
    y_validation,
    validation_probabilities
)

plt.figure(figsize=(7, 5))

plt.plot(
    fpr,
    tpr,
    label=f"Logistic Regression (AUC = {roc_auc:.4f})",
    linewidth=2
)

plt.plot(
    [0, 1], [0, 1],
    linestyle="--",
    color="gray",
    label="Random classifier"
)

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("Mortgage PD Model — Validation ROC Curve")
plt.legend(loc="lower right")
plt.grid(alpha=0.2)
plt.tight_layout()

plt.savefig(FIGURES / "logistic_roc.png", dpi=200)
plt.close()

# ----------------------------------------
# Chart 2: Calibration by Risk Decile
# ----------------------------------------

plt.figure(figsize=(7, 5))

plt.plot(
    calibration_summary["risk_decile"],
    calibration_summary["actual_event_rate"],
    marker="o",
    linewidth=2,
    label="Actual Event Rate"
)

plt.plot(
    calibration_summary["risk_decile"],
    calibration_summary["average_predicted_pd"],
    marker="s",
    linestyle="--",
    linewidth=2,
    label="Average Predicted PD"
)

plt.xlabel("Predicted Risk Decile")
plt.ylabel("Event Rate (%)")
plt.title("Mortgage PD Model — Validation Calibration")
plt.xticks(range(1, 11))
plt.legend()
plt.grid(alpha=0.2)
plt.tight_layout()

plt.savefig(
    FIGURES / "logistic_calibration.png",
    dpi=200
)
plt.close()

print("\n========== MODEL FIGURES ==========")
print("ROC curve       : logistic_roc.png")
print("Calibration plot: logistic_calibration.png")
print("Figures saved to:", FIGURES)
