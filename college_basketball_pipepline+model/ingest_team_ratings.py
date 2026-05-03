import os
import requests
import pandas as pd
from datetime import datetime
import google.auth

credentials, project = google.auth.default()

headers = {
    'Authorization': f"Bearer {os.environ['CBBD_API_KEY']}"
}

url = "https://api.collegebasketballdata.com/ratings/adjusted?season=2026"
response = requests.get(url, headers=headers)
response.raise_for_status()
all_records = response.json()
print(f"Fetched {len(all_records)} records")

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
