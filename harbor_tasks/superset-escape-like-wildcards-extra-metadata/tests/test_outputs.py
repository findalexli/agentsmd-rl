"""Held-out tests for apache/superset PR #38738.

The PR fixes ``ReportScheduleDAO.find_by_extra_metadata`` so that ``%`` and
``_`` in the slug are treated as literal characters, not SQL ``LIKE``
wildcards. We invoke the repo's own pytest harness against held-out test
cases that the gold patch's tests do not cover (different slug values and
fixtures), so this scaffold passes only when the contains/autoescape fix is
in place — not when the agent merely copy-pastes the gold tests.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/superset")
HELD_OUT_SRC = Path("/tests/held_out_extra_metadata_test.py")
# Place the held-out test file directly under tests/unit_tests so it picks
# up the existing conftest.py (session/app fixtures) without depending on a
# subdirectory the gold patch creates.
HELD_OUT_DEST = REPO / "tests/unit_tests/held_out_extra_metadata_test.py"


def _ensure_held_out_test_present() -> None:
    HELD_OUT_DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HELD_OUT_SRC, HELD_OUT_DEST)


def _run_pytest(test_node_id: str, timeout: int = 300) -> subprocess.CompletedProcess:
    _ensure_held_out_test_present()
    return subprocess.run(
        [
            "pytest",
            "-xvs",
            "--no-header",
            "-p",
            "no:cacheprovider",
            f"tests/unit_tests/held_out_extra_metadata_test.py::{test_node_id}",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _run_pytest_pr(test_node_id: str, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run a pytest node from the PR-added test file (created by the gold patch)."""
    return subprocess.run(
        [
            "pytest",
            "-xvs",
            "--no-header",
            "-p",
            "no:cacheprovider",
            f"tests/unit_tests/daos/test_report_dao.py::{test_node_id}",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _format(r: subprocess.CompletedProcess) -> str:
    tail_out = "\n".join(r.stdout.splitlines()[-80:])
    tail_err = "\n".join(r.stderr.splitlines()[-40:])
    return f"returncode={r.returncode}\n--- STDOUT ---\n{tail_out}\n--- STDERR ---\n{tail_err}"


# === Held-out fail_to_pass tests ===


def test_percent_in_slug_must_be_literal() -> None:
    """f2p — slug 'abc%xyz' must not also match 'abcZZxyz'."""
    r = _run_pytest("test_percent_in_slug_must_be_literal")
    assert r.returncode == 0, _format(r)


def test_underscore_in_slug_must_be_literal() -> None:
    """f2p — slug 'p_q' must not also match 'pXq'."""
    r = _run_pytest("test_underscore_in_slug_must_be_literal")
    assert r.returncode == 0, _format(r)


def test_trailing_percent_no_wildcard() -> None:
    """f2p — slug 'foo%' must not match 'foobar'."""
    r = _run_pytest("test_trailing_percent_no_wildcard")
    assert r.returncode == 0, _format(r)


# === Held-out pass_to_pass tests ===


def test_basic_substring_match_still_works() -> None:
    """p2p — a vanilla slug must still find its row after the fix."""
    r = _run_pytest("test_basic_substring_match_still_works")
    assert r.returncode == 0, _format(r)


def test_no_match_returns_empty_list() -> None:
    """p2p — slug not present anywhere returns []."""
    r = _run_pytest("test_no_match_returns_empty_list")
    assert r.returncode == 0, _format(r)


# === PR-added fail_to_pass tests (test file created by gold patch) ===


def test_pr_added_test_find_by_extra_metadata_returns_matching_rep() -> None:
    """f2p — PR test: basic matching works after fix."""
    r = _run_pytest_pr("test_find_by_extra_metadata_returns_matching_reports")
    assert r.returncode == 0, _format(r)


def test_pr_added_test_find_by_extra_metadata_returns_empty_when_n() -> None:
    """f2p — PR test: no-match slug returns empty list."""
    r = _run_pytest_pr("test_find_by_extra_metadata_returns_empty_when_no_match")
    assert r.returncode == 0, _format(r)


def test_pr_added_test_find_by_extra_metadata_escapes_percent_wild() -> None:
    """f2p — PR test: '%' in slug is treated as literal, not LIKE wildcard."""
    r = _run_pytest_pr("test_find_by_extra_metadata_escapes_percent_wildcard")
    assert r.returncode == 0, _format(r)


def test_pr_added_test_find_by_extra_metadata_escapes_underscore_w() -> None:
    """f2p — PR test: '_' in slug is treated as literal, not LIKE wildcard."""
    r = _run_pytest_pr("test_find_by_extra_metadata_escapes_underscore_wildcard")
    assert r.returncode == 0, _format(r)


# === Scoped CI regression test (pass_to_pass) ===


def test_existing_report_dao_unit_tests_still_pass() -> None:
    """p2p — existing daos and report-command unit tests pass after the fix."""
    r = subprocess.run(
        [
            "python3", "-m", "pytest",
            "tests/unit_tests/daos/",
            "tests/unit_tests/commands/report/",
            "-x", "--no-header", "-p", "no:cacheprovider",
            "-q",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, _format(r)
