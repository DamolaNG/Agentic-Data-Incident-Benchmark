from dagster import Definitions

from agentic_data_incident_benchmark.orchestration.assets import (
    dbt_models,
    raw_ecommerce_tables,
    synthetic_ecommerce_data,
)


defs = Definitions(assets=[synthetic_ecommerce_data, raw_ecommerce_tables, dbt_models])
