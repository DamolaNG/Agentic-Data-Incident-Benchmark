# agentic-data-incident-benchmark

A benchmark for measuring whether LLM coding agents improve data pipeline incident response speed and fix accuracy.

## Purpose

This project creates a local data platform where realistic data pipeline incidents can be introduced, diagnosed, fixed, and measured. The benchmark is designed to compare incident response with and without LLM coding agents.

The first phase establishes the project foundation:

- Python package layout for data platform code.
- DuckDB as a local analytical warehouse.
- dbt project for SQL transformations.
- Dagster project for orchestration.
- Incident catalog and benchmark result folders.
- Documentation and learning notes.
- Makefile commands for repeatable local workflows.

## Repository Layout

```text
.
├── analysis/                         # Notebooks and scripts for benchmark result analysis
├── benchmark_results/                # Output location for incident response measurements
├── data/                             # Generated and raw local data
├── dbt/                              # dbt transformation project
├── docs/                             # Architecture and learning documentation
├── incidents/                        # Incident definitions and scenarios
├── orchestration/                    # Dagster orchestration entry points
├── src/agentic_data_incident_benchmark/
│   ├── data_generation/              # Synthetic source data creation
│   ├── ingestion/                    # Loading raw data into DuckDB
│   ├── orchestration/                # Dagster assets and definitions
│   └── warehouse/                    # DuckDB connection helpers
├── Makefile                          # Repeatable local commands
├── pyproject.toml                    # Python project and dependency metadata
└── requirements.txt                  # pip-friendly dependency list
```

## Local Setup

Create a virtual environment and install dependencies:

```bash
make setup
```

Generate sample source data:

```bash
make generate-data
```

Load the sample data into DuckDB:

```bash
make ingest
```

Run dbt transformations:

```bash
make dbt-run
```

Run dbt tests:

```bash
make dbt-test
```

Start Dagster locally:

```bash
make dagster-dev
```

Run the full local pipeline:

```bash
make pipeline
```

