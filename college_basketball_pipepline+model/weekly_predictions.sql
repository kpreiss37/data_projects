CREATE OR REPLACE TABLE `project-bf3ebdef-3dea-4c35-a21.mbb.live_week_predictions` AS 

SELECT
start_date,
home_team,
away_team,
CAST(predicted_home_team_margin AS FLOAT64) predicted_home_team_spread,
CAST(spread as FLOAT64) spread,
home_team_margin,
CASE
    WHEN spread IS NULL THEN 0
    WHEN ABS(
        predicted_home_team_margin * -1
        - CAST(spread AS FLOAT64)
    ) >= 3 THEN 1
    ELSE 0
END AS place_bet,
CASE
    WHEN predicted_home_team_margin*-1 < CAST(spread AS FLOAT64)
        THEN CONCAT(home_team, ' ', CAST(spread AS STRING))
    WHEN predicted_home_team_margin*-1 > CAST(spread AS FLOAT64)
        THEN CONCAT(away_team, ' ', CAST(CAST(spread AS FLOAT64) * -1 AS STRING))
END AS bet
FROM ML.PREDICT(MODEL `mbb.rating_regression`,
   (
       SELECT
       home_net_diff
       home_game,
       rest_diff,
       form_diff,
       home_team_margin,
       home_team,
       away_team,
       spread,
       start_date,
       fg_perc_diff,
       ft_rate_diff,
       orb_perc_diff,
       to_ratio_diff
       FROM `project-bf3ebdef-3dea-4c35-a21.mbb.all_games_rated`
       WHERE 1=1
       AND DATE_DIFF(start_date,CURRENT_DATE('America/New_York'), DAY) BETWEEN 0 and 7
   ))
