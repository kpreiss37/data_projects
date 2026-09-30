
INSERT INTO `project-bf3ebdef-3dea-4c35-a21.mbb.historical_predictions` (prediction_date,id,start_date,home_team, away_team, predicted_home_team_spread, spread, home_team_margin,place_bet,bet)

--CREATE OR REPLACE TABLE `project-bf3ebdef-3dea-4c35-a21.mbb.historical_predictions` AS 

SELECT
CURRENT_DATE('America/New_York') prediction_date,
id,
start_date,
home_team,
away_team,
predicted_home_team_margin*-1 predicted_home_team_spread,
CAST(spread AS FLOAT64) spread,
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
END AS bet,
FROM ML.PREDICT(MODEL `mbb.rating_regression`,
   (
       SELECT
       id,
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
       WHERE start_date = CURRENT_DATE('America/New_York')
   )) 

;
------------------------------------------------------------------------------------------------

CREATE OR REPLACE TABLE `project-bf3ebdef-3dea-4c35-a21.mbb.prediction performance` AS

SELECT
p.*,
g.home_points - g.away_points AS real_home_team_margin,
CASE
    WHEN g.home_points - g.away_points + spread = 0
        THEN 'PUSH'

    WHEN predicted_home_team_spread < spread
        AND g.home_points - g.away_points + spread > 0
        THEN 'WIN'

    WHEN predicted_home_team_spread > spread
        AND g.home_points - g.away_points + spread < 0
        THEN 'WIN'

    ELSE 'LOSS'
END AS bet_result
FROM `project-bf3ebdef-3dea-4c35-a21.mbb.historical_predictions` p
LEFT JOIN `project-bf3ebdef-3dea-4c35-a21.mbb.all_games` g
ON p.id = g.id
