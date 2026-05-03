# Multitouch marketing attribution

A three-stage attribution pipeline in BigQuery that stitches together session data, phone call events, and form leads to construct a best-available touchpoint path for each user, matches users to closed invoices, and distributes revenue credit across all touchpoints using a time-decay model.

## Pipeline overview

Data flows into BigQuery from three sources:

- **GA4 bulk export** -- session-level traffic source data including source, medium, campaign, keyword, and GCLID
- **CallRail via Hevo** -- phone call events joined back to GA4 user IDs via a call ID passed through the GA4 event
- **Form submissions via webhook** -- lead records including email and phone number linked to GA4 user IDs

## How it works

### Stage 1 -- touchpoint path construction (`client_touchpaths`)

For each GA4 user, all session start events are aggregated into an ordered array of touchpoints. Phone numbers from CallRail and emails from form submissions are joined to each user and stored as arrays, giving the best available identity signals per user.

### Stage 2 -- invoice matching (`multitouch_matched`)

Users are matched to closed invoices from the CRM by joining on cleaned phone numbers and email addresses. Phone numbers are normalized to 10 digits by stripping formatting characters before joining. Only touchpoints that occurred before the invoice date are retained, ensuring no post-conversion sessions contaminate the path.

### Stage 3 -- time-decay attribution (`multitouch_attributed`)

Each touchpoint in a matched user's path is scored using an exponential time-decay function based on days before conversion. Scores are normalized so that all touchpoints for a given user sum to 1, and each touchpoint receives a proportional share of the invoice revenue. Results are grouped by source, medium, and campaign.

## Design decisions and limitations

This model is intentionally directional. Cookie-based tracking has inherent gaps, and user-level stitching across channels is probabilistic rather than deterministic -- a user who calls from a different device than they browsed on will not be stitched. That said, the model has had real business impact: by surfacing credit across the full conversion path, it demonstrated the value of upper-funnel awareness campaigns that are systematically undercredited in last-touch models, directly informing paid media budget decisions.

The decay rate (`-0.1` in the exponent) is tunable and should be adjusted based on the typical length of the sales cycle.

## Files

| File | Description |
|------|-------------|
| `attributed_touchpoints.sql` | All three pipeline stages: path construction, invoice matching, and time-decay attribution |

## Tools

BigQuery, SQL, GA4, CallRail, Hevo
