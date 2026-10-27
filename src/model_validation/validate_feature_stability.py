
import duckdb
import numpy as np
import pandas as pd

# Step 121 — Feature stability validation

con = duckdb.connect()

con.execute("SET memory_limit='3GB'")
con.execute("SET threads=2")

features = [
    "credit_score",
    "original_ltv",
    "original_cltv",
    "original_dti",
    "interest_rate",
    "loan_amount"
]

try:
    results = con.execute("""
        SELECT
            data_split,
            COUNT(*) AS mortgages,

            ROUND(AVG(credit_score), 2) AS credit_score,
            ROUND(AVG(original_ltv), 2) AS original_ltv,
            ROUND(AVG(original_cltv), 2) AS original_cltv,
            ROUND(AVG(original_dti), 2) AS original_dti,
            ROUND(AVG(interest_rate), 2) AS interest_rate,
            ROUND(AVG(loan_amount), 2) AS loan_amount

        FROM read_parquet(
            'data/processed/modeling_split.parquet'
        )

        WHERE data_split IN ('TRAIN', 'VALIDATION')

        GROUP BY data_split
        ORDER BY data_split
    """).df()

    print("========== FEATURE STABILITY ==========")

    print(results.to_string(index=False))

    assert len(results) == 2
    assert results["mortgages"].sum() == 676_698

    print("\nFeature comparison: PASSED")

# Step 122 — Population Stability Index

    df = con.execute("""
        SELECT
            data_split,
            credit_score,
            original_ltv,
            original_cltv,
            original_dti,
            interest_rate,
            loan_amount
        FROM read_parquet(
            'data/processed/modeling_split.parquet'
        )
        WHERE data_split IN ('TRAIN', 'VALIDATION')
    """).df()

    train = df[df["data_split"] == "TRAIN"]
    validation = df[df["data_split"] == "VALIDATION"]

    def calculate_psi(train_values, validation_values):
        # Remove missing values when determining bin boundaries
        valid_train = train_values.dropna().to_numpy()
        valid_validation = validation_values.dropna().to_numpy()

        # Use training quantiles for consistent comparison
        bins = np.unique(
            np.quantile(valid_train, np.linspace(0, 1, 11))
        )

        # Include values outside the training range
        bins[0] = -np.inf
        bins[-1] = np.inf

        train_counts = np.histogram(
            valid_train, bins=bins
        )[0]

        validation_counts = np.histogram(
            valid_validation, bins=bins
        )[0]

        # Treat missing values as their own group
        train_counts = np.append(
            train_counts, train_values.isna().sum()
        )

        validation_counts = np.append(
            validation_counts, validation_values.isna().sum()
        )

        # Smooth zero counts to allow logarithms
        epsilon = 1e-6

        expected = train_counts / len(train_values)
        actual = validation_counts / len(validation_values)

        expected = np.maximum(expected, epsilon)
        actual = np.maximum(actual, epsilon)

        expected /= expected.sum()
        actual /= actual.sum()

        return np.sum(
            (actual - expected) * np.log(actual / expected)
        )

    print("\n========== POPULATION STABILITY INDEX ==========")

    for feature in features:
        psi = calculate_psi(
            train[feature],
            validation[feature]
        )
        print(f"{feature:<20}: {psi:.4f}")

    print("\nPSI calculation: COMPLETED")

############################################


    # Step 123 — Investigate interest rate PSI

    feature = "interest_rate"

    train_rates = train[feature].dropna()
    validation_rates = validation[feature].dropna()

    # Create bins based on training interest rates
    bins = np.unique(
        np.quantile(train_rates, np.linspace(0, 1, 11))
    )

    bins[0] = -np.inf
    bins[-1] = np.inf

    # Apply identical bins to both populations
    train_groups = pd.cut(train_rates, bins=bins)
    validation_groups = pd.cut(validation_rates, bins=bins)

    comparison = pd.DataFrame({
        "train_pct": train_groups.value_counts(
            sort=False, normalize=True
        ) * 100,

        "validation_pct": validation_groups.value_counts(
            sort=False, normalize=True
        ) * 100
    })

    print("\n========== INTEREST RATE DISTRIBUTION ==========")

    print(
        comparison.to_string(
            float_format=lambda x: f"{x:.2f}"
        )
    )

    print("\nTraining median:", train_rates.median())
    print("Validation median:", validation_rates.median())
    print("Number of bins:", len(bins) - 1)


finally:
    con.close()
