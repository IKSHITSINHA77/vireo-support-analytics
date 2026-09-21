import pandas as pd

from app.analytics import (
    prepare_tickets,
    calculate_csat,
    calculate_handle_time,
    calculate_agent_metrics,
    get_bottom_agents,
    filter_q3,
)


def sample_data():

    return pd.DataFrame(
        {
            "ticket_id": [1, 2, 3, 4],
            "agent_id": ["A", "A", "B", "B"],
            "created_at": [
                "2025-07-01 10:00:00",
                "2025-08-01 10:00:00",
                "2025-09-01 10:00:00",
                "2025-10-01 10:00:00",
            ],
            "first_response_at": [
                "2025-07-01 10:10:00",
                "2025-08-01 10:20:00",
                "2025-09-01 11:00:00",
                "2025-10-01 11:00:00",
            ],
            "resolved_at": [
                "2025-07-01 11:10:00",
                "2025-08-01 11:20:00",
                "2025-09-01 12:00:00",
                "2025-10-01 12:00:00",
            ],
            "csat_score": [5, 4, 2, 3],
            "channel": [
                "chat",
                "chat",
                "chat",
                "chat",
            ],
            "source_system": [
                "helpdesk",
                "helpdesk",
                "helpdesk",
                "helpdesk",
            ],
        }
    )


def test_prepare_tickets():

    df = sample_data()

    result = prepare_tickets(df)

    assert len(result) == 4
    assert "handle_time_minutes" in result.columns
    assert "sla_breach" in result.columns


def test_csat():

    df = sample_data()

    df = prepare_tickets(df)

    assert calculate_csat(df) == 3.5


def test_handle_time():

    df = sample_data()

    df = prepare_tickets(df)

    # Each ticket has a 60-minute handle time.
    assert calculate_handle_time(df) == 60


def test_agent_metrics():

    df = sample_data()

    df = prepare_tickets(df)

    metrics = calculate_agent_metrics(df)

    assert len(metrics) == 2
    assert "agent_id" in metrics.columns
    assert "average_csat" in metrics.columns
    assert "csat_responses" in metrics.columns
    assert "average_handle_time" in metrics.columns


def test_bottom_agents():

    df = sample_data()

    df = prepare_tickets(df)

    metrics = calculate_agent_metrics(df)

    result = get_bottom_agents(
        metrics,
        n=1,
        min_csat_responses=2,
    )

    assert len(result) == 1
    assert result.iloc[0]["agent_id"] == "B"


def test_q3_filter():

    df = sample_data()

    df = prepare_tickets(df)

    result = filter_q3(
        df,
        "created_at",
        2025,
    )

    assert len(result) == 3