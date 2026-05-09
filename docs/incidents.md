# Incident Catalog

The project includes controlled data incidents that can be injected into the local data platform. Each incident is designed to force diagnosis across source files, DuckDB tables, dbt models, tests, features, dashboards, and business definitions.

## Commands

Start from a healthy pipeline:

```bash
make reset-incidents
make pipeline
```

List incidents:

```bash
make list-incidents
```

Inject an incident:

```bash
make break-incident-01
```

Validate the failure:

```bash
make ingest
make dbt-run
make dbt-test
```

Reset an incident:

```bash
make reset-incident-01
```

Reset all active incidents:

```bash
make reset-incidents
```

## Implemented Incidents

The executable catalog currently contains 8 controlled incidents in `incidents/incident_catalog.yml`.

| # | Incident | Injected failure | Expected signal | Correct diagnosis |
|---|---|---|---|---|
| 1 | Schema drift in payments feed | `raw_transactions.amount` is renamed to `transaction_amount`. | `stg_transactions` fails to build. | Upstream schema changed without a coordinated contract update. |
| 2 | Duplicate clickstream events | Replayed events get new `event_id` values but duplicate business attributes. | Business-grain duplicate test fails. | `event_id` uniqueness is insufficient because the real event grain is duplicated. |
| 3 | Delayed clickstream ingestion | Recent event rows are removed while sessions remain present. | Recent sessions have no events and funnel metrics collapse. | Event ingestion is delayed, not user activity. |
| 4 | Null spike in traffic source | Recent sessions lose `traffic_source`. | Not-null and recent null-rate tests fail. | A recent tracking or ingestion issue caused attribution loss. |
| 5 | Bad join multiplies fraud feature rows | Fraud features join by `user_id` instead of `session_id`. | Transaction-grain feature tests fail. | Join key is too broad and multiplies rows. |
| 6 | Stale fraud feature table | Feature model filters out recent dates. | Feature freshness parity test fails. | Table shape is valid, but the feature data is stale. |
| 7 | Broken dashboard conversion metric | Dashboard uses checkout-start rate instead of purchase conversion. | Dashboard reconciliation test fails. | Dashboard logic drifted from governed mart definition. |
| 8 | Mixed currencies in revenue feed | Some succeeded payments become USD/EUR with local amounts. | Currency contract test fails. | Revenue cannot be summed before currency normalization. |

## Incident Design Principles

Each incident has a business impact, technical root cause, expected symptoms, validation command, fix strategy, and regression risk. This matters because incident response is not only about making tests green. A reliable responder must identify the correct failure mode, implement the right fix, and avoid introducing unrelated damage.

Good incidents have these properties:

- They are reproducible with one command.
- They can be reset without a git checkout.
- They break a realistic platform assumption.
- They require evidence, not guessing.
- They have a known correct diagnosis for scoring.
- They include a regression risk that reviewers should consider.

## Debugging Examples

Inspect schema drift:

```sql
select *
from raw.raw_transactions
limit 5;
```

Find duplicate clickstream business events:

```sql
select
    session_id,
    user_id,
    event_timestamp,
    event_name,
    page_url,
    count(*) as rows_at_business_grain
from main.stg_events
group by 1, 2, 3, 4, 5
having count(*) > 1;
```

Check stale fraud features:

```sql
select
    max(transaction_date) as max_feature_transaction_date
from main.fct_fraud_features;
```

## How To Explain This In An Interview

The incidents are not random broken files. They represent common data-platform failure classes: schema drift, late data, duplicate ingestion, null spikes, incorrect join grain, stale features, dashboard metric drift, and semantic aggregation errors. The benchmark measures whether an AI-assisted workflow can reason through those failures faster while still producing a correct and reviewable fix.
