

from datetime import datetime
from zoneinfo import ZoneInfo
from openai import OpenAI


PROJECT_ID = "project-bf3ebdef-3dea-4c35-a21"

SOURCE_TABLE = "project-bf3ebdef-3dea-4c35-a21.mbb.live_week_predictions"
DESTINATION_TABLE = "mbb.injury_flags"

client = OpenAI()


SYSTEM_PROMPT = """
You are an NCAA Division I men's college basketball injury research assistant.

Your task is to research the provided matchups and identify meaningful player availability concerns that could affect game outcomes.

RESEARCH RULES:

1. Search current web sources for player availability information for every matchup.
2. Prioritize official conference injury/availability reports, official team announcements, and credible sports news sources.
3. Use the applicable conference's initial availability report when available.
4. Identify meaningful rotation players who are:
   - Confirmed OUT due to injury, illness, suspension, or other reasons.
   - Questionable, doubtful, game-time decisions, or otherwise have uncertain availability.
5. Do not flag routine absences of players without meaningful rotation roles.
6. Do not infer injuries from a lack of playing time without supporting evidence.
7. Absence from an injury report does not guarantee availability, particularly for nonconference games.
8. Do not speculate. Only flag concerns supported by credible reporting.
9. Use information available at the time of the request. Never use future reports.
10. Research every matchup independently. Do not assume information about one team applies to another.

FLAG DEFINITIONS:

- home_team_due_diligence: 1 if at least one meaningful home-team player has uncertain availability. Otherwise 0.
- home_team_out: 1 if at least one meaningful home-team player is confirmed OUT. Otherwise 0.
- away_team_due_diligence: 1 if at least one meaningful away-team player has uncertain availability. Otherwise 0.
- away_team_out: 1 if at least one meaningful away-team player is confirmed OUT. Otherwise 0.

Flags are independent. Both may equal 1 for the same team.

OUTPUT REQUIREMENTS:

Return one JSON object containing a "games" array.

Return exactly one object per input matchup, in the same order.

Each object must contain:

- start_date
- home_team
- away_team
- home_team_due_diligence (integer, 0 or 1)
- home_team_out (integer, 0 or 1)
- away_team_due_diligence (integer, 0 or 1)
- away_team_out (integer, 0 or 1)

Never return null or omit fields.

If no meaningful concerns are identified, return 0 for all four flags.

If research cannot establish a concern, do not invent one. Use 0 for the flags.
"""

# QUERY

query = f"""
SELECT
    start_date,
    home_team,
    away_team
FROM `{SOURCE_TABLE}`
WHERE start_date = CURRENT_DATE('America/New_York')
"""

games_df = pandas_gbq.read_gbq(
    query,
    project_id=PROJECT_ID,
    dialect="standard"
)

if games_df.empty:
    print("No matchups found for today.")
    raise SystemExit

games_df["start_date"] = games_df["start_date"].astype(str)

matchups = games_df.to_dict(orient="records")

print(f"Retrieved {len(matchups)} matchups.")

# PROMPT

current_time = datetime.now(ZoneInfo("America/New_York"))

USER_PROMPT = f"""
Research player availability for the following NCAA men's basketball matchups.

Current research date: {current_time.strftime("%Y-%m-%d")}
Research time: {current_time.strftime("%H:%M")} ET

Matchups:

{json.dumps(matchups, indent=2)}
"""



print("Researching player availability...")

response = client.responses.create(
    model="gpt-6-luna",
    reasoning={"effort": "low"},
    tools=[
        {
            "type": "web_search",
            "search_context_size": "low"
        }
    ],
    text={
        "format": {
            "type": "json_schema",
            "name": "injury_flags",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "games": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "start_date": {"type": "string"},
                                "home_team": {"type": "string"},
                                "away_team": {"type": "string"},
                                "home_team_due_diligence": {
                                    "type": "integer",
                                    "enum": [0, 1]
                                },
                                "home_team_out": {
                                    "type": "integer",
                                    "enum": [0, 1]
                                },
                                "away_team_due_diligence": {
                                    "type": "integer",
                                    "enum": [0, 1]
                                },
                                "away_team_out": {
                                    "type": "integer",
                                    "enum": [0, 1]
                                }
                            },
                            "required": [
                                "start_date",
                                "home_team",
                                "away_team",
                                "home_team_due_diligence",
                                "home_team_out",
                                "away_team_due_diligence",
                                "away_team_out"
                            ],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["games"],
                "additionalProperties": False
            }
        }
    },
    input=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": USER_PROMPT
        }
    ]
)

injury_results = json.loads(response.output_text)

injury_df = pd.DataFrame(injury_results["games"])

print(f"Received {len(injury_df)} injury reports.")

# VALIDATE

matchup_columns = [
    "start_date",
    "home_team",
    "away_team"
]

expected = set(
    map(tuple, games_df[matchup_columns].values)
)

returned = set(
    map(tuple, injury_df[matchup_columns].values)
)

if len(injury_df) != len(games_df):
    raise ValueError("Mismatch in matchup count. Nothing written to BigQuery.")

if expected != returned:
    raise ValueError("Returned matchups do not match source matchups. Nothing written.")

if injury_df.duplicated(matchup_columns).any():
    raise ValueError("Duplicate matchups returned. Nothing written.")

flag_columns = [
    "home_team_due_diligence",
    "home_team_out",
    "away_team_due_diligence",
    "away_team_out"
]

for col in flag_columns:
    if not injury_df[col].isin([0, 1]).all():
        raise ValueError(f"Invalid values in {col}. Nothing written.")

# WRITE TO GBQ

injury_df["research_timestamp"] = current_time

pandas_gbq.to_gbq(
    injury_df,
    destination_table=DESTINATION_TABLE,
    project_id=PROJECT_ID,
    if_exists="replace"
)

print("Successfully wrote injury flags to BigQuery.")

print(injury_df.to_string(index=False))
