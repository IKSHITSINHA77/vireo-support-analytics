import streamlit as st
import pandas as pd

from data_loader import check_data_files, load_all_data

from analytics import (
    calculate_channel_metrics,
    prepare_tickets,
    calculate_csat,
    calculate_handle_time,
    calculate_agent_metrics,
    get_bottom_agents,
    filter_q3,
    calculate_sla_breaches,
    calculate_sla_exposure,
)

from ai_analysis import generate_insights
from demo_data import create_demo_data

from validation import (
    validation_summary,
    sample_validation,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Vireo Audio Support Analytics",
    page_icon="🎧",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title("Vireo Audio — Support Analytics")

st.caption(
    "AI-assisted support ticket analysis dashboard"
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Dashboard Controls")

demo_mode = st.sidebar.checkbox(
    "Use demo data",
    value=False,
)

st.sidebar.caption(
    "Synthetic data is for application testing only. "
    "It must not be used for Vireo business conclusions."
)


# ============================================================
# DATA PACK STATUS
# ============================================================

st.subheader("Data Pack Status")

status = check_data_files()

missing_files = []

for _, details in status.items():

    if details["exists"]:

        st.success(
            f"✓ {details['filename']} found"
        )

    else:

        missing_files.append(
            details["filename"]
        )

        st.warning(
            f"⚠ {details['filename']} not provided"
        )


# ============================================================
# LOAD DATA
# ============================================================

if demo_mode:

    st.info(
        "DEMO MODE is active. The dashboard is using "
        "synthetic data generated locally for testing."
    )

    tickets = create_demo_data()

    agents = None

else:

    if missing_files:

        st.error(
            "The dashboard cannot run because required "
            "Vireo data files are missing."
        )

        st.write("Missing files:")

        for filename in missing_files:
            st.write(f"- `{filename}`")

        st.stop()

    data = load_all_data()

    tickets = data.get("tickets")
    agents = data.get("agents")

    if tickets is None:

        st.error(
            "tickets.csv could not be loaded."
        )

        st.stop()


# ============================================================
# PREPARE TICKETS
# ============================================================

tickets = prepare_tickets(
    tickets
)


# ============================================================
# Q3 2025 ANALYSIS
# ============================================================

st.divider()

st.header("Q3 2025 Performance")

st.caption(
    "Q3 is defined as July 1–September 30, 2025. "
    "The provided data ends June 30, 2026, so Q3 2025 "
    "is the available Q3 period in the supplied data."
)


# ------------------------------------------------------------
# Filter Q3 2025
# ------------------------------------------------------------

date_columns = [
    "created_at",
    "opened_at",
    "timestamp",
]

available_date_column = next(
    (
        column
        for column in date_columns
        if column in tickets.columns
    ),
    None,
)


if available_date_column:

    tickets[available_date_column] = pd.to_datetime(
        tickets[available_date_column],
        errors="coerce",
    )

    q3_tickets = filter_q3(
        tickets,
        available_date_column,
        2025,
    )

else:

    q3_tickets = pd.DataFrame()


# ------------------------------------------------------------
# Q3 KPI cards
# ------------------------------------------------------------

if q3_tickets.empty:

    st.warning(
        "No Q3 2025 tickets were found."
    )

else:

    q3_csat = calculate_csat(
        q3_tickets
    )

    q3_handle_time = calculate_handle_time(
        q3_tickets
    )

    q3_breaches = calculate_sla_breaches(
        q3_tickets
    )

    q3_exposure = calculate_sla_exposure(
        q3_tickets
    )

    q3_csat_responses = int(
        pd.to_numeric(
            q3_tickets["csat_score"],
            errors="coerce",
        ).notna().sum()
    ) if "csat_score" in q3_tickets.columns else 0


    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Q3 Tickets",
            f"{len(q3_tickets):,}",
        )

    with col2:

        st.metric(
            "Q3 CSAT",
            (
                f"{q3_csat:.2f} / 5"
                if q3_csat is not None
                else "N/A"
            ),
        )

        st.caption(
            f"{q3_csat_responses:,} survey responses"
        )

    with col3:

        st.metric(
            "Average Handle Time",
            (
                f"{q3_handle_time / 60:.1f} hrs"
                if q3_handle_time is not None
                else "N/A"
            ),
        )


    col4, col5, col6 = st.columns(3)

    with col4:

        st.metric(
            "SLA Breaches",
            f"{q3_breaches:,}",
        )

    with col5:

        st.metric(
            "SLA-Credit Exposure",
            f"₹{q3_exposure:,.0f}",
        )

    with col6:

        q3_breach_rate = (
            q3_breaches / len(q3_tickets)
            if len(q3_tickets) > 0
            else 0
        )

        st.metric(
            "SLA Breach Rate",
            f"{q3_breach_rate:.2%}",
        )

    st.caption(
        "SLA-credit exposure is policy-defined exposure "
        "based on ₹350 per first-response breach; it is "
        "not presented as confirmed cash loss."
    )


    st.subheader("Channel Performance")

channel_metrics = calculate_channel_metrics(q3_tickets)

if not channel_metrics.empty:

    channel_display = channel_metrics[
        [
        "channel",
        "tickets",
        "average_csat",
        "csat_responses",
        "average_handle_time_minutes",
        "sla_breaches",
        "breach_rate",
        "sla_exposure_inr",
        ]
    ].copy()

    channel_display = channel_display.rename(
        columns={
            "channel": "Channel",
            "tickets": "Tickets",
            "average_csat": "CSAT",
            "csat_responses": "CSAT Responses",
            "average_handle_time_minutes": "Avg Handle (min)",
            "sla_breaches": "SLA Breaches",
            "breach_rate": "SLA Breach Rate (%)",
            "sla_exposure_inr": "SLA Exposure (₹)",
        }
    )

    channel_display["CSAT"] = channel_display["CSAT"].round(2)
    channel_display["Avg Handle (min)"] = (
    channel_display["Avg Handle (min)"].round(1)
    )
    channel_display["SLA Breach Rate (%)"] = (
        channel_display["SLA Breach Rate (%)"].round(2)
    )
    channel_display["SLA Exposure (₹)"] = (
        channel_display["SLA Exposure (₹)"]
        .fillna(0)
        .round(0)
    )
    
    if not channel_metrics.empty:
        st.caption(
            "Channel SLA breach rates are descriptive. "
            "They should not be interpreted as causal drivers."
    )

    st.dataframe(
        channel_display,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "SLA exposure represents policy-defined SLA-credit exposure "
        "at ₹350 per first-response breach; it is not confirmed cash loss."
    )

else:
    st.info(
        "No channel-level metrics are available for the selected period."
    )
    
    st.subheader("Refund & Replacement Impact")

if "refund_amount_inr" in q3_tickets.columns:
    refund_amount = pd.to_numeric(
        q3_tickets["refund_amount_inr"],
        errors="coerce",
    ).fillna(0)
else:
    refund_amount = pd.Series(
        0,
        index=q3_tickets.index,
        dtype="float64",
    )

refund_tickets = int((refund_amount > 0).sum())
total_refunds = float(refund_amount.sum())

replacement_column = q3_tickets.get(
    "replacement_issued"
)

if replacement_column is not None:
    replacement_issued = int(
        replacement_column.astype(str)
        .str.upper()
        .eq("Y")
        .sum()
    )
else:
    replacement_issued = 0

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Refund Tickets",
        f"{refund_tickets:,}",
    )

with col2:
    st.metric(
        "Refund Amount",
        f"₹{total_refunds:,.0f}",
    )

with col3:
    st.metric(
        "Replacements Issued",
        f"{replacement_issued:,}",
    )

st.caption(
    "Refund amounts are taken from the exported ticket data. "
    "They are separate from the policy-defined SLA-credit exposure."
)

st.subheader("Business Outcome: SLA Credit Exposure")

q3_sla_breaches = calculate_sla_breaches(q3_tickets)
q3_sla_exposure = calculate_sla_exposure(q3_tickets)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Q3 SLA Breaches",
        f"{q3_sla_breaches:,}",
    )

with col2:
    st.metric(
        "Q3 SLA Exposure",
        f"₹{q3_sla_exposure:,.0f}",
    )

with col3:
    if len(q3_tickets) > 0:
        q3_breach_rate = (
            q3_sla_breaches
            / len(q3_tickets)
            * 100
        )
    else:
        q3_breach_rate = 0

    st.metric(
        "Q3 Breach Rate",
        f"{q3_breach_rate:.2f}%",
    )

st.info(
    "Business impact: Q3 2025 recorded "
    f"{q3_sla_breaches:,} first-response SLA breaches, "
    f"representing ₹{q3_sla_exposure:,.0f} of "
    "policy-defined SLA-credit exposure. "
    "This is an exposure measure under the support policy, "
    "not confirmed cash loss."
)
   
# ============================================================
# Q3 AGENT PERFORMANCE
# ============================================================

if not q3_tickets.empty:

    st.divider()

    st.header("Q3 2025 Agent Performance")

    st.caption(
        "Primary training view: Tier 1 agents with at least "
        "3 CSAT responses. Tier 2 agents are excluded from "
        "Tier 1 volume/CSAT comparisons."
    )

    q3_metrics = calculate_agent_metrics(
        q3_tickets,
        agents,
    )


    if q3_metrics.empty:

        st.warning(
            "Q3 tickets exist, but agent-level metrics "
            "could not be calculated."
        )

    else:

        st.subheader(
            "Bottom 10 Qualified Tier 1 Agents"
        )

        bottom_agents = get_bottom_agents(
            q3_metrics,
            n=10,
            tier=1,
            min_csat_responses=3,
        )

        if bottom_agents.empty:

            st.info(
                "No Tier 1 agents met the minimum "
                "CSAT-response threshold."
            )

        else:

            st.dataframe(
                bottom_agents,
                use_container_width=True,
                hide_index=True,
            )

        st.caption(
            "Minimum sample rule: ≥3 CSAT responses per agent. "
            "This threshold is an analytical guardrail rather "
            "than a Vireo policy requirement."
        )


# ============================================================
# SUPPORT OVERVIEW
# ============================================================

st.divider()

st.header("Support Overview")

overall_col1, overall_col2, overall_col3 = st.columns(3)


with overall_col1:

    st.metric(
        "Total Tickets",
        f"{len(tickets):,}",
    )


with overall_col2:

    overall_csat = calculate_csat(
        tickets
    )

    st.metric(
        "Average CSAT",
        (
            f"{overall_csat:.2f} / 5"
            if overall_csat is not None
            else "N/A"
        ),
    )


with overall_col3:

    overall_handle_time = calculate_handle_time(
        tickets
    )

    st.metric(
        "Average Handle Time",
        (
            f"{overall_handle_time / 60:.1f} hrs"
            if overall_handle_time is not None
            else "N/A"
        ),
    )


# ============================================================
# OVERALL SLA PERFORMANCE
# ============================================================

st.subheader("SLA Performance")

overall_breaches = calculate_sla_breaches(
    tickets
)

overall_exposure = calculate_sla_exposure(
    tickets
)

sla_col1, sla_col2 = st.columns(2)


with sla_col1:

    st.metric(
        "First-Response SLA Breaches",
        f"{overall_breaches:,}",
    )


with sla_col2:

    st.metric(
        "Policy-Defined SLA Exposure",
        f"₹{overall_exposure:,.0f}",
    )

st.caption(
    "Exposure uses the support-policy first-response "
    "credit of ₹350 per breach."
)


# ============================================================
# OVERALL AGENT PERFORMANCE
# ============================================================

st.divider()

st.header("Agent Performance")

agent_metrics = calculate_agent_metrics(
    tickets,
    agents,
)


if agent_metrics.empty:

    st.warning(
        "Agent-level analysis is unavailable because "
        "no recognized agent identifier was found."
    )

else:

    st.dataframe(
        agent_metrics,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# OVERALL BOTTOM 10
# ============================================================

if not agent_metrics.empty:

    st.divider()

    st.subheader(
        "Bottom 10 Qualified Tier 1 Agents"
    )

    overall_bottom_agents = get_bottom_agents(
        agent_metrics,
        n=10,
        tier=1,
        min_csat_responses=3,
    )

    if overall_bottom_agents.empty:

        st.info(
            "No Tier 1 agents met the minimum "
            "CSAT-response threshold."
        )

    else:

        st.dataframe(
            overall_bottom_agents,
            use_container_width=True,
            hide_index=True,
        )

    st.caption(
        "Tier 2 agents are excluded. Primary ranking "
        "requires at least 3 CSAT responses."
    )


# ============================================================
# AI-ASSISTED INSIGHTS
# ============================================================

if not agent_metrics.empty:

    st.divider()

    st.header(
        "AI-Assisted Insights"
    )

    insights = generate_insights(
        tickets,
        agent_metrics,
    )

    for insight in insights:

        st.info(
            f"💡 {insight}"
        )


# ============================================================
# DATA QUALITY & VALIDATION
# ============================================================

st.divider()

st.header(
    "Data Quality & Validation"
)

quality = validation_summary(
    tickets
)

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Rows",
        f"{quality['rows']:,}",
    )


with col2:

    st.metric(
        "Columns",
        f"{quality['columns']:,}",
    )


with col3:

    st.metric(
        "Missing Cells",
        f"{quality['missing_cells']:,}",
    )


with col4:

    st.metric(
        "Duplicate Rows",
        f"{quality['duplicate_rows']:,}",
    )


sample = sample_validation(
    tickets,
    sample_size=50,
)


st.write(
    f"Validation sample: "
    f"{sample['sample_size']} records"
)

st.write(
    f"Invalid sampled rows: "
    f"{sample['invalid_rows']}"
)

st.write(
    f"Validation error rate: "
    f"{sample['error_rate']:.2%}"
)


# ------------------------------------------------------------
# Validation checks
# ------------------------------------------------------------

if "checks" in sample:

    with st.expander(
        "Validation checks"
    ):

        validation_labels = {
            "invalid_channels":
                "Invalid channel values",

            "invalid_statuses":
                "Invalid status values",

            "invalid_csat":
                "CSAT values outside 1–5",

            "invalid_timestamp_order":
                "Resolution before first response",

            "negative_handle_time":
                "Negative handle times",

            "invalid_sla_mapping":
                "Invalid SLA target mapping",

            "missing_agent_id":
                "Missing agent IDs",
        }

        for key, label in validation_labels.items():

            count = sample["checks"].get(
                key,
                0,
            )

            if count == 0:

                st.write(
                    f"✓ {label}: 0"
                )

            else:

                st.write(
                    f"⚠ {label}: {count}"
                )


st.caption(
    "Missing cells are reported separately because some "
    "Vireo fields legitimately allow blanks, such as "
    "CSAT for customers who did not respond and order IDs "
    "when customers did not quote an order."
)


# ============================================================
# DATA SOURCE WARNING
# ============================================================

st.divider()

if demo_mode:

    st.warning(
        "⚠ DEMO DATA: All displayed metrics are synthetic "
        "and must not be presented as actual Vireo Audio results."
    )

else:

    st.success(
        "✓ Metrics shown above are calculated from the "
        "provided Vireo data pack."
    )