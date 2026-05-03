CREATE OR REPLACE TABLE `project.dataset.2025games_rated` AS


WITH deduped AS (
   SELECT
       id,
       status,
       DATE(DATETIME(TIMESTAMP(startdate), 'America/New_York')) AS start_date,
       CASE
         WHEN neutralsite = FALSE THEN 1
         ELSE 0
       END as home_game,
       hometeamid AS home_team_id,
       hometeam AS home_team,
       homepoints AS home_points,
       CAST(hometeamelostart AS INT64) AS home_elo,
       awayteamid AS away_team_id,
       awayteam AS away_team,
       awaypoints AS away_points,
       CAST(awayteamelostart AS INT64) AS away_elo,
       homepoints - awaypoints AS home_team_margin,
       CAST(hometeamelostart AS INT64) - CAST(awayteamelostart AS INT64) AS home_elo_diff,
       ROW_NUMBER() OVER (PARTITION BY id) AS game_row_num
   FROM `project.dataset.games2025`
   WHERE status NOT IN ('postponed', 'cancelled')
)


, game_rating_dates AS (
   SELECT
       g.id AS game_id,
       g.home_team_id,
       g.away_team_id,
       g.start_date,
       MAX(CASE WHEN r.teamid = g.home_team_id AND DATE(r.ingested_at) <= DATE(g.start_date) THEN DATE(r.ingested_at) END) AS home_rating_date,
       MAX(CASE WHEN r.teamid = g.away_team_id AND DATE(r.ingested_at) <= DATE(g.start_date) THEN DATE(r.ingested_at) END) AS away_rating_date
   FROM deduped g
   CROSS JOIN (SELECT DISTINCT teamid, ingested_at FROM `project.dataset.ratings2025`) r
   GROUP BY g.id, g.home_team_id, g.away_team_id, g.start_date
)


, game_stats_dates AS (
   SELECT
       g.id AS game_id,
       g.home_team_id,
       g.away_team_id,
       g.start_date,
       MAX(CASE WHEN r.teamid = g.home_team_id AND DATE(r.ingested_at) <= DATE(g.start_date) THEN DATE(r.ingested_at) END) AS home_stats_date,
       MAX(CASE WHEN r.teamid = g.away_team_id AND DATE(r.ingested_at) <= DATE(g.start_date) THEN DATE(r.ingested_at) END) AS away_stats_date
   FROM deduped g
   CROSS JOIN (SELECT DISTINCT teamid, ingested_at FROM `project.dataset.team_stats2025`) r
   GROUP BY g.id, g.home_team_id, g.away_team_id, g.start_date
)


, home_rating AS (
   SELECT
       g.*,
       r.offensiverating AS home_off_rat,
       r.defensiverating AS home_def_rat,
       r.netrating AS home_net_rat
   FROM deduped g
   LEFT JOIN game_rating_dates grd ON g.id = grd.game_id
   LEFT JOIN `project.dataset.ratings2025` r
       ON r.teamid = g.home_team_id
       AND DATE(r.ingested_at) = grd.home_rating_date
)


, away_rating AS (
   SELECT
       g.*,
       r.offensiverating AS away_off_rat,
       r.defensiverating AS away_def_rat,
       r.netrating AS away_net_rat
   FROM home_rating g
   LEFT JOIN game_rating_dates grd ON g.id = grd.game_id
   LEFT JOIN `project.dataset.ratings2025` r
       ON r.teamid = g.away_team_id
       AND DATE(r.ingested_at) = grd.away_rating_date
)


, home_stats AS (
   SELECT
   g.*,
   r.teamStats_fourFactors_effectiveFieldGoalPct home_effectiveFieldGoalPct,
   r.teamStats_fourFactors_freeThrowRate home_freeThrowRate,
   r.teamStats_fourFactors_offensiveReboundPct home_offensiveReboundPct,
   r.teamStats_fourFactors_turnoverRatio home_turnoverRatio
   FROM away_rating g
   LEFT JOIN game_stats_dates grd ON g.id = grd.game_id
   LEFT JOIN `project.dataset.team_stats2025` r
       ON r.teamid = g.home_team_id
       AND DATE(r.ingested_at) = grd.home_stats_date
)


, away_stats AS (
   SELECT
   g.*,
   r.teamStats_fourFactors_effectiveFieldGoalPct away_effectiveFieldGoalPct,
   r.teamStats_fourFactors_freeThrowRate away_freeThrowRate,
   r.teamStats_fourFactors_offensiveReboundPct away_offensiveReboundPct,
   r.teamStats_fourFactors_turnoverRatio away_turnoverRatio
   FROM home_stats g
   LEFT JOIN game_stats_dates grd ON g.id = grd.game_id
   LEFT JOIN `project.dataset.team_stats2025` r
       ON r.teamid = g.away_team_id
       AND DATE(r.ingested_at) = grd.away_stats_date
)


, lines_dedupe AS (
   SELECT
       gameid,
       spread,
       ROW_NUMBER() OVER (PARTITION BY gameid ORDER BY gameid) AS row_num
   FROM `project.dataset.lines2025`
)


, team_games AS (
   SELECT
       id AS game_id,
       start_date,
       home_team_id AS team_id,
       CASE WHEN home_points > away_points THEN 1 ELSE 0 END AS win
   FROM deduped


   UNION ALL


   SELECT
       id AS game_id,
       start_date,
       away_team_id AS team_id,
       CASE WHEN away_points > home_points THEN 1 ELSE 0 END AS win
   FROM deduped
)


, team_rolling AS (
   SELECT
       game_id,
       team_id,
       start_date,
       -- Days of rest: days since their previous game
       DATE_DIFF(
           start_date,
           LAG(start_date) OVER (PARTITION BY team_id ORDER BY start_date),
           DAY
       ) AS days_rest,
       -- Wins in last 5 games
       AVG(win) OVER (
           PARTITION BY team_id
           ORDER BY start_date
           ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
       ) AS win_pct_last5
   FROM team_games
)




, home_form AS (
   SELECT * FROM team_rolling
)
, away_form AS (
   SELECT * FROM team_rolling
)


SELECT
   r.*,
   l.spread,
   home_net_rat - away_net_rat AS home_net_diff,
   hf.days_rest AS home_days_rest,
   af.days_rest AS away_days_rest,
   hf.win_pct_last5 AS home_win_pct_last5,
   af.win_pct_last5 AS away_win_pct_last5,
   hf.days_rest - af.days_rest AS rest_diff,
   hf.win_pct_last5 - af.win_pct_last5 AS form_diff
FROM away_stats r
LEFT JOIN lines_dedupe l
   ON r.id = l.gameid
   AND l.row_num = 1
LEFT JOIN home_form hf
   ON r.id = hf.game_id
   AND r.home_team_id = hf.team_id
LEFT JOIN away_form af
   ON r.id = af.game_id
   AND r.away_team_id = af.team_id
WHERE r.game_row_num = 1
/*AND home_off_rat IS NOT NULL
AND home_def_rat IS NOT NULL
AND away_off_rat IS NOT NULL
AND away_def_rat IS NOT NULL*/







