# Product Thinking

## The Business Problem
Nivesh monetizes on assets under management and transaction volume, both
of which depend on getting users to (1) actually make a first investment
after signing up, and (2) keep investing consistently rather than pausing
or redeeming at the first sign of market volatility. Both of these are
genuinely harder problems for an investing app than for most consumer
apps — the product is asking people to commit money under regulatory
constraints (KYC) and psychological pressure (loss aversion), not just to
tap a button.

## Why Two Fairly Different Analyses Sit in One Project
The onboarding funnel and the market-correction study look at completely
different time horizons — one is about the first hour/day of a user's
relationship with the app, the other is about behavior months in, under
stress. They belong together because they're the same underlying business
risk viewed at two different points: lose users at signup because of slow
KYC, or lose their invested capital and recurring SIPs later because of
poor volatility communication. A Product Analyst working on retention here
needs both halves of the picture.

## Hypotheses
- **H1: KYC is a major bottleneck, but the fix isn't the same as a typical
  onboarding-friction fix.** → **Confirmed, with a twist.** PAN/KYC
  approval only drops conversion by about 12pp (88% step conversion) — not
  catastrophic — but it takes a median of 25 hours and a p90 of 84 hours
  to actually clear, which is a genuinely different problem (users waiting,
  possibly losing momentum/interest during the wait) than a UX drop-off.
- **H2: Influencer/content-driven signups convert better than paid ads,
  reflecting pre-educated intent.** → **Confirmed.** 53.4% activation vs.
  24.5% for paid ads — more than double.
- **H3: Conservative investors will react more strongly to a market
  correction than aggressive investors (classic loss-aversion behavior).**
  → **Confirmed, and statistically significant.** SIP stoppage rate rose
  +17.1pp for Conservative investors during the correction month (p<0.0001)
  vs. only +1.1pp for Aggressive investors (not statistically significant,
  p=0.36) — Aggressive investors genuinely didn't change behavior in a way
  distinguishable from normal month-to-month noise.
- **H4: Risk tolerance also predicts product diversification speed, not
  just correction-period reactions.** → **Confirmed.** Aggressive investors
  expand into a 2nd product type at 45.7%, nearly double Conservative
  investors at 22.9% — the same underlying trait (risk tolerance) showing
  up in both a stress scenario and an ordinary growth metric.

## North Star Metric
**Active Investing Relationships** — users with at least one Active SIP or
a transaction (investment or redemption net-positive) in the trailing 30
days. Chosen over AUM alone because AUM can be propped up by a small number
of large investors while the broader base quietly disengages — Active
Investing Relationships tracks breadth of engagement, which is what
protects the business against concentration risk on both AUM and revenue.

### Input Metrics
- Signup → first investment activation rate (funnel)
- PAN/KYC time-to-approve (a distinct lever from conversion rate)
- SIP stoppage rate, overall and by risk profile
- Product expansion rate

### Output Metrics
- Active Investing Relationships — North Star
- Total AUM
- SIP stoppage ratio during volatility events specifically (a leading
  indicator of AUM risk, not just a lagging retention number)

## What I'd Do Next
- **Set explicit expectations on KYC timing** — a simple "your PAN
  verification typically takes 24–48 hours, we'll notify you" message at
  the point of submission could meaningfully reduce the drop-off between
  KYC submission and bank linking, since users currently have no signal
  for how long to wait.
- **Build a volatility-specific communication flow for Conservative-profile
  users specifically** — since the reaction is concentrated and
  statistically confirmed in that segment, a targeted "here's what a
  correction means for a long-term SIP, don't panic-sell" nudge (timed to
  actual volatility, not blanket-sent) is a much more efficient
  intervention than an app-wide banner.
- **Use first-product placement deliberately** — Direct Stocks and ETF as
  entry points correlate with the highest expansion rates; worth testing
  whether *steering* more new users toward these products (vs. the current
  default-to-Equity-MF pattern) causally increases expansion, rather than
  just correlating with users who were already going to diversify anyway.
- **Watch Aggressive-investor product transitions as a "what's next"
  signal** for the whole base — since this segment already diversifies
  fastest, their most common 2nd-product choices are a reasonable
  hypothesis for what other segments might respond to if nudged.
