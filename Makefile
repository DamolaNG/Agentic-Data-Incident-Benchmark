PYTHON := .venv/bin/python
PIP := .venv/bin/pip
DBT := .venv/bin/dbt
DAGSTER := .venv/bin/dagster
WAREHOUSE_PATH := warehouse/local/benchmark.duckdb
VENV_PYTHON ?= python3
INCIDENT_CLI := $(PYTHON) -m agentic_data_incident_benchmark.incidents.cli
export PYTHONPATH := src

.PHONY: help setup install generate-data ingest dbt-debug dbt-run dbt-test dbt-docs dagster-dev pipeline test lint clean list-incidents reset-incidents benchmark-analyze benchmark-score-example break-incident-01 break-incident-02 break-incident-03 break-incident-04 break-incident-05 break-incident-06 break-incident-07 break-incident-08 reset-incident-01 reset-incident-02 reset-incident-03 reset-incident-04 reset-incident-05 reset-incident-06 reset-incident-07 reset-incident-08

help:
	@echo "Available commands:"
	@echo "  make setup          Create .venv and install dependencies"
	@echo "  make generate-data  Create synthetic source CSV files"
	@echo "  make ingest         Load generated CSV files into DuckDB"
	@echo "  make dbt-debug      Validate dbt configuration"
	@echo "  make dbt-run        Run dbt transformations"
	@echo "  make dbt-test       Run dbt tests"
	@echo "  make dbt-docs       Generate dbt documentation"
	@echo "  make dagster-dev    Start Dagster webserver locally"
	@echo "  make pipeline       Generate, ingest, transform, and test"
	@echo "  make test           Run Python tests"
	@echo "  make lint           Run Ruff checks"
	@echo "  make list-incidents List controlled data incidents"
	@echo "  make break-incident-01..08 Inject a controlled incident"
	@echo "  make reset-incident-01..08 Reset a controlled incident"
	@echo "  make reset-incidents Reset every active controlled incident"
	@echo "  make benchmark-analyze Generate benchmark summary and charts"
	@echo "  make benchmark-score-example Show explanation scoring output"
	@echo "  make clean          Remove generated local outputs"

setup:
	$(VENV_PYTHON) -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install:
	$(PIP) install -r requirements.txt

generate-data:
	$(PYTHON) -m agentic_data_incident_benchmark.data_generation.generate_ecommerce_data

ingest:
	$(PYTHON) -m agentic_data_incident_benchmark.ingestion.load_raw

dbt-debug:
	$(DBT) debug --project-dir dbt --profiles-dir dbt

dbt-run:
	$(DBT) run --project-dir dbt --profiles-dir dbt

dbt-test:
	$(DBT) test --project-dir dbt --profiles-dir dbt

dbt-docs:
	$(DBT) docs generate --project-dir dbt --profiles-dir dbt

dagster-dev:
	DAGSTER_HOME=.dagster $(DAGSTER) dev -m agentic_data_incident_benchmark.orchestration.definitions

pipeline: generate-data ingest dbt-run dbt-test

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

list-incidents:
	$(INCIDENT_CLI) list

break-incident-01:
	$(INCIDENT_CLI) inject 1

break-incident-02:
	$(INCIDENT_CLI) inject 2

break-incident-03:
	$(INCIDENT_CLI) inject 3

break-incident-04:
	$(INCIDENT_CLI) inject 4

break-incident-05:
	$(INCIDENT_CLI) inject 5

break-incident-06:
	$(INCIDENT_CLI) inject 6

break-incident-07:
	$(INCIDENT_CLI) inject 7

break-incident-08:
	$(INCIDENT_CLI) inject 8

reset-incident-01:
	$(INCIDENT_CLI) reset 1

reset-incident-02:
	$(INCIDENT_CLI) reset 2

reset-incident-03:
	$(INCIDENT_CLI) reset 3

reset-incident-04:
	$(INCIDENT_CLI) reset 4

reset-incident-05:
	$(INCIDENT_CLI) reset 5

reset-incident-06:
	$(INCIDENT_CLI) reset 6

reset-incident-07:
	$(INCIDENT_CLI) reset 7

reset-incident-08:
	$(INCIDENT_CLI) reset 8

reset-incidents:
	$(INCIDENT_CLI) reset-all

benchmark-analyze:
	$(PYTHON) scripts/analyze_results.py

benchmark-score-example:
	$(PYTHON) scripts/score_explanation.py --explanation "Root cause: the dashboard model used checkout starts instead of purchases. Evidence: dashboard conversion failed reconciliation against mart_daily_funnel. Fix: restore the purchase numerator and validate with dbt test to check regressions."

clean:
	rm -rf data/generated/*.csv data/raw/*.csv warehouse/local/*.duckdb warehouse/local/*.wal dbt/target dbt/logs dbt/dbt_packages .dagster
