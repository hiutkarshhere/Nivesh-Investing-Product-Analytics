# Power BI Setup

Same pattern as the rest of this series — model + DAX to paste into Power
BI Desktop, not a pre-built .pbix (can't be authored outside the actual app).

## Get Data
Import from `data/raw/`: `users.csv`, `onboarding_events.csv`,
`investments.csv`, `sip_monthly_status.csv`, `redemptions.csv`.

## Model
```
users (user_id) ─── 1:M ─── onboarding_events (user_id)
users (user_id) ─── 1:M ─── investments (user_id)
users (user_id) ─── 1:M ─── sip_monthly_status (user_id)
users (user_id) ─── 1:M ─── redemptions (user_id)
```

## DAX Measures

```dax
Total Signups = DISTINCTCOUNT(users[user_id])

Activated Investors =
CALCULATE(DISTINCTCOUNT(onboarding_events[user_id]), onboarding_events[event_name] = "first_investment_made")

Activation Rate % = DIVIDE([Activated Investors], [Total Signups], 0) * 100

Total AUM Invested = SUM(investments[amount_inr])

Active SIPs = CALCULATE(COUNTROWS(sip_monthly_status), sip_monthly_status[status] = "Active")

SIP Stoppage Rate % =
DIVIDE(
    CALCULATE(COUNTROWS(sip_monthly_status), sip_monthly_status[status] IN {"Paused", "Cancelled"}),
    COUNTROWS(sip_monthly_status), 0
) * 100

Total Redemptions = SUM(redemptions[amount_inr])
```

## Pages
1. **Onboarding Funnel** — funnel visual on `onboarding_events`, with a
   callout card for PAN/KYC median approval time (compute this one in
   Power Query or import `kyc_approval_time_stats.csv` directly — it needs
   a timestamp diff between two specific events, easier to bring in
   pre-computed)
2. **SIP Continuation** — matrix visual using `sip_continuation_matrix.csv`
   imported directly from `data/processed/` (rows = cohort, columns =
   month index, values = continuation %), conditional-formatted like the
   heatmap
3. **Market Correction Event Study** — clustered column chart, baseline vs
   correction stoppage rate, split by `risk_profile` — import
   `correction_event_study_sip.csv` for the exact rates and p-values used
   in the write-up
4. **Product Adoption** — bar chart of expansion rate by `first_product`
   and by `risk_profile`, plus a table of `product_transition_pairs.csv`
   for the "what do they buy next" view

## Also Worth Opening Directly in Excel/Sheets
`correction_event_study_sip.csv` and `expansion_by_first_product.csv` are
small, clean, and worth a look before building any dashboard around them.

## Note on the .pbix
Build it here, then drop the `.pbix` in this folder and add a screenshot
or two to the README before pushing — same as the rest of this series.
