"""Shared helpers for benchmark result scripts."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

RESULT_COLUMNS = [
    "incident_id",
    "incident_name",
    "workflow_mode",
    "start_time",
    "diagnosis_time_seconds",
    "fix_time_seconds",
    "total_time_seconds",
    "root_cause_correct",
    "fix_correct",
    "tests_passed",
    "regression_detected",
    "wrong_fix_count",
    "explanation_score",
    "human_review_needed",
    "llm_tool",
    "estimated_cost_usd",
    "notes",
]

RESULTS_PATH = Path("results/results.csv")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def format_time(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def ensure_results_file(path: Path = RESULTS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        write_rows([], path)


def read_rows(path: Path = RESULTS_PATH) -> list[dict[str, str]]:
    ensure_results_file(path)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [normalise_row(row) for row in reader]


def write_rows(rows: Iterable[dict[str, str]], path: Path = RESULTS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(normalise_row(row))


def normalise_row(row: dict[str, str | None]) -> dict[str, str]:
    return {column: str(row.get(column) or "") for column in RESULT_COLUMNS}


def bool_string(value: bool | None) -> str:
    if value is None:
        return ""
    return "true" if value else "false"


def parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"true", "t", "yes", "y", "1"}:
        return True
    if normalized in {"false", "f", "no", "n", "0"}:
        return False
    raise ValueError(f"Expected a boolean value, got {value!r}")


def append_note(existing: str, addition: str | None) -> str:
    if not addition:
        return existing
    if not existing:
        return addition
    return f"{existing} | {addition}"


def find_latest_open_row(
    rows: list[dict[str, str]],
    incident_id: str,
    workflow_mode: str | None = None,
    require_missing: str | None = None,
) -> int:
    for index in range(len(rows) - 1, -1, -1):
        row = rows[index]
        if row["incident_id"] != incident_id:
            continue
        if workflow_mode and row["workflow_mode"] != workflow_mode:
            continue
        if require_missing and row[require_missing]:
            continue
        return index
    mode_hint = f" and workflow_mode={workflow_mode!r}" if workflow_mode else ""
    missing_hint = f" with empty {require_missing!r}" if require_missing else ""
    raise SystemExit(f"No benchmark row found for incident_id={incident_id!r}{mode_hint}{missing_hint}.")


def elapsed_seconds(start_time: str, end_time: datetime | None = None) -> str:
    end = end_time or utc_now()
    elapsed = max(0.0, (end - parse_time(start_time)).total_seconds())
    return str(round(elapsed, 3))


def load_incident_name(incident_id: str) -> str:
    try:
        import yaml
    except ImportError:
        return ""

    catalog_path = Path("incidents/incident_catalog.yml")
    if not catalog_path.exists():
        return ""

    with catalog_path.open(encoding="utf-8") as handle:
        catalog = yaml.safe_load(handle) or {}

    for incident in catalog.get("incidents", []):
        if str(incident.get("incident_id", "")) == incident_id:
            return str(incident.get("incident_name", ""))
        short_id = str(incident.get("id", ""))
        if short_id and short_id == incident_id:
            return str(incident.get("incident_name", ""))
    return ""

