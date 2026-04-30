from __future__ import annotations

import os
from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_WAREHOUSE_PATH = PROJECT_ROOT / "warehouse" / "local" / "benchmark.duckdb"


def warehouse_path() -> Path:
    return Path(os.getenv("WAREHOUSE_PATH", DEFAULT_WAREHOUSE_PATH))


def connect() -> duckdb.DuckDBPyConnection:
    path = warehouse_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path))

