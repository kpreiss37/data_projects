CREATE OR REPLACE MODEL `mbb.rating_regression`
OPTIONS (
model_type='linear_reg',
input_label_cols=['home_team_margin']
) AS
SELECT
home_team_margin,
(PREDICTION FEATURES)
FROM
`PROJECT.DATASET.games_rated`
WHERE 1=1
AND abs(home_team_margin) <= 35
AND status = 'final'
;

