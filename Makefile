PYTHON := .venv/bin/python
PIP := .venv/bin/pip
DBT := .venv/bin/dbt
DAGSTER := .venv/bin/dagster
WAREHOUSE_PATH := warehouse/local/benchmark.duckdb

.PHONY: help setup install generate-data ingest dbt-debug dbt-run dbt-test dagster-dev pipeline test lint clean

help:
	@echo "Available commands:"
	@echo "  make setup          Create .venv and install dependencies"
	@echo "  make generate-data  Create synthetic source CSV files"
	@echo "  make ingest         Load generated CSV files into DuckDB"
	@echo "  make dbt-debug      Validate dbt configuration"
	@echo "  make dbt-run        Run dbt transformations"
	@echo "  make dbt-test       Run dbt tests"
	@echo "  make dagster-dev    Start Dagster webserver locally"
	@echo "  make pipeline       Generate, ingest, transform, and test"
	@echo "  make test           Run Python tests"
	@echo "  make lint           Run Ruff checks"
	@echo "  make clean          Remove generated local outputs"

setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install:
	$(PIP) install -r requirements.txt

generate-data:
	$(PYTHON) -m agentic_data_incident_benchmark.data_generation.generate_orders

ingest:
	$(PYTHON) -m agentic_data_incident_benchmark.ingestion.load_raw

dbt-debug:
	$(DBT) debug --project-dir dbt --profiles-dir dbt

dbt-run:
	$(DBT) run --project-dir dbt --profiles-dir dbt

dbt-test:
	$(DBT) test --project-dir dbt --profiles-dir dbt

dagster-dev:
	DAGSTER_HOME=.dagster $(DAGSTER) dev -m agentic_data_incident_benchmark.orchestration.definitions

pipeline: generate-data ingest dbt-run dbt-test

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

clean:
	rm -rf data/generated/*.csv data/raw/*.csv warehouse/local/*.duckdb warehouse/local/*.wal dbt/target dbt/logs dbt/dbt_packages .dagster

