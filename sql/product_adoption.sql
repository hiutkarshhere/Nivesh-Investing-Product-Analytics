-- product_adoption.sql
-- Product expansion rate by first product and by risk profile, matches
-- scripts/05_product_adoption_mix.py

WITH first_product AS (
  SELECT user_id, product_type AS first_product
  FROM (
    SELECT user_id, product_type,
           ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY investment_date) AS rn
    FROM `YOUR_GCP_PROJECT_ID.nivesh_analytics.investments`
  )
  WHERE rn = 1
),
product_counts AS (
  SELECT user_id, COUNT(DISTINCT product_type) AS n_products
  FROM `YOUR_GCP_PROJECT_ID.nivesh_analytics.investments`
  GROUP BY user_id
)
SELECT
  fp.first_product,
  COUNT(*) AS users,
  ROUND(COUNTIF(pc.n_products >= 2) / COUNT(*) * 100, 1) AS expansion_rate_pct
FROM first_product fp
JOIN product_counts pc USING (user_id)
GROUP BY fp.first_product
ORDER BY expansion_rate_pct DESC;

-- expansion rate by risk profile
SELECT
  u.risk_profile,
  COUNT(*) AS users,
  ROUND(COUNTIF(pc.n_products >= 2) / COUNT(*) * 100, 1) AS expansion_rate_pct
FROM `YOUR_GCP_PROJECT_ID.nivesh_analytics.users` u
JOIN (
  SELECT user_id, COUNT(DISTINCT product_type) AS n_products
  FROM `YOUR_GCP_PROJECT_ID.nivesh_analytics.investments`
  GROUP BY user_id
) pc USING (user_id)
GROUP BY u.risk_profile
ORDER BY expansion_rate_pct DESC;
