CREATE OR REPLACE MODEL `mbb.rating_regression`
OPTIONS (
model_type='linear_reg',
input_label_cols=['home_team_margin']
) AS
SELECT
home_net_diff
home_game,
rest_diff,
form_diff,
home_team_margin,
fg_perc_diff,
ft_rate_diff,
orb_perc_diff,
to_ratio_diff
FROM
`PROJECT.DATASET.2025games_rated`
WHERE 1=1
AND abs(home_team_margin) <= 35
AND home_elo != 1500
AND away_elo != 1500
AND status = 'final'
;




----------------------------------------------------------------------------------------------




SELECT
home_team,
away_team,
home_elo_diff,
predicted_home_team_margin*-1 predicted_home_team_spread,
spread,
home_team_margin,
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
      FROM `PROJECT.DATASET.2025games_rated`
  ))
WHERE start_date >= current_date()
ORDER BY start_date desc























