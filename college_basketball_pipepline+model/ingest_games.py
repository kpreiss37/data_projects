pip install pandas-gbq
from google.colab import auth
auth.authenticate_user()
import requests
import json
from datetime import datetime, timedelta
headers = {
'Authorization': 'Bearer ‘API KEY’
}
date_ranges = [
(datetime.today() + timedelta(days=-21)).strftime("%Y-%m-%d")
]
all_records = []
for start_date in date_ranges:
url =
f"https://api.collegebasketballdata.com/stats/team/season?startDateRange={
start_date}&season=2026"
response = requests.get(url, headers=headers)
data = response.json()
all_records.extend(data)
print(f"Fetched {len(data)} records for startDateRange={start_date}")
print(f"\nTotal records: {len(all_records)}")
