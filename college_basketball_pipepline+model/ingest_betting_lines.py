import os
import json
import requests
import pandas as pd
from datetime import datetime
import google.auth

credentials, project = google.auth.default()

headers = {
    'Authorization': f"Bearer {os.environ['CBBD_API_KEY']}"
}

date_ranges = [
    datetime.today().strftime("%Y-%m-%d")
]

all_records = []
for start_date in date_ranges:
    url = f"https://api.collegebasketballdata.com/lines?startDateRange={start_date}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    all_records.extend(data)
    print(f"Fetched {len(data)} records for startDateRange={start_date}")

print(f"\nTotal records: {len(all_records)}")

exploded = []
for record in all_records:
    lines = record.get("lines", [])
    base = {
        "gameId": record["gameId"],
        "season": record["season"],
        "seasonType": record["seasonType"],
        "startDate": record["startDate"],
        "homeTeamId": record["homeTeamId"],
        "homeTeam": record["homeTeam"],
        "homeConference": record["homeConference"],
        "homeScore": record["homeScore"],
        "awayTeamId": record["awayTeamId"],
        "awayTeam": record["awayTeam"],
        "awayConference": record["awayConference"],
        "awayScore": record["awayScore"],
    }
    if lines:
        for line in lines:
            exploded.append({
                **base,
                "provider": line.get("provider"),
                "spread": line.get("spread"),
                "overUnder": line.get("overUnder"),
                "homeMoneyline": line.get("homeMoneyline"),
                "awayMoneyline": line.get("awayMoneyline"),
                "spreadOpen": line.get("spreadOpen"),
                "overUnderOpen": line.get("overUnderOpen")
            })
    else:
        exploded.append({
            **base,
            "provider": None,
            "spread": None,
            "overUnder": None,
            "homeMoneyline": None,
            "awayMoneyline": None,
            "spreadOpen": None,
            "overUnderOpen": None
        })

df = pd.DataFrame(exploded)
df.to_gbq(
    destination_table="TABLE",
    project_id="PROJECT ID",
    if_exists="replace",
    credentials=credentials
)
print(f"Done! Loaded {len(df)} records into BigQuery")
