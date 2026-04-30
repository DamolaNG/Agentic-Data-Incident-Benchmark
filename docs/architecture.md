# Architecture

The benchmark uses a small local data platform:

1. Python generates synthetic source data.
2. Python ingestion loads source data into DuckDB raw tables.
3. dbt transforms raw tables into modeled analytical tables.
4. Dagster orchestrates pipeline steps as assets.
5. Incident definitions describe controlled failures to introduce.
6. Benchmark results record response speed and fix quality.

The first phase focuses on the foundation rather than complex incidents. Later phases can add broken schemas, late-arriving data, duplicate records, bad joins, freshness failures, and faulty transformations.

