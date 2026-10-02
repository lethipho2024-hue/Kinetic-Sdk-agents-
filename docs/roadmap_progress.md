# Roadmap progress

## 2026-10-02 — Benchmark 10 task và baseline workflow

- Đã xây harness deterministic tại `kpi_sdk/bench/harness.py`, 10 task tại `benchmarks/tasks/`, cùng test oracle/hidden-test isolation trong `tests/test_benchmark_harness.py`.
- Đã thêm `scripts/run_baseline.sh`, `scripts/run_baseline.py`, `scripts/make_baseline.py`; mẫu summary ở `benchmarks/baselines/baseline.json`; hướng dẫn người dùng ở `docs/baseline_howto.md`.
- Lệnh đã chạy: `python -m pytest -q tests/test_benchmark_harness.py tests/test_baseline_scripts.py`, `ruff check kpi_sdk scripts tests/test_benchmark_harness.py tests/test_baseline_scripts.py`, và mock baseline 5 lần.
- Vấn đề còn mở: chưa có adapter `BENCH_REAL_RUNNER` cụ thể cho provider, nên chưa chạy model thật, chưa đo chi phí thật, và trường Wilson CI đang đánh dấu `not_computed` thay vì bịa số liệu.
