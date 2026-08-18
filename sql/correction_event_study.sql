-- correction_event_study.sql
-- Baseline vs correction-month SIP stoppage rate by risk profile. The
-- significance test itself (two-proportion z-test) is done in Python
-- (scripts/04_market_correction_behavior.py) since BigQuery Standard SQL
-- has no native z-test function -- same split as the diff-in-diff query in
-- project 3: SQL for the aggregation, Python/scipy for the test.

WITH tagged AS (
  SELECT
    risk_profile,
    status,
    CASE
      WHEN month IN ('2026-02', '2026-03', '2026-04') THEN 'baseline'
      WHEN month = '2026-05' THEN 'correction'
    END AS period
  FROM `YOUR_GCP_PROJECT_ID.nivesh_analytics.sip_monthly_status`
  WHERE month IN ('2026-02', '2026-03', '2026-04', '2026-05')
)
SELECT
  risk_profile,
  period,
  COUNTIF(status IN ('Paused', 'Cancelled')) AS stopped,
  COUNT(*) AS total,
  ROUND(COUNTIF(status IN ('Paused', 'Cancelled')) / COUNT(*) * 100, 2) AS stoppage_rate_pct
FROM tagged
WHERE period IS NOT NULL
GROUP BY risk_profile, period
ORDER BY risk_profile, period;
