# Men's College Basketball Pipeline and Prediction Model

An end-to-end NCAA men's college basketball data pipeline and point-spread prediction project. Python ingestion scripts pull game results, team ratings, four-factor statistics, and betting lines from the College Basketball Data API and load them into BigQuery. SQL transforms the raw data into point-in-time matchup features, which are used by a BigQuery ML linear regression model to predict home-team margin of victory.

The project also includes automated prediction tracking, performance reporting, and an experimental AI-assisted player availability research workflow.

## Pipeline overview

The pipeline is split across independent Python ingestion scripts, with GitHub Actions handling scheduled runs:

| Data source | Ingestion | Description |
|---|---|---|
| Games | Daily | Final scores, ELO ratings, home/away context, conferences, and game status |
| Betting lines | Daily | Spreads, moneylines, and over/unders, flattened from the API's nested lines structure |
| Team ratings | Twice weekly | Adjusted offensive, defensive, and net ratings, stored with ingestion timestamps |
| Team stats | Twice weekly | Four-factor statistics: effective field goal percentage, free throw rate, offensive rebounding rate, and turnover ratio |

Each source is ingested independently so that the pipeline can refresh on different schedules without requiring a full reload.

## Feature engineering

The main data challenge is making sure every historical matchup only uses information that would have been available before the game was played. Joining games to the latest team ratings or statistics without accounting for when those values were ingested would introduce future data leakage.

The SQL transformation in `stats_and_matchups.sql` uses a point-in-time join pattern. For each matchup, it identifies the latest ratings and team-stat snapshots ingested on or before the game date, then joins those snapshots to the game.

The resulting matchup dataset includes features such as:

- Home and away adjusted offensive, defensive, and net ratings
- Net rating and ELO differentials
- Four-factor differentials: effective field goal percentage, free throw rate, offensive rebounding rate, and turnover ratio
- Conference classification and conference-type differential
- Days of rest and recent rolling win percentage
- Home-court indicator
- Vegas spread

This approach allows the training data to reflect the information available at the time of each game rather than relying on end-of-season statistics.

## Prediction model

A linear regression model is trained in BigQuery ML to predict the home team's margin of victory. The training query excludes games with margins greater than 35 points to limit the influence of extreme blowouts.

The model is evaluated against actual game results after games are completed. Historical predictions and outcomes are retained so performance can be reviewed over time, rather than evaluating the model only on the data used to train it.

Two SQL workflows support the prediction process:

- `ml_model.sql` trains the model and generates predictions.
- `weekly_predictions.sql` creates a rolling seven-day view of upcoming matchups and model predictions.

## Automation and monitoring

GitHub Actions automates the ingestion scripts using scheduled workflows. Google Cloud authentication uses Workload Identity Federation, so service account key files do not need to be stored in the repository.

The project also includes a performance notification script that queries completed predictions in BigQuery and sends a daily summary through ntfy. A Looker Studio dashboard provides a view of current-season predictions and performance.

[View the current-season prediction dashboard](https://datastudio.google.com/reporting/bfc031e1-ad85-4daa-9521-8fd2e26a3e90)

## AI-assisted player availability research

An additional workflow explores using AI and web search to research player availability for the day's matchups. It checks for reported injuries and uncertain availability among meaningful rotation players, then writes team-level flags to BigQuery.

The flags are intended to identify games that warrant additional review. They are a due-diligence aid, not an automatic prediction adjustment or a substitute for evaluating the underlying reports.

## Repository files

| File | Description |
|---|---|
| `ingest_games.py` | Pulls game results and team/game context from the API into BigQuery |
| `ingest_team_ratings.py` | Pulls adjusted team ratings and appends timestamped snapshots |
| `ingest_team_stats.py` | Pulls four-factor team statistics and appends timestamped snapshots |
| `ingest_betting_lines.py` | Pulls betting lines and flattens the nested API response |
| `stats_and_matchups.sql` | Builds the game dataset and performs point-in-time feature engineering |
| `ml_model.sql` | Trains the BigQuery ML regression model and generates predictions |
| `weekly_predictions.sql` | Builds the rolling seven-day prediction dataset |
| `historical_prediction_performance.sql` | Compares pregame predictions with actual results after games are completed |
| `ai_injuries_reingest.py` | Experimental AI-assisted player availability research and BigQuery flag output |
| `performance_notification.py` | Queries recent model performance and sends a notification through ntfy |
| `requirements.txt` | Python dependencies for the ingestion and automation scripts |
| `automation_files/` | GitHub Actions workflow definitions for scheduled jobs |

## Tools

Python, SQL, BigQuery, BigQuery ML, pandas, College Basketball Data API, GitHub Actions, Google Cloud Workload Identity Federation, Looker Studio, ntfy
