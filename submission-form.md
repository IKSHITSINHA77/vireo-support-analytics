# Vireo Audio — Submission Form

## 1. What did you build?

I built an AI-assisted Streamlit dashboard for Vireo Audio support analytics.

The application analyzes the supplied support-ticket data and provides:
- CSAT and survey-response analysis
- Average handle time
- Ticket volume
- Agent-level performance
- Qualified bottom-ten Tier 1 agent view
- Channel-level SLA performance
- SLA-credit exposure
- Refund and replacement summaries
- Data-quality and validation checks
- Deterministic AI-assisted operational insights
- Synthetic demo mode for safe end-to-end testing

### Business outcome

For the available Q3 period in the supplied data, Q3 2025 contained **1,577 tickets** and **151 first-response SLA breaches**.

Under Vireo's support policy, each first-response SLA breach results in a **₹350 store-credit issuance on resolution**. Therefore:

**151 × ₹350 = ₹52,850**

This is **₹52,850 of policy-defined SLA-credit exposure**, not confirmed cash loss.

Across the complete supplied dataset, there were **1,064 first-response SLA breaches**, corresponding to:

**1,064 × ₹350 = ₹372,400**

Again, this is policy-defined exposure rather than confirmed cash loss.

## 2. What does one run cost?

The current application does not call an external paid AI/API service.

### Application / AI cost
- External AI inference cost per run: **₹0**
- Local application software cost: **₹0**
- Excludes electricity, hardware and any optional hosting/API costs.

### Support-volume arithmetic requested by the task

Vireo's policy gives a blended contact cost of **₹290/contact**.

At 650 tickets/week:

**650 × ₹290 = ₹188,500/week**

Using 52 weeks / 12 months:

**650 × 52 / 12 = 2,816.67 tickets/month**

**2,816.67 × ₹290 ≈ ₹816,833/month**

This is the policy-based support contact cost, not the cost of running this dashboard.

## 3. How did you validate it?

Validation was performed at both code and application levels.

- Automated analytics tests: **6 passed**
- Production dataset size: **11,750 tickets**
- Validation sample in the dashboard: **50 records**, selected reproducibly with a fixed random seed.
- Checks include invalid channel/status values, CSAT outside 1–5, resolution before first response, negative handle time, SLA-target mapping and missing agent IDs.
- Missing cells are reported separately because the supplied schema permits legitimate blanks, including unanswered CSAT and missing order IDs.
- Legacy resolution timestamps were normalized by **+5:30** because the supplied support policy states that legacy event-log timestamps are UTC while reporting is in IST.

The dashboard displays the sampled invalid-row count and error rate directly so the result can be inspected during the demonstration.

## 4. Did you change, narrow or push back on the ask?

Yes.

I kept the primary training view focused on **Tier 1 agents** and excluded Tier 2 agents from Tier 1 volume/CSAT comparisons, following the supplied support policy.

I also added a minimum **3 CSAT responses** threshold for the qualified bottom-ten view. This is an analytical guardrail, not a Vireo policy requirement.

I treated SLA-credit exposure separately from confirmed cash loss because the policy supports the former, not the latter.

## 5. What is wrong, incomplete or shortcut?

- The supplied `email-thread.txt` did not contain usable message content beyond its header, so no additional requirements were invented from it.
- The bottom-ten view is an analytical training view, not a statement that the displayed agents are causally responsible for lower CSAT.
- Channel breach rates are descriptive and are not presented as causal drivers.
- The current AI-assisted insight layer is deterministic rather than dependent on an external LLM API.
- The dashboard uses a reproducible sample for validation rather than claiming that every possible data-quality issue is exhaustively detected by the sample.

## 6. What did you deliberately leave out?

I deliberately left out:
- Unsupported causal explanations for CSAT or SLA performance.
- LLM-generated numerical calculations; core business metrics are calculated deterministically.
- Tier 2 agents from Tier 1 volume/CSAT comparisons.
- Any claim that SLA-credit exposure represents confirmed cash loss.

## 7. Anything extra?

The application includes:
- Synthetic demo mode
- Missing-file detection
- Automated validation
- Modular analytics architecture
- Deterministic AI-assisted insight generation
- Production CSV loading
- Q3 filtering
- Channel-level SLA analysis
- Refund/replacement summary
- README setup documentation
- Automated tests

## 8. AI tools/models used

AI assistance was used during development for:
- application architecture
- code generation and refactoring
- debugging
- test development
- documentation
- interpreting the assignment requirements
- reviewing analytical logic

AI-generated code was reviewed, executed and tested locally.

No external paid AI inference API is required by the submitted application.

## 9. Recording

Recording link:

[ADD GOOGLE DRIVE RECORDING LINK]

## 10. Public Google Drive Link

[ADD GOOGLE DRIVE FOLDER LINK]

## 11. Top 3 handoff items

1. Keep the supplied Vireo data pack in the `data/` directory and use the production-data path for actual reporting.
2. Run the dashboard and review the validation panel before relying on recurring metrics.
3. Preserve the policy definitions and timezone normalization when extending the reporting workflow.

## 12. Honest hours spent

[ENTER ACTUAL HOURS]

## 13. GitHub Repository

https://github.com/IKSHITSINHA77/vireo-support-analytics
