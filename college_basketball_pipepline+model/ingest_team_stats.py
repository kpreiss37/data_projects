pip install pandas-gbq
from google.colab import auth
auth.authenticate_user()
import requests
import json
headers = {
'Authorization': 'Bearer ‘API KEY’
}
date_ranges = [
"2025-10-01",
"2026-01-06",
"2026-03-08"
]
all_records = []
for start_date in date_ranges:
url =
f"https://api.collegebasketballdata.com/games?startDateRange={start_date}"
response = requests.get(url, headers=headers)
data = response.json()
all_records.extend(data)
print(f"Fetched {len(data)} records for startDateRange={start_date}")
print(f"\nTotal records: {len(all_records)}")
import pandas as pd
df = pd.DataFrame(all_records)

df["homePeriodPoints"] = df["homePeriodPoints"].apply(json.dumps)
df["awayPeriodPoints"] = df["awayPeriodPoints"].apply(json.dumps)
df.to_gbq(
destination_table="TABLE",
project_id="PROJECT ID",
if_exists="replace"
)

print(f"Done! Loaded {len(df)} records into BigQuery")
import pandas as pd
df = pd.json_normalize(all_records)
df.columns = df.columns.str.replace(".", "_", regex=False)
df["ingested_at"] = datetime.today().strftime("%Y-%m-%d")
df.to_gbq(
destination_table="TABLE",
project_id="PROJECT ID",
if_exists="append"
)
print(f"Done! Loaded {len(df)} records into BigQuery")
