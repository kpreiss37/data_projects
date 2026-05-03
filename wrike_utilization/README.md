# Wrike utilization reporting

A data pipeline and analytics model built on top of Wrike's project management data, transforming raw task, time log, and user data into a standardized effort metric for leadership reporting.

## Pipeline overview

Wrike data is ingested into BigQuery via Hevo, pulling from Wrike's API across four core tables: tasks, time logs, contacts, and custom fields. The SQL model joins and reshapes these into a single analytics-ready table.

## How it works

The query is structured in four CTEs before a final join:

**Custom fields** -- Wrike stores custom field values as a nested array on each task. The model unnests these into one row per field, joins to a lookup table to resolve field IDs into human-readable names, then re-aggregates back to one row per task with a clean array of name/value structs. Client name and budget department are then pivoted out as flat columns.

**Authors and assignees** -- Author and assignee IDs are stored as arrays on each task. Both are unnested, joined to the contacts table to resolve IDs to full names, and re-aggregated into name arrays per task.

**Time and effort** -- Time logs are joined to tasks and users to produce a per-user, per-task summary of hours logged. A window function calculates total minutes logged across all users for each task.

**Effort rating** -- Allocated effort from Wrike's task metadata is compared against actual logged minutes with a 20% tolerance band, producing an `on_time` flag of OVER, UNDER, or GOOD for each task.

## Output

The final table powers a Google Data Studio dashboard used by leadership to track budgeted vs. actual time across users, clients, and departments.

## Files

| File | Description |
|------|-------------|
| `wrike_analytics_table.sql` | Full model joining tasks, time logs, users, and custom fields into an analytics-ready table |

## Tools

Hevo, BigQuery, SQL, Google Data Studio
