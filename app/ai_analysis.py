import pandas as pd


def generate_insights(tickets: pd.DataFrame, agent_metrics: pd.DataFrame):
    """
    Generate deterministic AI-assisted operational insights.

    Numerical calculations remain deterministic and reproducible.
    This layer converts calculated metrics into concise business insights.
    """

    insights = []

    # ---------------------------------------------------------
    # Overall CSAT
    # ---------------------------------------------------------

    if "csat_score" in tickets.columns:
        csat_values = pd.to_numeric(
            tickets["csat_score"],
            errors="coerce",
        ).dropna()

        if not csat_values.empty:
            overall_csat = csat_values.mean()

            insights.append(
                f"Overall CSAT is {overall_csat:.2f}/5 "
                f"across {len(csat_values):,} survey responses."
            )

    # ---------------------------------------------------------
    # Handle time
    # ---------------------------------------------------------

    if "handle_time_minutes" in tickets.columns:
        handle_values = pd.to_numeric(
            tickets["handle_time_minutes"],
            errors="coerce",
        ).dropna()

        if not handle_values.empty:
            average_handle = handle_values.mean()

            insights.append(
                f"Average handle time is "
                f"{average_handle / 60:.1f} hours."
            )

    # ---------------------------------------------------------
    # SLA breaches
    # ---------------------------------------------------------

    if "sla_breach" in tickets.columns:

        breaches = int(
            tickets["sla_breach"]
            .fillna(False)
            .astype(bool)
            .sum()
        )

        if breaches > 0:

            exposure = breaches * 350

            insights.append(
                f"{breaches:,} tickets breached the first-response "
                f"SLA, representing ₹{exposure:,.0f} of "
                f"policy-defined SLA-credit exposure."
            )

    # ---------------------------------------------------------
    # Bottom agents
    # ---------------------------------------------------------

    if not agent_metrics.empty and "average_csat" in agent_metrics.columns:

        bottom = agent_metrics.dropna(
            subset=["average_csat"]
        ).sort_values(
            "average_csat",
            ascending=True,
        )

        # Only use agents with a meaningful CSAT sample.
        if "csat_responses" in bottom.columns:
            bottom = bottom[
                bottom["csat_responses"] >= 3
            ]

        if not bottom.empty:

            agent_identifier = (
                "agent_id"
                if "agent_id" in bottom.columns
                else "agent"
                if "agent" in bottom.columns
                else None
            )

            if agent_identifier:

                worst = bottom.iloc[0]

                agent_name = worst[agent_identifier]

                insights.append(
                    f"The lowest-CSAT Tier 1 agent in the "
                    f"qualified sample is {agent_name}, with "
                    f"CSAT of {worst['average_csat']:.2f}/5."
                )

    # ---------------------------------------------------------
    # Fallback
    # ---------------------------------------------------------

    if not insights:

        insights.append(
            "No sufficient metrics were available to generate "
            "operational insights."
        )

    return insights