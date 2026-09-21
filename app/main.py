import streamlit as st
import pandas as pd

from data_loader import check_data_files, load_all_data
from analytics import (
    prepare_tickets,
    calculate_csat,
    calculate_handle_time,
    calculate_agent_metrics,
    get_bottom_agents,
    filter_q3,
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
    "Use synthetic demo data",
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

        st.info(
            "The dashboard is ready, but the Vireo data "
            "pack has not been provided yet."
        )

        st.write("Waiting for:")

        for filename in missing_files:

            st.write(
                f"- `{filename}`"
            )

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
# Q3 ANALYSIS
# ============================================================

st.divider()

st.subheader("Q3 Analysis")


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

    valid_dates = tickets[
        available_date_column
    ].dropna()

    if not valid_dates.empty:

        min_year = int(
            valid_dates.dt.year.min()
        )

        max_year = int(
            valid_dates.dt.year.max()
        )

        selected_year = st.selectbox(
            "Select Q3 year",
            list(
                range(
                    min_year,
                    max_year + 1,
                )
            ),
        )

        q3_tickets = filter_q3(
            tickets,
            available_date_column,
            selected_year,
        )

        st.metric(
            "Q3 Tickets",
            f"{len(q3_tickets):,}",
        )

        if not q3_tickets.empty:

            q3_metrics = calculate_agent_metrics(
                q3_tickets
            )

            if not q3_metrics.empty:

                st.write(
                    f"Agent-level Q3 analysis for "
                    f"{selected_year}"
                )

                st.dataframe(
                    get_bottom_agents(
                        q3_metrics,
                        n=10,
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.warning(
                    "Q3 tickets exist, but agent-level "
                    "metrics could not be calculated."
                )

        else:

            st.info(
                "No tickets were found during Q3 "
                "for the selected year."
            )

    else:

        st.info(
            "The available date column contains "
            "no valid dates."
        )

else:

    st.info(
        "No recognized ticket date column is available "
        "for Q3 analysis."
    )


# ============================================================
# SUPPORT OVERVIEW
# ============================================================

st.divider()

st.subheader("Support Overview")

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Total Tickets",
        f"{len(tickets):,}",
    )


with col2:

    csat = calculate_csat(
        tickets
    )

    if csat is not None:

        st.metric(
            "Average CSAT",
            f"{csat:.2f}",
        )

    else:

        st.metric(
            "Average CSAT",
            "N/A",
        )


with col3:

    handle_time = calculate_handle_time(
        tickets
    )

    if handle_time is not None:

        st.metric(
            "Average Handle Time",
            f"{handle_time:.2f}",
        )

    else:

        st.metric(
            "Average Handle Time",
            "N/A",
        )


# ============================================================
# AGENT PERFORMANCE
# ============================================================

st.divider()

st.subheader("Agent Performance")

agent_metrics = calculate_agent_metrics(
    tickets
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
# BOTTOM 10 AGENTS
# ============================================================

if not agent_metrics.empty:

    st.divider()

    st.subheader(
        "Bottom 10 Agents by CSAT"
    )

    bottom_agents = get_bottom_agents(
        agent_metrics,
        n=10,
    )

    st.dataframe(
        bottom_agents,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# AI-ASSISTED INSIGHTS
# ============================================================

if not agent_metrics.empty:

    st.divider()

    st.subheader(
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
# DATA QUALITY
# ============================================================

st.divider()

st.subheader(
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
    f"Rows containing at least one missing value: "
    f"{sample['invalid_rows']}"
)

st.write(
    f"Sample error rate: "
    f"{sample['error_rate']:.2%}"
)


# ============================================================
# DATA SOURCE WARNING
# ============================================================

st.divider()

if demo_mode:

    st.warning(
        "⚠ DEMO DATA: All displayed metrics are "
        "synthetic and must not be presented as "
        "actual Vireo Audio results."
    )

else:

    st.success(
        "✓ Metrics shown above are calculated "
        "from the provided Vireo data pack."
    )