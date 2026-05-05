# Architecture

The benchmark uses a small local data platform:

1. Python generates synthetic ecommerce source data for users, sessions, events, transactions, and fraud labels.
2. Python ingestion loads source data into DuckDB raw tables.
3. dbt transforms raw tables into staging, intermediate, mart, feature, and dashboard models.
4. Dagster orchestrates pipeline steps as assets.
5. Incident definitions describe controlled failures to introduce.
6. Benchmark results record response speed and fix quality.

The first phase focused on the foundation rather than complex incidents. The second phase adds a clean data platform that can support later incidents such as broken schemas, late-arriving data, duplicate records, bad joins, freshness failures, faulty transformations, and fraud feature regressions.

