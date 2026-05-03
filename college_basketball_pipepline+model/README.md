# Men's college basketball pipeline and prediction model

Built an end-to-end data pipeline ingesting from multiple College Basketball Data API endpoints into BigQuery, covering games, team ratings, four-factor stats, and betting lines, each on independent ingestion schedules.

## Pipeline overview

Four Python ingestion scripts pull from separate API endpoints and load into BigQuery:

- **Games** -- scores, ELO ratings, home/away context, and game status
- **Team ratings** -- adjusted offensive and defensive ratings, appended daily with an ingestion timestamp
- **Team stats** -- four-factor statistics (eFG%, free throw rate, offensive rebounding rate, turnover ratio), appended with ingestion timestamps
- **Betting lines** -- spreads, moneylines, and over/unders for each game, exploded from a nested lines array into a flat table

## Feature engineering

The core modeling challenge was temporal: each game needed to be joined to the most recent ratings and stats available before it was played, not season-end figures. A naive join would leak future data into the training set.

The solution was a point-in-time join pattern using ingestion timestamps. For each game, the pipeline identifies the latest ratings and stats snapshot with an ingestion date on or before the game date, then joins on that specific snapshot. This is implemented in `stats_and_matchups.sql`.

The final dataset includes:

- Adjusted net rating differential between home and away teams
- Four-factor differentials (eFG%, free throw rate, offensive rebounding %, turnover ratio)
- Days of rest for each team
- Rolling win percentage over the last five games
- Home court indicator
- Vegas spread

## Model

A linear regression model was trained in BigQuery ML (`ml_game_predictions.sql`) to predict the home team's margin of victory. Games with margins greater than 35 points and teams with default ELO ratings were excluded from training to reduce noise.

The model achieves an R² of 0.29. The main caveat is that the pipeline was completed late in the 2025 season, so historical rating snapshots were limited for earlier games. The ingestion layer is already designed to accumulate snapshots via append-only loads, so the point-in-time join logic will work as intended with a full season of data. The plan is to run it in full for 2026 and evaluate properly against the spread.

## Files

| File | Description |
|------|-------------|
| `ingest_games.py` | Pulls game results from the API and loads to BigQuery |
| `ingest_team_ratings.py` | Pulls adjusted ratings and appends with ingestion timestamp |
| `ingest_team_stats.py` | Pulls four-factor stats and appends with ingestion timestamp |
| `ingest_betting_lines.py` | Pulls betting lines and explodes nested structure into flat table |
| `stats_and_matchups.sql` | Point-in-time feature engineering and matchup assembly |
| `ml_game_predictions.sql` | BigQuery ML model training and prediction queries |

## Tools

Python, BigQuery, SQL, BigQuery ML, College Basketball Data API
