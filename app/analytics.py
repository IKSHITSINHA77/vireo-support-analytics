import pandas as pd


# ============================================================
# VIREO AUDIO — SUPPORT ANALYTICS
# ============================================================

SLA_TARGET_MINUTES = {
    "chat": 15,
    "voice": 120,
    "social": 240,
    "email": 480,
}

SLA_CREDIT_INR = 350
TRANSFER_COST_INR = 305
AGENT_COST_PER_HOUR_INR = 165


# ============================================================
# COLUMN HELPERS
# ============================================================

def find_column(df: pd.DataFrame, candidates):
    """
    Find the first matching column from possible column names.

    Matching is case-insensitive and whitespace/underscore tolerant.
    """

    normalized = {
        str(column).strip().lower().replace(" ", "_"): column
        for column in df.columns
    }

    for candidate in candidates:
        candidate = (
            candidate.strip()
            .lower()
            .replace(" ", "_")
        )

        if candidate in normalized:
            return normalized[candidate]

    return None


def get_csat_column(df):
    return find_column(
        df,
        [
            "csat_score",
            "csat",
            "customer_satisfaction",
            "satisfaction_score",
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


# ============================================================
# TICKET PREPARATION
# ============================================================

def prepare_tickets(tickets: pd.DataFrame):
    """
    Clean and standardize Vireo ticket data.

    Policy basis:
    - Reporting timestamps are IST.
    - Legacy resolution timestamps were reconstructed from UTC.
    - Handle time = first human response to resolution.
    - SLA breach = first response later than the channel target.
    """

    df = tickets.copy()

    # --------------------------------------------------------
    # Normalize column names
    # --------------------------------------------------------

    df.columns = [
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        for column in df.columns
    ]

    # --------------------------------------------------------
    # Parse date columns
    # --------------------------------------------------------

    date_columns = [
        "created_at",
        "first_response_at",
        "resolved_at",
        "opened_at",
        "closed_at",
        "timestamp",
    ]

    for column in date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce",
            )

    # --------------------------------------------------------
    # Convert numeric columns
    # --------------------------------------------------------

    numeric_columns = [
        "csat_score",
        "csat",
        "refund_amount_inr",
        "transfers",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # --------------------------------------------------------
    # Normalize channel values
    # --------------------------------------------------------

    if "channel" in df.columns:
        df["channel"] = (
            df["channel"]
            .astype("string")
            .str.strip()
            .str.lower()
        )

    # --------------------------------------------------------
    # Legacy resolution timestamps
    #
    # Policy:
    # Helpdesk timestamps are IST.
    # Legacy event-log resolution timestamps are UTC.
    #
    # Therefore legacy resolution timestamps receive +05:30.
    # --------------------------------------------------------

    if {
        "source_system",
        "resolved_at",
    }.issubset(df.columns):

        legacy_mask = (
            df["source_system"]
            .astype("string")
            .str.strip()
            .str.lower()
            .eq("legacy_fd")
        )

        df.loc[legacy_mask, "resolved_at"] = (
            df.loc[legacy_mask, "resolved_at"]
            + pd.Timedelta(hours=5, minutes=30)
        )

    # --------------------------------------------------------
    # Handle time
    #
    # Policy:
    # Handle time = first response to resolution.
    # --------------------------------------------------------

    if {
        "first_response_at",
        "resolved_at",
    }.issubset(df.columns):

        df["handle_time_minutes"] = (
            (
                df["resolved_at"]
                - df["first_response_at"]
            )
            .dt.total_seconds()
            / 60
        )

        # Negative handle times are invalid.
        df.loc[
            df["handle_time_minutes"] < 0,
            "handle_time_minutes",
        ] = pd.NA

    # --------------------------------------------------------
    # SLA first-response calculation
    # --------------------------------------------------------

    if {
        "created_at",
        "first_response_at",
        "channel",
    }.issubset(df.columns):

        # Map channel to policy SLA target.
        df["sla_target_minutes"] = (
            df["channel"]
            .map(SLA_TARGET_MINUTES)
        )

        # Calculate first response time BEFORE using it below.
        df["first_response_minutes"] = (
            (
                df["first_response_at"]
                - df["created_at"]
            )
            .dt.total_seconds()
            / 60
        )

        # A ticket can only be classified as a breach when
        # both response time and SLA target are available.
        valid_sla = (
            df["first_response_minutes"].notna()
            & df["sla_target_minutes"].notna()
        )

        # Nullable Boolean supports:
        # True  = breach
        # False = within target
        # NA    = cannot determine
        df["sla_breach"] = pd.Series(
            pd.NA,
            index=df.index,
            dtype="boolean",
        )

        df.loc[valid_sla, "sla_breach"] = (
            df.loc[
                valid_sla,
                "first_response_minutes",
            ]
            >
            df.loc[
                valid_sla,
                "sla_target_minutes",
            ]
        )

        # ₹350 policy-defined credit exposure per breach.
        # Missing/unknown SLA status contributes ₹0.
        df["sla_credit_exposure_inr"] = (
            df["sla_breach"]
            .fillna(False)
            .astype(int)
            * SLA_CREDIT_INR
        )

    else:
        # Keep expected columns available even when a non-production
        # or incomplete dataset is passed to this function.
        df["sla_target_minutes"] = pd.NA
        df["first_response_minutes"] = pd.NA
        df["sla_breach"] = pd.Series(
            pd.NA,
            index=df.index,
            dtype="boolean",
        )
        df["sla_credit_exposure_inr"] = 0

    return df


# ============================================================
# OVERALL METRICS
# ============================================================

def calculate_csat(df):
    """
    Calculate average CSAT.

    Policy:
    Blank CSAT means no response and must be excluded.
    """

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


def calculate_csat_responses(df):
    """
    Number of tickets with a CSAT response.
    """

    column = get_csat_column(df)

    if column is None:
        return 0

    return (
        pd.to_numeric(
            df[column],
            errors="coerce",
        )
        .notna()
        .sum()
    )


def calculate_handle_time(df):
    """
    Average handle time in minutes.

    Policy:
    Handle time = first response to resolution.
    """

    if "handle_time_minutes" not in df.columns:
        return None

    values = pd.to_numeric(
        df["handle_time_minutes"],
        errors="coerce",
    ).dropna()

    if values.empty:
        return None

    return values.mean()


def calculate_sla_breaches(df):
    """
    Count valid first-response SLA breaches.
    """

    if "sla_breach" not in df.columns:
        return 0

    return int(
        df["sla_breach"]
        .fillna(False)
        .astype(bool)
        .sum()
    )


def calculate_sla_exposure(df):
    """
    Calculate policy-defined SLA credit exposure.

    ₹350 per first-response SLA breach.
    """

    return (
        calculate_sla_breaches(df)
        * SLA_CREDIT_INR
    )


# ============================================================
# AGENT METRICS
# ============================================================

def calculate_agent_metrics(
    tickets: pd.DataFrame,
    agents: pd.DataFrame | None = None,
):
    """
    Calculate resolving-agent performance.

    Important:
    - agent_id identifies the resolving agent.
    - assigned_team is the first-routed team and is NOT
      treated as the resolving agent's team.
    - Agent roster information comes from agents.csv.
    """

    agent_column = get_agent_column(tickets)

    if agent_column is None:
        return pd.DataFrame()

    df = tickets.copy()

    # --------------------------------------------------------
    # Base ticket counts
    # --------------------------------------------------------

    grouped = (
        df.groupby(agent_column)
        .size()
        .reset_index(name="ticket_count")
    )

    grouped = grouped.rename(
        columns={
            agent_column: "agent_id"
        }
    )

    # --------------------------------------------------------
    # CSAT
    # --------------------------------------------------------

    csat_column = get_csat_column(df)

    if csat_column:

        df["_csat_numeric"] = pd.to_numeric(
            df[csat_column],
            errors="coerce",
        )

        csat_data = (
            df.groupby(agent_column)["_csat_numeric"]
            .agg(
                average_csat="mean",
                csat_responses="count",
            )
            .reset_index()
            .rename(
                columns={
                    agent_column: "agent_id"
                }
            )
        )

        grouped = grouped.merge(
            csat_data,
            on="agent_id",
            how="left",
        )

    else:
        grouped["average_csat"] = pd.NA
        grouped["csat_responses"] = 0

    # --------------------------------------------------------
    # Handle time
    # --------------------------------------------------------

    if "handle_time_minutes" in df.columns:

        handle_data = (
            df.groupby(agent_column)["handle_time_minutes"]
            .mean()
            .reset_index()
            .rename(
                columns={
                    agent_column: "agent_id",
                    "handle_time_minutes":
                        "average_handle_time",
                }
            )
        )

        grouped = grouped.merge(
            handle_data,
            on="agent_id",
            how="left",
        )

    # --------------------------------------------------------
    # SLA breaches
    # --------------------------------------------------------

    if "sla_breach" in df.columns:

        breach_data = (
        df.groupby(agent_column)["sla_breach"]
        .agg(
            sla_breaches=lambda x: int(
                x.fillna(False)
                .astype(bool)
                .sum()
            ),
            sla_observations=lambda x: int(
                x.notna().sum()
            ),
        )
        .reset_index()
        .rename(
            columns={
                agent_column: "agent_id"
            }
        )
    )

    # Force both columns to numeric dtype.
    # This prevents Pandas BooleanArray division errors.
    breach_data["sla_breaches"] = pd.to_numeric(
        breach_data["sla_breaches"],
        errors="coerce",
    ).fillna(0).astype(float)

    breach_data["sla_observations"] = pd.to_numeric(
        breach_data["sla_observations"],
        errors="coerce",
    ).fillna(0).astype(float)

    grouped = grouped.merge(
        breach_data,
        on="agent_id",
        how="left",
    )

    grouped["sla_breaches"] = pd.to_numeric(
        grouped["sla_breaches"],
        errors="coerce",
    ).fillna(0).astype(float)

    grouped["sla_observations"] = pd.to_numeric(
        grouped["sla_observations"],
        errors="coerce",
    ).fillna(0).astype(float)

    grouped["sla_breach_rate"] = 0.0

    observed = grouped["sla_observations"] > 0

    grouped.loc[observed, "sla_breach_rate"] = (
        grouped.loc[observed, "sla_breaches"]
        / grouped.loc[observed, "sla_observations"]
        * 100
    )
    # --------------------------------------------------------
    # Join roster
    # --------------------------------------------------------

    if agents is not None and not agents.empty:

        roster = agents.copy()

        roster.columns = [
            str(column)
            .strip()
            .lower()
            .replace(" ", "_")
            for column in roster.columns
        ]

        roster_columns = [
            column
            for column in [
                "agent_id",
                "name",
                "site",
                "team",
                "shift",
                "tier",
            ]
            if column in roster.columns
        ]

        roster = roster[roster_columns].drop_duplicates(
            subset=["agent_id"]
        )

        grouped = grouped.merge(
            roster,
            on="agent_id",
            how="left",
        )

    # --------------------------------------------------------
    # Ordering
    # --------------------------------------------------------

    return (
        grouped
        .sort_values(
            [
                "average_csat",
                "csat_responses",
            ],
            ascending=[
                True,
                False,
            ],
            na_position="last",
        )
        .reset_index(drop=True)
    )


# ============================================================
# BOTTOM AGENTS
# ============================================================

def get_bottom_agents(
    agent_metrics,
    n=10,
    tier=1,
    min_csat_responses=3,
):
    """
    Return the lowest-CSAT Tier 1 agents for training review.

    Tier 2 agents are excluded because the Vireo policy states
    that Tier 2 agents are not to be compared with Tier 1
    on volume metrics.

    Agents with fewer than min_csat_responses are excluded
    from the primary bottom-agent list so that a single survey
    does not dominate the ranking.

    The response count remains visible in the resulting table.
    """

    if agent_metrics.empty:
        return agent_metrics

    result = agent_metrics.copy()

    # --------------------------------------------------------
    # Tier filtering
    # --------------------------------------------------------

    if "tier" in result.columns:

        result["tier"] = pd.to_numeric(
            result["tier"],
            errors="coerce",
        )

        result = result[
            result["tier"] == tier
        ].copy()

    # --------------------------------------------------------
    # Minimum CSAT sample
    # --------------------------------------------------------

    if "csat_responses" in result.columns:

        result = result[
            result["csat_responses"]
            >= min_csat_responses
        ].copy()

    # --------------------------------------------------------
    # Bottom-CSAT ordering
    # --------------------------------------------------------

    if "average_csat" in result.columns:

        return (
            result
            .sort_values(
                [
                    "average_csat",
                    "csat_responses",
                ],
                ascending=[
                    True,
                    False,
                ],
                na_position="last",
            )
            .head(n)
        )

    return result.head(n)


# ============================================================
# DATE FILTERING
# ============================================================

def filter_by_date_range(
    df,
    date_column,
    start_date,
    end_date,
):
    """
    Filter records between two dates, inclusive.
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
        &
        (result[date_column] <= pd.Timestamp(end_date))
    ].copy()


def filter_q3(
    df,
    date_column,
    year,
):
    """
    Filter July 1 through September 30 for the selected year.
    """

    start_date = f"{year}-07-01"
    end_date = f"{year}-09-30 23:59:59"

    return filter_by_date_range(
        df,
        date_column,
        start_date,
        end_date,
    )


# ============================================================
# CHANNEL METRICS
# ============================================================

def calculate_channel_metrics(df):
    """
    Calculate ticket, SLA, CSAT and handle-time metrics by channel.
    """

    if "channel" not in df.columns:
        return pd.DataFrame()

    metrics = (
        df.groupby("channel")
        .agg(
            tickets=("ticket_id", "size"),

            sla_breaches=(
                "sla_breach",
                lambda x: int(
                    x.fillna(False)
                    .astype(bool)
                    .sum()
                ),
            ),

            sla_observations=(
                "sla_breach",
                lambda x: int(
                    x.notna().sum()
                ),
            ),
        )
        .reset_index()
    )

    # Ensure arithmetic columns are numeric.
    metrics["sla_breaches"] = pd.to_numeric(
        metrics["sla_breaches"],
        errors="coerce",
    ).fillna(0)

    metrics["sla_observations"] = pd.to_numeric(
        metrics["sla_observations"],
        errors="coerce",
    ).fillna(0)

    # SLA breach rate
    metrics["breach_rate"] = (
        metrics["sla_breaches"]
        /
        metrics["sla_observations"]
        .replace(0, pd.NA)
        * 100
    )

    # Policy-defined SLA-credit exposure
    metrics["sla_exposure_inr"] = (
        metrics["sla_breaches"]
        * SLA_CREDIT_INR
    )

    # CSAT
    csat_column = get_csat_column(df)

    if csat_column:

        csat = (
            df.groupby("channel")[csat_column]
            .agg(
                average_csat="mean",
                csat_responses="count",
            )
            .reset_index()
        )

        metrics = metrics.merge(
            csat,
            on="channel",
            how="left",
        )

    # Handle time
    if "handle_time_minutes" in df.columns:

        handle = (
            df.groupby("channel")["handle_time_minutes"]
            .agg(
                average_handle_time_minutes="mean",
            )
            .reset_index()
        )

        metrics = metrics.merge(
            handle,
            on="channel",
            how="left",
        )

    return (
        metrics
        .sort_values(
            "tickets",
            ascending=False,
        )
        .reset_index(drop=True)
    )