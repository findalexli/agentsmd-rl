# CI Failure Checker Is Too Slow With Many Failing Tests

## Problem

The `utils/check_bad_commit.py` script and the `.github/workflows/check_failed_tests.yml` workflow currently process all failing tests sequentially on a single GPU runner. When a CI run has many new test failures (e.g. 30-40 across multiple models), the `check_new_failures` job takes a very long time because `find_bad_commit()` does a git bisect for each failing test one at a time.

There is even a comment in the workflow acknowledging this limitation:

> "Currently, we only run with a single runner by using `run_idx: [1]`. We might try to run with multiple runners to further reduce the false positive caused by flaky tests, which requires further processing to merge reports."

## What Needs to Change

### 1. `utils/check_bad_commit.py`

The script needs to support splitting work across multiple parallel runners:

- It should read `run_idx` and `n_runners` from environment variables
- When these are set, it should only process its assigned slice of the failing tests (partitioning evenly across runners). The partitioning must be fair: each runner gets a non-empty subset, together they cover all tests exactly once (no duplicates, no missing tests), and no single runner receives all tests
- The script must remain backward-compatible: when `run_idx` and `n_runners` are **not** set, it should process all tests as before
- To support partitioning, the per-model loop that processes failures individually needs to be restructured: first collect all `(model, test)` pairs into a flat list, then partition by runner index, then process only the assigned partition

**Output JSON schema:** The script writes its output (to the file given by `--output_file`) as a JSON object structured like this:

```json
{
  "model_a": {
    "single-gpu": [
      {"test": "tests/test_a.py::test_1", "bad_commit": "abc123", ...}
    ]
  },
  "model_b": {
    "single-gpu": [
      {"line": "tests/test_b.py::test_2", "bad_commit": "def456", ...}
    ]
  }
}
```

The top-level keys are model names. Each model value is an object with a `"single-gpu"` key whose value is a list of test-entry objects. Each entry has either a `"test"` or `"line"` key identifying the failing test, plus additional fields (e.g. `"bad_commit"`, commit info) added during processing. When partitioning is active, the output contains only the tests assigned to this runner, still keyed by their respective model names.

The script accepts these CLI arguments: `--start_commit`, `--end_commit`, `--file` (path to failures JSON), and `--output_file`.

### 2. `.github/workflows/check_failed_tests.yml`

The workflow needs several changes:

- **Add a setup job** (running on a cheap non-GPU runner like `ubuntu-22.04`) that runs before the GPU jobs to determine the dynamic runner matrix. The `check_new_failures` job should depend on this setup job.
- **Add a `max_num_runners` workflow input** with type `number` and a default value, so callers can configure the parallelism level.
- **Update `check_new_failures`** to use a dynamic matrix (instead of the current hardcoded `run_idx: [1]`) driven by the setup job's output. Pass `n_runners` as an env var to each runner. Since the setup job now handles the check for whether failures exist, the per-step conditions guarding against the "no failures" case within this job can be removed — the job-level condition handles it.
- **Update the merge step** in the `process_new_failures` job to correctly combine results from all parallel runners into a single JSON file. The merge must:
  - Read output files from **all** runners (not just one runner's file)
  - For each model found across any runner output, collect its `"single-gpu"` test entries into one combined list
  - Write the merged result as a JSON object keyed by model name, where each model has a `"single-gpu"` list containing the union of entries from all runners
  - The merge step must NOT simply copy a single runner's output file as-is

## Relevant Files

- `utils/check_bad_commit.py` — the bisect script
- `.github/workflows/check_failed_tests.yml` — the reusable workflow
