-- schema.sql
-- BigQuery Standard SQL. Same swap-the-project-ID convention as the rest
-- of this portfolio series.

CREATE SCHEMA IF NOT EXISTS `YOUR_GCP_PROJECT_ID.nivesh_analytics`;

CREATE OR REPLACE TABLE `YOUR_GCP_PROJECT_ID.nivesh_analytics.users` (
  user_id              STRING NOT NULL,
  signup_date          DATE NOT NULL,
  signup_month         STRING NOT NULL,
  acquisition_channel  STRING,
  city_tier            STRING,
  age_bracket          STRING,
  risk_profile         STRING   -- Conservative | Moderate | Aggressive
);

CREATE OR REPLACE TABLE `YOUR_GCP_PROJECT_ID.nivesh_analytics.onboarding_events` (
  user_id           STRING NOT NULL,
  event_name        STRING NOT NULL,  -- signup_started | mobile_otp_verified |
                                       -- pan_kyc_submitted | pan_kyc_approved |
                                       -- risk_assessment_completed | bank_account_linked |
                                       -- first_investment_made
  event_timestamp   DATETIME NOT NULL
);
-- pan_kyc_submitted -> pan_kyc_approved has a genuine multi-day gap (median
-- ~25h, p90 ~84h) representing real NSDL/CDSL-style regulatory verification
-- time, not just a conversion-rate drop. Worth measuring time-to-approve,
-- not just whether it happened -- see scripts/02_onboarding_funnel.py.

CREATE OR REPLACE TABLE `YOUR_GCP_PROJECT_ID.nivesh_analytics.investments` (
  investment_id     INT64 NOT NULL,
  user_id           STRING NOT NULL,
  investment_date   DATE NOT NULL,
  product_type      STRING,   -- Mutual Fund - Equity | Mutual Fund - Debt |
                               -- Mutual Fund - Hybrid | Direct Stocks | ETF
  investment_mode   STRING,   -- SIP | Lumpsum
  amount_inr        NUMERIC
);

CREATE OR REPLACE TABLE `YOUR_GCP_PROJECT_ID.nivesh_analytics.sip_monthly_status` (
  sip_id         INT64 NOT NULL,
  user_id        STRING NOT NULL,
  month          STRING NOT NULL,  -- 'YYYY-MM'
  risk_profile   STRING,
  status         STRING,   -- Active | Paused | Cancelled
  amount_inr     NUMERIC
);

CREATE OR REPLACE TABLE `YOUR_GCP_PROJECT_ID.nivesh_analytics.redemptions` (
  redemption_id         INT64 NOT NULL,
  user_id               STRING NOT NULL,
  redemption_date       DATE NOT NULL,
  product_type          STRING,
  amount_inr            NUMERIC,
  is_correction_period  BOOL
);
-- NOTE: the "correction period" (May 2026) referenced throughout this
-- dataset is a simulated hypothetical scenario built to study behavioral
-- response to volatility, not real market data. See docs/assumptions.md.

-- bq load --source_format=CSV --skip_leading_rows=1 YOUR_GCP_PROJECT_ID:nivesh_analytics.users data/raw/users.csv
-- bq load --source_format=CSV --skip_leading_rows=1 YOUR_GCP_PROJECT_ID:nivesh_analytics.onboarding_events data/raw/onboarding_events.csv
-- bq load --source_format=CSV --skip_leading_rows=1 YOUR_GCP_PROJECT_ID:nivesh_analytics.investments data/raw/investments.csv
-- bq load --source_format=CSV --skip_leading_rows=1 YOUR_GCP_PROJECT_ID:nivesh_analytics.sip_monthly_status data/raw/sip_monthly_status.csv
-- bq load --source_format=CSV --skip_leading_rows=1 YOUR_GCP_PROJECT_ID:nivesh_analytics.redemptions data/raw/redemptions.csv
