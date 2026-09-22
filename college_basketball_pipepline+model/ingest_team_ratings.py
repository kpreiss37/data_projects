import os
import requests
import pandas as pd
import pandas_gbq
from datetime import datetime
import google.auth
import sys

credentials, project = google.auth.default()

season_start_year = today.year if today.month >= 5 else today.year - 1

headers = {
    'Authorization': f"Bearer {os.environ['CBBD_API_KEY']}"
}

url = f"https://api.collegebasketballdata.com/ratings/adjusted?season={season_start_year}"
response = requests.get(url, headers=headers)
response.raise_for_status()
all_records = response.json()
print(f"Fetched {len(all_records)} records")

if len(all_records) == 0:
    print("No records returned, nothing to ingest. Exiting.")
    sys.exit(0)

df = pd.json_normalize(all_records)
df.columns = df.columns.str.replace(".", "_", regex=False)
df["ingested_at"] = datetime.today().strftime("%Y-%m-%d")
pandas_gbq.to_gbq(
    df,
    destination_table="mbb.ratings",
    project_id="project-bf3ebdef-3dea-4c35-a21",
    if_exists="append",
    credentials=credentials
)
print(f"Done! Loaded {len(df)} records into BigQuery")
