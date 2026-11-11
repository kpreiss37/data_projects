import pandas
import pandas_gbq
import requests

project_id = 'project-bf3ebdef-3dea-4c35-a21'

sql = """
SELECT 
SUM(CASE WHEN bet_result = 'WIN' THEN 1 ELSE 0 END) won_bets,
SUM(CASE WHEN bet_result = 'LOSS' THEN 1 ELSE 0 END) lost_bets,
SUM(CASE WHEN bet_result = 'PUSH' THEN 1 ELSE 0 END) push_bets,
ROUND(SUM(
CASE
  WHEN bet_result = "WIN" THEN 0.9091
  WHEN bet_result = "LOSS" THEN -1
  WHEN bet_result = "PUSH" THEN 0
  ELSE 0
END),2) return
 FROM `project-bf3ebdef-3dea-4c35-a21.mbb.prediction performance`
 WHERE 1=1
 AND place_bet = 1
 AND start_date = DATE_ADD(current_date(), INTERVAL -1 DAY)
"""

table = pandas_gbq.read_gbq(sql,project_id=project_id)

requests.post("https://ntfy.sh/kevinpreisscollegehoopsperformance",
    data=f"Live: {table['won_bets'][0]}-{table['lost_bets'][0]}-{table['push_bets'][0]}  {table['return'][0]}u\n\n"
    "Tap to see today's recommended bets",
              headers={"title": "Yesterday's Performance:",
                      "Click": "https://datastudio.google.com/reporting/5ce29c70-40be-458a-a87f-b7430782ff4a",
                      "Markdown":"yes"}
             )
