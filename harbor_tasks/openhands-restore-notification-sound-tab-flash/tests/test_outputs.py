"""Verifier tests for OpenHands#14049 — restore notification sound + tab flash.

Strategy: the gold PR ships its own vitest tests. Those test files live in
this verifier directory (/tests/vitest/) and are NEVER mounted into the
agent's working directory before the agent runs. At test time we copy them
into frontend/__tests__/ and invoke the project's vitest runner. The agent
must implement the required source files for those tests to pass.

Each pytest function below maps to one vitest test name and inspects a
single shared JSON result file produced by a session-scoped fixture.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/OpenHands")
FRONTEND = REPO / "frontend"
VITEST_TESTS_SRC = Path("/tests/vitest")
VITEST_RESULT = Path("/tmp/vitest-result.json")

VITEST_FILES = [
    ("__tests__/utils/browser-tab.test.ts", "browser-tab.test.ts"),
    ("__tests__/hooks/use-agent-notification.test.ts", "use-agent-notification.test.ts"),
]


def _install_vitest_files() -> list[str]:
    """Copy the verifier vitest test files into the frontend/__tests__/ tree.

    Returns the list of relative paths under FRONTEND that were installed.
    """
    installed = []
    for rel_dst, src_name in VITEST_FILES:
        dst = FRONTEND / rel_dst
        dst.parent.mkdir(parents=True, exist_ok=True)
        src = VITEST_TESTS_SRC / src_name
        if not src.exists():
            raise FileNotFoundError(f"Verifier test file missing: {src}")
        shutil.copy(src, dst)
        installed.append(rel_dst)
    return installed


@pytest.fixture(scope="session")
def vitest_results() -> dict:
    """Run vitest once for the session and return the parsed JSON result.

    If vitest fails to even produce output (e.g., import errors, source
    files missing), we synthesize a result indicating all tests failed.
    """
    if VITEST_RESULT.exists():
        VITEST_RESULT.unlink()

    rel_files = _install_vitest_files()

    cmd = [
        "npx", "--no-install", "vitest", "run",
        *rel_files,
        "--reporter=json",
        f"--outputFile={VITEST_RESULT}",
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(FRONTEND),
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "true", "NODE_OPTIONS": "--max-old-space-size=4096"},
    )

    if VITEST_RESULT.exists():
        try:
            data = json.loads(VITEST_RESULT.read_text())
        except json.JSONDecodeError:
            data = {"testResults": [], "_stdout": proc.stdout, "_stderr": proc.stderr}
    else:
        data = {
            "testResults": [],
            "_stdout": proc.stdout,
            "_stderr": proc.stderr,
            "_returncode": proc.returncode,
        }

    return data


def _vitest_test_status(results: dict, title_substring: str) -> tuple[bool, str]:
    """Return (passed, message) for the vitest test whose title contains substring."""
    for suite in results.get("testResults", []):
        for test in suite.get("assertionResults", []):
            title = test.get("title", "") or test.get("fullName", "")
            if title_substring in title:
                status = test.get("status")
                if status == "passed":
                    return True, ""
                msgs = test.get("failureMessages") or []
                return False, "\n".join(msgs)[:1500]
    err = (results.get("_stderr") or "")[-2000:]
    return False, f"vitest test '{title_substring}' not found in results.\n{err}"


# -----------------------------
# fail-to-pass: browser-tab.ts
# -----------------------------

def test_browser_tab_flashes_title(vitest_results):
    """startNotification toggles document.title between baseline and message every 1000ms."""
    ok, msg = _vitest_test_status(vitest_results, "flashes the browser tab title")
    assert ok, msg


def test_browser_tab_stop_restores_title(vitest_results):
    """stopNotification clears the interval and restores the baseline title."""
    ok, msg = _vitest_test_status(vitest_results, "stops flashing and restores original title")
    assert ok, msg


def test_browser_tab_updates_baseline_on_external_rename(vitest_results):
    """If document.title is changed externally during flashing, the flasher updates its baseline."""
    ok, msg = _vitest_test_status(vitest_results, "updates baseline when title changes")
    assert ok, msg


# -----------------------------------
# fail-to-pass: use-agent-notification
# -----------------------------------

def test_hook_starts_notification_on_finished_unfocused(vitest_results):
    """Hook calls browserTab.startNotification on transition to FINISHED when tab is not focused."""
    ok, msg = _vitest_test_status(
        vitest_results, "starts browser tab notification when agent reaches FINISHED state"
    )
    assert ok, msg


def test_hook_plays_sound_on_finished_when_enabled(vitest_results):
    """Hook plays the notification audio on FINISHED when sound notifications are enabled."""
    ok, msg = _vitest_test_status(
        vitest_results, "plays notification sound when agent reaches FINISHED state"
    )
    assert ok, msg


def test_hook_starts_on_awaiting_user_input(vitest_results):
    ok, msg = _vitest_test_status(
        vitest_results, "starts notification when agent reaches AWAITING_USER_INPUT"
    )
    assert ok, msg


def test_hook_starts_on_awaiting_user_confirmation(vitest_results):
    ok, msg = _vitest_test_status(
        vitest_results, "starts notification when agent reaches AWAITING_USER_CONFIRMATION"
    )
    assert ok, msg


def test_hook_stops_notification_on_window_focus(vitest_results):
    """Window 'focus' event handler must call browserTab.stopNotification."""
    ok, msg = _vitest_test_status(vitest_results, "stops browser tab notification when window gains focus")
    assert ok, msg


def test_hook_no_tab_flash_when_focused_but_sound_plays(vitest_results):
    """When document is focused, do not start tab flash; sound still plays."""
    ok, msg = _vitest_test_status(vitest_results, "does not start tab flash when focused")
    assert ok, msg


def test_hook_no_sound_when_disabled(vitest_results):
    """When enable_sound_notifications is false, do not call audio.play."""
    ok, msg = _vitest_test_status(vitest_results, "does not play sound when sound notifications are disabled")
    assert ok, msg


def test_hook_ignores_non_notification_states(vitest_results):
    """Hook does not fire for states like RUNNING / LOADING."""
    ok, msg = _vitest_test_status(vitest_results, "does not trigger for non-notification states")
    assert ok, msg


# ---------------------------------------------------------
# pass-to-pass: existing repo tests still pass after the fix
# ---------------------------------------------------------

def test_repo_existing_format_time_delta_passes():
    """A pre-existing repo unit test (unrelated to this PR) still passes.

    Acts as a smoke check that we haven't broken vitest or the broader test
    setup. This file already exists in the base commit and its behavior is
    independent of the agent's change."""
    target = "__tests__/utils/format-time-delta.test.ts"
    assert (FRONTEND / target).exists(), f"sanity: {target} should exist at base commit"

    proc = subprocess.run(
        ["npx", "--no-install", "vitest", "run", target, "--reporter=default"],
        cwd=str(FRONTEND),
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "true"},
    )
    tail = (proc.stdout + "\n" + proc.stderr)[-1500:]
    assert proc.returncode == 0, f"existing repo test failed:\n{tail}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_openhands_ui_build_package():
    """pass_to_pass | CI job 'Build openhands-ui' → step 'Build package'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run build'], cwd=os.path.join(REPO, './openhands-ui'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build package' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_enterprise_python_unit_tests_run_unit_tests():
    """pass_to_pass | CI job 'Enterprise Python Unit Tests' → step 'Run Unit Tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'PYTHONPATH=".:$PYTHONPATH" poetry run --project=enterprise pytest --forked -n auto -s -p no:ddtrace -p no:ddtrace.pytest_bdd -p no:ddtrace.pytest_benchmark ./enterprise/tests/unit --cov=enterprise --cov-branch'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Unit Tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_python_tests_on_linux_build_environment():
    """pass_to_pass | CI job 'Python Tests on Linux' → step 'Build Environment'"""
    r = subprocess.run(
        ["bash", "-lc", 'make build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build Environment' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_python_tests_on_linux_run_unit_tests():
    """pass_to_pass | CI job 'Python Tests on Linux' → step 'Run Unit Tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'PYTHONPATH=".:$PYTHONPATH" poetry run pytest --forked -n auto -s ./tests/unit --cov=openhands --cov-branch'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Unit Tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_python_tests_on_linux_run_runtime_tests_with_cliruntime():
    """pass_to_pass | CI job 'Python Tests on Linux' → step 'Run Runtime Tests with CLIRuntime'"""
    r = subprocess.run(
        ["bash", "-lc", 'PYTHONPATH=".:$PYTHONPATH" TEST_RUNTIME=cli poetry run pytest -n 5 --reruns 2 --reruns-delay 3 -s tests/runtime/test_bash.py --cov=openhands --cov-branch'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Runtime Tests with CLIRuntime' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_fe_unit_tests_run_typescript_compilation():
    """pass_to_pass | CI job 'FE Unit Tests' → step 'Run TypeScript compilation'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build'], cwd=os.path.join(REPO, './frontend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run TypeScript compilation' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_fe_unit_tests_run_tests_and_collect_coverage():
    """pass_to_pass | CI job 'FE Unit Tests' → step 'Run tests and collect coverage'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run test:coverage'], cwd=os.path.join(REPO, './frontend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests and collect coverage' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_package_versions_check_for_any_rev_fields_in_pyproject_to():
    """pass_to_pass | CI job 'check-package-versions' → step "Check for any 'rev' fields in pyproject.toml""""
    r = subprocess.run(
        ["bash", "-lc", "python - <<'PY'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step "Check for any 'rev' fields in pyproject.toml" failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_fe_e2e_tests_run_playwright_tests():
    """pass_to_pass | CI job 'FE E2E Tests' → step 'Run Playwright tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'npx playwright test --project=chromium'], cwd=os.path.join(REPO, './frontend'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Playwright tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_frontend_lint_typescript_compilation_and_translat():
    """pass_to_pass | CI job 'Lint frontend' → step 'Lint, TypeScript compilation, and translation checks'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run lint && npm run make-i18n && npx tsc && npm run check-translation-completeness'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint, TypeScript compilation, and translation checks' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")