from __future__ import annotations

from pathlib import Path

from agentic_data_incident_benchmark.warehouse.connection import connect


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_PATH = PROJECT_ROOT / "data" / "generated" / "orders.csv"


def load_orders() -> None:
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(
            f"Missing {SOURCE_PATH}. Run `make generate-data` before ingestion."
        )

    with connect() as con:
        con.execute("create schema if not exists raw")
        con.execute(
            """
            create or replace table raw.orders as
            select * from read_csv_auto(?)
            """,
            [str(SOURCE_PATH)],
        )


def main() -> None:
    load_orders()
    print(f"Loaded {SOURCE_PATH} into raw.orders")


if __name__ == "__main__":
    main()

