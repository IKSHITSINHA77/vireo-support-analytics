import pandas as pd


def find_column(df: pd.DataFrame, candidates):
    """
    Find the first matching column from possible column names.
    """

    normalized = {
        str(column).strip().lower().replace(" ", "_"): column
        for column in df.columns
    }

    for candidate in candidates:

        candidate = (
            candidate
            .strip()
            .lower()
            .replace(" ", "_")
        )

        if candidate in normalized:
            return normalized[candidate]

    return None


def prepare_tickets(tickets: pd.DataFrame):
    """
    Clean and standardize ticket data.
    """

    df = tickets.copy()

    df.columns = [
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        for column in df.columns
    ]

    date_columns = [
        "created_at",
        "opened_at",
        "closed_at",
        "resolved_at",
        "timestamp",
    ]

    for column in date_columns:

        if column in df.columns:

            df[column] = pd.to_datetime(
                df[column],
                errors="coerce",
            )

    numeric_columns = [
        "csat",
        "csat_score",
        "handle_time",
        "handle_time_minutes",
        "aht",
        "average_handle_time",
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    return df


def get_csat_column(df):
    return find_column(
        df,
        [
            "csat",
            "csat_score",
            "customer_satisfaction",
            "satisfaction_score",
        ],
    )


def get_handle_time_column(df):
    return find_column(
        df,
        [
            "handle_time",
            "handle_time_minutes",
            "aht",
            "average_handle_time",
        ],
    )


def get_agent_column(df):
    return find_column(
        df,
        [
            "agent_id",
            "agent",
            "agent_name",
            "assigned_agent",
        ],
    )


def calculate_csat(df):

    column = get_csat_column(df)

    if column is None:
        return None

    values = pd.to_numeric(
        df[column],
        errors="coerce",
    ).dropna()

    if values.empty:
        return None

    return values.mean()


def calculate_handle_time(df):

    column = get_handle_time_column(df)

    if column is None:
        return None

    values = pd.to_numeric(
        df[column],
        errors="coerce",
    ).dropna()

    if values.empty:
        return None

    return values.mean()


def calculate_agent_metrics(df):

    agent_column = get_agent_column(df)

    if agent_column is None:
        return pd.DataFrame()

    csat_column = get_csat_column(df)
    handle_column = get_handle_time_column(df)

    grouped = (
        df.groupby(agent_column)
        .size()
        .reset_index(name="ticket_count")
    )

    grouped = grouped.rename(
        columns={
            agent_column: "agent"
        }
    )

    if csat_column:

        csat_data = (
            df.groupby(agent_column)[csat_column]
            .mean()
            .reset_index()
        )

        csat_data = csat_data.rename(
            columns={
                agent_column: "agent",
                csat_column: "average_csat",
            }
        )

        grouped = grouped.merge(
            csat_data,
            on="agent",
            how="left",
        )

    if handle_column:

        handle_data = (
            df.groupby(agent_column)[handle_column]
            .mean()
            .reset_index()
        )

        handle_data = handle_data.rename(
            columns={
                agent_column: "agent",
                handle_column: "average_handle_time",
            }
        )

        grouped = grouped.merge(
            handle_data,
            on="agent",
            how="left",
        )

    return grouped.sort_values(
        "ticket_count",
        ascending=False,
    )


def get_bottom_agents(
    agent_metrics,
    n=10,
):

    if agent_metrics.empty:
        return agent_metrics

    if "average_csat" in agent_metrics.columns:

        return (
            agent_metrics
            .sort_values(
                "average_csat",
                ascending=True,
                na_position="last",
            )
            .head(n)
        )

    return agent_metrics.head(n)

def filter_by_date_range(
    df,
    date_column,
    start_date,
    end_date,
):
    """
    Filter records between two dates.
    """

    if date_column not in df.columns:
        return pd.DataFrame()

    result = df.copy()

    result[date_column] = pd.to_datetime(
        result[date_column],
        errors="coerce",
    )

    return result[
        (result[date_column] >= pd.Timestamp(start_date))
        & (result[date_column] <= pd.Timestamp(end_date))
    ].copy()


def filter_q3(
    df,
    date_column,
    year,
):
    """
    Filter July-September for the selected year.

    Q3 is defined here as:
    July 1 through September 30.
    """

    start_date = f"{year}-07-01"
    end_date = f"{year}-09-30 23:59:59"

    return filter_by_date_range(
        df,
        date_column,
        start_date,
        end_date,
    )
