"""Verifier for vitess-ers-restart-stopped-io-cleanup task.

Strategy:
- The repo is checked out at the PR's base commit. The agent (or solve.sh) edits
  source files only. The test additions from the PR ship inside this verifier
  bundle and are applied with `git apply` immediately before each f2p test, so
  the new test functions exercise the agent's source changes.
- For p2p (pre-existing) tests, we make sure the test patch is NOT applied,
  so the package compiles against the agent's source changes alone.
"""
import os
import subprocess
from pathlib import Path

import pytest

REPO = "/workspace/vitess"
PKG = "./go/vt/vtctl/reparentutil/..."
ERS_TEST = "go/vt/vtctl/reparentutil/emergency_reparenter_test.go"
TEST_PATCH = "/tests/test_patch.diff"

_PATCH_MARKER = "TestEmergencyReparenterRestartsStoppedIOThreadsOnFailure"


def run(cmd, *, cwd=REPO, timeout=900, env_extra=None):
    env = os.environ.copy()
    env["CGO_ENABLED"] = "0"
    if env_extra:
        env.update(env_extra)
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          timeout=timeout, env=env)


def _test_patch_applied():
    return _PATCH_MARKER in (Path(REPO) / ERS_TEST).read_text()


def _reset_test_files():
    r = run(["git", "checkout", "--", ERS_TEST])
    assert r.returncode == 0, f"git checkout test files failed:\n{r.stderr}"


def ensure_clean_tests():
    """For p2p tests: pre-existing test files only, no PR test additions."""
    if _test_patch_applied():
        _reset_test_files()
    assert not _test_patch_applied(), "test patch still present after reset"


def ensure_patched_tests():
    """For f2p tests: PR's new test functions present."""
    if not _test_patch_applied():
        _reset_test_files()
        r = run(["git", "apply", "--whitespace=nowarn", TEST_PATCH])
        assert r.returncode == 0, (
            f"failed to apply test patch:\nstdout={r.stdout}\nstderr={r.stderr}"
        )
    assert _test_patch_applied(), "test patch did not apply"


def go_test(run_filter, *, timeout=600):
    return run([
        "go", "test", "-count=1", "-run", run_filter, "-v", PKG,
    ], timeout=timeout)


# ---------- p2p tests (must pass on base) ----------

def test_repo_vet():
    """`go vet` on the reparentutil package must keep passing."""
    ensure_clean_tests()
    r = run(["go", "vet", PKG], timeout=600)
    assert r.returncode == 0, f"go vet failed:\n{r.stderr[-2000:]}"


def test_repo_replication_tests_pass():
    """Pre-existing TestReplicaWasRunning still passes."""
    ensure_clean_tests()
    r = go_test("^TestReplicaWasRunning$", timeout=300)
    assert r.returncode == 0, (
        f"TestReplicaWasRunning regressed:\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n--- stderr ---\n{r.stderr[-1500:]}"
    )


def test_repo_existing_emergency_reparenter_tests_pass():
    """A representative pre-existing emergency_reparenter test must keep passing."""
    ensure_clean_tests()
    r = go_test("^TestEmergencyReparenter_promotionOfNewPrimary$", timeout=600)
    assert r.returncode == 0, (
        f"TestEmergencyReparenter_promotionOfNewPrimary regressed:\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n--- stderr ---\n{r.stderr[-1500:]}"
    )


# ---------- f2p tests (must FAIL on base, PASS after the fix) ----------

def test_ers_restarts_on_stop_replication_failure():
    """ERS cleanup after a partial stop-replication failure."""
    ensure_patched_tests()
    r = go_test(
        "^TestEmergencyReparenterRestartsStoppedIOThreadsOnStopReplicationFailure$",
        timeout=600,
    )
    assert r.returncode == 0, (
        f"TestEmergencyReparenterRestartsStoppedIOThreadsOnStopReplicationFailure failed:\n"
        f"--- stdout ---\n{r.stdout[-3000:]}\n--- stderr ---\n{r.stderr[-1500:]}"
    )


def test_ers_restarts_on_relay_log_timeout():
    """ERS cleanup after a relay-log apply timeout."""
    ensure_patched_tests()
    r = go_test(
        "^TestEmergencyReparenterRestartsStoppedIOThreadsOnFailure$",
        timeout=600,
    )
    assert r.returncode == 0, (
        f"TestEmergencyReparenterRestartsStoppedIOThreadsOnFailure failed:\n"
        f"--- stdout ---\n{r.stdout[-3000:]}\n--- stderr ---\n{r.stderr[-1500:]}"
    )
