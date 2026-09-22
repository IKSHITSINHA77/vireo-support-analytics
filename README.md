# Vireo Audio — Support Analytics

AI-assisted support ticket analytics dashboard built for the Vireo Audio hiring task.

## What it does

The application analyzes the supplied Vireo support data to provide:

- Q3 2025 CSAT and ticket volume
- Average handle time
- Agent-level performance
- Qualified bottom-ten Tier 1 agent view
- Channel-level SLA performance
- SLA breach rate and policy-defined SLA-credit exposure
- Refund and replacement summaries
- Data-quality checks and validation
- Deterministic AI-assisted operational insights
- Synthetic demo mode for safe application testing

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
├── app/
│   ├── __init__.py
│   ├── ai_analysis.py
│   ├── analytics.py
│   ├── business_outcome.py
│   ├── data_loader.py
│   ├── demo_data.py
│   ├── main.py
│   └── validation.py
├── data/
│   ├── README.txt
│   ├── tickets.csv
│   ├── agents.csv
│   ├── orders.csv
│   ├── customers.csv
│   ├── products.csv
│   ├── support-policy.pdf
│   └── email-thread.txt
├── tests/
│   └── test_analytics.py
├── .gitignore
├── README.md
├── requirements.txt
└── submission-form.md
```

## Setup on a clean machine

### 1. Clone the repository

```powershell
git clone https://github.com/IKSHITSINHA77/vireo-support-analytics.git
cd vireo-support-analytics
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution for the current user, use:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate the environment again.

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the tests

```powershell
python -m pytest -q
```

Expected result for the submitted test suite:

```text
6 passed
```

### 5. Start the dashboard

```powershell
streamlit run app\main.py
```

The dashboard opens in the browser.

## Production data vs demo data

The sidebar contains a **Use demo data** checkbox.

- Leave it **unchecked** for the supplied Vireo production data.
- Enable it only to test the application with synthetic data.
- Demo values must not be presented as actual Vireo business results.

The production workflow expects the supplied data pack in `data/`.

## Key reporting definitions

The application follows the supplied Vireo support policy.

- Q3 2025 = July 1–September 30, 2025.
- CSAT blanks are excluded from CSAT averages.
- Handle time = first human response to resolution.
- First-response SLA targets: chat 15 min, voice 2 hr, social 4 hr, email 8 hr.
- SLA-credit exposure = ₹350 per first-response SLA breach.
- Legacy resolution timestamps are normalized from UTC to IST (+5:30).
- Tier 2 agents are excluded from Tier 1 volume/CSAT comparisons.
- The qualified bottom-ten view requires at least 3 CSAT responses per agent.

## Q3 2025 result from the supplied data

- Tickets: **1,577**
- CSAT: **3.43 / 5**
- CSAT responses: **726**
- Average handle time: **23.9 hours**
- SLA breaches: **151**
- SLA breach rate: **9.58%**
- Policy-defined SLA-credit exposure: **₹52,850**

The ₹52,850 figure is an exposure measure under the supplied support policy, not confirmed cash loss.

## Validation

The dashboard reports:
- row/column counts
- missing cells
- duplicate rows
- a reproducible 50-record validation sample
- invalid sampled rows
- validation error rate
- detailed integrity checks

Missing cells are reported separately because the supplied schema permits legitimate blanks, such as unanswered CSAT and missing order IDs.

## Important analytical limitation

The dashboard describes observed relationships and performance metrics. It does not claim that a channel, agent or other factor caused a CSAT or SLA outcome.

## AI usage

The project was developed with AI assistance for architecture, coding, debugging, tests, documentation and requirement interpretation. Numerical business calculations are deterministic and testable. The submitted application does not require a paid external AI inference API.
