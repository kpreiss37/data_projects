CREATE OR REPLACE TABLE `PROJECT.DATASET.client_touchpaths` AS

WITH touches as (
WITH unioned AS (
  SELECT 
  event_date,
  event_name,
  user_pseudo_id,
  collected_traffic_source,
  event_params
  FROM `PROJECT.DATASET.events_*` --GA4 bulk export dataset
  WHERE _TABLE_SUFFIX BETWEEN '20250101' AND '20260205'
)

,params AS (
  SELECT
    event_date,
    event_name,
    user_pseudo_id,
    CASE 
      WHEN collected_traffic_source.gclid IS NOT NULL THEN 'google'
      ELSE collected_traffic_source.manual_source
    END AS source,
    CASE 
      WHEN collected_traffic_source.gclid IS NOT NULL THEN 'cpc'
      ELSE collected_traffic_source.manual_medium
    END AS medium,
    collected_traffic_source.manual_campaign_name AS campaign,
    collected_traffic_source.manual_term AS keyword,
    collected_traffic_source.manual_content AS content,
    collected_traffic_source.gclid AS gclid
  FROM unioned,
  UNNEST(event_params) ep
  WHERE 1=1
  AND event_name = 'session_start'
)

SELECT
  user_pseudo_id,
      event_date,
      source,
      medium,
      campaign,
      keyword,
      content,
      gclid
FROM params
),

callrail AS (
  WITH unioned AS (
  SELECT 
  event_name,
  user_pseudo_id,
  event_params
  FROM `PROJECT.DATASET.events_*` --GA4 bulk export dataset
  WHERE _TABLE_SUFFIX BETWEEN '20250101' AND '20260205' 
  AND event_name LIKE "%phone_call"
)

,params AS (
  SELECT
    event_date,
    event_name,
    user_pseudo_id,
    ep.value.string_value AS callrail_id
  FROM unioned,
  UNNEST(event_params) ep
  WHERE 1=1
  AND event_name LIKE "%phone_call"
  AND ep.key = 'call_id'
)
select 
user_pseudo_id,
callrail_id,
c.id,
RIGHT(REGEXP_REPLACE(c.customer_phone_number, r'[\s\(\)\-\+]', ''), 10) customer_phone_number
FROM params p
LEFT JOIN PROJECT.DATASET.callrail_calls c
ON p.callrail_id = c.id
)

, form_submissions AS (
SELECT
RIGHT(REGEXP_REPLACE(phone_number, r'[\s\(\)\-\+]', ''), 10) AS phone_number,
email,
ga4_user_id,
FROM PROJECT.DATASET.form_leads
)

SELECT
t.user_pseudo_id,
  ARRAY_AGG(
    STRUCT(
      event_date,
      source,
      medium,
      campaign,
      keyword,
      content,
      gclid
    )
    ORDER BY event_date
  ) AS touchpoint_path,
ARRAY_AGG(DISTINCT c.customer_phone_number IGNORE NULLS) AS phone_numbers,
ARRAY_AGG(DISTINCT LOWER(f.email) IGNORE NULLS) AS emails
FROM touches t
LEFT JOIN callrail c
ON t.user_pseudo_id = c.user_pseudo_id
LEFT JOIN form_submissions f
ON t.user_pseudo_id = f.ga4_user_id
group by 1

;

CREATE OR REPLACE TABLE `PROJECT.DATASET.multitouch_matched` AS

WITH cleaned_invoices AS (
  SELECT
  invoice_id,
  invoice_date,
  total,
  RIGHT(REGEXP_REPLACE(customer_phone, r'[\s\(\)\-\+]', ''), 10) AS customer_phone,
  LOWER(customer_email) customer_email
  FROM PROJECT.DATASET.client_invoices
  WHERE total > 0
)

SELECT
t.*,
i.invoice_date,
i.total,
1 AS sale_flag
FROM PROJECT.DATASET.client_touchpaths t
LEFT JOIN cleaned_invoices i
ON (
  (i.customer_phone IN UNNEST(t.phone_numbers) AND i.customer_phone != '')
  OR
  (i.customer_email IN UNNEST(t.emails) AND i.customer_email != '')
)
WHERE i.invoice_date IS NULL OR t.event_date < i.invoice_date

;

CREATE OR REPLACE TABLE `PROJECT.DATASET.multitouch_attributed` AS 

WITH unnested AS (
  SELECT
    t.user_pseudo_id,
    t.invoice_date,
    t.total,
    touch,
    touch.event_date AS touch_date,
    DATE_DIFF(t.invoice_date, touch.event_date, DAY) AS days_before_conversion,
    ROW_NUMBER() OVER (PARTITION BY t.user_pseudo_id ORDER BY touch.event_date) AS touch_number
  FROM `PROJECT.DATASET.multitouch_matched` t,
  UNNEST(t.touchpoint_path) AS touch
)
, scored AS (
  SELECT
    *,
    EXP(-0.1 * days_before_conversion) AS raw_weight --The multiplier is a tunable decay rate
  FROM unnested
)
, normalized AS (
  SELECT
    *,
    raw_weight / SUM(raw_weight) OVER (PARTITION BY user_pseudo_id) AS attribution_credit
  FROM scored
)
SELECT
  user_pseudo_id,
  touch.source,
  touch.medium,
  touch.campaign,
  SUM(total * attribution_credit) AS attributed_revenue
FROM normalized
GROUP BY 1, 2, 3, 4
