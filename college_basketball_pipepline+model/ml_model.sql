CREATE OR REPLACE MODEL `mbb.rating_regression`
OPTIONS (
model_type='linear_reg',
input_label_cols=['home_team_margin']
) AS
SELECT
    -- Team strength features
    team_strength_features,

    -- Game context
    game_context_features,

    -- Recent performance
    form_features,

    -- Efficiency metrics
    efficiency_features,

    home_team_margin
FROM
`PROJECT.DATASET.games_rated`
WHERE 1=1
AND abs(home_team_margin) <= 35
AND status = 'final'
;

