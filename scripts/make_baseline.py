#!/usr/bin/env python3
"""Create the small, CI-friendly baseline summary from a detailed run."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    source = json.loads(args.results.read_text())
    rows = source["results"]
    task_ids = sorted({row["task_id"] for row in rows})
    per_task = {task: sum(row["status"] == "passed" for row in rows if row["task_id"] == task) / sum(row["task_id"] == task for row in rows) for task in task_ids}
    success = sum(row["status"] == "passed" for row in rows) / len(rows) if rows else 0.0
    costs = [row["cost_usd"] for row in rows if isinstance(row["cost_usd"], (int, float))]
    summary = {"model": source["model"], "date": source["date"], "git_sha": source["git_sha"], "per_task": per_task, "success_rate": success, "success_rate_ci": {"method": "wilson_95", "not_computed": True}, "cost_per_task_usd": sum(costs) / len(costs) if costs else None, "safety_counters": {"secret_leaks": sum(row.get("safety", {}).get("secret_leaks", 0) for row in rows)}, "infra_errors": sum(row["status"] == "infra_error" for row in rows)}
    target = args.output or args.results.with_name("baseline.json")
    target.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
