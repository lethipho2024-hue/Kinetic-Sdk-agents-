# Baseline test suite

## Environment and reproducibility

- Date (UTC): 2026-10-02
- Python: CPython 3.14.4
- OS: Linux 15ff73ec47b2 6.18.44 x86_64
- Installation command: `python -m pip install -e ".[dev,llm]"`
- Test command: `python -m pytest -q --durations=10`

The preparatory `python -m pytest -q` run before changes was retained in the
working log. The post-Task-1 command above is the authoritative, reproducible
baseline below; it produced the same three environment-dependent tiktoken
failures. No tests were modified, removed, or skipped to improve these results.

## Result

| passed | failed | skipped | xfailed | errors | deselected | elapsed |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1235 | 3 | 2 | 0 | 0 | 4 | 30.47 s |

There are **96** `test_*.py` files and **1147** functions matching
`def test_` or `async def test_`.

## Failures, errors, and skips

| Test | Status | Reason |
| --- | --- | --- |
| `tests/test_context_manager.py::test_tiktoken_counter_counts_real_tokens` | failed | `tiktoken` attempted to download `cl100k_base.tiktoken`; TLS certificate verification for `openaipublic.blob.core.windows.net` failed. |
| `tests/test_context_manager.py::test_tiktoken_counter_integrates_with_manager` | failed | Same unavailable tokenizer download / TLS certificate verification failure. |
| `tests/test_context_manager.py::test_tiktoken_counter_never_returns_zero_or_negative` | failed | Same unavailable tokenizer download / TLS certificate verification failure. |
| `tests/integration/test_llm_integration.py` (4 tests) | deselected | Integration marker is excluded by the configured default `-m 'not integration'`. |
| `tests/test_otel_export.py` | skipped | Optional `opentelemetry.sdk` dependency is not installed. |
| `tests/test_browser_tool.py` (one test) | skipped | Optional `playwright.sync_api` dependency is not installed. |

No xfailed tests or collection/runtime errors were reported. The failing
tokenizer cases were not changed because they are unrelated to Task 1. No test
showed flaky behaviour during this baseline run, so three repeat suite runs
were not required.

## Ten slowest tests

| Duration | Test |
| ---: | --- |
| 4.54 s | `tests/test_litellm_client.py::test_litellm_client_is_llm_client` |
| 2.01 s | `tests/test_mcp_transport.py::TestSSETransport::test_receive_timeout_after_endpoint` |
| 1.15 s | `tests/test_search_tools.py::test_python_regex_redos_times_out_without_hanging` |
| 1.00 s | `tests/test_standard_tools.py::test_terminal_per_call_timeout_is_capped` |
| 0.65 s | `tests/test_git_snapshot_store_isolation.py::test_parallel_snapshots_share_a_repository_lock_across_store_instances` |
| 0.51 s | `tests/test_server_eval_docker.py::test_remote_workspace_round_trip_through_agent_server` |
| 0.51 s | `tests/test_mcp_transport.py::TestSSETransport::test_full_handshake_and_call` |
| 0.51 s | `tests/test_mcp_registry.py::TestSSEConnect::test_connect_over_sse` |
| 0.51 s | `tests/test_server_eval_docker.py::test_server_rate_limits_one_client` |
| 0.51 s | `tests/test_mcp_registry.py::TestCredentials::test_sse_headers_secret_revealed_on_the_wire` |
