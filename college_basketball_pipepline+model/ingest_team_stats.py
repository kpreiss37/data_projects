import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import google.auth

credentials, project = google.auth.default()

headers = {
    'Authorization': f"Bearer {os.environ['CBBD_API_KEY']}"
}

date_ranges = [
    (datetime.today() + timedelta(days=-21)).strftime("%Y-%m-%d")
]

all_records = []
for start_date in date_ranges:
    url = f"https://api.collegebasketballdata.com/stats/team/season?startDateRange={start_date}&season=2026"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    all_records.extend(data)
    print(f"Fetched {len(data)} records for startDateRange={start_date}")

print(f"\nTotal records: {len(all_records)}")

df = pd.json_normalize(all_records)
df.columns = df.columns.str.replace(".", "_", regex=False)
df["ingested_at"] = datetime.today().strftime("%Y-%m-%d")
df.to_gbq(
    destination_table="TABLE",
    project_id="PROJECT ID",
    if_exists="append",
    credentials=credentials
)
print(f"Done! Loaded {len(df)} records into BigQuery")
