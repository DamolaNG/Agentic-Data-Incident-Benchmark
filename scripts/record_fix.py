"""Record fix timing, validation, and quality metrics."""

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
    parser = argparse.ArgumentParser(description="Record benchmark fix outcome.")
    parser.add_argument("--incident-id", required=True)
    parser.add_argument("--workflow-mode", default="")
    parser.add_argument("--fix-correct", required=True, help="true/false")
    parser.add_argument("--tests-passed", required=True, help="true/false")
    parser.add_argument("--regression-detected", required=True, help="true/false")
    parser.add_argument("--wrong-fix-count", default="0")
    parser.add_argument("--explanation-score", default="")
    parser.add_argument("--human-review-needed", default="")
    parser.add_argument("--estimated-cost-usd", default="")
    parser.add_argument("--notes", default="")
    parser.add_argument("--results-path", default=str(RESULTS_PATH))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_rows(Path(args.results_path))
    row_index = find_latest_open_row(
        rows,
        args.incident_id,
        args.workflow_mode or None,
        require_missing="fix_time_seconds",
    )
    row = rows[row_index]
    total = float(elapsed_seconds(row["start_time"]))
    diagnosis = float(row["diagnosis_time_seconds"] or 0)
    row["total_time_seconds"] = str(round(total, 3))
    row["fix_time_seconds"] = str(round(max(0.0, total - diagnosis), 3))
    row["fix_correct"] = bool_string(parse_bool(args.fix_correct))
    row["tests_passed"] = bool_string(parse_bool(args.tests_passed))
    row["regression_detected"] = bool_string(parse_bool(args.regression_detected))
    row["wrong_fix_count"] = str(int(args.wrong_fix_count))
    if args.explanation_score:
        row["explanation_score"] = str(int(args.explanation_score))
    if args.human_review_needed:
        row["human_review_needed"] = bool_string(parse_bool(args.human_review_needed))
    elif row["fix_correct"] == "false" or row["tests_passed"] == "false" or row["regression_detected"] == "true":
        row["human_review_needed"] = "true"
    elif not row["human_review_needed"]:
        row["human_review_needed"] = "false"
    if args.estimated_cost_usd:
        row["estimated_cost_usd"] = args.estimated_cost_usd
    row["notes"] = append_note(row["notes"], args.notes)
    write_rows(rows, Path(args.results_path))
    print(f"Recorded fix for {row['incident_id']} after {row['total_time_seconds']} seconds.")


if __name__ == "__main__":
    main()

