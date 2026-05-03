# Data Projects

A collection of data projects, including end to end pipelines with REST APIs, BigQuery queries transforming data into analytics ready tables, and ML models.

## Projects

### Men's College Basketball 
Built an end-to-end data pipeline to ingest data from multiple REST API endpoints into BigQuery, where it was transformed into a matchup-level dataset with team performance metrics. Developed a machine learning model using BigQuery ML to predict the home team’s margin of victory, enabling game-level forecasting and exploratory analysis.

**Tools:** Python, BigQuery, SQL, BigQuery ML

### Multitouch Marketing Attribution
Built a three-stage attribution pipeline in BigQuery across data ingested via GA4's native BigQuery export, Hevo pipelines connecting CRM and CallRail APIs, and a webhook-based form submission feed. Stitches together session data, phone call events, and form leads to construct a best-available touchpoint path for each user. Matched users to closed invoices from a CRM via cleaned phone numbers and email addresses, then applied a time-decay model to distribute revenue credit across all touchpoints proportional to their proximity to conversion.

This model is intentionally directional. Cookie-based tracking has inherent gaps, and the user-level stitching across channels is probabilistic rather than deterministic. That said, it has had real business impact: by surfacing credit across the full conversion path, it demonstrated the value of upper-funnel awareness campaigns that are systematically undercredited in traditional first-contact or last-touch attribution models, directly informing paid media budget decisions.

**Tools:** BigQuery, SQL, GA4, CallRail, Hevo

### Wrike
Designed a data pipeline using Hevo to ingest project management data from Wrike into BigQuery. Modeled and joined task, user, and custom field tables to create a standardized “effort rating” metric aligned with business logic. Powered a Google Data Studio dashboard used by leadership to analyze budgeted time across users, clients, and departments.

**Tools:** Hevo, Bigquery, SQL, Google Data Studio

## About Me

Data Analyst in digital marketing with experience building data pipelines, modeling datasets, and delivering insights to stakeholders. Interested in data engineering and sports analytics.

Find me on [LinkedIn](https://linkedin.com/in/kevin-preiss)
