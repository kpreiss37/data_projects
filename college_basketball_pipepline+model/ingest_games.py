import os
import json
import requests
import pandas as pd
import pandas_gbq
from datetime import datetime
import google.auth

credentials, project = google.auth.default()

today = datetime.now()

season_start_year = today.year if today.month >= 5 else today.year - 1

destination_table_dynamic = f"mbb.games_{season_start_year}"

headers = {
    'Authorization': f"Bearer {os.environ['CBBD_API_KEY']}"
}

date_ranges = [
    f"{season_start_year}-10-01",
    f"{season_start_year + 1}-01-06",
    f"{season_start_year + 1}-03-08"
]

all_records = []
for start_date in date_ranges:
    url = f"https://api.collegebasketballdata.com/games?startDateRange={start_date}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    all_records.extend(data)
    print(f"Fetched {len(data)} records for startDateRange={start_date}")

print(f"\nTotal records: {len(all_records)}")

df = pd.DataFrame(all_records)
df["homePeriodPoints"] = df["homePeriodPoints"].apply(json.dumps)
df["awayPeriodPoints"] = df["awayPeriodPoints"].apply(json.dumps)
pandas_gbq.to_gbq(
    df,
    destination_table = destination_table_dynamic,
    project_id="project-bf3ebdef-3dea-4c35-a21",
    if_exists="replace",
    credentials=credentials
)
print(f"Done! Loaded {len(df)} records into BigQuery")
