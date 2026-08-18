"""
Behavioral event study: did investor behavior actually change during the
simulated May 2026 correction, and does it differ by risk profile the way
behavioral finance would predict (loss-averse investors overreact to
volatility more than risk-tolerant ones)? Tests this properly with the
same two-proportion z-test used for the A/B test in project 2 -- not a new
technique, just applied to an observational "event" instead of a
randomized experiment, which is an important distinction stated explicitly
below rather than glossed over.

Reminder: the correction itself is a simulated scenario, not real market
data -- see the note in scripts/01_generate_data.py.
"""

import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
VIZ = ROOT / "visuals"

sns.set_theme(style="whitegrid", context="talk")

sip = pd.read_csv(RAW / "sip_monthly_status.csv")
redemptions = pd.read_csv(RAW / "redemptions.csv", parse_dates=["redemption_date"])
users = pd.read_csv(RAW / "users.csv")

BASELINE_MONTHS = ["2026-02", "2026-03", "2026-04"]  # calm months right before the correction
CORRECTION_MONTH = "2026-05"

# ---------------------------------------------------------------------------
# 1. SIP stoppage rate: baseline vs correction month, by risk profile
# ---------------------------------------------------------------------------
def stoppage_rate(df, months):
    sub = df[df.month.isin(months) if isinstance(months, list) else df.month == months]
    return sub.assign(stopped=sub.status.isin(["Paused", "Cancelled"])).groupby("risk_profile")["stopped"].agg(["sum", "count"])

baseline = stoppage_rate(sip, BASELINE_MONTHS)
correction = stoppage_rate(sip, CORRECTION_MONTH)

print("=== SIP STOPPAGE RATE: BASELINE (Feb-Apr avg) vs CORRECTION (May) ===")
results = []
for risk in ["Conservative", "Moderate", "Aggressive"]:
    n_base, x_base = baseline.loc[risk, "count"], baseline.loc[risk, "sum"]
    n_corr, x_corr = correction.loc[risk, "count"], correction.loc[risk, "sum"]
    p_base, p_corr = x_base / n_base, x_corr / n_corr

    # two-proportion z-test -- same test as project 2's A/B analysis
    p_pool = (x_base + x_corr) / (n_base + n_corr)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n_base + 1 / n_corr))
    z = (p_corr - p_base) / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    lift_pp = (p_corr - p_base) * 100

    print(f"\n{risk}:")
    print(f"  Baseline stoppage rate: {p_base*100:.2f}% (n={n_base:,})")
    print(f"  Correction stoppage rate: {p_corr*100:.2f}% (n={n_corr:,})")
    print(f"  Lift: {lift_pp:+.2f}pp   z={z:.3f}   p={p_value:.5f}   "
          f"{'SIGNIFICANT' if p_value < 0.05 else 'not significant'} at α=0.05")

    results.append({"risk_profile": risk, "baseline_rate_pct": round(p_base*100, 2),
                     "correction_rate_pct": round(p_corr*100, 2), "lift_pp": round(lift_pp, 2),
                     "z_stat": round(z, 3), "p_value": round(p_value, 5),
                     "significant": bool(p_value < 0.05)})

results_df = pd.DataFrame(results)
results_df.to_csv(PROC / "correction_event_study_sip.csv", index=False)

# ---------------------------------------------------------------------------
# 2. Same comparison for outright redemptions
# ---------------------------------------------------------------------------
users_risk = users.set_index("user_id")["risk_profile"]
redemptions["risk_profile"] = redemptions.user_id.map(users_risk)
redemptions["month"] = redemptions.redemption_date.astype(str).str.slice(0, 7)

# need a denominator: how many activated users existed (and were eligible to
# redeem) in each month, by risk profile -- approximate with distinct users
# who had ANY sip/investment activity that month as the eligible base
sip_users_by_month_risk = sip.groupby(["month", "risk_profile"])["user_id"].nunique()

print("\n\n=== REDEMPTION RATE: BASELINE vs CORRECTION ===")
redemption_results = []
for risk in ["Conservative", "Moderate", "Aggressive"]:
    n_base = sip_users_by_month_risk.reindex(
        pd.MultiIndex.from_product([BASELINE_MONTHS, [risk]])
    ).sum()
    x_base = redemptions[(redemptions.month.isin(BASELINE_MONTHS)) & (redemptions.risk_profile == risk)].shape[0]
    n_corr = sip_users_by_month_risk.get((CORRECTION_MONTH, risk), 0)
    x_corr = redemptions[(redemptions.month == CORRECTION_MONTH) & (redemptions.risk_profile == risk)].shape[0]

    if n_base == 0 or n_corr == 0:
        continue
    p_base, p_corr = x_base / n_base, x_corr / n_corr
    p_pool = (x_base + x_corr) / (n_base + n_corr)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n_base + 1 / n_corr)) if p_pool not in (0, 1) else np.nan
    z = (p_corr - p_base) / se if se and se > 0 else np.nan
    p_value = 2 * (1 - stats.norm.cdf(abs(z))) if not np.isnan(z) else np.nan

    print(f"\n{risk}: baseline {p_base*100:.2f}% -> correction {p_corr*100:.2f}%  "
          f"(lift {(p_corr-p_base)*100:+.2f}pp, p={p_value:.5f})" if not np.isnan(p_value) else f"\n{risk}: insufficient data")
    redemption_results.append({"risk_profile": risk, "baseline_rate_pct": round(p_base*100, 2),
                                "correction_rate_pct": round(p_corr*100, 2),
                                "lift_pp": round((p_corr-p_base)*100, 2),
                                "p_value": round(p_value, 5) if not np.isnan(p_value) else None})

pd.DataFrame(redemption_results).to_csv(PROC / "correction_event_study_redemptions.csv", index=False)

# ---------------------------------------------------------------------------
# charts
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6.5))
x = np.arange(len(results_df))
width = 0.35
ax.bar(x - width/2, results_df.baseline_rate_pct, width, label="Baseline (Feb-Apr avg)", color="#8ba3c7")
ax.bar(x + width/2, results_df.correction_rate_pct, width, label="Correction Month (May)", color="#b34d4d")
ax.set_xticks(x)
ax.set_xticklabels(results_df.risk_profile)
ax.set_ylabel("SIP Stoppage Rate (%)")
ax.set_title("SIP Stoppage Rate: Baseline vs Correction Month, by Risk Profile")
ax.legend()
for i, row in results_df.iterrows():
    sig = "*" if row.significant else ""
    ax.text(i, max(row.baseline_rate_pct, row.correction_rate_pct) + 0.8,
            f"+{row.lift_pp}pp{sig}", ha="center", fontsize=11)
plt.tight_layout()
plt.savefig(VIZ / "06_correction_event_study.png", dpi=150)
plt.close()

print("\nsaved: visuals/06_correction_event_study.png")
print("saved: data/processed/correction_event_study_sip.csv, correction_event_study_redemptions.csv")
