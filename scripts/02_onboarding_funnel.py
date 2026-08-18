"""
Signup -> first investment funnel. The step worth paying attention to here
is PAN/KYC approval -- unlike the funnels in the rest of this portfolio
series (UPI KYC, seller KYC), this one has a genuine multi-day regulatory
delay baked in (NSDL/CDSL-style verification), not just a conversion-rate
drop. So this script reports both the conversion rate AND the time-to-
approve, since a slow-but-eventually-approved step needs a different fix
(progress messaging, expectation-setting) than a step people just abandon.
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
PROC.mkdir(parents=True, exist_ok=True)
VIZ.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", context="talk")
PALETTE = sns.light_palette("#1d4ed8", n_colors=9, reverse=True)

users = pd.read_csv(RAW / "users.csv")
funnel = pd.read_csv(RAW / "onboarding_events.csv", parse_dates=["event_timestamp"])

STAGE_ORDER = ["signup_started", "mobile_otp_verified", "pan_kyc_submitted", "pan_kyc_approved",
               "risk_assessment_completed", "bank_account_linked", "first_investment_made"]
STAGE_LABELS = {
    "signup_started": "Signup Started", "mobile_otp_verified": "Mobile OTP Verified",
    "pan_kyc_submitted": "PAN/KYC Submitted", "pan_kyc_approved": "PAN/KYC Approved",
    "risk_assessment_completed": "Risk Assessment Done", "bank_account_linked": "Bank Linked",
    "first_investment_made": "First Investment Made",
}

reached = funnel.groupby("event_name")["user_id"].nunique().reindex(STAGE_ORDER)
total = reached["signup_started"]

funnel_summary = pd.DataFrame({
    "stage": [STAGE_LABELS[s] for s in STAGE_ORDER],
    "users_reached": reached.values,
    "pct_of_total": (reached.values / total * 100).round(2),
    "step_conversion_pct": (reached.values / reached.shift(1).values * 100).round(2),
})
funnel_summary.loc[0, "step_conversion_pct"] = 100.0
funnel_summary.to_csv(PROC / "onboarding_funnel.csv", index=False)
print(funnel_summary.to_string(index=False))

overall_conv = funnel_summary.loc[funnel_summary.stage == "First Investment Made", "pct_of_total"].iloc[0]
print(f"\nSignup -> first investment conversion: {overall_conv}%")

# ---------------------------------------------------------------------------
# time-to-approve for the PAN/KYC step specifically
# ---------------------------------------------------------------------------
submitted = funnel[funnel.event_name == "pan_kyc_submitted"].set_index("user_id")["event_timestamp"]
approved = funnel[funnel.event_name == "pan_kyc_approved"].set_index("user_id")["event_timestamp"]
common = submitted.index.intersection(approved.index)
kyc_hours = (approved.loc[common] - submitted.loc[common]).dt.total_seconds() / 3600
print(f"\nPAN/KYC approval time: median {kyc_hours.median():.1f}h, "
      f"p75 {kyc_hours.quantile(0.75):.1f}h, p90 {kyc_hours.quantile(0.90):.1f}h")
kyc_hours.describe().to_csv(PROC / "kyc_approval_time_stats.csv", header=["hours"])

# ---------------------------------------------------------------------------
# funnel by acquisition channel
# ---------------------------------------------------------------------------
funnel_ch = funnel.merge(users[["user_id", "acquisition_channel"]], on="user_id")
by_channel = (funnel_ch.groupby(["acquisition_channel", "event_name"])["user_id"]
              .nunique().unstack(fill_value=0).reindex(columns=STAGE_ORDER))
by_channel_pct = (by_channel.div(by_channel["signup_started"], axis=0) * 100).round(2)
by_channel_pct.to_csv(PROC / "funnel_by_channel.csv")
activation_by_channel = by_channel_pct["first_investment_made"].sort_values(ascending=False)
print("\nActivation rate (signup -> first investment) by channel:")
print(activation_by_channel.to_string())

# ---- chart: funnel ----
fig, ax = plt.subplots(figsize=(11, 6.5))
bars = ax.barh(funnel_summary.stage[::-1], funnel_summary.pct_of_total[::-1], color=PALETTE[:len(funnel_summary)][::-1])
for bar, pct, n in zip(bars, funnel_summary.pct_of_total[::-1], funnel_summary.users_reached[::-1]):
    ax.text(bar.get_width() + 1.3, bar.get_y() + bar.get_height() / 2, f"{pct}%  ({n:,})", va="center", fontsize=10.5)
ax.set_xlim(0, 112)
ax.set_xlabel("% of Total Signups")
ax.set_title(f"Nivesh Onboarding Funnel (n={total:,} signups, Jan-May 2026)")
plt.tight_layout()
plt.savefig(VIZ / "01_onboarding_funnel.png", dpi=150)
plt.close()

# ---- chart: KYC approval time distribution ----
fig, ax = plt.subplots(figsize=(9.5, 5.5))
sns.histplot(kyc_hours.clip(upper=120), bins=30, color="#1d4ed8", ax=ax)
ax.axvline(kyc_hours.median(), color="#b34d4d", linestyle="--", linewidth=2, label=f"Median: {kyc_hours.median():.0f}h")
ax.set_xlabel("Hours from KYC Submission to Approval")
ax.set_ylabel("Users")
ax.set_title("PAN/KYC Approval Time Distribution")
ax.legend()
plt.tight_layout()
plt.savefig(VIZ / "02_kyc_approval_time.png", dpi=150)
plt.close()

# ---- chart: activation by channel ----
fig, ax = plt.subplots(figsize=(9, 5.5))
activation_by_channel.plot(kind="bar", ax=ax, color=PALETTE[1:5])
ax.set_ylabel("Signup -> First Investment Rate (%)")
ax.set_xlabel("Acquisition Channel")
ax.set_title("Activation Rate by Acquisition Channel")
ax.set_xticklabels(ax.get_xticklabels(), rotation=20, ha="right")
for i, v in enumerate(activation_by_channel.values):
    ax.text(i, v + 0.5, f"{v}%", ha="center", fontsize=10.5)
plt.tight_layout()
plt.savefig(VIZ / "03_activation_by_channel.png", dpi=150)
plt.close()

print("\nsaved: visuals/01_onboarding_funnel.png, 02_kyc_approval_time.png, 03_activation_by_channel.png")
