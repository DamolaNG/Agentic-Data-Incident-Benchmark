# Benchmark System

This phase adds a benchmark system for measuring whether Claude/Codex-assisted debugging reduces MTTR without reducing fix accuracy. The benchmark records each incident response attempt in `results/results.csv`, then analyzes the results with Pandas and chart generation.

## Goal

The benchmark compares response workflows across the same controlled data incidents. The primary question is whether an LLM-assisted workflow lowers Mean Time To Resolution while preserving or improving the correctness of the diagnosis and fix.

MTTR means Mean Time To Resolution. Diagnosis time is the time from benchmark start until the responder identifies the correct root cause. Fix time is the time from diagnosis until the responder implements and validates a fix. Fix accuracy means the fix solves the real root cause instead of only hiding a symptom. Regression rate measures whether unrelated tests or behaviors broke after the fix. Explanation quality measures whether the diagnosis is useful to a human reviewer.

## Results Schema

The benchmark writes one row per response attempt to `results/results.csv`. The columns are `incident_id`, `incident_name`, `workflow_mode`, `start_time`, `diagnosis_time_seconds`, `fix_time_seconds`, `total_time_seconds`, `root_cause_correct`, `fix_correct`, `tests_passed`, `regression_detected`, `wrong_fix_count`, `explanation_score`, `human_review_needed`, `llm_tool`, `estimated_cost_usd`, and `notes`.

The CSV format makes the benchmark easy to inspect manually, commit as a lightweight artifact, and load into Pandas for analysis.

## Scripts

`scripts/start_benchmark.py` starts a benchmark run. It appends a row to `results/results.csv` with the incident ID, workflow mode, optional LLM tool, optional cost estimate, and UTC start time.

```bash
.venv/bin/python scripts/start_benchmark.py \
  --incident-id incident_01_schema_drift \
  --workflow-mode manual \
  --notes "Manual baseline run"
```

`scripts/record_diagnosis.py` records when the responder has identified the root cause. It calculates diagnosis time from the row's `start_time` and records whether the root cause was correct.

```bash
.venv/bin/python scripts/record_diagnosis.py \
  --incident-id incident_01_schema_drift \
  --workflow-mode manual \
  --root-cause-correct true \
  --notes "Raw transactions column amount was renamed to transaction_amount."
```

`scripts/record_fix.py` records the validated fix outcome. It calculates total time and fix time, then records fix correctness, test status, regression status, wrong fix attempts, explanation score, human review status, cost, and notes.

```bash
.venv/bin/python scripts/record_fix.py \
  --incident-id incident_01_schema_drift \
  --workflow-mode manual \
  --fix-correct true \
  --tests-passed true \
  --regression-detected false \
  --wrong-fix-count 0 \
  --explanation-score 5 \
  --notes "Mapped the renamed source column deliberately and reran validation."
```

`scripts/score_explanation.py` scores a diagnosis explanation from 1 to 5 using a transparent rubric. It checks whether the explanation covers root cause, affected layer, evidence, fix, and validation or regression risk.

```bash
.venv/bin/python scripts/score_explanation.py \
  --explanation "Root cause: duplicate clickstream replay emitted new event IDs. Evidence: duplicates appear at business grain. Fix: dedupe by business key and validate dbt tests."
```

`scripts/analyze_results.py` loads `results/results.csv`, writes `analysis/benchmark_summary.json`, and generates charts under `analysis/charts/`.

```bash
make benchmark-analyze
```

## Example Manual Benchmark Workflow

First, reset all active incidents and start from a healthy pipeline.

```bash
make reset-incidents
make pipeline
```

Next, inject the target incident and start the manual timer.

```bash
make break-incident-01
.venv/bin/python scripts/start_benchmark.py \
  --incident-id incident_01_schema_drift \
  --workflow-mode manual \
  --notes "Manual responder without LLM assistance"
```

Then the responder investigates using dbt output, SQL inspection, source files, and the incident symptoms available during normal debugging. When they can state the root cause, record the diagnosis.

```bash
.venv/bin/python scripts/record_diagnosis.py \
  --incident-id incident_01_schema_drift \
  --workflow-mode manual \
  --root-cause-correct true \
  --notes "The source payment CSV renamed amount to transaction_amount."
```

Finally, the responder implements the fix, validates with the incident's validation command, records the outcome, resets the incident, and regenerates analysis.

```bash
make ingest
make dbt-run
.venv/bin/python scripts/record_fix.py \
  --incident-id incident_01_schema_drift \
  --workflow-mode manual \
  --fix-correct true \
  --tests-passed true \
  --regression-detected false \
  --wrong-fix-count 0 \
  --explanation-score 5
make reset-incident-01
make benchmark-analyze
```

## Example Claude/Codex Benchmark Workflow

First, start from the same healthy baseline and inject the same incident.

```bash
make reset-incidents
make pipeline
make break-incident-01
```

Start the assisted benchmark run and record which tool is being used.

```bash
.venv/bin/python scripts/start_benchmark.py \
  --incident-id incident_01_schema_drift \
  --workflow-mode codex \
  --llm-tool Codex \
  --estimated-cost-usd 0.25 \
  --notes "Codex-assisted response"
```

Ask Claude or Codex to diagnose the incident using the same repository and validation commands. When the agent gives a root cause that the reviewer accepts, record diagnosis time and correctness.

```bash
.venv/bin/python scripts/record_diagnosis.py \
  --incident-id incident_01_schema_drift \
  --workflow-mode codex \
  --root-cause-correct true \
  --notes "Agent identified upstream schema drift in raw_transactions."
```

Let the agent implement the fix, then validate with dbt and project tests. Record whether the fix solved the real cause, whether all relevant tests passed, whether unrelated regressions appeared, and how much human review was needed.

```bash
make ingest
make dbt-run
make dbt-test
.venv/bin/python scripts/record_fix.py \
  --incident-id incident_01_schema_drift \
  --workflow-mode codex \
  --fix-correct true \
  --tests-passed true \
  --regression-detected false \
  --wrong-fix-count 0 \
  --explanation-score 4 \
  --human-review-needed false \
  --estimated-cost-usd 0.25
make benchmark-analyze
```

The comparison is useful only when manual and assisted runs use the same incident set, the same validation commands, and the same correctness rubric.

## Analysis Charts

The analysis script generates six chart files. `median_diagnosis_time_by_workflow.png` compares how quickly each workflow reaches the correct root cause. `median_fix_time_by_workflow.png` compares implementation and validation speed after diagnosis. `accuracy_by_workflow.png` measures the share of runs with both correct root cause and correct fix. `regression_rate_by_workflow.png` measures how often a workflow breaks unrelated behavior. `cost_per_incident.png` tracks estimated LLM or platform cost per incident. `speed_vs_accuracy_scatter.png` shows whether faster runs were also accurate.

## Learning Section

### 1. Summary of What Was Done

The benchmark starts when `scripts/start_benchmark.py` appends a run row to `results/results.csv` with the incident, workflow mode, tool name, cost estimate, notes, and UTC start time.

Diagnosis is recorded with `scripts/record_diagnosis.py`. The script finds the latest open run for the incident, calculates elapsed seconds from `start_time`, records `diagnosis_time_seconds`, and stores whether the root cause was correct.

Fixes are recorded with `scripts/record_fix.py`. The script calculates `total_time_seconds`, derives `fix_time_seconds` by subtracting diagnosis time, and records whether the fix was correct, tests passed, regressions appeared, and wrong fixes were attempted.

Results are scored through explicit fields and `scripts/score_explanation.py`. Correctness is reviewed against the known incident root cause. Explanation quality is scored from 1 to 5 based on whether it names the root cause, affected layer, evidence, fix, and validation or regression risk.

Charts are generated by `scripts/analyze_results.py`. It loads the CSV with Pandas, computes workflow-level summary metrics, writes JSON output, and uses Matplotlib to save PNG charts under `analysis/charts/`.

### 2. Tools Used

CSV stores benchmark runs in a simple tabular file. It matters because benchmark results should be easy to review, diff, and load into analysis tools. This demonstrates data engineering skill in designing a measurable results schema.

JSON stores the analysis summary in `analysis/benchmark_summary.json`. It matters because JSON is machine-readable and easy to pass to dashboards, reports, or future automation. This demonstrates the ability to create structured analytical outputs.

Python datetime records UTC start times and calculates elapsed seconds. It matters because MTTR benchmarks need consistent timing. This demonstrates practical handling of timestamps and durations in operational data.

Pandas loads the CSV and computes medians, rates, and grouped summaries. It matters because benchmark interpretation depends on aggregating multiple incident attempts by workflow. This demonstrates analytical data processing.

Matplotlib creates the benchmark charts as PNG files. It matters because visual comparisons make speed, accuracy, regression rate, and cost tradeoffs easier to inspect. This demonstrates basic analytics visualization.

Makefile commands provide repeatable entry points such as `make benchmark-analyze`. They matter because responders need consistent commands for benchmark workflows. This demonstrates local automation and developer experience.

Claude/Codex as coding agents represent assisted debugging workflows. They matter because the benchmark measures whether agents reduce time without lowering correctness. This demonstrates evaluation design for AI-assisted data engineering work.

### 3. Programming Languages Used

Python is used for timing, recording, scoring, and analysis.

```python
row["diagnosis_time_seconds"] = elapsed_seconds(row["start_time"])
```

Markdown is used for methodology, workflows, learning notes, and quiz material.

```markdown
## Example Manual Benchmark Workflow
```

Makefile syntax is used to expose repeatable benchmark commands.

```makefile
benchmark-analyze:
	$(PYTHON) scripts/analyze_results.py
```

### 4. What You Should Understand Before Moving On

- You can explain what MTTR means and how this benchmark measures it.
- You can distinguish diagnosis time from fix time.
- You understand why faster fixes are not useful if fix accuracy drops.
- You know how `results/results.csv` stores benchmark runs.
- You can start a manual or Codex-assisted benchmark run.
- You can record a diagnosis and explain what `root_cause_correct` means.
- You can record a fix and explain what `fix_correct`, `tests_passed`, and `regression_detected` mean.
- You understand why explanation quality is scored separately from fix correctness.
- You know why LLM output needs validation through tests and human review.
- You can run `make benchmark-analyze` and find the generated charts.
- You can interpret median diagnosis and fix time charts.
- You can interpret accuracy and regression-rate charts.
- You can explain why cost per incident matters when evaluating agent usefulness.
- You understand why benchmark runs must use the same incidents and validation commands for a fair comparison.

### 5. Quiz Me

Beginner questions:

1. What does MTTR stand for?
2. What is the difference between diagnosis time and fix time?
3. Which file stores benchmark result rows?
4. What command generates benchmark analysis charts?
5. Why do we record `workflow_mode`?

Intermediate questions:

6. Why is a fast fix not enough to prove an LLM-assisted workflow is better?
7. What does `root_cause_correct` measure that `tests_passed` does not?
8. Why should regression rate be measured separately from fix accuracy?
9. How does explanation quality help evaluate agent usefulness?
10. Why should manual and Claude/Codex runs use the same incidents and validation commands?

Interview-style questions:

11. If Codex has lower median MTTR but a higher regression rate than manual debugging, how would you interpret the result?
12. If an agent passes tests but gives a weak explanation, what risk remains?
13. How would you improve this benchmark to reduce bias between manual and assisted runs?
14. What chart would you use to explain the tradeoff between speed and correctness, and why?
15. How would you decide whether human review is still needed for an LLM-generated fix?

Do not move to the next phase until you answer these questions.
