# Make `dev/check_whitespace_only.py` resilient to transient HTTP failures

The CI step that flags whitespace-only file changes is implemented as a
small Python script in `dev/check_whitespace_only.py`. It makes two HTTP
calls to `github.com` / `api.github.com`:

* `get_pr_diff(owner, repo, pull_number)` — fetches the PR `.diff`.
* `github_api_request(url, accept)` — used by `get_pr_labels(...)`.

Both currently call `urllib.request.urlopen(...)` once with no recovery
path. When GitHub returns a transient `5xx` error (e.g. `503 Service
Unavailable`) or the network connection drops (`URLError`), the whole
CI job fails on a flake.

## What you need to fix

Make `get_pr_diff` and `github_api_request` resilient to transient
failures by retrying with exponential backoff. The script is the only
file that should change. The CLI interface, `parse_diff`'s logic, the
GitHub Actions workflow, and every other function must stay the same.

### Required behaviour

1. **Up to 3 attempts total.** The very first call counts as attempt 1;
   after a retryable failure the script may try again at most 2 more
   times (3 total).

2. **Exponential backoff between retries.** Sleep `2**i` seconds before
   retry attempt `i+1`, where `i` is the zero-indexed number of failures
   so far. Concretely:
   * after the 1st failure, sleep `1` second, then retry;
   * after the 2nd failure, sleep `2` seconds, then retry;
   * after the 3rd failure, give up and re-raise the last exception
     (no `4`-second sleep — the third attempt is the last, so there is
     nothing left to sleep before).

3. **Retryable vs non-retryable classification.**
   * `urllib.error.HTTPError` with `code >= 500` → retryable.
   * `urllib.error.HTTPError` with `code < 500` (e.g. `403`, `404`) →
     **not** retryable — re-raise immediately on the first failure with
     no sleep and no further attempts.
   * `urllib.error.URLError` (any non-HTTP URL error, e.g. DNS failure
     or connection refused) → retryable.
   * Any other exception type (e.g. `ValueError`) → **not** retryable;
     re-raise immediately.

   Note: `HTTPError` is a subclass of `URLError`, so the order in which
   you classify them matters — handle `HTTPError` before the generic
   `URLError` case.

4. On a retry-eligible failure that has not exhausted the attempt
   budget, the script should sleep, then call `urllib.request.urlopen`
   again with the same `Request` object.

5. On success, return the response body as a UTF-8 decoded `str`, just
   as the original code did.

### What stays the same

* The 30-second per-call timeout passed to `urlopen`.
* The CLI flags (`--repo`, `--pr`) and the script's exit codes.
* The `parse_diff(...)` function and its whitespace-detection logic.
* The `.github/workflows/lint.yml` workflow file.
* `BYPASS_LABEL = "allow-whitespace-only"` and the bypass-label flow.

## How your fix is checked

Tests load the script as a Python module and patch
`urllib.request.urlopen` and `time.sleep` to drive each scenario:

* A 503 followed by a 200 must return the 200 body and have invoked
  `urlopen` exactly twice.
* A 404 must propagate as `urllib.error.HTTPError` after exactly one
  `urlopen` call with zero sleeps.
* Three consecutive 503s must raise `HTTPError(503)` with `urlopen`
  called exactly 3 times and `time.sleep` called exactly 2 times.
* When backoff sleeps are observed, the durations must be `[1, 2]`
  (in that order).
* A `urllib.error.URLError` followed by a 200 must succeed.
* A non-retryable exception type (`ValueError`) must propagate after a
  single `urlopen` call with no sleeps.
* `parse_diff(...)` must continue to flag whitespace-only diffs and
  ignore real code changes.
* The script's `--help` must still exit 0.

## Code Style Requirements

`dev/check_whitespace_only.py` is checked by **`ruff`** (lint and
format) using the repo's existing configuration in `pyproject.toml`.
Both `ruff check dev/check_whitespace_only.py` and
`ruff format --check dev/check_whitespace_only.py` must pass after your
change.

The repository's `CLAUDE.md` requires top-level imports — any new
modules you need (e.g. `time`, `urllib.error`) should be imported at
the top of the file, not lazily inside functions, unless a lazy import
is genuinely necessary.
