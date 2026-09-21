import pandas as pd


def validate_required_columns(df, required_columns):
    """
    Check whether expected columns are present.
    """

    available = set(df.columns)

    missing = [
        column
        for column in required_columns
        if column not in available
    ]

    return {
        "valid": len(missing) == 0,
        "missing_columns": missing,
    }


def validate_numeric_column(df, column):
    """
    Check whether a numeric column contains invalid values.
    """

    if column not in df.columns:
        return {
            "column": column,
            "exists": False,
            "invalid_count": None,
            "error_rate": None,
        }

    values = pd.to_numeric(
        df[column],
        errors="coerce",
    )

    invalid_count = values.isna().sum()
    total_count = len(df)

    error_rate = (
        invalid_count / total_count
        if total_count > 0
        else 0
    )

    return {
        "column": column,
        "exists": True,
        "invalid_count": int(invalid_count),
        "error_rate": float(error_rate),
    }


def validation_summary(df):
    """
    Produce a compact validation summary.
    """

    total_rows = len(df)

    missing_cells = int(
        df.isna().sum().sum()
    )

    total_cells = (
        df.shape[0] * df.shape[1]
    )

    missing_rate = (
        missing_cells / total_cells
        if total_cells > 0
        else 0
    )

    duplicate_rows = int(
        df.duplicated().sum()
    )

    return {
        "rows": total_rows,
        "columns": df.shape[1],
        "missing_cells": missing_cells,
        "missing_rate": missing_rate,
        "duplicate_rows": duplicate_rows,
    }


def sample_validation(df, sample_size=50):
    """
    Validate a sample of records.

    This is intentionally simple and transparent so that
    the sample size and resulting error rate can be reported.
    """

    if df.empty:
        return {
            "sample_size": 0,
            "invalid_rows": 0,
            "error_rate": 0,
        }

    sample_size = min(
        sample_size,
        len(df),
    )

    sample = df.sample(
        n=sample_size,
        random_state=42,
    )

    invalid_rows = int(
        sample.isna()
        .any(axis=1)
        .sum()
    )

    error_rate = (
        invalid_rows / sample_size
        if sample_size > 0
        else 0
    )

    return {
        "sample_size": sample_size,
        "invalid_rows": invalid_rows,
        "error_rate": error_rate,
    }