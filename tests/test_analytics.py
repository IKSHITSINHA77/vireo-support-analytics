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

    return pd.DataFrame({
        "ticket_id": [1, 2, 3, 4],
        "agent_id": [
            "A",
            "A",
            "B",
            "B",
        ],
        "created_at": [
            "2025-07-01",
            "2025-08-01",
            "2025-09-01",
            "2025-10-01",
        ],
        "csat": [
            5,
            4,
            2,
            3,
        ],
        "handle_time_minutes": [
            10,
            20,
            30,
            40,
        ],
    })


def test_prepare_tickets():

    df = sample_data()

    result = prepare_tickets(df)

    assert len(result) == 4


def test_csat():

    df = sample_data()

    result = calculate_csat(df)

    assert result == 3.5


def test_handle_time():

    df = sample_data()

    result = calculate_handle_time(df)

    assert result == 25


def test_agent_metrics():

    df = sample_data()

    result = calculate_agent_metrics(df)

    assert len(result) == 2


def test_bottom_agents():

    df = sample_data()

    metrics = calculate_agent_metrics(df)

    result = get_bottom_agents(
        metrics,
        n=1,
    )

    assert len(result) == 1


def test_q3_filter():

    df = sample_data()

    df["created_at"] = pd.to_datetime(
        df["created_at"]
    )

    result = filter_q3(
        df,
        "created_at",
        2025,
    )

    assert len(result) == 3