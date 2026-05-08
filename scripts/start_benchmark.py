"""Start a benchmark timing row."""

from __future__ import annotations

import argparse

from benchmark_utils import RESULTS_PATH, append_note, format_time, load_incident_name, read_rows, utc_now, write_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start timing a data incident benchmark run.")
    parser.add_argument("--incident-id", required=True, help="Incident identifier, for example incident_01_schema_drift.")
    parser.add_argument("--incident-name", default="", help="Human-readable incident name.")
    parser.add_argument(
        "--workflow-mode",
        required=True,
        choices=["manual", "claude", "codex", "agent_assisted"],
        help="Response workflow being measured.",
    )
    parser.add_argument("--llm-tool", default="", help="Agent/tool used, if any.")
    parser.add_argument("--estimated-cost-usd", default="", help="Estimated LLM or platform cost.")
    parser.add_argument("--notes", default="", help="Optional run notes.")
    parser.add_argument("--results-path", default=str(RESULTS_PATH), help="CSV output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results_path = RESULTS_PATH if args.results_path == str(RESULTS_PATH) else __import__("pathlib").Path(args.results_path)
    rows = read_rows(results_path)
    incident_name = args.incident_name or load_incident_name(args.incident_id)
    row = {
        "incident_id": args.incident_id,
        "incident_name": incident_name,
        "workflow_mode": args.workflow_mode,
        "start_time": format_time(utc_now()),
        "llm_tool": args.llm_tool,
        "estimated_cost_usd": args.estimated_cost_usd,
        "notes": append_note("", args.notes),
    }
    rows.append(row)
    write_rows(rows, results_path)
    print(f"Started benchmark run for {args.incident_id} in {args.workflow_mode} mode.")
    print(f"Results file: {results_path}")


if __name__ == "__main__":
    main()

