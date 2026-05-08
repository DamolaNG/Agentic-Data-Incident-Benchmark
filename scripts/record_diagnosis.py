"""Record root-cause diagnosis timing and correctness."""

from __future__ import annotations

import argparse
from pathlib import Path

from benchmark_utils import (
    RESULTS_PATH,
    append_note,
    bool_string,
    elapsed_seconds,
    find_latest_open_row,
    parse_bool,
    read_rows,
    write_rows,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record benchmark diagnosis outcome.")
    parser.add_argument("--incident-id", required=True)
    parser.add_argument("--workflow-mode", default="")
    parser.add_argument("--root-cause-correct", required=True, help="true/false")
    parser.add_argument("--notes", default="", help="Diagnosis explanation or reviewer note.")
    parser.add_argument("--results-path", default=str(RESULTS_PATH))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_rows(Path(args.results_path))
    row_index = find_latest_open_row(
        rows,
        args.incident_id,
        args.workflow_mode or None,
        require_missing="diagnosis_time_seconds",
    )
    row = rows[row_index]
    row["diagnosis_time_seconds"] = elapsed_seconds(row["start_time"])
    row["root_cause_correct"] = bool_string(parse_bool(args.root_cause_correct))
    row["notes"] = append_note(row["notes"], args.notes)
    if row["root_cause_correct"] == "false" and not row["human_review_needed"]:
        row["human_review_needed"] = "true"
    write_rows(rows, Path(args.results_path))
    print(
        "Recorded diagnosis for "
        f"{row['incident_id']} after {row['diagnosis_time_seconds']} seconds."
    )


if __name__ == "__main__":
    main()

