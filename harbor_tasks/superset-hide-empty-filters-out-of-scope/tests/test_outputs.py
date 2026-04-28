"""Behavioral tests for apache/superset PR #39201.

Verifies that the "Filters out of scope" UI section is hidden when there are
no out-of-scope filters, instead of being rendered as a disabled
'Filters out of scope (0)' placeholder.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess

REPO = "/workspace/superset"
FRONTEND = f"{REPO}/superset-frontend"
ORACLE_DIR = f"{FRONTEND}/src/__oracle_check__"
ORACLE_FILE = f"{ORACLE_DIR}/oracle.test.tsx"
TESTS_DIR = "/tests"
JEST_TIMEOUT = 240
JEST_ENV = {**os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"}


def _setup_oracle() -> None:
    os.makedirs(ORACLE_DIR, exist_ok=True)
    src = os.path.join(TESTS_DIR, "oracle.test.tsx")
    shutil.copy(src, ORACLE_FILE)


def _run_jest(test_path: str, timeout: int = JEST_TIMEOUT,
              extra_args: list[str] | None = None) -> dict:
    """Run jest on `test_path`, return parsed JSON aggregate result."""
    cmd = ["npx", "jest", test_path, "--silent", "--json"]
    if extra_args:
        cmd.extend(extra_args)
    r = subprocess.run(
        cmd,
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=JEST_ENV,
    )
    try:
        result = json.loads(r.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Could not parse jest JSON output (rc={r.returncode}).\n"
            f"stdout tail:\n{r.stdout[-1500:]}\n"
            f"stderr tail:\n{r.stderr[-1500:]}"
        ) from exc
    result["_rc"] = r.returncode
    result["_stderr_tail"] = r.stderr[-1500:]
    return result


def _failed_test_summaries(result: dict) -> list[str]:
    summaries: list[str] = []
    for suite in result.get("testResults", []):
        for assertion in suite.get("assertionResults", []):
            if assertion.get("status") == "failed":
                msg = "\n".join(assertion.get("failureMessages", []))[:600]
                summaries.append(
                    f"  - {assertion.get('fullName')}\n{msg}"
                )
    return summaries


def test_oracle_filters_out_of_scope_visibility() -> None:
    """Oracle (f2p): the FiltersDropdownContent component must hide the
    "Filters out of scope" section when filtersOutOfScope is empty, render
    it when at least one filter is out of scope, and respect showCollapsePanel.
    """
    _setup_oracle()
    result = _run_jest("src/__oracle_check__/oracle.test.tsx")
    failed = result.get("numFailedTests", -1)
    passed = result.get("numPassedTests", 0)
    if failed != 0:
        details = "\n".join(_failed_test_summaries(result))
        raise AssertionError(
            f"Oracle: {failed} failing test(s), {passed} passing.\n{details}"
        )
    assert passed == 3, (
        f"Oracle: expected 3 passing tests (empty / populated / no-panel), "
        f"got {passed}."
    )


def test_repo_actionbuttons_regression() -> None:
    """p2p (repo test): ActionButtons.test.tsx must keep passing after the fix."""
    result = _run_jest(
        "src/dashboard/components/nativeFilters/FilterBar/ActionButtons/ActionButtons.test.tsx"
    )
    failed = result.get("numFailedTests", -1)
    if failed != 0:
        details = "\n".join(_failed_test_summaries(result))
        raise AssertionError(
            f"ActionButtons regression: {failed} failing test(s).\n{details}"
        )
    assert result.get("numPassedTests", 0) >= 4, (
        f"ActionButtons: expected at least 4 passing tests, got "
        f"{result.get('numPassedTests')}."
    )


def test_repo_filtercontrols_suite_passes() -> None:
    """p2p (repo test): FilterControls.test.tsx is a regression suite for the
    component that holds the fix. It must still pass overall — at gold it
    contains the new test added by the PR (13 tests), at base it has 12.
    Both must pass.
    """
    result = _run_jest(
        "src/dashboard/components/nativeFilters/FilterBar/FilterControls/FilterControls.test.tsx"
    )
    failed = result.get("numFailedTests", -1)
    if failed != 0:
        details = "\n".join(_failed_test_summaries(result))
        raise AssertionError(
            f"FilterControls regression: {failed} failing test(s).\n{details}"
        )
    assert result.get("numPassedTests", 0) >= 12, (
        f"FilterControls: expected at least 12 passing tests, got "
        f"{result.get('numPassedTests')}."
    )


def test_ci_frontend_check_translations_lint() -> None:
    """p2p | CI job 'frontend-check-translations' — translation build/lint."""
    r = subprocess.run(
        ["bash", "-lc", "npm run build-translation"],
        cwd=FRONTEND,
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"CI step 'build-translation' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


# --- PR-added fail_to_pass tests (run specific tests added by the gold patch) ---

def test_pr_added_does_not_render() -> None:
    """f2p | PR added test 'does not render ...' in FilterControls.test.tsx."""
    result = _run_jest(
        "src/dashboard/components/nativeFilters/FilterBar/FilterControls/FilterControls.test.tsx",
        extra_args=["-t", r"all filters are in scope"],
    )
    failed = result.get("numFailedTests", -1)
    if failed != 0:
        details = "\n".join(_failed_test_summaries(result))
        raise AssertionError(
            f"PR-added test 'does not render' (FilterControls): "
            f"{failed} failing.\n{details}"
        )
    assert result.get("numPassedTests", 0) >= 1, (
        f"Expected at least 1 passing test matching 'all filters are in scope' "
        f"in FilterControls.test.tsx, got {result.get('numPassedTests', 0)}."
    )


def test_pr_added_does_not_render_2() -> None:
    """f2p | PR added test 'does not render ...' in FiltersDropdownContent.test.tsx."""
    result = _run_jest(
        "src/dashboard/components/nativeFilters/FilterBar/FiltersDropdownContent/FiltersDropdownContent.test.tsx",
        extra_args=["-t", r"does not render"],
    )
    failed = result.get("numFailedTests", -1)
    if failed != 0:
        details = "\n".join(_failed_test_summaries(result))
        raise AssertionError(
            f"PR-added test 'does not render' (FiltersDropdownContent): "
            f"{failed} failing.\n{details}"
        )
    assert result.get("numPassedTests", 0) >= 2, (
        f"Expected at least 2 passing tests matching 'does not render' "
        f"in FiltersDropdownContent.test.tsx, got {result.get('numPassedTests', 0)}."
    )


def test_pr_added_renders() -> None:
    """f2p | PR added test 'renders ...' in FiltersDropdownContent.test.tsx."""
    result = _run_jest(
        "src/dashboard/components/nativeFilters/FilterBar/FiltersDropdownContent/FiltersDropdownContent.test.tsx",
        extra_args=["-t", r"renders"],
    )
    failed = result.get("numFailedTests", -1)
    if failed != 0:
        details = "\n".join(_failed_test_summaries(result))
        raise AssertionError(
            f"PR-added test 'renders' (FiltersDropdownContent): "
            f"{failed} failing.\n{details}"
        )
    assert result.get("numPassedTests", 0) >= 1, (
        f"Expected at least 1 passing test matching 'renders' "
        f"in FiltersDropdownContent.test.tsx, got {result.get('numPassedTests', 0)}."
    )
