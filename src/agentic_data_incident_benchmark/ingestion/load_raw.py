from __future__ import annotations

from pathlib import Path

from agentic_data_incident_benchmark.warehouse.connection import connect


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = PROJECT_ROOT / "data" / "generated"
RAW_TABLES = [
    "raw_users",
    "raw_sessions",
    "raw_events",
    "raw_transactions",
    "raw_fraud_labels",
]


def load_raw_tables() -> None:
    missing_paths = [
        SOURCE_DIR / f"{table}.csv"
        for table in RAW_TABLES
        if not (SOURCE_DIR / f"{table}.csv").exists()
    ]
    if missing_paths:
        raise FileNotFoundError(
            "Missing generated source files. Run `make generate-data` before ingestion. "
            f"Missing: {', '.join(str(path) for path in missing_paths)}"
        )

    with connect() as con:
        con.execute("create schema if not exists raw")
        for table in RAW_TABLES:
            source_path = SOURCE_DIR / f"{table}.csv"
            con.execute(
                f"""
                create or replace table raw.{table} as
                select * from read_csv_auto(?)
                """,
                [str(source_path)],
            )


def load_orders() -> None:
    load_raw_tables()


def main() -> None:
    load_raw_tables()
    print(f"Loaded {len(RAW_TABLES)} raw tables into DuckDB")


if __name__ == "__main__":
    main()
