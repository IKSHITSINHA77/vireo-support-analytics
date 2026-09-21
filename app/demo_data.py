import pandas as pd
import numpy as np


def create_demo_data():
    """
    Synthetic data used only to test the dashboard.
    This is NOT Vireo production data.
    """

    np.random.seed(42)

    agents = [
        "Agent-001",
        "Agent-002",
        "Agent-003",
        "Agent-004",
        "Agent-005",
        "Agent-006",
        "Agent-007",
        "Agent-008",
        "Agent-009",
        "Agent-010",
        "Agent-011",
        "Agent-012",
    ]

    rows = 600

    data = pd.DataFrame({
        "ticket_id": range(1, rows + 1),

        "agent_id": np.random.choice(
            agents,
            rows
        ),

        "created_at": pd.date_range(
            "2025-01-01",
            periods=rows,
            freq="D",
        ),

        "csat": np.random.choice(
            [1, 2, 3, 4, 5],
            rows,
            p=[
                0.05,
                0.10,
                0.15,
                0.30,
                0.40,
            ],
        ),

        "handle_time_minutes": np.round(
            np.random.normal(
                12,
                4,
                rows,
            ).clip(2, 40),
            2,
        ),
    })

    return data