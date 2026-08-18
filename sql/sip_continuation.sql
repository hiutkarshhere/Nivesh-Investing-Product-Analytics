-- sip_continuation.sql
-- SIP cohort continuation matrix + stoppage ratio by risk profile, matches
-- scripts/03_sip_continuation_retention.py

WITH sip_with_cohort AS (
  SELECT
    s.*,
    MIN(PARSE_DATE('%Y-%m-%d', CONCAT(month, '-01'))) OVER (PARTITION BY sip_id) AS cohort_start
  FROM `YOUR_GCP_PROJECT_ID.nivesh_analytics.sip_monthly_status` s
),
indexed AS (
  SELECT
    *,
    DATE_DIFF(PARSE_DATE('%Y-%m-%d', CONCAT(month, '-01')), cohort_start, MONTH) AS month_index
  FROM sip_with_cohort
),
cohort_sizes AS (
  SELECT cohort_start, COUNT(DISTINCT sip_id) AS cohort_size
  FROM indexed WHERE month_index = 0
  GROUP BY cohort_start
)
SELECT
  i.cohort_start,
  i.month_index,
  COUNTIF(i.status = 'Active') AS active_sips,
  cs.cohort_size,
  ROUND(COUNTIF(i.status = 'Active') / cs.cohort_size * 100, 1) AS continuation_pct
FROM indexed i
JOIN cohort_sizes cs USING (cohort_start)
GROUP BY i.cohort_start, i.month_index, cs.cohort_size
ORDER BY i.cohort_start, i.month_index;

-- stoppage ratio by risk profile for a given month (AMFI-style metric)
SELECT
  risk_profile,
  COUNTIF(status IN ('Paused', 'Cancelled')) AS stopped,
  COUNT(*) AS total,
  ROUND(COUNTIF(status IN ('Paused', 'Cancelled')) / COUNT(*) * 100, 1) AS stoppage_ratio_pct
FROM `YOUR_GCP_PROJECT_ID.nivesh_analytics.sip_monthly_status`
WHERE month = '2026-06'
GROUP BY risk_profile
ORDER BY stoppage_ratio_pct DESC;
