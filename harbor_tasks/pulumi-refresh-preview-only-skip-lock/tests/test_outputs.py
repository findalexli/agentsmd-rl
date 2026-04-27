"""Behavioural checks for pulumi/pulumi#22385 — `pulumi refresh
--preview-only` on the diy backend must not acquire the state lock.

Each ``def test_*`` here corresponds 1:1 to a check in eval_manifest.yaml.
The two harbor tests are added to the diy package by the Dockerfile
(``preview_only_test.go``); they exist at the base commit and run via
``go test`` regardless of whether the agent has applied the fix.
"""

from __future__ import annotations

import subprocess

REPO = "/workspace/pulumi"
DIY_PKG = "./backend/diy/..."


def _go_test(run_pattern: str, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            "go",
            "test",
            "-count=1",
            "-timeout=180s",
            f"-run={run_pattern}",
            "-v",
            DIY_PKG,
        ],
        cwd=f"{REPO}/pkg",
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_refresh_preview_only_skips_lock():
    """fail_to_pass: Refresh(PreviewOnly=true) must not check the state lock.

    A second backend pre-acquires the lock; before the fix the call returns
    "the stack is currently locked"; after the fix it does not.
    """
    r = _go_test(r"^TestRefreshPreviewOnlySkipsLockHarbor$")
    assert r.returncode == 0, (
        "Refresh with PreviewOnly=true still hits the state-lock path.\n"
        f"stdout:\n{r.stdout[-3000:]}\nstderr:\n{r.stderr[-2000:]}"
    )
    assert "PASS: TestRefreshPreviewOnlySkipsLockHarbor" in r.stdout, (
        f"Expected PASS line for harbor test in:\n{r.stdout[-1500:]}"
    )


def test_refresh_non_preview_still_locks():
    """pass_to_pass: Refresh without PreviewOnly must still acquire the lock.

    Guards against an over-broad fix that removes locking for all refresh
    calls, not just the preview variant.
    """
    r = _go_test(r"^TestRefreshNonPreviewStillLocksHarbor$")
    assert r.returncode == 0, (
        "Refresh without PreviewOnly no longer fails on a held lock — "
        "the fix must only skip locking for the preview-only path.\n"
        f"stdout:\n{r.stdout[-3000:]}\nstderr:\n{r.stderr[-2000:]}"
    )
    assert "PASS: TestRefreshNonPreviewStillLocksHarbor" in r.stdout, (
        f"Expected PASS line in:\n{r.stdout[-1500:]}"
    )


def test_diy_backend_package_tests_pass():
    """pass_to_pass: pre-existing pkg/backend/diy unit tests still green.

    Runs the upstream diy backend test suite (TestCancel, TestRemoveMakesBackups,
    lock_test.go cases, etc.) to catch regressions in unrelated code paths.
    The two harbor-injected tests are excluded from this run — they are
    measured by the dedicated f2p / p2p checks above. We only want to know
    here whether the upstream tests still hold.
    """
    r = subprocess.run(
        [
            "go",
            "test",
            "-count=1",
            "-short",
            "-timeout=300s",
            "-skip=TestRefreshPreviewOnlySkipsLockHarbor|TestRefreshNonPreviewStillLocksHarbor",
            "./backend/diy/...",
        ],
        cwd=f"{REPO}/pkg",
        capture_output=True,
        text=True,
        timeout=420,
    )
    assert r.returncode == 0, (
        "Existing diy backend tests regressed.\n"
        f"stdout:\n{r.stdout[-3000:]}\nstderr:\n{r.stderr[-2000:]}"
    )


def test_diy_backend_package_vets_clean():
    """pass_to_pass: `go vet` on pkg/backend/diy reports no issues.

    Source-level invariants the upstream CI enforces.
    """
    r = subprocess.run(
        ["go", "vet", "./backend/diy/..."],
        cwd=f"{REPO}/pkg",
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        "go vet failed on pkg/backend/diy:\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
