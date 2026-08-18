"""
Generates data for Nivesh -- a fictional Indian investing app (mutual
funds, direct stocks, SIPs), modeled on the Groww/Zerodha/Kuvera category.

Important: the "market correction" simulated in this dataset (May 2026) is
a hypothetical scenario built to study behavioral response, not a real
market event. Nothing here should be read as actual NSE/BSE/Nifty data --
this project has no visibility into real markets beyond its training data,
and 2026 market movements specifically aren't something to assert as fact.
It's a plausible, documented "what if a correction happened" setup, same
spirit as every other simulated dataset in this portfolio series.

Stack stays consistent with the rest of the series: pandas/numpy for
generation and analysis, no ML/stats libraries beyond a single two-
proportion z-test later (same technique used in project 2's A/B test).
"""

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

rng = np.random.default_rng(31)

OUT = Path(__file__).resolve().parent.parent / "data" / "raw"
OUT.mkdir(parents=True, exist_ok=True)

SIM_START = datetime(2026, 1, 1)
SIM_END = datetime(2026, 7, 31)
ONBOARDING_MONTHS = [datetime(2026, m, 1) for m in range(1, 6)]  # Jan-May
MONTHLY_SIGNUPS = [1780, 2010, 2240, 1920, 1650]  # 9,600 total, not a clean ramp

CHANNELS = ["Organic App Store", "Referral", "Influencer/Content", "Paid Ads"]
CHANNEL_WEIGHTS = [0.35, 0.25, 0.20, 0.20]
CHANNEL_MODIFIER = {  # applied per onboarding stage, same pattern as elsewhere
    "Organic App Store": 0.0, "Referral": 0.03, "Influencer/Content": 0.05, "Paid Ads": -0.06,
}

CITY_TIER_WEIGHTS = {"Tier 1": 0.40, "Tier 2": 0.38, "Tier 3": 0.22}
AGE_BRACKETS = ["18-24", "25-34", "35-44", "45-54", "55+"]
AGE_WEIGHTS = [0.18, 0.42, 0.25, 0.11, 0.04]
RISK_PROFILES = ["Conservative", "Moderate", "Aggressive"]
RISK_WEIGHTS = [0.30, 0.45, 0.25]

# ---------------------------------------------------------------------------
# 1. USERS
# ---------------------------------------------------------------------------
user_rows = []
uid = 400000
for month_start, n in zip(ONBOARDING_MONTHS, MONTHLY_SIGNUPS):
    days = 28 if month_start.month == 2 else 30
    offsets = rng.integers(0, days, size=n)
    channels = rng.choice(CHANNELS, size=n, p=CHANNEL_WEIGHTS)
    tiers = rng.choice(list(CITY_TIER_WEIGHTS), size=n, p=list(CITY_TIER_WEIGHTS.values()))
    ages = rng.choice(AGE_BRACKETS, size=n, p=AGE_WEIGHTS)
    risks = rng.choice(RISK_PROFILES, size=n, p=RISK_WEIGHTS)
    for i in range(n):
        user_rows.append({
            "user_id": f"NV{uid}",
            "signup_date": (month_start + timedelta(days=int(offsets[i]))).date(),
            "signup_month": month_start.strftime("%Y-%m"),
            "acquisition_channel": channels[i],
            "city_tier": tiers[i],
            "age_bracket": ages[i],
            "risk_profile": risks[i],
        })
        uid += 1

users = pd.DataFrame(user_rows)

# ---------------------------------------------------------------------------
# 2. ONBOARDING FUNNEL (KYC-heavy, with a realistic multi-day PAN/KYC delay)
# ---------------------------------------------------------------------------
STAGE_RATES = {
    "mobile_otp_verified": 0.91,
    "pan_kyc_submitted": 0.84,
    "pan_kyc_approved": 0.88,
    "risk_assessment_completed": 0.92,
    "bank_account_linked": 0.90,
    "first_investment_made": 0.68,
}

funnel_rows = []
for _, row in users.iterrows():
    u = row.user_id
    t = pd.Timestamp(row.signup_date)
    mod = CHANNEL_MODIFIER[row.acquisition_channel]
    funnel_rows.append({"user_id": u, "event_name": "signup_started", "event_timestamp": t})
    still_going = True
    for stage, base_p in STAGE_RATES.items():
        if not still_going:
            break
        p = min(max(base_p + mod, 0.05), 0.99)
        if rng.random() < p:
            if stage == "pan_kyc_approved":
                # this is the real-world friction point -- NSDL/CDSL-style
                # regulatory verification genuinely takes 1-3+ days, unlike
                # every other step here which is same-day
                delay_hours = rng.exponential(scale=36)
            else:
                delay_hours = rng.exponential(scale=4)
            t = t + timedelta(hours=float(delay_hours))
            funnel_rows.append({"user_id": u, "event_name": stage, "event_timestamp": t})
        else:
            still_going = False

funnel = pd.DataFrame(funnel_rows)
activated_users = sorted(funnel.loc[funnel.event_name == "first_investment_made", "user_id"].unique())
print(f"users: {len(users):,}  activated (made first investment): {len(activated_users):,}")

# ---------------------------------------------------------------------------
# 3. FIRST INVESTMENT + PRODUCT MIX
# ---------------------------------------------------------------------------
PRODUCT_TYPES = ["Mutual Fund - Equity", "Mutual Fund - Debt", "Mutual Fund - Hybrid",
                  "Direct Stocks", "ETF"]
FIRST_PRODUCT_WEIGHTS = [0.48, 0.14, 0.12, 0.18, 0.08]

first_investment_time = funnel[funnel.event_name == "first_investment_made"].set_index("user_id")["event_timestamp"]
user_risk = users.set_index("user_id")["risk_profile"].to_dict()

investment_rows = []
iid = 700000
first_product_map = {}
for u in activated_users:
    t0 = first_investment_time[u]
    first_prod = rng.choice(PRODUCT_TYPES, p=FIRST_PRODUCT_WEIGHTS)
    first_product_map[u] = first_prod
    mode = "SIP" if rng.random() < 0.62 else "Lumpsum"
    amount = float(np.clip(rng.lognormal(np.log(2800 if mode == "SIP" else 12000), 0.55), 500, 200000))
    investment_rows.append({
        "investment_id": iid, "user_id": u, "investment_date": t0.date(),
        "product_type": first_prod, "investment_mode": mode, "amount_inr": round(amount, 2),
    })
    iid += 1

    # chance of adding a second product type later on (product expansion) --
    # more likely for users with more time-since-activation and varies by
    # risk profile (aggressive investors diversify into more products faster)
    months_since = max((SIM_END - t0.to_pydatetime()).days // 30, 0)
    expand_p = {"Conservative": 0.22, "Moderate": 0.34, "Aggressive": 0.46}[user_risk[u]]
    if rng.random() < expand_p and months_since >= 1:
        remaining = [p for p in PRODUCT_TYPES if p != first_prod]
        second_prod = rng.choice(remaining)
        second_delay_days = int(rng.integers(20, max(months_since * 30, 21)))
        second_date = (t0 + timedelta(days=second_delay_days))
        if second_date.to_pydatetime() <= SIM_END:
            mode2 = "SIP" if rng.random() < 0.55 else "Lumpsum"
            amount2 = float(np.clip(rng.lognormal(np.log(2400 if mode2 == "SIP" else 9000), 0.6), 500, 200000))
            investment_rows.append({
                "investment_id": iid, "user_id": u, "investment_date": second_date.date(),
                "product_type": second_prod, "investment_mode": mode2, "amount_inr": round(amount2, 2),
            })
            iid += 1

investments = pd.DataFrame(investment_rows)

# ---------------------------------------------------------------------------
# 4. SIP MONTHLY STATUS PANEL
# ---------------------------------------------------------------------------
# the hypothetical correction: a sharp simulated drawdown in May 2026,
# partial recovery in June. NOT real market data -- see module docstring.
CORRECTION_MONTHS = {"2026-05": 1.0, "2026-06": 0.4}  # elevation multiplier weight
BASELINE_PAUSE_RATE = 0.040
BASELINE_CANCEL_RATE = 0.018
CORRECTION_PAUSE_LIFT = {"Conservative": 0.10, "Moderate": 0.045, "Aggressive": 0.012}
CORRECTION_CANCEL_LIFT = {"Conservative": 0.045, "Moderate": 0.018, "Aggressive": 0.004}

sip_investments = investments[investments.investment_mode == "SIP"].copy()
sip_rows = []
sid = 900000
for _, inv in sip_investments.iterrows():
    u = inv.user_id
    risk = user_risk[u]
    start_month = pd.Timestamp(inv.investment_date).to_period("M")
    months = pd.period_range(start_month, pd.Period("2026-07", "M"), freq="M")
    status = "Active"
    for m in months:
        m_str = str(m)
        if status in ("Cancelled",):
            break  # once cancelled, stays cancelled -- no further rows needed conceptually,
            # but we still want a record showing it stopped, handled by just not appending further
        correction_weight = CORRECTION_MONTHS.get(m_str, 0.0)
        pause_p = BASELINE_PAUSE_RATE + CORRECTION_PAUSE_LIFT[risk] * correction_weight
        cancel_p = BASELINE_CANCEL_RATE + CORRECTION_CANCEL_LIFT[risk] * correction_weight

        if status == "Paused":
            # paused SIPs mostly resume next month if no longer in correction window, some cancel
            if correction_weight > 0 and rng.random() < 0.35:
                status = "Paused"
            elif rng.random() < 0.20:
                status = "Cancelled"
            else:
                status = "Active"
        else:
            roll = rng.random()
            if roll < cancel_p:
                status = "Cancelled"
            elif roll < cancel_p + pause_p:
                status = "Paused"
            else:
                status = "Active"

        sip_rows.append({
            "sip_id": sid, "user_id": u, "month": m_str, "risk_profile": risk,
            "status": status, "amount_inr": inv.amount_inr if status == "Active" else 0.0,
        })
        if status == "Cancelled":
            break
    sid += 1

sip_status = pd.DataFrame(sip_rows)

# ---------------------------------------------------------------------------
# 5. REDEMPTIONS (partial/full withdrawals -- separate from SIP pausing)
# ---------------------------------------------------------------------------
BASELINE_REDEMPTION_RATE = 0.030
CORRECTION_REDEMPTION_LIFT = {"Conservative": 0.075, "Moderate": 0.030, "Aggressive": 0.006}

redemption_rows = []
rid = 950000
months_all = pd.period_range("2026-01", "2026-07", freq="M")
for u in activated_users:
    t0 = first_investment_time[u].to_period("M")
    risk = user_risk[u]
    eligible_months = [m for m in months_all if m >= t0]
    for m in eligible_months:
        m_str = str(m)
        correction_weight = CORRECTION_MONTHS.get(m_str, 0.0)
        redeem_p = BASELINE_REDEMPTION_RATE + CORRECTION_REDEMPTION_LIFT[risk] * correction_weight
        if rng.random() < redeem_p:
            prod = first_product_map[u]
            amt = float(np.clip(rng.lognormal(np.log(4500), 0.7), 300, 150000))
            redemption_rows.append({
                "redemption_id": rid, "user_id": u,
                "redemption_date": (pd.Period(m_str, "M").to_timestamp() + timedelta(days=int(rng.integers(0, 27)))).date(),
                "product_type": prod, "amount_inr": round(amt, 2),
                "is_correction_period": m_str in CORRECTION_MONTHS,
            })
            rid += 1

redemptions = pd.DataFrame(redemption_rows)

# ---------------------------------------------------------------------------
# WRITE
# ---------------------------------------------------------------------------
users.to_csv(OUT / "users.csv", index=False)
funnel.to_csv(OUT / "onboarding_events.csv", index=False)
investments.to_csv(OUT / "investments.csv", index=False)
sip_status.to_csv(OUT / "sip_monthly_status.csv", index=False)
redemptions.to_csv(OUT / "redemptions.csv", index=False)

print(f"onboarding_events: {len(funnel):,} rows")
print(f"investments: {len(investments):,} rows")
print(f"sip_monthly_status: {len(sip_status):,} rows")
print(f"redemptions: {len(redemptions):,} rows")
print(f"total invested (first + expansion investments): Rs {investments.amount_inr.sum():,.0f}")
