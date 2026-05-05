from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta
import shutil
from collections.abc import Callable
from pathlib import Path
import random


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = PROJECT_ROOT / "incidents" / "incident_catalog.yml"
GENERATED_DIR = PROJECT_ROOT / "data" / "generated"
DBT_DIR = PROJECT_ROOT / "dbt"
STATE_DIR = PROJECT_ROOT / "incidents" / ".state"
BACKUP_DIR = STATE_DIR / "backups"


IncidentMutator = Callable[[], None]


def _relative(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def _backup_path(incident_id: str, target_path: Path) -> Path:
    relative_name = "__".join(target_path.relative_to(PROJECT_ROOT).parts)
    return BACKUP_DIR / incident_id / relative_name


def _ensure_backup(incident_id: str, target_path: Path) -> None:
    if not target_path.exists():
        raise FileNotFoundError(f"Cannot inject {incident_id}; missing {_relative(target_path)}")

    backup_path = _backup_path(incident_id, target_path)
    if backup_path.exists():
        return

    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target_path, backup_path)


def _restore_backups(incident_id: str) -> list[Path]:
    incident_backup_dir = BACKUP_DIR / incident_id
    if not incident_backup_dir.exists():
        return []

    restored_paths = []
    for backup_path in sorted(incident_backup_dir.iterdir()):
        relative_parts = backup_path.name.split("__")
        target_path = PROJECT_ROOT.joinpath(*relative_parts)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup_path, target_path)
        restored_paths.append(target_path)

    shutil.rmtree(incident_backup_dir)
    return restored_paths


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing {_relative(path)}. Run `make generate-data` first.")
    with path.open(newline="") as source_file:
        reader = csv.DictReader(source_file)
        fieldnames = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader]
    return fieldnames, rows


def _write_csv(fieldnames: list[str], rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", newline="") as target_file:
        writer = csv.DictWriter(target_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _replace_text(path: Path, old: str, new: str, incident_id: str) -> None:
    _ensure_backup(incident_id, path)
    text = path.read_text()
    if new in text:
        return
    if old not in text:
        raise ValueError(f"Could not find expected SQL fragment in {_relative(path)}")
    path.write_text(text.replace(old, new))


def inject_schema_drift() -> None:
    incident_id = "incident_01_schema_drift"
    path = GENERATED_DIR / "raw_transactions.csv"
    _ensure_backup(incident_id, path)
    fieldnames, rows = _read_csv(path)
    if "amount" not in fieldnames:
        return
    mutated_fieldnames = ["transaction_amount" if name == "amount" else name for name in fieldnames]
    mutated_rows = []
    for row in rows:
        row["transaction_amount"] = row.pop("amount")
        mutated_rows.append(row)
    _write_csv(mutated_fieldnames, mutated_rows, path)


def inject_duplicate_events() -> None:
    incident_id = "incident_02_duplicate_events"
    path = GENERATED_DIR / "raw_events.csv"
    _ensure_backup(incident_id, path)
    fieldnames, rows = _read_csv(path)

    eligible = [
        row
        for row in rows
        if row["event_name"] in {"product_view", "add_to_cart", "checkout_started", "purchase"}
    ]
    duplicate_count = min(180, max(25, int(len(eligible) * 0.12)))
    sampled = random.Random(20260505).sample(eligible, duplicate_count)
    max_event_id = max(int(row["event_id"]) for row in rows)
    duplicates = []
    for offset, row in enumerate(sampled, start=1):
        duplicate = dict(row)
        duplicate["event_id"] = str(max_event_id + offset)
        duplicates.append(duplicate)

    mutated = sorted(
        [*rows, *duplicates],
        key=lambda row: (int(row["session_id"]), row["event_timestamp"], int(row["event_id"])),
    )
    _write_csv(fieldnames, mutated, path)


def inject_delayed_ingestion() -> None:
    incident_id = "incident_03_delayed_ingestion"
    events_path = GENERATED_DIR / "raw_events.csv"
    sessions_path = GENERATED_DIR / "raw_sessions.csv"
    _ensure_backup(incident_id, events_path)

    event_fieldnames, events = _read_csv(events_path)
    _, sessions = _read_csv(sessions_path)
    session_dates = {
        row["session_id"]: datetime.fromisoformat(row["session_started_at"]).date()
        for row in sessions
    }
    cutoff_date = max(session_dates.values()) - timedelta(days=1)
    delayed_session_ids = {
        session_id for session_id, session_date in session_dates.items() if session_date >= cutoff_date
    }

    held_back = [row for row in events if row["session_id"] in delayed_session_ids]
    held_back_path = STATE_DIR / f"{incident_id}_held_back_events.csv"
    held_back_path.parent.mkdir(parents=True, exist_ok=True)
    _write_csv(event_fieldnames, held_back, held_back_path)

    mutated = [row for row in events if row["session_id"] not in delayed_session_ids]
    _write_csv(event_fieldnames, mutated, events_path)


def inject_null_spike() -> None:
    incident_id = "incident_04_null_spike"
    path = GENERATED_DIR / "raw_sessions.csv"
    _ensure_backup(incident_id, path)
    fieldnames, rows = _read_csv(path)
    session_dates = [datetime.fromisoformat(row["session_started_at"]).date() for row in rows]
    cutoff_date = max(session_dates) - timedelta(days=6)
    recent_indices = [
        index for index, session_date in enumerate(session_dates) if session_date >= cutoff_date
    ]
    null_count = max(1, int(len(recent_indices) * 0.45))
    null_indices = random.Random(20260505).sample(recent_indices, null_count)
    for index in null_indices:
        rows[index]["traffic_source"] = ""
    _write_csv(fieldnames, rows, path)


def inject_bad_join() -> None:
    incident_id = "incident_05_bad_join"
    path = DBT_DIR / "models" / "features" / "fct_fraud_features.sql"
    old = "left join {{ ref('int_session_events') }} as se\n    on t.session_id = se.session_id"
    new = "left join {{ ref('int_session_events') }} as se\n    on t.user_id = se.user_id"
    _replace_text(path, old, new, incident_id)


def inject_stale_feature_table() -> None:
    incident_id = "incident_06_stale_feature_table"
    path = DBT_DIR / "models" / "features" / "fct_fraud_features.sql"
    _ensure_backup(incident_id, path)
    text = path.read_text()
    marker = "-- INCIDENT_06_STALE_FEATURE_TABLE"
    if marker in text:
        return
    stale_filter = """
-- INCIDENT_06_STALE_FEATURE_TABLE
where t.transaction_date <= (
    select max(transaction_date) - interval '5 days'
    from {{ ref('stg_transactions') }}
)
"""
    path.write_text(text.rstrip() + "\n" + stale_filter)


def inject_broken_dashboard_metric() -> None:
    incident_id = "incident_07_broken_dashboard_metric"
    path = DBT_DIR / "models" / "dashboards" / "dashboard_business_metrics.sql"
    old = "coalesce(f.session_conversion_rate, 0) as session_conversion_rate"
    new = (
        "coalesce(f.checkout_started_sessions * 1.0 / nullif(f.sessions, 0), 0) "
        "as session_conversion_rate"
    )
    _replace_text(path, old, new, incident_id)


def inject_currency_conversion_issue() -> None:
    incident_id = "incident_08_currency_conversion_issue"
    path = GENERATED_DIR / "raw_transactions.csv"
    _ensure_backup(incident_id, path)
    fieldnames, rows = _read_csv(path)
    succeeded_indices = [
        index for index, row in enumerate(rows) if row["transaction_status"] == "succeeded"
    ]
    sample_size = min(len(succeeded_indices), max(20, int(len(succeeded_indices) * 0.28)))
    sampled_indices = random.Random(20260505).sample(succeeded_indices, sample_size)
    midpoint = len(sampled_indices) // 2
    for index in sampled_indices[:midpoint]:
        rows[index]["currency"] = "USD"
        rows[index]["amount"] = f"{float(rows[index]['amount']) * 1.27:.2f}"
    for index in sampled_indices[midpoint:]:
        rows[index]["currency"] = "EUR"
        rows[index]["amount"] = f"{float(rows[index]['amount']) * 1.16:.2f}"
    _write_csv(fieldnames, rows, path)


MUTATORS: dict[str, IncidentMutator] = {
    "incident_01_schema_drift": inject_schema_drift,
    "incident_02_duplicate_events": inject_duplicate_events,
    "incident_03_delayed_ingestion": inject_delayed_ingestion,
    "incident_04_null_spike": inject_null_spike,
    "incident_05_bad_join": inject_bad_join,
    "incident_06_stale_feature_table": inject_stale_feature_table,
    "incident_07_broken_dashboard_metric": inject_broken_dashboard_metric,
    "incident_08_currency_conversion_issue": inject_currency_conversion_issue,
}


def catalog_summary() -> list[tuple[int, str, str]]:
    incidents: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for line in CATALOG_PATH.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("- incident_id:"):
            if current:
                incidents.append(current)
            current = {"incident_id": stripped.split(":", 1)[1].strip()}
        elif current is not None and stripped.startswith("sequence:"):
            current["sequence"] = stripped.split(":", 1)[1].strip()
        elif current is not None and stripped.startswith("incident_name:"):
            current["incident_name"] = stripped.split(":", 1)[1].strip()

    if current:
        incidents.append(current)

    return sorted(
        (
            int(incident["sequence"]),
            incident["incident_id"],
            incident["incident_name"],
        )
        for incident in incidents
    )


def incident_id_for_sequence(sequence: int) -> str:
    for catalog_sequence, incident_id, _ in catalog_summary():
        if catalog_sequence == sequence:
            return incident_id
    raise ValueError(f"No incident found for sequence {sequence}")


def normalize_incident_id(value: str) -> str:
    if value.isdigit():
        return incident_id_for_sequence(int(value))
    if value.startswith("incident_"):
        return value
    if value.startswith("break-incident-"):
        return incident_id_for_sequence(int(value.rsplit("-", 1)[1]))
    raise ValueError(f"Unknown incident identifier: {value}")


def inject(incident_id: str) -> None:
    normalized_id = normalize_incident_id(incident_id)
    if normalized_id not in MUTATORS:
        raise ValueError(f"No injector is implemented for {normalized_id}")
    MUTATORS[normalized_id]()
    print(f"Injected {normalized_id}")


def reset(incident_id: str) -> None:
    normalized_id = normalize_incident_id(incident_id)
    restored_paths = _restore_backups(normalized_id)
    held_back_path = STATE_DIR / f"{normalized_id}_held_back_events.csv"
    if held_back_path.exists():
        held_back_path.unlink()
    if not restored_paths:
        print(f"No active backup found for {normalized_id}")
        return
    restored = ", ".join(_relative(path) for path in restored_paths)
    print(f"Reset {normalized_id}: restored {restored}")


def reset_all() -> None:
    if not BACKUP_DIR.exists():
        print("No active incident backups found")
        return
    incident_ids = sorted(path.name for path in BACKUP_DIR.iterdir() if path.is_dir())
    for incident_id in incident_ids:
        reset(incident_id)


def list_incidents() -> None:
    for sequence, incident_id, incident_name in catalog_summary():
        print(f"{sequence:02d} {incident_id} - {incident_name}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inject or reset benchmark data incidents.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inject_parser = subparsers.add_parser("inject", help="Inject an incident by ID or sequence.")
    inject_parser.add_argument("incident")

    reset_parser = subparsers.add_parser("reset", help="Reset an incident by ID or sequence.")
    reset_parser.add_argument("incident")

    subparsers.add_parser("reset-all", help="Reset every active incident backup.")
    subparsers.add_parser("list", help="List available incidents.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "inject":
        inject(args.incident)
    elif args.command == "reset":
        reset(args.incident)
    elif args.command == "reset-all":
        reset_all()
    elif args.command == "list":
        list_incidents()
    else:
        parser.error(f"Unknown command {args.command}")


if __name__ == "__main__":
    main()
