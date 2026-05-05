from __future__ import annotations

import subprocess

from dagster import AssetExecutionContext, asset

from agentic_data_incident_benchmark.data_generation.generate_ecommerce_data import (
    main as generate_ecommerce_data,
)
from agentic_data_incident_benchmark.ingestion.load_raw import load_raw_tables


@asset
def synthetic_ecommerce_data(context: AssetExecutionContext) -> None:
    generate_ecommerce_data()
    context.log.info("Generated synthetic ecommerce CSV files.")


@asset(deps=[synthetic_ecommerce_data])
def raw_ecommerce_tables(context: AssetExecutionContext) -> None:
    load_raw_tables()
    context.log.info("Loaded raw ecommerce tables into DuckDB.")


@asset(deps=[raw_ecommerce_tables])
def dbt_models(context: AssetExecutionContext) -> None:
    result = subprocess.run(
        [".venv/bin/dbt", "build", "--project-dir", "dbt", "--profiles-dir", "dbt"],
        check=True,
        capture_output=True,
        text=True,
    )
    context.log.info(result.stdout)
