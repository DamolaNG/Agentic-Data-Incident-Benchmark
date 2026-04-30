from __future__ import annotations

import subprocess

from dagster import AssetExecutionContext, asset

from agentic_data_incident_benchmark.data_generation.generate_orders import main as generate_orders
from agentic_data_incident_benchmark.ingestion.load_raw import load_orders


@asset
def synthetic_orders(context: AssetExecutionContext) -> None:
    generate_orders()
    context.log.info("Generated synthetic orders CSV.")


@asset(deps=[synthetic_orders])
def raw_orders(context: AssetExecutionContext) -> None:
    load_orders()
    context.log.info("Loaded raw.orders into DuckDB.")


@asset(deps=[raw_orders])
def dbt_models(context: AssetExecutionContext) -> None:
    result = subprocess.run(
        [".venv/bin/dbt", "build", "--project-dir", "dbt", "--profiles-dir", "dbt"],
        check=True,
        capture_output=True,
        text=True,
    )
    context.log.info(result.stdout)

