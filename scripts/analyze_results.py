"""Analyze benchmark results and generate charts."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

import pandas as pd

from benchmark_utils import RESULTS_PATH

MPL_CACHE_DIR = Path(tempfile.gettempdir()) / "agentic_data_incident_benchmark_matplotlib"
MPL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))
os.environ.setdefault("XDG_CACHE_HOME", str(MPL_CACHE_DIR))

import matplotlib.pyplot as plt  # noqa: E402

NUMERIC_COLUMNS = [
    "diagnosis_time_seconds",
    "fix_time_seconds",
    "total_time_seconds",
    "wrong_fix_count",
    "explanation_score",
    "estimated_cost_usd",
]

BOOLEAN_COLUMNS = [
    "root_cause_correct",
    "fix_correct",
    "tests_passed",
    "regression_detected",
    "human_review_needed",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze benchmark CSV results.")
    parser.add_argument("--results-path", default=str(RESULTS_PATH))
    parser.add_argument("--output-dir", default="analysis/charts")
    parser.add_argument("--summary-path", default="analysis/benchmark_summary.json")
    return parser.parse_args()


def load_results(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"Results file does not exist: {path}")
    frame = pd.read_csv(path)
    for column in NUMERIC_COLUMNS:
        if column in frame:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    for column in BOOLEAN_COLUMNS:
        if column in frame:
            frame[column] = frame[column].map({"true": True, "false": False, True: True, False: False})
    return frame


def save_bar(series: pd.Series, title: str, ylabel: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    if series.empty:
        ax.text(0.5, 0.5, "No completed benchmark data", ha="center", va="center")
        ax.set_axis_off()
    else:
        series.plot(kind="bar", ax=ax, color="#3274a1")
        ax.set_title(title)
        ax.set_xlabel("Workflow mode")
        ax.set_ylabel(ylabel)
        ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def generate_charts(frame: pd.DataFrame, output_dir: Path) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    chart_paths: list[str] = []

    completed = frame.dropna(subset=["workflow_mode"])
    median_diagnosis = completed.groupby("workflow_mode")["diagnosis_time_seconds"].median().dropna()
    path = output_dir / "median_diagnosis_time_by_workflow.png"
    save_bar(median_diagnosis, "Median diagnosis time by workflow", "Seconds", path)
    chart_paths.append(str(path))

    median_fix = completed.groupby("workflow_mode")["fix_time_seconds"].median().dropna()
    path = output_dir / "median_fix_time_by_workflow.png"
    save_bar(median_fix, "Median fix time by workflow", "Seconds", path)
    chart_paths.append(str(path))

    accuracy = completed.assign(
        accurate=completed["root_cause_correct"].fillna(False) & completed["fix_correct"].fillna(False)
    ).groupby("workflow_mode")["accurate"].mean()
    path = output_dir / "accuracy_by_workflow.png"
    save_bar(accuracy, "Accuracy by workflow", "Share accurate", path)
    chart_paths.append(str(path))

    regression_rate = completed.groupby("workflow_mode")["regression_detected"].mean().dropna()
    path = output_dir / "regression_rate_by_workflow.png"
    save_bar(regression_rate, "Regression rate by workflow", "Share with regression", path)
    chart_paths.append(str(path))

    cost = completed.groupby("incident_id")["estimated_cost_usd"].sum(min_count=1).dropna()
    fig, ax = plt.subplots(figsize=(9, 5))
    if cost.empty:
        ax.text(0.5, 0.5, "No cost data", ha="center", va="center")
        ax.set_axis_off()
    else:
        cost.plot(kind="bar", ax=ax, color="#6a994e")
        ax.set_title("Cost per incident")
        ax.set_xlabel("Incident")
        ax.set_ylabel("Estimated cost USD")
        ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    path = output_dir / "cost_per_incident.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    chart_paths.append(str(path))

    scatter = completed.dropna(subset=["total_time_seconds", "root_cause_correct", "fix_correct"])
    fig, ax = plt.subplots(figsize=(8, 5))
    if scatter.empty:
        ax.text(0.5, 0.5, "No completed benchmark data", ha="center", va="center")
        ax.set_axis_off()
    else:
        y_values = (scatter["root_cause_correct"] & scatter["fix_correct"]).astype(int)
        ax.scatter(scatter["total_time_seconds"], y_values, s=80, alpha=0.8, color="#bc4749")
        for _, row in scatter.iterrows():
            ax.annotate(row["workflow_mode"], (row["total_time_seconds"], int(row["root_cause_correct"] and row["fix_correct"])))
        ax.set_title("Speed vs accuracy")
        ax.set_xlabel("Total time seconds")
        ax.set_ylabel("Accurate fix")
        ax.set_yticks([0, 1], ["No", "Yes"])
    fig.tight_layout()
    path = output_dir / "speed_vs_accuracy_scatter.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    chart_paths.append(str(path))

    return chart_paths


def build_summary(frame: pd.DataFrame) -> dict[str, object]:
    completed = frame.dropna(subset=["workflow_mode"])
    if completed.empty:
        return {"runs": 0, "by_workflow": {}}

    summary = {}
    for workflow, group in completed.groupby("workflow_mode"):
        accurate = group["root_cause_correct"].fillna(False) & group["fix_correct"].fillna(False)
        summary[workflow] = {
            "runs": int(len(group)),
            "median_diagnosis_time_seconds": float(group["diagnosis_time_seconds"].median())
            if group["diagnosis_time_seconds"].notna().any()
            else None,
            "median_fix_time_seconds": float(group["fix_time_seconds"].median())
            if group["fix_time_seconds"].notna().any()
            else None,
            "accuracy_rate": float(accurate.mean()),
            "regression_rate": float(group["regression_detected"].dropna().mean())
            if group["regression_detected"].notna().any()
            else None,
            "median_explanation_score": float(group["explanation_score"].median())
            if group["explanation_score"].notna().any()
            else None,
            "total_estimated_cost_usd": float(group["estimated_cost_usd"].fillna(0).sum()),
        }
    return {"runs": int(len(completed)), "by_workflow": summary}


def main() -> None:
    args = parse_args()
    frame = load_results(Path(args.results_path))
    chart_paths = generate_charts(frame, Path(args.output_dir))
    summary = build_summary(frame)
    Path(args.summary_path).parent.mkdir(parents=True, exist_ok=True)
    Path(args.summary_path).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"summary_path": args.summary_path, "charts": chart_paths, "summary": summary}, indent=2))


if __name__ == "__main__":
    main()
