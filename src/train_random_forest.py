
import duckdb

from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss
)

# 1. Load modeling data
con = duckdb.connect()

df = con.execute("""
    SELECT *
    FROM read_parquet(
        'data/processed/modeling_split.parquet'
    )
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

# 2. Handle missing values using training data
imputer = SimpleImputer(strategy="median")

X_train = imputer.fit_transform(train[features])
X_validation = imputer.transform(validation[features])

y_train = train["target"].astype(int)
y_validation = validation["target"].astype(int)

# 3. Train Random Forest
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_leaf=100,
    max_features="sqrt",
    n_jobs=2,
    random_state=42
)

print("Training Random Forest...", flush=True)

model.fit(X_train, y_train)

# 4. Generate validation predictions
predictions = model.predict_proba(X_validation)[:, 1]

# 5. Evaluate
print("\n========== RANDOM FOREST RESULTS ==========")

print("Training mortgages  :", f"{len(train):,}")
print("Validation mortgages:", f"{len(validation):,}")

print(
    "ROC-AUC            :",
    f"{roc_auc_score(y_validation, predictions):.4f}"
)

print(
    "Average Precision  :",
    f"{average_precision_score(y_validation, predictions):.4f}"
)

print(
    "Brier Score        :",
    f"{brier_score_loss(y_validation, predictions):.4f}"
)

print(
    "Actual Event Rate  :",
    f"{y_validation.mean():.2%}"
)

print(
    "Average Predicted PD:",
    f"{predictions.mean():.2%}"
)

print("\nRandom Forest validation: COMPLETED")
