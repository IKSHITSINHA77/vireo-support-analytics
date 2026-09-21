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

    Blank values are treated as missing, not automatically invalid.
    """

    if column not in df.columns:
        return {
            "column": column,
            "exists": False,
            "invalid_count": None,
            "error_rate": None,
        }

    original = df[column]

    # Blank values are allowed for optional fields.
    non_blank = original.notna() & (
        original.astype(str).str.strip() != ""
    )

    converted = pd.to_numeric(
        original,
        errors="coerce",
    )

    invalid_count = int(
        (non_blank & converted.isna()).sum()
    )

    checked_count = int(non_blank.sum())

    error_rate = (
        invalid_count / checked_count
        if checked_count > 0
        else 0
    )

    return {
        "column": column,
        "exists": True,
        "invalid_count": invalid_count,
        "checked_count": checked_count,
        "error_rate": float(error_rate),
    }


def validation_summary(df):
    """
    Produce a compact validation summary.

    Missing values are reported separately because several
    Vireo fields legitimately allow blanks.
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
    Run integrity checks on a reproducible random sample.

    Missing optional values are not treated as errors.
    The checks focus on invalid categorical values,
    invalid CSAT values, timestamp ordering, and
    negative handle times.
    """

    if df.empty:
        return {
            "sample_size": 0,
            "invalid_rows": 0,
            "error_rate": 0,
            "checks": {},
        }

    sample_size = min(
        sample_size,
        len(df),
    )

    sample = df.sample(
        n=sample_size,
        random_state=42,
    ).copy()

    checks = {}

    # ---------------------------------------------------------
    # Channel validation
    # ---------------------------------------------------------
    valid_channels = {
        "chat",
        "email",
        "voice",
        "social",
    }

    if "channel" in sample.columns:
        invalid_channels = int(
            (
                sample["channel"].notna()
                & ~sample["channel"].isin(valid_channels)
            ).sum()
        )
    else:
        invalid_channels = sample_size

    checks["invalid_channels"] = invalid_channels

    # ---------------------------------------------------------
    # Status validation
    # ---------------------------------------------------------
    valid_statuses = {
        "resolved",
        "closed",
        "open",
        "pending",
    }

    if "status" in sample.columns:
        invalid_statuses = int(
            (
                sample["status"].notna()
                & ~sample["status"].isin(valid_statuses)
            ).sum()
        )
    else:
        invalid_statuses = sample_size

    checks["invalid_statuses"] = invalid_statuses

    # ---------------------------------------------------------
    # CSAT validation
    # ---------------------------------------------------------
    if "csat_score" in sample.columns:
        csat = pd.to_numeric(
            sample["csat_score"],
            errors="coerce",
        )

        invalid_csat = int(
            (
                csat.notna()
                & ~csat.between(1, 5)
            ).sum()
        )
    else:
        invalid_csat = sample_size

    checks["invalid_csat"] = invalid_csat

    # ---------------------------------------------------------
    # Timestamp ordering
    # ---------------------------------------------------------
    invalid_timestamp_order = 0

    if {
        "first_response_at",
        "resolved_at",
    }.issubset(sample.columns):

        first_response = pd.to_datetime(
            sample["first_response_at"],
            errors="coerce",
        )

        resolved = pd.to_datetime(
            sample["resolved_at"],
            errors="coerce",
        )

        comparable = (
            first_response.notna()
            & resolved.notna()
        )

        invalid_timestamp_order = int(
            (
                comparable
                & (resolved < first_response)
            ).sum()
        )

    checks["invalid_timestamp_order"] = (
        invalid_timestamp_order
    )

    # ---------------------------------------------------------
    # Handle-time validation
    # ---------------------------------------------------------
    invalid_handle_time = 0

    if "handle_time_minutes" in sample.columns:
        handle_time = pd.to_numeric(
            sample["handle_time_minutes"],
            errors="coerce",
        )

        invalid_handle_time = int(
            (
                handle_time.notna()
                & (handle_time < 0)
            ).sum()
        )

    checks["negative_handle_time"] = (
        invalid_handle_time
    )

    # ---------------------------------------------------------
    # SLA mapping validation
    # ---------------------------------------------------------
    expected_sla = {
        "chat": 15,
        "voice": 120,
        "social": 240,
        "email": 480,
    }

    invalid_sla_mapping = 0

    if {
        "channel",
        "sla_target_minutes",
    }.issubset(sample.columns):

        sla_target = pd.to_numeric(
            sample["sla_target_minutes"],
            errors="coerce",
        )

        for channel, target in expected_sla.items():
            mask = sample["channel"].eq(channel)

            invalid_sla_mapping += int(
                (
                    mask
                    & sla_target.notna()
                    & sla_target.ne(target)
                ).sum()
            )

    checks["invalid_sla_mapping"] = (
        invalid_sla_mapping
    )

    # ---------------------------------------------------------
    # Agent ID validation
    # ---------------------------------------------------------
    invalid_agent_ids = 0

    if "agent_id" in sample.columns:
        invalid_agent_ids = int(
            (
                sample["agent_id"].isna()
                | (
                    sample["agent_id"]
                    .astype(str)
                    .str.strip()
                    .eq("")
                )
            ).sum()
        )

    checks["missing_agent_id"] = (
        invalid_agent_ids
    )

    # ---------------------------------------------------------
    # Overall result
    # ---------------------------------------------------------
    invalid_rows = 0

    for check_name, count in checks.items():
        invalid_rows += count

    # A row can fail more than one check, so calculate
    # row-level invalidity separately.
    row_invalid = pd.Series(
        False,
        index=sample.index,
    )

    if "channel" in sample.columns:
        row_invalid |= (
            sample["channel"].notna()
            & ~sample["channel"].isin(valid_channels)
        )

    if "status" in sample.columns:
        row_invalid |= (
            sample["status"].notna()
            & ~sample["status"].isin(valid_statuses)
        )

    if "csat_score" in sample.columns:
        csat = pd.to_numeric(
            sample["csat_score"],
            errors="coerce",
        )
        row_invalid |= (
            csat.notna()
            & ~csat.between(1, 5)
        )

    if {
        "first_response_at",
        "resolved_at",
    }.issubset(sample.columns):

        first_response = pd.to_datetime(
            sample["first_response_at"],
            errors="coerce",
        )

        resolved = pd.to_datetime(
            sample["resolved_at"],
            errors="coerce",
        )

        comparable = (
            first_response.notna()
            & resolved.notna()
        )

        row_invalid |= (
            comparable
            & (resolved < first_response)
        )

    if "handle_time_minutes" in sample.columns:
        handle_time = pd.to_numeric(
            sample["handle_time_minutes"],
            errors="coerce",
        )

        row_invalid |= (
            handle_time.notna()
            & (handle_time < 0)
        )

    invalid_rows = int(row_invalid.sum())

    error_rate = (
        invalid_rows / sample_size
        if sample_size > 0
        else 0
    )

    return {
        "sample_size": sample_size,
        "invalid_rows": invalid_rows,
        "error_rate": float(error_rate),
        "checks": checks,
    }