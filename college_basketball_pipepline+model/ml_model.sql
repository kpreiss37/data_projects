CREATE OR REPLACE MODEL `mbb.rating_regression`
OPTIONS (
model_type='linear_reg',
input_label_cols=['home_team_margin']
) AS
SELECT
home_net_diff,
home_game,
rest_diff,
form_diff,
home_team_margin,
fg_perc_diff,
ft_rate_diff,
orb_perc_diff,
to_ratio_diff
FROM
`PROJECT.DATASET.games_rated`
WHERE 1=1
AND abs(home_team_margin) <= 35
AND status = 'final'
;

