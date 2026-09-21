import pandas as pd


def generate_insights(
    tickets: pd.DataFrame,
    agent_metrics: pd.DataFrame,
):
    """
    Generate deterministic AI-assisted business insights
    from calculated metrics.

    No external API is required.
    """

    insights = []

    if tickets.empty:
        return [
            "No ticket records are available for analysis."
        ]

    total_tickets = len(tickets)

    insights.append(
        f"The dataset contains {total_tickets:,} support tickets."
    )

    if "average_csat" in agent_metrics.columns:

        csat = agent_metrics["average_csat"].dropna()

        if not csat.empty:

            overall_csat = csat.mean()

            insights.append(
                f"Average agent-level CSAT is "
                f"{overall_csat:.2f}."
            )

            lowest = csat.min()

            insights.append(
                f"The lowest observed agent-level CSAT "
                f"is {lowest:.2f}."
            )

    if "average_handle_time" in agent_metrics.columns:

        handle = (
            agent_metrics[
                "average_handle_time"
            ]
            .dropna()
        )

        if not handle.empty:

            insights.append(
                f"Average handle time across available "
                f"agent records is {handle.mean():.2f}."
            )

            highest = handle.max()

            insights.append(
                f"The highest observed agent-level "
                f"handle time is {highest:.2f}."
            )

    if "average_csat" in agent_metrics.columns:

        valid = agent_metrics.dropna(
            subset=["average_csat"]
        )

        if len(valid) >= 3:

            bottom = valid.nsmallest(
                min(3, len(valid)),
                "average_csat",
            )

            agents = ", ".join(
                bottom["agent"]
                .astype(str)
                .tolist()
            )

            insights.append(
                "Agents requiring closer review based "
                f"on lowest CSAT include: {agents}."
            )

    return insights