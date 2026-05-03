# Data projects

A collection of end-to-end data projects spanning pipeline engineering, analytics modeling, and machine learning.

## Projects

### [Men's college basketball pipeline and prediction model](./college_basketball_pipeline/)
Built a full ingestion and modeling pipeline on top of the College Basketball Data API, transforming raw game, rating, and betting line data into a point-in-time matchup dataset. Trained a BigQuery ML linear regression model to predict home team margin of victory.

**Tools:** Python, BigQuery, SQL, BigQuery ML

---

### [Multitouch marketing attribution](./ga4_multitouch_attribution/)
Built a time-decay attribution pipeline in BigQuery stitching together GA4 session data, CallRail phone events, and form submissions to construct user-level touchpoint paths. Matched users to closed invoices and distributed revenue credit across all touchpoints proportional to proximity to conversion.

**Tools:** BigQuery, SQL, GA4, CallRail, Hevo

---

### [Wrike utilization reporting](./wrike_utilization/)
Designed a pipeline to ingest Wrike project management data into BigQuery and modeled task, user, and custom field tables into a standardized effort rating metric. Powered a leadership dashboard for analyzing budgeted vs. actual time across users, clients, and departments.

**Tools:** Hevo, BigQuery, SQL, Google Data Studio

---

## About me

Data analyst with a habit of building the pipeline before writing the query. I work across the full stack of a data project, from REST API ingestion and BigQuery modeling to dashboards and ML, and I'm equally comfortable talking about infrastructure decisions and business impact with stakeholders.

My background is in digital marketing analytics, where I've built attribution models, utilization reporting, and data pipelines that inform real budget and resourcing decisions. Outside of work, I apply the same toolkit to sports data, where the feedback loops are tighter and the questions are more fun to argue about.

I'm drawn to roles where the data engineering and the analysis aren't separate jobs, where building something right and making it useful are the same problem.

Find me on [LinkedIn](https://linkedin.com/in/kevin-preiss)
