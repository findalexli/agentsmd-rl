"""Behaviour tests for the SignalCancellation parallelization PR.

Each test_* function corresponds to a check in eval_manifest.yaml. The Go
test file alongside this script is copied into the Pulumi plugin package and
exercised with `go test`.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/pulumi")
PKG_REL = "go/common/resource/plugin"
PKG_DIR = REPO / "sdk" / PKG_REL
TEST_FILE_NAME = "zz_signal_cancellation_test.go"

# Make Go's CLI quieter and offline-friendly during the test run.
GO_ENV = {
    **os.environ,
    "GOFLAGS": "-mod=mod",
    "GOMODCACHE": os.environ.get("GOMODCACHE", "/go/pkg/mod"),
    "CGO_ENABLED": "0",
}


def _install_test_file() -> None:
    """Copy the canonical Go test file into the package under test."""
    src = Path("/tests") / TEST_FILE_NAME
    if not src.exists():
        # Fallback for local invocations during scaffold development.
        src = Path(__file__).resolve().parent / TEST_FILE_NAME
    dst = PKG_DIR / TEST_FILE_NAME
    shutil.copyfile(src, dst)


def _run_go_test(run_pattern: str, timeout: int) -> subprocess.CompletedProcess:
    _install_test_file()
    cmd = [
        "go", "test",
        "-count=1",
        f"-timeout={timeout}s",
        "-run", run_pattern,
        f"./{PKG_REL}/...",
    ]
    return subprocess.run(
        cmd,
        cwd=REPO / "sdk",
        env=GO_ENV,
        capture_output=True,
        text=True,
        timeout=timeout + 30,
    )


def test_signal_cancellation_resource_and_analyzer_concurrent():
    """Resource provider and analyzer cancellations run concurrently in phase 1.

    A barrier of size 2 forces the two cancel callbacks to be active at the
    same time. With sequential iteration the goroutine running
    SignalCancellation deadlocks; with goroutine fan-out it completes.
    """
    r = _run_go_test("^TestSignalCancellation_ResourceAndAnalyzerConcurrent$", 60)
    assert r.returncode == 0, (
        "TestSignalCancellation_ResourceAndAnalyzerConcurrent failed:\n"
        + r.stdout[-2000:] + "\n" + r.stderr[-2000:]
    )


def test_signal_cancellation_language_runtimes_concurrent():
    """Language runtime cancellations run concurrently with each other."""
    r = _run_go_test("^TestSignalCancellation_LanguageRuntimesConcurrent$", 60)
    assert r.returncode == 0, (
        "TestSignalCancellation_LanguageRuntimesConcurrent failed:\n"
        + r.stdout[-2000:] + "\n" + r.stderr[-2000:]
    )


def test_signal_cancellation_passes_deadline_context():
    """Resource and analyzer plugins must receive a context with a deadline."""
    r = _run_go_test("^TestSignalCancellation_DeadlineContext$", 60)
    assert r.returncode == 0, (
        "TestSignalCancellation_DeadlineContext failed:\n"
        + r.stdout[-2000:] + "\n" + r.stderr[-2000:]
    )


def test_existing_plugin_unit_tests():
    """Pass-to-pass: pre-existing host tests in the same package still pass."""
    r = _run_go_test(
        "^(TestIsLocalPluginPath|TestClosePanic|TestNewDefaultHost_LoaderAddress"
        "|TestNewDefaultHost_PackagesResolution"
        "|TestNewDefaultHost_BothPluginsAndPackages)$",
        180,
    )
    assert r.returncode == 0, (
        "Existing host tests regressed:\n"
        + r.stdout[-2000:] + "\n" + r.stderr[-2000:]
    )


def test_plugin_package_builds():
    """Pass-to-pass: the plugin package compiles cleanly with the test file added."""
    _install_test_file()
    r = subprocess.run(
        ["go", "build", f"./{PKG_REL}/..."],
        cwd=REPO / "sdk",
        env=GO_ENV,
        capture_output=True,
        text=True,
        timeout=240,
    )
    assert r.returncode == 0, f"go build failed:\n{r.stderr}\n{r.stdout}"
    # And the test file itself must compile in test mode.
    r = subprocess.run(
        ["go", "test", "-count=1", "-run=^$", f"./{PKG_REL}/..."],
        cwd=REPO / "sdk",
        env=GO_ENV,
        capture_output=True,
        text=True,
        timeout=240,
    )
    assert r.returncode == 0, f"test compile failed:\n{r.stderr}\n{r.stdout}"
