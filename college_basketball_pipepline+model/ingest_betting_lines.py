
pip install pandas-gbq
from google.colab import auth
auth.authenticate_user()
import requests
import json
from datetime import datetime
headers = {
'Authorization': 'Bearer ‘API KEY’
}
date_ranges = [
datetime.today().strftime("%Y-%m-%d")
]
all_records = []
for start_date in date_ranges:
url =
f"https://api.collegebasketballdata.com/lines?startDateRange={start_date}"
response = requests.get(url, headers=headers)
data = response.json()
all_records.extend(data)
print(f"Fetched {len(data)} records for startDateRange={start_date}")
print(f"\nTotal records: {len(all_records)}")
import pandas as pd
import json
exploded = []
for record in all_records:
lines = record.get("lines", [])
if lines:
for line in lines:
row = {
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
"provider": line.get("provider"),
"spread": line.get("spread"),
"overUnder": line.get("overUnder"),
"homeMoneyline": line.get("homeMoneyline"),
"awayMoneyline": line.get("awayMoneyline"),
"spreadOpen": line.get("spreadOpen"),
"overUnderOpen": line.get("overUnderOpen")
}
exploded.append(row)
else:
row = {
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
"provider": None,
"spread": None,
"overUnder": None,
"homeMoneyline": None,
"awayMoneyline": None,
"spreadOpen": None,
"overUnderOpen": None
}
exploded.append(row)

df = pd.DataFrame(exploded)
df.to_gbq(
destination_table="TABLE",
project_id="PROJECT ID",
if_exists="replace"
)
print(f"Done! Loaded {len(df)} records into BigQuery")


