from dagster import Definitions

from agentic_data_incident_benchmark.orchestration.assets import dbt_models, raw_orders, synthetic_orders


defs = Definitions(assets=[synthetic_orders, raw_orders, dbt_models])

