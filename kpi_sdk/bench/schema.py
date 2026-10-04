"""Typed result schema for benchmark runs.

Month-1 roadmap ("measurement first"): every benchmark run must produce the
same artifact shape so CI gates, dashboards and A/B comparisons can trust
the numbers instead of re-parsing ad-hoc dicts.

``TaskResult`` keeps the historical ``run_baseline.py`` keys
(``task_id``/``run``/``status``/``cost_usd``/``safety``/``output``) and adds
``duration_s`` for the time-to-green metric. ``BenchmarkReport`` aggregates
one run directory (``results.json``) and derives the summary that
``scripts/make_baseline.py`` compacts into ``baseline.json``.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

FORMAT = "kinetic-benchmark-results-v1"

VALID_STATUSES = ("passed", "failed", "infra_error")


@dataclass(frozen=True)
class TaskResult:
    """One task attempt: grader verdict plus cost/safety/time evidence."""

    task_id: str
    run: int
    status: str
    duration_s: float = 0.0
    cost_usd: float | None = None
    safety: dict[str, int] = field(default_factory=lambda: {"secret_leaks": 0})
    output: str = ""

    def __post_init__(self) -> None:
        if self.status not in VALID_STATUSES:
            raise ValueError(f"unknown status {self.status!r}; expected one of {VALID_STATUSES}")
        if self.run < 1:
            raise ValueError("run must be >= 1")
        if self.duration_s < 0:
            raise ValueError("duration_s must be >= 0")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BenchmarkReport:
    """One benchmark invocation: metadata plus every task attempt."""

    model: str = "mock"
    profile: str = "mock"
    runs: int = 1
    git_sha: str = ""
    date: str = ""
    results: list[TaskResult] = field(default_factory=list)
    format: str = FORMAT

    @property
    def success_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(row.status == "passed" for row in self.results) / len(self.results)

    def per_task_rates(self) -> dict[str, float]:
        rates: dict[str, float] = {}
        for task_id in sorted({row.task_id for row in self.results}):
            attempts = [row for row in self.results if row.task_id == task_id]
            rates[task_id] = sum(row.status == "passed" for row in attempts) / len(attempts)
        return rates

    @property
    def infra_errors(self) -> int:
        return sum(row.status == "infra_error" for row in self.results)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["results"] = [row.to_dict() if isinstance(row, TaskResult) else row for row in self.results]
        return payload
