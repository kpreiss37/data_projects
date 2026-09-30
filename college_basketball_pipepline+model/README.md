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

A linear regression model was trained in BigQuery ML (`ml_model.sql`) to predict the home team's margin of victory. Games with margins greater than 35 points were excluded from training to reduce noise.

This model was first made at the tail end of the 2025 season, but with limited historical data on ratings and team stats, the model achieved an R² of 0.29.

Since the end of the season, I've spent time making sure that the model will be fully automated for future years so the dataset can continuously grow. You can view this season's performance in this [Google Data Studio dashboard](https://datastudio.google.com/reporting/bfc031e1-ad85-4daa-9521-8fd2e26a3e90).

## Files

| File | Description |
|------|-------------|
| `ingest_games.py` | Pulls game results from the API and loads to BigQuery |
| `ingest_team_ratings.py` | Pulls adjusted ratings and appends with ingestion timestamp |
| `ingest_team_stats.py` | Pulls four-factor stats and appends with ingestion timestamp |
| `ingest_betting_lines.py` | Pulls betting lines and explodes nested structure into flat table |
| `stats_and_matchups.sql` | Point-in-time feature engineering and matchup assembly |
| `ml_model.sql` | BigQuery ML model training and prediction queries |
| `historical_prediction_performance.sql` | Takes the models prediction before the game is played and evaluates it against actual data the next day |
| `weekly_predictions.sql` | A rolling 7 day window of predictions from the model |
| `requirements.txt` | Libraries to be installed for automating scripts | 

## Tools

Python, BigQuery, SQL, BigQuery ML, College Basketball Data API, Google Data Studio
