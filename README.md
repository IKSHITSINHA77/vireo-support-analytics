# Vireo Audio — Support Analytics

AI-assisted support ticket analytics dashboard built for the Vireo Audio hiring task.

## Objective

The tool analyzes customer-support ticket data to help the Customer Experience team understand:

- Customer Satisfaction (CSAT)
- Average Handle Time
- Agent-level performance
- Q3 performance
- Bottom-ten agents by CSAT
- Data quality
- Validation/error rate
- AI-assisted operational insights

## Tech Stack

- Python
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
│   ├── main.py
│   ├── data_loader.py
│   ├── analytics.py
│   ├── ai_analysis.py
│   ├── validation.py
│   ├── business_outcome.py
│   └── demo_data.py
│
├── data/
│   └── README.md
│
├── tests/
│   └── test_analytics.py
│
├── README.md
├── requirements.txt
└── .gitignore