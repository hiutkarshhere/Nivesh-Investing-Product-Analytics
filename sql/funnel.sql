-- funnel.sql
-- Onboarding funnel + PAN/KYC time-to-approve, matches
-- scripts/02_onboarding_funnel.py

WITH stage_counts AS (
  SELECT event_name, COUNT(DISTINCT user_id) AS users_reached
  FROM `YOUR_GCP_PROJECT_ID.nivesh_analytics.onboarding_events`
  GROUP BY event_name
),
ordered AS (
  SELECT
    event_name, users_reached,
    CASE event_name
      WHEN 'signup_started' THEN 0 WHEN 'mobile_otp_verified' THEN 1
      WHEN 'pan_kyc_submitted' THEN 2 WHEN 'pan_kyc_approved' THEN 3
      WHEN 'risk_assessment_completed' THEN 4 WHEN 'bank_account_linked' THEN 5
      WHEN 'first_investment_made' THEN 6
    END AS stage_order
  FROM stage_counts
)
SELECT
  stage_order, event_name, users_reached,
  ROUND(users_reached / FIRST_VALUE(users_reached) OVER (ORDER BY stage_order) * 100, 2) AS pct_of_total,
  ROUND(users_reached / LAG(users_reached) OVER (ORDER BY stage_order) * 100, 2) AS step_conversion_pct
FROM ordered
ORDER BY stage_order;

-- PAN/KYC approval time distribution -- the step with a genuine multi-day
-- regulatory delay, not just a conversion drop
WITH submitted AS (
  SELECT user_id, event_timestamp AS submitted_at
  FROM `YOUR_GCP_PROJECT_ID.nivesh_analytics.onboarding_events`
  WHERE event_name = 'pan_kyc_submitted'
),
approved AS (
  SELECT user_id, event_timestamp AS approved_at
  FROM `YOUR_GCP_PROJECT_ID.nivesh_analytics.onboarding_events`
  WHERE event_name = 'pan_kyc_approved'
)
SELECT
  APPROX_QUANTILES(TIMESTAMP_DIFF(approved_at, submitted_at, MINUTE) / 60.0, 100)[OFFSET(50)] AS median_hours,
  APPROX_QUANTILES(TIMESTAMP_DIFF(approved_at, submitted_at, MINUTE) / 60.0, 100)[OFFSET(75)] AS p75_hours,
  APPROX_QUANTILES(TIMESTAMP_DIFF(approved_at, submitted_at, MINUTE) / 60.0, 100)[OFFSET(90)] AS p90_hours
FROM submitted JOIN approved USING (user_id);
