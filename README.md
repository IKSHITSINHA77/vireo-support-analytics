# Vireo Audio — Support Analytics

AI-assisted support ticket analytics dashboard built for the Vireo Audio hiring task.

## Overview

This application analyzes customer-support data to help identify:

- CSAT performance
- Average handle time
- Agent-level performance
- Bottom-performing agents
- Support trends
- Data-quality issues
- Potential operational improvement opportunities

The application is built with Python, Streamlit, Pandas and lightweight analytics/AI-assisted components.

## Tech Stack

- Python 3.10+
- Streamlit
- Pandas
- NumPy
- Plotly
- Scikit-learn
- Pytest

## Project Structure

```text
vireo-support-analytics/
│
├── app/
│   ├── __init__.py
│   ├── ai_analysis.py
│   ├── analytics.py
│   ├── business_outcome.py
│   ├── data_loader.py
│   ├── demo_data.py
│   ├── main.py
│   └── validation.py
│
├── data/
│   └── README.md
│
├── tests/
│   └── test_analytics.py
│
├── .gitignore
├── README.md
└── requirements.txt