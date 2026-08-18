"""
SIP continuation cohort analysis. This is a real, specifically-Indian
retail-investing metric -- AMFI (the mutual fund industry association)
publishes an industry-wide "SIP stoppage ratio" every month, and it's
watched closely because SIPs are the primary way retail India invests.
A SIP that gets paused or cancelled isn't like a buyer skipping a
purchase -- it's a recurring commitment breaking, which is a much bigger
deal for both the investor's long-term outcomes and the platform's AUM.

Cohorts here are grouped by SIP start month, tracking Active/Paused/
Cancelled status forward -- same cohort-matrix shape used elsewhere in this
portfolio series, applied to a genuinely different underlying behavior.
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
VIZ = ROOT / "visuals"

sns.set_theme(style="white", context="talk")

sip = pd.read_csv(RAW / "sip_monthly_status.csv")
investments = pd.read_csv(RAW / "investments.csv", parse_dates=["investment_date"])

# SIP start month per sip_id -- earliest month row for that sip
sip_start = sip.groupby("sip_id")["month"].min().rename("start_month")
sip = sip.merge(sip_start, on="sip_id")
sip["cohort_p"] = pd.PeriodIndex(sip.start_month, freq="M")
sip["month_p"] = pd.PeriodIndex(sip.month, freq="M")
sip["month_index"] = (sip.month_p - sip.cohort_p).apply(lambda x: x.n)

cohort_sizes = sip.groupby("cohort_p")["sip_id"].nunique()

active_matrix = (sip[sip.status == "Active"]
                  .groupby(["cohort_p", "month_index"])["sip_id"].nunique()
                  .unstack(fill_value=0))
active_pct = (active_matrix.div(cohort_sizes, axis=0) * 100).round(1)

last_period = pd.Period("2026-07", freq="M")
for cohort in active_pct.index:
    max_idx = (last_period - cohort).n
    for col in active_pct.columns:
        if col > max_idx:
            active_pct.loc[cohort, col] = np.nan

active_pct.to_csv(PROC / "sip_continuation_matrix.csv")
print("=== SIP COHORT SIZES (by start month) ===")
print(cohort_sizes.to_string())
print("\n=== SIP CONTINUATION % (still Active, by months since start) ===")
print(active_pct.to_string())

# blended, correcting for observation-window bias the way project 4 did
valid_mask = active_pct.notna()
active_masked = active_matrix.where(valid_mask)
denom_per_month = pd.Series({col: cohort_sizes[valid_mask[col]].sum() for col in active_pct.columns})
blended = (active_masked.sum(axis=0, skipna=True) / denom_per_month * 100).round(1)
print("\n=== BLENDED SIP CONTINUATION CURVE ===")
print(blended.to_string())
blended.to_csv(PROC / "blended_sip_continuation.csv", header=["continuation_pct"])

# stoppage ratio (Paused + Cancelled combined) overall and by risk profile,
# for the most recent fully-observed month, since this is the number AMFI
# actually reports monthly
latest_full_month = "2026-06"  # July is the newest but many July cohorts have <1mo history
latest = sip[sip.month == latest_full_month]
stoppage_by_risk = (
    latest.groupby("risk_profile")["status"]
    .apply(lambda s: (s.isin(["Paused", "Cancelled"])).mean() * 100)
    .round(1).sort_values(ascending=False)
)
print(f"\n=== SIP STOPPAGE RATIO BY RISK PROFILE ({latest_full_month}) ===")
print(stoppage_by_risk.to_string())
stoppage_by_risk.to_csv(PROC / "sip_stoppage_ratio_by_risk.csv", header=["stoppage_ratio_pct"])

# ---- chart: heatmap ----
fig, ax = plt.subplots(figsize=(10.5, 6))
sns.heatmap(active_pct, annot=True, fmt=".0f", cmap="Blues", cbar_kws={"label": "% Active"},
            linewidths=0.5, ax=ax, vmin=0, vmax=100)
ax.set_xlabel("Months Since SIP Start")
ax.set_ylabel("SIP Start Cohort")
ax.set_title("SIP Continuation by Start Cohort (% still Active)")
plt.tight_layout()
plt.savefig(VIZ / "04_sip_continuation_heatmap.png", dpi=150)
plt.close()

# ---- chart: stoppage ratio by risk profile ----
fig, ax = plt.subplots(figsize=(8, 5.5))
colors = {"Conservative": "#b34d4d", "Moderate": "#d99a4e", "Aggressive": "#3f7d5c"}
ax.bar(stoppage_by_risk.index, stoppage_by_risk.values,
       color=[colors[r] for r in stoppage_by_risk.index])
for i, v in enumerate(stoppage_by_risk.values):
    ax.text(i, v + 0.3, f"{v}%", ha="center", fontsize=12)
ax.set_ylabel(f"SIP Stoppage Ratio, {latest_full_month} (%)")
ax.set_xlabel("Risk Profile")
ax.set_title("SIP Stoppage Ratio by Risk Profile")
plt.tight_layout()
plt.savefig(VIZ / "05_sip_stoppage_by_risk.png", dpi=150)
plt.close()

print("\nsaved: visuals/04_sip_continuation_heatmap.png, 05_sip_stoppage_by_risk.png")
