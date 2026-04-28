"""
Behavioral tests for apache/superset PR #38851.

Tests the Safari race-condition fix in `getUrlParam` (superset-frontend/src/utils/urlUtils.ts):
the function must accept an optional `search` string parameter so callers
can pass React Router's `location.search` instead of relying on the
synchronously-stale `window.location.search`.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

REPO = Path("/workspace/superset")
FRONTEND = REPO / "superset-frontend"
URLUTILS_DIR = FRONTEND / "src" / "utils"
URLUTILS_TS = URLUTILS_DIR / "urlUtils.ts"
URLUTILS_TEST_TS = URLUTILS_DIR / "urlUtils.test.ts"
CHART_INDEX_TSX = FRONTEND / "src" / "pages" / "Chart" / "index.tsx"

# A jest test file we inject at test time. Lives outside the agent's view
# under /tests/, but is materialised inside the repo for jest to pick up.
INJECTED_TEST_REL = Path("src") / "utils" / "urlUtils.race.test.ts"
INJECTED_TEST_ABS = FRONTEND / INJECTED_TEST_REL

INJECTED_TEST_CONTENT = """\
/* Auto-injected by the benchmark harness; do not commit. */
import { getUrlParam } from './urlUtils';
import { URL_PARAMS } from '../constants';

describe('getUrlParam Safari race condition', () => {
  let originalLocation: Location;

  beforeEach(() => {
    originalLocation = window.location;
  });

  afterEach(() => {
    Object.defineProperty(window, 'location', {
      value: originalLocation,
      writable: true,
      configurable: true,
    });
  });

  test('reads from window.location.search by default', () => {
    Object.defineProperty(window, 'location', {
      value: { ...originalLocation, search: '?dashboard_page_id=from-window' },
      writable: true,
      configurable: true,
    });
    expect(getUrlParam(URL_PARAMS.dashboardPageId)).toBe('from-window');
  });

  test('returns null when window.location.search is stale and no override', () => {
    Object.defineProperty(window, 'location', {
      value: { ...originalLocation, search: '' },
      writable: true,
      configurable: true,
    });
    expect(getUrlParam(URL_PARAMS.dashboardPageId)).toBeNull();
  });

  test('uses provided search string instead of window.location.search', () => {
    Object.defineProperty(window, 'location', {
      value: { ...originalLocation, search: '' },
      writable: true,
      configurable: true,
    });
    expect(
      getUrlParam(URL_PARAMS.dashboardPageId, '?dashboard_page_id=correct-id'),
    ).toBe('correct-id');
  });

  test('parses a number-typed param from override search string', () => {
    Object.defineProperty(window, 'location', {
      value: { ...originalLocation, search: '' },
      writable: true,
      configurable: true,
    });
    expect(getUrlParam(URL_PARAMS.sliceId, '?slice_id=42')).toBe(42);
  });

  test('override search string takes precedence over window.location.search', () => {
    Object.defineProperty(window, 'location', {
      value: { ...originalLocation, search: '?dashboard_page_id=stale' },
      writable: true,
      configurable: true,
    });
    expect(
      getUrlParam(URL_PARAMS.dashboardPageId, '?dashboard_page_id=fresh'),
    ).toBe('fresh');
  });
});
"""


def _materialise_injected_test() -> None:
    INJECTED_TEST_ABS.write_text(INJECTED_TEST_CONTENT)


def _run_jest(test_path_rel: str, timeout: int = 600) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["NODE_ENV"] = "test"
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    env["TZ"] = "America/New_York"
    env["CI"] = "true"
    return subprocess.run(
        [
            "npx",
            "--no-install",
            "jest",
            "--no-coverage",
            "--colors=false",
            "--runInBand",
            test_path_rel,
        ],
        cwd=str(FRONTEND),
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def test_injected_race_condition_jest_suite():
    """fail_to_pass: the injected jest suite must pass after the fix.

    At base, getUrlParam ignores any second argument (the function signature
    only accepts one parameter), so the override-search assertions return null
    instead of the expected value and the suite fails.
    """
    _materialise_injected_test()
    try:
        r = _run_jest(str(INJECTED_TEST_REL))
    finally:
        if INJECTED_TEST_ABS.exists():
            INJECTED_TEST_ABS.unlink()
    assert r.returncode == 0, (
        "Injected race-condition jest suite failed.\n"
        f"--- stdout (last 4000) ---\n{r.stdout[-4000:]}\n"
        f"--- stderr (last 4000) ---\n{r.stderr[-4000:]}"
    )


def test_existing_url_utils_tests_still_pass():
    """pass_to_pass: pre-existing urlUtils.test.ts continues to pass."""
    r = _run_jest("src/utils/urlUtils.test.ts")
    assert r.returncode == 0, (
        "Existing urlUtils.test.ts regressed.\n"
        f"--- stdout (last 4000) ---\n{r.stdout[-4000:]}\n"
        f"--- stderr (last 4000) ---\n{r.stderr[-4000:]}"
    )


def test_chart_index_threads_search_into_dashboard_context_form_data():
    """fail_to_pass: ExplorePage must thread its location.search through
    getDashboardContextFormData so the per-render value (not stale
    window.location.search) is used to look up the dashboard context.

    At base, getDashboardContextFormData is invoked with no arguments and
    its definition takes no parameters; both must change for the Safari
    fix to actually reach the call site.
    """
    src = CHART_INDEX_TSX.read_text()

    # The helper definition must declare a parameter (any name; agents may
    # legitimately call it `search`, `locationSearch`, `searchString`, etc.).
    def_match = re.search(
        r"\bgetDashboardContextFormData\s*=\s*\(\s*([A-Za-z_$][\w$]*)\s*:\s*string\s*\)\s*=>",
        src,
    )
    assert def_match is not None, (
        "Expected `getDashboardContextFormData` to be defined as an arrow function "
        "taking a single `string` parameter, but did not find that signature in "
        f"{CHART_INDEX_TSX.relative_to(REPO)}.\n"
        "First 200 chars of file:\n" + src[:200]
    )
    param_name = def_match.group(1)

    # The body must propagate that parameter to getUrlParam (otherwise the
    # override is dead) — at least one getUrlParam(...) call inside the
    # helper must pass `param_name` as a second argument.
    helper_body_match = re.search(
        r"getDashboardContextFormData\s*=\s*\([^)]*\)\s*=>\s*\{(.*?)\n\};",
        src,
        re.DOTALL,
    )
    assert helper_body_match is not None, (
        "Could not locate the body of `getDashboardContextFormData`."
    )
    helper_body = helper_body_match.group(1)
    assert re.search(
        rf"getUrlParam\([^)]*,\s*{re.escape(param_name)}\b",
        helper_body,
    ), (
        f"Expected at least one `getUrlParam(..., {param_name})` call inside "
        "`getDashboardContextFormData`, but the helper does not propagate the "
        "search parameter to getUrlParam. The override is dead without it."
    )

    # The call site inside ExplorePage must pass an argument derived from the
    # router location (loc.search / location.search / locationSearch). Empty
    # invocations or hard-coded strings would defeat the fix.
    call_match = re.search(
        r"getDashboardContextFormData\(\s*([^)]+?)\s*\)",
        src,
    )
    assert call_match is not None, (
        "Could not find a call to `getDashboardContextFormData(...)` in the file."
    )
    call_arg = call_match.group(1)
    assert call_arg.strip(), (
        "`getDashboardContextFormData()` is called with no arguments — the "
        "Safari fix requires threading the per-render search string through."
    )
    assert re.search(r"\.search\b|locationSearch\b", call_arg), (
        f"`getDashboardContextFormData({call_arg})` does not reference a "
        "`.search` property or a `locationSearch` variable. The per-render "
        "search string from React Router's location must be used to avoid "
        "Safari's stale `window.location.search`."
    )


def test_get_url_param_signature_accepts_search():
    """fail_to_pass: the public `getUrlParam` must accept a second `search` argument.

    Without this, callers cannot pass through React Router's location.search
    and the Safari race condition cannot be fixed at all.
    """
    src = URLUTILS_TS.read_text()

    # The implementation signature must accept a second parameter. The exact
    # name and optionality are up to the implementer; we accept any
    # `string`-typed (optional or required) parameter in the second slot.
    impl_match = re.search(
        r"export\s+function\s+getUrlParam\s*\(\s*\{\s*name\s*,\s*type\s*\}\s*:\s*UrlParam\s*,\s*"
        r"([A-Za-z_$][\w$]*)\s*\??\s*:\s*string\s*,?\s*\)\s*:\s*unknown",
        src,
        re.DOTALL,
    )
    assert impl_match is not None, (
        "The implementation signature of `getUrlParam` must accept a second "
        "string parameter (e.g. `search?: string`). Found signature does not "
        "match this shape.\n"
        "Looked in: " + str(URLUTILS_TS.relative_to(REPO))
    )

    # The body must read from that parameter when present (fall back to
    # window.location.search when not). Verify the parameter name from the
    # signature appears in a `URLSearchParams(...)` argument.
    param_name = impl_match.group(1)
    body_match = re.search(
        r"export\s+function\s+getUrlParam\s*\([^)]*\)\s*:\s*unknown\s*\{(.*?)\n\}\n",
        src,
        re.DOTALL,
    )
    assert body_match is not None, (
        "Could not locate the body of the implementation `getUrlParam`."
    )
    body = body_match.group(1)
    assert re.search(
        rf"new\s+URLSearchParams\([^)]*\b{re.escape(param_name)}\b",
        body,
    ), (
        f"`new URLSearchParams(...)` does not reference the second parameter "
        f"`{param_name}`. The override is silently ignored."
    )


def test_repo_lint_urlutils_files():
    """pass_to_pass: oxlint passes on the files this PR touches.

    Whole-repo lint is too slow / noisy at the base commit, but the changed
    files specifically must remain clean per the project's style rules.
    """
    targets = [
        "src/utils/urlUtils.ts",
        "src/pages/Chart/index.tsx",
    ]
    r = subprocess.run(
        ["npx", "--no-install", "oxlint", "--config", "oxlint.json", "--quiet", *targets],
        cwd=str(FRONTEND),
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        "oxlint failed on the touched files.\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n"
        f"--- stderr ---\n{r.stderr[-2000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_check_python_deps_run_uv():
    """pass_to_pass | CI job 'check-python-deps' → step 'Run uv'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/uv-pip-compile.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run uv' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_python_deps_check_for_uncommitted_changes():
    """pass_to_pass | CI job 'check-python-deps' → step 'Check for uncommitted changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'echo "Full diff (for logging/debugging):"\ngit diff\n\necho "Filtered diff (excluding comments and whitespace):"\nfiltered_diff=$(git diff -U0 | grep \'^[-+]\' | grep -vE \'^[-+]{3}\' | grep -vE \'^[-+][[:space:]]*#\' | grep -vE \'^[-+][[:space:]]*$\' || true)\necho "$filtered_diff"\n\nif [[ -n "$filtered_diff" ]]; then\n  echo\n  echo "ERROR: The pinned dependencies are not up-to-date."\n  echo "Please run \'./scripts/uv-pip-compile.sh\' and commit the changes."\n  echo "More info: https://github.com/apache/superset/tree/master/requirements"\n  exit 1\nelse\n  echo "Pinned dependencies are up-to-date."\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check for uncommitted changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_sqlite_python_integration_tests_sqlite():
    """pass_to_pass | CI job 'test-sqlite' → step 'Python integration tests (SQLite)'"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/python_tests.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Python integration tests (SQLite)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")