from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


REQUIRED_FILES = {
    "tickets": "tickets.csv",
    "agents": "agents.csv",
    "orders": "orders.csv",
    "customers": "customers.csv",
    "products": "products.csv",
}


def check_data_files():
    """
    Check which expected data files are available.
    """

    status = {}

    for name, filename in REQUIRED_FILES.items():
        file_path = DATA_DIR / filename

        status[name] = {
            "filename": filename,
            "exists": file_path.exists(),
            "path": file_path,
        }

    return status


def load_csv(filename):
    """
    Load a CSV file from the data directory.
    """

    file_path = DATA_DIR / filename

    if not file_path.exists():
        return None

    try:
        return pd.read_csv(file_path)
    except Exception as exc:
        raise RuntimeError(
            f"Could not read {filename}: {exc}"
        ) from exc


def load_all_data():
    """
    Load all available Vireo data files.
    """

    data = {}

    for name, filename in REQUIRED_FILES.items():
        data[name] = load_csv(filename)

    return data