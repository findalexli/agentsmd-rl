# CI Failure Checker Is Too Slow With Many Failing Tests

## Problem

The `utils/check_bad_commit.py` script and the `.github/workflows/check_failed_tests.yml` workflow currently process all failing tests sequentially on a single GPU runner. When a CI run has many new test failures (e.g. 30-40 across multiple models), the `check_new_failures` job takes a very long time because `find_bad_commit()` does a git bisect for each failing test one at a time.

There is even a comment in the workflow acknowledging this limitation:

> "Currently, we only run with a single runner by using `run_idx: [1]`. We might try to run with multiple runners to further reduce the false positive caused by flaky tests, which requires further processing to merge reports."

## What Needs to Change

### 1. `utils/check_bad_commit.py`

The script needs to support splitting work across multiple parallel runners:

- It should read `run_idx` and `n_runners` from environment variables
- When these are set, it should only process its assigned slice of the failing tests (partitioning evenly across runners)
- The per-model loop that processes failures individually needs to be restructured: first collect all `(model, test)` pairs into a flat list, then partition by runner index, then process only the assigned partition
- The output format should reflect which tests this runner actually processed (keyed by model name, with only the `single-gpu` failures this runner handled)

### 2. `.github/workflows/check_failed_tests.yml`

The workflow needs three changes:

- **Add a setup job** (`setup_check_new_failures`) that runs on a cheap `ubuntu-22.04` runner before the GPU jobs. It should download the `ci_results` artifact, read `new_failures.json`, count the total number of single-gpu test failures across all models, and compute how many runners to use (capped at a configurable maximum, with roughly 10 tests per runner). It outputs a JSON matrix array and the runner count.
- **Update `check_new_failures`** to depend on the setup job, use the dynamic matrix, pass `n_runners` as an env var, and remove the old `check_file` step (the setup job now handles the "file exists?" check via its `process` output). Remove all the `if: ${{ env.process == 'true' }}` conditions from subsequent steps since the job only runs when `process == 'true'`.
- **Update the merge step** in `process_new_failures_with_commit_info` to merge results from all runners (glob for `*_*.json` files) instead of just copying the single `_1.json` file. The merge should combine test results per model across all runner output files.

Also add a new workflow input `max_num_runners` (number type, default 4) so callers can configure the parallelism level.

## Relevant Files

- `utils/check_bad_commit.py` — the bisect script (main block starting around line 308)
- `.github/workflows/check_failed_tests.yml` — the reusable workflow
