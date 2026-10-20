
"""
Freddie Mac Single-Family Loan-Level Dataset schema.

Raw staging schema: preserve every column as text.
Semantic names and data types will be applied in a
subsequent validated transformation step.
"""

# Number of columns verified from the 2007 Q1 files
ORIGINATION_COLUMN_COUNT = 31
PERFORMANCE_COLUMN_COUNT = 35

# Raw positional column names
ORIGINATION_COLUMNS = [
    f"col_{i:02d}"
    for i in range(1, ORIGINATION_COLUMN_COUNT + 1)
]

PERFORMANCE_COLUMNS = [
    f"col_{i:02d}"
    for i in range(1, PERFORMANCE_COLUMN_COUNT + 1)
]

# Verified field positions (1-based)

ORIGINATION_FIELDS = {
    "credit_score": 1,
    "first_payment_date": 2,
    "original_cltv": 9,
    "original_dti": 10,
    "original_upb": 11,
    "original_ltv": 12,
    "original_interest_rate": 13,
    "loan_sequence_number": 20,
}


PERFORMANCE_FIELDS = {
    "loan_sequence_number": 1,
    "monthly_reporting_period": 2,
    "current_actual_upb": 3,
    "current_delinquency_status": 4,
    "loan_age": 5,
    "remaining_months_to_maturity": 6,
}

DELIMITER = "|"


def validate_schema():
    """Validate column counts and mapped positions."""

    assert len(ORIGINATION_COLUMNS) == 31
    assert len(PERFORMANCE_COLUMNS) == 35

    assert len(set(ORIGINATION_COLUMNS)) == 31
    assert len(set(PERFORMANCE_COLUMNS)) == 35

    for position in ORIGINATION_FIELDS.values():
        assert 1 <= position <= ORIGINATION_COLUMN_COUNT

    for position in PERFORMANCE_FIELDS.values():
        assert 1 <= position <= PERFORMANCE_COLUMN_COUNT

    return True
