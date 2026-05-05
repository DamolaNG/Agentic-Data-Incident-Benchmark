# Incident Injection System

This phase adds a controlled incident injection system for the local ecommerce data platform. Each incident is realistic enough to require diagnosis across source files, DuckDB-loaded raw tables, dbt staging models, marts, feature tables, and dashboard logic.

## How to Use

Start from a healthy local pipeline:

```bash
make pipeline
```

List the available incidents:

```bash
make list-incidents
```

Inject one incident:

```bash
make break-incident-01
```

Run the validation command listed in `incidents/incident_catalog.yml`. For most incidents this is:

```bash
make ingest && make dbt-run && make dbt-test
```

Reset the incident:

```bash
make reset-incident-01
```

Reset every active incident backup:

```bash
make reset-incidents
```

## Incident Catalog

The incident registry lives in `incidents/incident_catalog.yml`. It stores the operational metadata for each incident: incident ID, name, business impact, technical root cause, affected source or model, symptoms, expected failing tests, hidden diagnosis, fix strategy, regression risk, reset command, validation command, and expected failure output.

| # | Incident | What Is Injected | Expected Breakage |
|---|---|---|---|
| 1 | Schema drift in payments feed | Renames `raw_transactions.amount` to `transaction_amount` in the generated CSV. | `stg_transactions` cannot build because `amount` is missing. |
| 2 | Duplicate clickstream events | Replays realistic clickstream rows with new `event_id` values but identical business event attributes. | `assert_no_duplicate_clickstream_business_events` fails. |
| 3 | Delayed clickstream ingestion | Removes event rows for the newest session dates while leaving sessions present. | `assert_recent_sessions_have_events` fails and recent funnel metrics collapse. |
| 4 | Null spike in traffic source | Sets `traffic_source` to null for a large share of recent sessions. | `not_null` and recent null-rate tests fail. |
| 5 | Bad join multiplies fraud feature rows | Changes the fraud feature join from `session_id` to `user_id`. | Feature rows multiply and transaction grain tests fail. |
| 6 | Stale fraud feature table | Adds a stale date filter to the fraud feature model. | The table builds but fails recency parity against transactions. |
| 7 | Broken dashboard conversion metric | Replaces purchase conversion with checkout-start rate in the dashboard model. | The dashboard is valid SQL but fails reconciliation to the governed mart metric. |
| 8 | Mixed currencies in revenue feed | Changes a share of succeeded payments to USD and EUR and scales local amounts. | Currency contract tests fail and revenue would be semantically wrong if summed. |

## Implementation Details

The injector is implemented in `src/agentic_data_incident_benchmark/incidents/cli.py`. It provides four commands:

```bash
.venv/bin/python -m agentic_data_incident_benchmark.incidents.cli list
.venv/bin/python -m agentic_data_incident_benchmark.incidents.cli inject 1
.venv/bin/python -m agentic_data_incident_benchmark.incidents.cli reset 1
.venv/bin/python -m agentic_data_incident_benchmark.incidents.cli reset-all
```

Before mutating a file, the injector stores a per-incident backup under `incidents/.state/backups/`. Reset restores those backed-up files and removes the active backup. This makes incidents repeatable without requiring a full repository checkout reset.

The incidents use two injection styles. Source incidents mutate generated CSVs under `data/generated/`, then require `make ingest` to load the changed raw data into DuckDB. Model incidents patch dbt SQL files directly, then require `make dbt-run` and `make dbt-test`.

Expected failure notes live in `incidents/expected_failures/`. These are intentionally short because real dbt output varies by adapter and version.

## Useful DuckDB Inspection Queries

Use DuckDB directly when dbt output tells you where to look but not why it failed:

```sql
select *
from raw.raw_transactions
limit 5;
```

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

```sql
select
    max(transaction_date) as max_transaction_date
from main.stg_transactions;
```

```sql
select
    max(transaction_date) as max_feature_transaction_date
from main.fct_fraud_features;
```

## Learning Section

### 1. Summary of What Was Done

This phase created eight controlled data incidents: schema drift, duplicate events, delayed ingestion, null spike, bad join, stale feature table, broken dashboard metric, and currency conversion issue.

Incidents are injected with Python. Some injections mutate generated source CSV files, such as `raw_events.csv`, `raw_sessions.csv`, and `raw_transactions.csv`. Other injections mutate dbt model SQL, such as `fct_fraud_features.sql` or `dashboard_business_metrics.sql`.

When an incident runs, different parts of the platform break. Schema drift can stop dbt models from building. Duplicate events and null spikes are caught by dbt tests. Delayed ingestion appears as missing recent events. A bad join multiplies feature-table rows. A stale feature table remains structurally valid but fails freshness expectations. A broken dashboard metric produces valid SQL with business-wrong output. Mixed currencies make revenue semantically invalid unless normalized.

Reset works by restoring the exact files that were backed up before injection. Each incident has its own reset command, and `make reset-incidents` restores every active incident backup.

### 2. Tools Used

Python incident scripts are needed because realistic incidents require controlled file mutations, sampling, SQL patching, and reset logic. This simulates production failure injection because many real incidents come from changed source files, bad deploys, or replayed data. It demonstrates automation, reproducibility, and incident-response engineering to employers.

The YAML incident registry is needed because incident metadata should be data, not hidden in Python code. It helps simulate production incident runbooks by documenting impact, symptoms, expected failures, diagnosis, and fix strategy in one place. It demonstrates structured configuration and operational documentation.

dbt tests are needed because they turn assumptions about data quality and business logic into executable checks. They simulate production monitors for uniqueness, null rate, freshness, grain, and metric reconciliation. They demonstrate analytics engineering discipline and the ability to encode data contracts.

DuckDB inspection queries are needed because a responder must investigate raw and transformed data, not only read test names. They simulate production warehouse debugging with targeted SQL. They demonstrate practical data diagnosis skills.

Makefile automation is needed because incident workflows should be repeatable with simple commands. It helps simulate production runbooks where responders need consistent break, validate, and reset steps. It demonstrates build tooling and local developer experience.

### 3. Programming Languages Used

Python is used for incident injection and reset logic. Example:

```python
frame = frame.rename(columns={"amount": "transaction_amount"})
frame.to_csv(path, index=False)
```

SQL is used for dbt models and detector tests. Example:

```sql
select transaction_id, count(*) as feature_rows
from {{ ref('fct_fraud_features') }}
group by 1
having count(*) > 1
```

YAML is used for the incident registry. Example:

```yaml
incident_id: incident_02_duplicate_events
incident_name: Duplicate clickstream events
reset_command: make reset-incident-02
```

Markdown is used for documentation and learning material. Example:

```markdown
## Incident Catalog

The incident registry lives in `incidents/incident_catalog.yml`.
```

Makefile syntax is used for repeatable commands. Example:

```makefile
break-incident-02:
	$(INCIDENT_CLI) inject 2
```

### 4. What You Should Understand Before Moving On

- You can explain what each of the eight incidents changes.
- You can run `make break-incident-XX`, validate the failure, and run `make reset-incident-XX`.
- You understand why some incidents fail during `dbt run` while others fail during `dbt test`.
- You can distinguish a technical pipeline failure from a business metric failure.
- You can inspect raw DuckDB tables and dbt models to confirm a diagnosis.
- You understand why `event_id` uniqueness does not catch all duplicate event problems.
- You understand why a table can be valid, unique, and still stale.
- You can explain why fixing a bad join with `distinct` is risky.
- You can explain why currency normalization belongs before revenue aggregation.
- You can describe what regression risk means after an incident fix.

### 5. Quiz Me

Beginner questions:

1. What is a data incident?
2. What command injects the first incident?
3. What command resets the first incident?
4. Why does schema drift often break staging models first?
5. What is the difference between `dbt run` and `dbt test` in this benchmark?
6. Why is a null spike more serious when it appears suddenly in recent data?

Intermediate questions:

7. Why can duplicate clickstream events pass an `event_id` uniqueness test?
8. How does delayed ingestion differ from a real drop in user activity?
9. Why does joining transaction features by `user_id` instead of `session_id` multiply rows?
10. Why can a stale fraud feature table pass most schema and uniqueness tests?
11. Why is summing revenue across GBP, USD, and EUR without normalization wrong?

Interview-style questions:

12. A dashboard conversion rate increases sharply, but revenue is flat. How would you debug whether this is a business change or metric bug?
13. A dbt model builds successfully but stakeholders say the numbers are wrong. What checks would you run first?
14. How would you design a test that catches duplicate events without deleting legitimate repeated user actions?
15. What regression risks would you watch for after fixing a bad join in a feature table?

Do not move to the next phase until you can answer these questions.
