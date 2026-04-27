"""Pytest harness that runs the dashboard's vitest tests for this scaffold.

Each pytest function maps 1:1 to a check id in ``eval_manifest.yaml``.

The vitest test file is shipped under ``/tests/team_multi_select.test.tsx``
and copied into the dashboard's ``tests/`` directory so vitest's project
config (path aliases, setup file, jsdom env) applies.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/litellm")
DASHBOARD = REPO / "ui/litellm-dashboard"

# Where our vitest test gets dropped (must be under DASHBOARD for the
# project's vitest.config.ts ``include`` glob to match).
SCAFFOLD_TEST_REL = "tests/_scaffold_team_multi_select.test.tsx"
SCAFFOLD_TEST_ABS = DASHBOARD / SCAFFOLD_TEST_REL
SCAFFOLD_RESULTS = DASHBOARD / "_scaffold_results.json"

THIS_DIR = Path(__file__).parent


@pytest.fixture(scope="session", autouse=True)
def _provision_scaffold_test():
    """Copy the vitest test into the dashboard so vitest can run it."""
    src = THIS_DIR / "team_multi_select.test.tsx"
    SCAFFOLD_TEST_ABS.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, SCAFFOLD_TEST_ABS)
    yield
    SCAFFOLD_TEST_ABS.unlink(missing_ok=True)
    SCAFFOLD_RESULTS.unlink(missing_ok=True)


@pytest.fixture(scope="session")
def vitest_results(_provision_scaffold_test) -> dict:
    """Run vitest once and return the parsed JSON report."""
    SCAFFOLD_RESULTS.unlink(missing_ok=True)
    proc = subprocess.run(
        [
            "npx",
            "vitest",
            "run",
            SCAFFOLD_TEST_REL,
            "--reporter=json",
            f"--outputFile={SCAFFOLD_RESULTS.name}",
        ],
        cwd=str(DASHBOARD),
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "1", "NO_COLOR": "1"},
    )
    if not SCAFFOLD_RESULTS.exists():
        # vitest occasionally writes into a sub-path or skips writing on
        # collection failure.  Surface stderr/stdout so we can tell what
        # went wrong, then return an empty payload — every behavioural
        # assertion will fail, which is the correct f2p behaviour at base.
        return {
            "_collection_failure": True,
            "stdout": proc.stdout[-4000:],
            "stderr": proc.stderr[-4000:],
            "returncode": proc.returncode,
            "testResults": [],
        }
    return json.loads(SCAFFOLD_RESULTS.read_text())


def _vitest_status(results: dict, title_substring: str) -> str:
    """Return the status of the first vitest assertion whose title contains
    the given substring."""
    for tf in results.get("testResults", []):
        for assertion in tf.get("assertionResults", []):
            full = (assertion.get("fullName") or "") + " " + (
                assertion.get("title") or ""
            )
            if title_substring in full:
                return assertion.get("status", "unknown")
    return "missing"


def _assert_vitest_pass(results: dict, title_substring: str) -> None:
    status = _vitest_status(results, title_substring)
    if status == "passed":
        return
    debug = (
        f"\nvitest assertion '{title_substring}' had status={status!r}.\n"
        f"collection_failure={results.get('_collection_failure')}\n"
        f"vitest stderr (tail): {results.get('stderr','')[-1500:]}\n"
        f"vitest stdout (tail): {results.get('stdout','')[-1500:]}\n"
    )
    raise AssertionError(debug)


# --- f2p (fail-to-pass): each maps to a vitest 'it' block ----------------


def test_team_multi_select_renders_multi_select(vitest_results):
    _assert_vitest_pass(vitest_results, "should render an antd multi-select")


def test_team_multi_select_has_search_input(vitest_results):
    _assert_vitest_pass(
        vitest_results, "should enable searching with a real input"
    )


def test_team_multi_select_calls_use_infinite_teams(vitest_results):
    _assert_vitest_pass(
        vitest_results, "should call useInfiniteTeams with the page size"
    )


def test_team_multi_select_renders_placeholder(vitest_results):
    _assert_vitest_pass(
        vitest_results, "should render the placeholder for searching teams"
    )


def test_team_multi_select_renders_team_options(vitest_results):
    _assert_vitest_pass(
        vitest_results, "should expose team aliases in the popup options"
    )


def test_team_multi_select_does_not_import_tremor(vitest_results):
    _assert_vitest_pass(
        vitest_results, "should not import any tremor module"
    )


def test_entity_usage_team_renders_filter_by_team(vitest_results):
    _assert_vitest_pass(
        vitest_results,
        "should show the 'Filter by team' label and disable the legacy filter UI",
    )


def test_entity_usage_non_team_no_filter_by_team(vitest_results):
    _assert_vitest_pass(
        vitest_results,
        "should not show the 'Filter by team' label for non-team entity types",
    )


# --- p2p (pass-to-pass): existing repo tests ------------------------------


def test_p2p_spend_by_provider_tests():
    """A sibling test file in the same dir must still pass."""
    proc = subprocess.run(
        [
            "npx",
            "vitest",
            "run",
            "src/components/UsagePage/components/EntityUsage/SpendByProvider.test.tsx",
        ],
        cwd=str(DASHBOARD),
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "1", "NO_COLOR": "1"},
    )
    assert proc.returncode == 0, (
        "SpendByProvider.test.tsx failed:\n"
        f"stdout: {proc.stdout[-2000:]}\nstderr: {proc.stderr[-2000:]}"
    )


def test_p2p_team_dropdown_unchanged():
    """The single-select TeamDropdown component should still be the
    component used elsewhere — i.e. team_dropdown.tsx still renders an
    antd Select with mode != 'multiple'."""
    src = (
        DASHBOARD / "src/components/common_components/team_dropdown.tsx"
    ).read_text()
    # Single-select TeamDropdown does not declare mode="multiple".
    assert 'mode="multiple"' not in src
