"""Score diagnosis explanation quality with a transparent rubric."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmark_utils import RESULTS_PATH, append_note, find_latest_open_row, read_rows, write_rows

RUBRIC = {
    "root_cause": ["root cause", "caused by", "because", "bug", "failure"],
    "affected_layer": ["raw", "staging", "intermediate", "mart", "feature", "dashboard", "dbt"],
    "evidence": ["evidence", "test", "query", "observed", "failing", "reproduce"],
    "fix": ["fix", "change", "patch", "restore", "join", "normalize", "ingest"],
    "validation": ["validate", "validation", "dbt test", "tests pass", "regression", "rerun"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score explanation quality from 1 to 5.")
    parser.add_argument("--explanation", default="", help="Explanation text to score.")
    parser.add_argument("--file", default="", help="Path to a file containing the explanation.")
    parser.add_argument("--incident-id", default="", help="Update latest matching row when provided.")
    parser.add_argument("--workflow-mode", default="")
    parser.add_argument("--results-path", default=str(RESULTS_PATH))
    return parser.parse_args()


def load_text(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    return args.explanation


def score_explanation(text: str) -> dict[str, object]:
    normalized = text.lower()
    matched = {
        category: any(keyword in normalized for keyword in keywords)
        for category, keywords in RUBRIC.items()
    }
    score = max(1, sum(1 for value in matched.values() if value))
    return {
        "score": score,
        "matched_categories": [category for category, value in matched.items() if value],
        "missing_categories": [category for category, value in matched.items() if not value],
        "human_review_needed": score < 4,
    }


def main() -> None:
    args = parse_args()
    text = load_text(args)
    if not text.strip():
        raise SystemExit("Provide --explanation or --file.")

    result = score_explanation(text)
    if args.incident_id:
        rows = read_rows(Path(args.results_path))
        row_index = find_latest_open_row(rows, args.incident_id, args.workflow_mode or None)
        row = rows[row_index]
        row["explanation_score"] = str(result["score"])
        row["human_review_needed"] = "true" if result["human_review_needed"] else "false"
        row["notes"] = append_note(row["notes"], f"explanation_score={result['score']}")
        write_rows(rows, Path(args.results_path))

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

