-- arrival_01.sql — EXPLORATORY (docs/EXPLORATORY.md E1), post-result.
-- Mean and max reduced NEWS in hours 0-2, fast vs stable.
WITH p AS (
  SELECT n.stay_id, o.label,
         AVG(n.news) AS news_mean, MAX(n.news) AS news_max
  FROM `project-688c444c-3632-4faa-a13.missh.news_hourly_cal` n
  JOIN `project-688c444c-3632-4faa-a13.missh.outcome_cal` o USING (stay_id)
  WHERE n.hour_idx <= 2 AND n.n_items >= 3
    AND o.label IN ('stable', 'escalated_hyperacute')
  GROUP BY n.stay_id, o.label
)
SELECT label, COUNT(*) AS patients,
  APPROX_QUANTILES(news_mean, 4)[OFFSET(1)] AS news_q25,
  APPROX_QUANTILES(news_mean, 4)[OFFSET(2)] AS news_median,
  APPROX_QUANTILES(news_mean, 4)[OFFSET(3)] AS news_q75,
  ROUND(COUNTIF(news_max >= 5) / COUNT(*), 3) AS share_news5_any,
  ROUND(COUNTIF(news_max >= 7) / COUNT(*), 3) AS share_news7_any
FROM p GROUP BY label
