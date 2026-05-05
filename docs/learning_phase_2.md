# Phase 2 Learning Guide

## 1. Summary of What Was Done

This phase built a clean local data platform for a simulated digital product or ecommerce company.

The generated data now includes users, sessions, clickstream events, transactions, and fraud labels. The Python generation script writes these datasets as CSV files into `data/generated/`. The ingestion script reads those CSV files and loads them into DuckDB as raw warehouse tables named `raw_users`, `raw_sessions`, `raw_events`, `raw_transactions`, and `raw_fraud_labels` in the `raw` schema.

The dbt project now transforms those raw tables through several layers. The staging layer contains `stg_users`, `stg_sessions`, `stg_events`, `stg_transactions`, and `stg_fraud_labels`. The intermediate layer contains `int_user_sessions` and `int_session_events`. The mart layer contains `mart_daily_funnel` and `mart_revenue_daily`. The feature layer contains `fct_fraud_features`. The dashboard layer contains `dashboard_business_metrics`.

The raw layer is the warehouse landing area. It should look close to the source files and should avoid business logic. The staging layer cleans names, types, and basic assumptions while keeping the same basic grain as the raw source. The intermediate layer joins and reshapes data into reusable building blocks. The mart layer creates business-facing tables for analytics. The feature layer creates machine-learning or risk-analysis-ready columns. The dashboard layer creates a final reporting table designed for business consumption.

## 2. Tools Used

### Python Random Generation

Python random generation creates realistic fake data without needing production systems. In this project, `random` is used to create user acquisition channels, session devices, event funnels, transaction amounts, and fraud labels.

It was chosen because it is built into Python and simple enough for a controlled benchmark. It fits the data engineering workflow by giving us repeatable source data that can be regenerated when testing ingestion, transformations, and incident scenarios.

### Pandas

Pandas is a Python library for working with tabular data. In this project, Pandas turns generated Python dictionaries into data frames and writes them to CSV files.

It was chosen because it is familiar, widely used, and convenient for small local datasets. It fits the workflow as the bridge between synthetic Python objects and file-based source data.

### DuckDB

DuckDB is a local analytical database. In this project, DuckDB stores the raw warehouse tables and dbt output models in `warehouse/local/benchmark.duckdb`.

It was chosen because it gives us warehouse-style SQL locally without cloud infrastructure. It fits the workflow by acting as the database where ingestion lands data and dbt runs transformations.

### dbt-duckdb

`dbt-duckdb` is the adapter that lets dbt run SQL models against DuckDB. In this project, `dbt/profiles.yml` tells dbt to connect to the local DuckDB file.

It was chosen because dbt needs a database adapter for each warehouse type. It fits the workflow by allowing standard dbt commands such as `dbt run`, `dbt test`, and `dbt docs generate` to work with DuckDB.

### dbt Tests

dbt tests check whether data follows expected rules. In this project, tests include `not_null`, `unique`, `relationships`, `accepted_values`, and custom SQL business tests.

They were chosen because data quality is central to incident response. Tests fit the workflow by turning assumptions into executable checks. When an incident breaks a pipeline, tests help detect what failed and prove whether the fix worked.

### dbt Docs

dbt docs generate documentation from model SQL and YAML metadata. In this project, YAML files include model descriptions, column descriptions, owners, tags, and expected grain.

dbt docs were chosen because analytics projects need discoverability and shared context. They fit the workflow by helping engineers understand what each model means, who owns it, and how it should be used.

## 3. Programming Languages and Config Types Used

### Python for Scripts

Python appears in `src/agentic_data_incident_benchmark/data_generation/generate_ecommerce_data.py` and `src/agentic_data_incident_benchmark/ingestion/load_raw.py`.

Example:

```python
datasets = build_ecommerce_data()
frame.to_csv(path, index=False)
```

This creates synthetic datasets and writes each one to a CSV file.

### SQL for Transformations

SQL appears in dbt models under `dbt/models/`.

Example:

```sql
select
    session_date,
    count(*) as sessions,
    sum(has_purchase_event) as purchase_sessions
from {{ ref('int_session_events') }}
group by 1
```

This transforms session-level data into daily funnel metrics.

### YAML for Tests and Configuration

YAML appears in files such as `dbt/models/staging/staging.yml`.

Example:

```yaml
- name: user_id
  description: Stable unique identifier for a user.
  tests: [not_null, unique]
```

This documents a column and tells dbt to test that it is populated and unique.

### Markdown for Docs

Markdown appears in `README.md` and files under `docs/`.

Example:

```markdown
## Local Setup

Run the full local pipeline:
```

Markdown creates readable project documentation using headings, text, lists, and code blocks.

## 4. What You Should Understand Before Moving On

- You can explain the difference between raw, staging, intermediate, mart, feature, and dashboard layers.
- You know which five raw tables are loaded into DuckDB.
- You understand why staging models cast data types and document source columns.
- You understand how `ref()` creates dbt model dependencies.
- You understand how `source()` points dbt to raw warehouse tables.
- You can explain why `relationships` tests protect joins between tables.
- You understand why accepted values are useful for fields like event names and transaction status.
- You know why a mart table is different from a feature table.
- You can explain why dashboard tables should have clear grain and stable metric definitions.
- You know how `make generate-data`, `make ingest`, `make dbt-run`, and `make dbt-test` fit together.
- You understand how tests help detect incidents and prove fixes.
- You can inspect a dbt model and identify its upstream dependencies.

## 5. Quiz Me

Do not move to the next phase until you answer these questions.

### Beginner Questions

1. What are the five raw tables loaded into DuckDB in phase 2?
2. What is the difference between a raw table and a staging model?
3. Why do we use dbt instead of writing one large SQL script manually?
4. What does DuckDB do in this project?
5. Why do dbt tests matter in an incident benchmark?

### Intermediate Questions

6. How does `ref('int_session_events')` help dbt understand model dependencies?
7. Why is `mart_daily_funnel` grouped by `session_date`?
8. What problem does a `relationships` test catch?
9. Why is `fct_fraud_features` considered a feature table rather than a dashboard table?

### Interview-Style Questions

10. If `mart_revenue_daily` suddenly shows zero revenue for a day that had transactions, how would you investigate?
11. If a new event name appears in raw clickstream data and breaks an `accepted_values` test, what are the possible correct responses?
12. How would you decide whether a data quality test belongs in staging, intermediate, mart, or feature layers?

