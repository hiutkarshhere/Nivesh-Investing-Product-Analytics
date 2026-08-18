# Assumptions Behind the Data

Same reasoning as the rest of this portfolio series: no public dataset
covers investing-app-level onboarding, SIP behavior, and redemption
patterns at the granularity a Product Analyst would work with internally,
so this is a documented simulation.

## The Market Correction Is Not Real Data
This is the most important assumption to state up front. `sip_monthly_status.csv`
and `redemptions.csv` model a hypothetical market correction in May 2026 —
a scenario built specifically to study how investor behavior might differ
by risk profile during volatility. **This is not real NSE/BSE/Nifty data,
and nothing in this project should be cited as an actual 2026 market
event.** A model built to answer "how would investors likely react" doesn't
need real market data to be a legitimate analytical exercise — the point is
the analytical method (event study, two-proportion z-test, segmentation by
risk profile), which would be applied to real market data exactly the same
way if this were running against a live warehouse.

## Footprint
- 9,600 users signed up Jan–May 2026, ~1,650–2,240/month (not a smooth ramp)
- 3,910 activated (made a first investment) — 40.7% overall
- Risk profile split: 30% Conservative / 45% Moderate / 25% Aggressive,
  assigned via the mandatory risk-assessment step every Indian investing
  app requires before allowing transactions
- Acquisition channels include "Influencer/Content" (20% of signups) —
  reflecting a real, well-documented channel for Indian fintech/investing
  apps ("finfluencer" marketing), not an invented category

## Onboarding Funnel
| Stage | Base conversion |
|---|---|
| Signup → Mobile OTP Verified | 91% |
| → PAN/KYC Submitted | 84% |
| → PAN/KYC Approved | 88% |
| → Risk Assessment Completed | 92% |
| → Bank Account Linked | 90% |
| → First Investment Made | 68% |

**The PAN/KYC approval step is modeled with a genuine multi-day delay**
(exponential distribution, mean ~36 hours, long tail out to several days) —
unlike every other step in this funnel, and unlike the KYC steps in the
other fintech-adjacent projects in this series, which are same-day. This
reflects a real, well-known friction point in Indian investing apps: PAN
verification against NSDL/CDSL records is a regulatory dependency outside
the app's direct control, so it needs to be measured as a *time-to-approve*
problem (progress messaging, expectation-setting) rather than purely as a
conversion-rate problem (which would suggest a UX fix instead).

Channel modifiers follow the same pattern used elsewhere in this series
(Referral +3pp, Influencer/Content +5pp, Paid Ads −6pp per stage) — the
Influencer/Content channel converting best reflects that content-driven
leads arrive pre-educated about investing basics, unlike a cold ad click.

## SIP Behavior & the Correction Response
Baseline monthly SIP pause rate: 4.0%, cancel rate: 1.8% — small, steady
natural attrition. During the simulated correction (May 2026, with a
lingering effect into June), these rates are elevated by risk profile:

| Risk Profile | Pause Rate Lift | Cancel Rate Lift |
|---|---:|---:|
| Conservative | +10.0pp | +4.5pp |
| Moderate | +4.5pp | +1.8pp |
| Aggressive | +1.2pp | +0.4pp |

This reflects a well-established behavioral finance pattern — loss-averse
investors (who by definition selected a Conservative risk profile) react
more strongly to volatility than risk-tolerant ones, often to their own
long-term detriment (selling into a dip locks in losses that a "stay the
course" investor wouldn't realize). The redemption-rate lifts follow the
same by-risk-profile pattern for the same reason.

## Product Mix
First-investment product split skews toward Mutual Fund - Equity (48%),
consistent with how investing apps typically default new users toward
diversified equity funds as a "starter" product, rather than direct
stocks or higher-complexity instruments. Product expansion probability
(picking up a 2nd distinct product type) varies by risk profile
(Conservative 22%, Moderate 34%, Aggressive 46%) for the same underlying
behavioral reason as the correction response — risk tolerance and
willingness to diversify/experiment are correlated traits, not independent
random draws.

## What This Doesn't Claim
Nivesh isn't a real company and none of these figures are Groww,
Zerodha, Kuvera, or any other real platform's actual numbers, funnel
conversion rates, or user behavior. It's a transparent simulation built to
demonstrate KYC-heavy onboarding analysis, SIP-specific retention (the
AMFI "stoppage ratio" concept), a behavioral event study with a proper
significance test, and product-adoption analysis — the way it'd actually
be done against a live investing-app warehouse.
