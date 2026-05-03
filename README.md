# Data Projects

A collection of data projects, including end to end pipelines with REST APIs, BigQuery queries transforming data into analytics ready tables, and ML models.

### Men's college basketball pipeline and prediction model

Built an end-to-end data pipeline ingesting from multiple College Basketball Data API endpoints into BigQuery, covering games, team ratings, four-factor stats, and betting lines, each on independent ingestion schedules.

The core modeling challenge was temporal: each game needed to be joined to the most recent ratings and stats available before it was played, not season-end figures. This required a point-in-time join pattern using ingestion timestamps, adding meaningful complexity to the feature engineering SQL.

The assembled dataset includes adjusted offensive and defensive ratings, four factors (eFG%, free throw rate, offensive rebounding rate, turnover ratio), days of rest, rolling win percentage over the last five games, and the Vegas spread. A linear regression model trained in BigQuery ML to predict home team margin of victory achieves an R² of 0.29, with the caveat that the pipeline was completed late in the season so historical snapshots were limited. The ingestion layer is already designed to accumulate snapshots via append-only loads, so the point-in-time logic will work as intended with a full season of data. The plan is to run it in full for 2026 and scale from there.

**Tools:** Python, BigQuery, SQL, BigQuery ML

### Multitouch Marketing Attribution
Built a three-stage attribution pipeline in BigQuery across data ingested via GA4's native BigQuery export, Hevo pipelines connecting CRM and CallRail APIs, and a webhook-based form submission feed. Stitches together session data, phone call events, and form leads to construct a best-available touchpoint path for each user. Matched users to closed invoices from a CRM via cleaned phone numbers and email addresses, then applied a time-decay model to distribute revenue credit across all touchpoints proportional to their proximity to conversion.

This model is intentionally directional. Cookie-based tracking has inherent gaps, and the user-level stitching across channels is probabilistic rather than deterministic. That said, it has had real business impact: by surfacing credit across the full conversion path, it demonstrated the value of upper-funnel awareness campaigns that are systematically undercredited in traditional first-contact or last-touch attribution models, directly informing paid media budget decisions.

**Tools:** BigQuery, SQL, GA4, CallRail, Hevo

### Wrike
Designed a data pipeline using Hevo to ingest project management data from Wrike into BigQuery. Modeled and joined task, user, and custom field tables to create a standardized “effort rating” metric aligned with business logic. Powered a Google Data Studio dashboard used by leadership to analyze budgeted time across users, clients, and departments.

**Tools:** Hevo, Bigquery, SQL, Google Data Studio

## About me

Data analyst with a habit of building the pipeline before writing the query. I work across the full stack of a data project, from REST API ingestion and BigQuery modeling to dashboards and ML, and I'm equally comfortable talking about infrastructure decisions and business impact with stakeholders.

My background is in digital marketing analytics, where I've built attribution models, utilization reporting, and data pipelines that inform real budget and resourcing decisions. Outside of work, I apply the same toolkit to sports data, where the feedback loops are tighter and the questions are more fun to argue about.

I'm drawn to roles where the data engineering and the analysis aren't separate jobs, where building something right and making it useful are the same problem.

Find me on [LinkedIn](https://linkedin.com/in/kevin-preiss)
