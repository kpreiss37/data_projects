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
    "2025-10-01",
    "2026-01-06",
    "2026-03-08"
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
df.to_gbq(
    destination_table="TABLE",
    project_id="PROJECT ID",
    if_exists="replace",
    credentials=credentials
)
print(f"Done! Loaded {len(df)} records into BigQuery")
