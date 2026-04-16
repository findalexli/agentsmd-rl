# CI Failure Checker Is Too Slow With Many Failing Tests

## Problem

The `utils/check_bad_commit.py` script and the `.github/workflows/check_failed_tests.yml` workflow currently process all failing tests sequentially on a single GPU runner. When a CI run has many new test failures (e.g. 30-40 across multiple models), the `check_new_failures` job takes a very long time because `find_bad_commit()` does a git bisect for each failing test one at a time.

The workflow currently uses a hardcoded `run_idx: [1]` matrix, meaning it always runs on just one runner. There is even a comment in the workflow acknowledging this limitation:

> "Currently, we only run with a single runner by using `run_idx: [1]`. We might try to run with multiple runners to further reduce the false positive caused by flaky tests, which requires further processing to merge reports."

## Required Behavior

### Script: `utils/check_bad_commit.py`

The script needs to support partitioning work across multiple parallel runners:

- When environment variables `run_idx` and `n_runners` are both set, the script should only process its assigned slice of the failing tests. The partitioning must be fair: each runner gets a non-empty subset, together they cover all tests exactly once (no duplicates, no missing tests), and no single runner receives all tests. Partitioning must work for different runner counts (not just 3 — it should also work correctly with 2 or 4 runners, for example).
- When `run_idx` and `n_runners` are **not** set, the script must remain backward-compatible and process all tests as before (i.e. all tests are processed by a single invocation).
- The script must retain the existing functions `find_bad_commit` and `get_commit_info`.
- The script accepts these CLI arguments: `--start_commit`, `--end_commit`, `--file` (path to failures JSON), and `--output_file`.

**Output JSON schema:** The script writes its output (to the file given by `--output_file`) as a JSON object keyed by model name:

```json
{
  "model_a": {
    "single-gpu": [
      {"test": "tests/test_a.py::test_1", "bad_commit": "abc123", ...}
    ]
  },
  "model_b": {
    "single-gpu": [
      {"test": "tests/test_b.py::test_2", "bad_commit": "def456", ...}
    ]
  }
}
```

The top-level keys are model names. Each model value is an object with a `"single-gpu"` key whose value is a list of test-entry objects. Each entry has either a `"test"` or `"line"` key identifying the failing test, plus additional fields (e.g. `"bad_commit"`, commit info) added during processing. When partitioning is active, the output contains only the tests assigned to this runner, still keyed by their respective model names.

### Workflow: `.github/workflows/check_failed_tests.yml`

The workflow needs the following changes:

- **Setup job:** A new job (whose name contains `setup`) must run before `check_new_failures` to determine the dynamic runner matrix. The `check_new_failures` job must declare a dependency on this setup job (via `needs`).
- **Runner count input:** A new `workflow_call` input for configuring the maximum number of runners. The input name must contain both `runner` and either `max` or `num` (e.g. `max_num_runners`). It must have type `number` and include a default value.
- **Dynamic matrix in `check_new_failures`:** The `run_idx` matrix must no longer be hardcoded as `[1]`. Instead, it should be driven dynamically by the setup job's output. Each runner instance should have access to `n_runners` (e.g. via environment variable) so the script knows the total runner count.
- **Preserved structure:** The workflow must retain the `workflow_call` trigger, the required `docker` and `job` inputs, and jobs whose names contain `check_new_failures` and `process_new_failures`.
- **Merge step in `process_new_failures`:** A step whose name contains the word "merge" (case-insensitive) must correctly combine results from all parallel runners into a single merged JSON file. Specifically:
  - Per-runner output files are located in the directory `/transformers/new_failures_with_bad_commit_{job}/`, with each file named `new_failures_with_bad_commit_{job}_{i}.json` (where `{job}` is the job name from the `job` environment variable and `{i}` is the runner index).
  - The merge must read **all** runner output files (not just copy one runner's file).
  - For each model found across any runner output, collect its `"single-gpu"` test entries into one combined list.
  - Write the merged result as a JSON object keyed by model name (same schema as the per-runner output) — for example, to `/transformers/new_failures_with_bad_commit.json`.

## Code Quality

- The modified script must pass `ruff check` and `ruff format --check`.
- Do not use bare `# type: ignore` comments — always specify the error code (e.g. `# type: ignore[call-arg]`).
- Do not use `assert` for type narrowing (e.g. `assert isinstance(...)` or `assert x is not None`) — use `if ...: raise` instead.
- `check_bad_commit.py` should remain concise (under 500 lines).
