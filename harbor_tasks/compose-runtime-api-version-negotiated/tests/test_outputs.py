"""Tests for docker/compose#13690 — RuntimeAPIVersion refactor.

Each f2p test exercises the new RuntimeAPIVersion method via Go's testing
framework. The Go test file `runtime_api_version_extra_test.go` is copied
into pkg/compose/ before each f2p test so we can run it as part of
the package and access unexported symbols (composeService, etc.).

P2P tests intentionally REMOVE the helper test file first, so they
exercise only the repo's own files and pass on the unmodified base.
"""

import os
import shutil
import subprocess
from pathlib import Path

REPO = "/workspace/compose"
PKG = "./pkg/compose/"
EXTRA_TEST_SRC_PRIMARY = "/tests/runtime_api_version_extra_test.go"
EXTRA_TEST_DST = "/workspace/compose/pkg/compose/runtime_api_version_extra_test.go"

GO_ENV = {
    **os.environ,
    "GOFLAGS": "-mod=mod",
    "GOTOOLCHAIN": "local",
    "GOCACHE": "/root/.cache/go-build",
    "GOMODCACHE": "/go/pkg/mod",
}


def _resolve_extra_test_src() -> Path:
    p = Path(EXTRA_TEST_SRC_PRIMARY)
    if p.exists():
        return p
    alt = Path(__file__).parent / "runtime_api_version_extra_test.go"
    if alt.exists():
        return alt
    raise FileNotFoundError(
        "runtime_api_version_extra_test.go not found at /tests/ or alongside test_outputs.py"
    )


def _ensure_extra_test_installed() -> None:
    shutil.copy(_resolve_extra_test_src(), EXTRA_TEST_DST)


def _remove_extra_test() -> None:
    try:
        os.remove(EXTRA_TEST_DST)
    except FileNotFoundError:
        pass


def _go_test(run_pattern: str, timeout: int = 600) -> subprocess.CompletedProcess:
    _ensure_extra_test_installed()
    return subprocess.run(
        ["go", "test", "-count=1", "-run", run_pattern, "-timeout", "300s", PKG],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=GO_ENV,
    )


# ---------------------------------------------------------------------------
# fail-to-pass tests
# ---------------------------------------------------------------------------

def test_runtime_api_version_uses_negotiation():
    """RuntimeAPIVersion must Ping with NegotiateAPIVersion=true and return ClientVersion."""
    r = _go_test("^TestExtraRuntimeAPIVersionUsesNegotiation$")
    assert r.returncode == 0, (
        "Go test TestExtraRuntimeAPIVersionUsesNegotiation failed.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_runtime_api_version_caches_success():
    """A successful negotiation must be cached; later calls must NOT re-Ping."""
    r = _go_test("^TestExtraRuntimeAPIVersionCachesSuccess$")
    assert r.returncode == 0, (
        "Go test TestExtraRuntimeAPIVersionCachesSuccess failed.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_runtime_api_version_does_not_cache_error():
    """Failed Ping must NOT poison the cache — a retry must succeed."""
    r = _go_test("^TestExtraRuntimeAPIVersionDoesNotCacheError$")
    assert r.returncode == 0, (
        "Go test TestExtraRuntimeAPIVersionDoesNotCacheError failed.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_runtime_api_version_per_instance_cache():
    """Cache must be per-composeService instance, not package-global."""
    r = _go_test("^TestExtraRuntimeAPIVersionPerInstanceCache$")
    assert r.returncode == 0, (
        "Go test TestExtraRuntimeAPIVersionPerInstanceCache failed.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# pass-to-pass tests (run on the repo's own files, without the helper)
# ---------------------------------------------------------------------------

def test_pkg_compose_vet_clean():
    """`go vet ./pkg/compose/...` must pass on the agent's tree (catches
    receiver-copy/mutex issues and any rename leftovers in the test files)."""
    _remove_extra_test()
    r = subprocess.run(
        ["go", "vet", "./pkg/compose/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env=GO_ENV,
    )
    assert r.returncode == 0, f"Vet failed:\nSTDERR:\n{r.stderr[-2500:]}"


def test_existing_unit_tests_unrelated_pass():
    """Existing pkg/compose tests that have nothing to do with API version
    (e.g. TestContainerName, TestServiceLinks) must still pass on the
    agent's tree. This catches package-level compilation regressions."""
    _remove_extra_test()
    r = subprocess.run(
        [
            "go", "test", "-count=1",
            "-run", "^(TestContainerName|TestServiceLinks)$",
            "-timeout", "120s", PKG,
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env=GO_ENV,
    )
    assert r.returncode == 0, (
        f"Existing tests failed:\nSTDOUT:\n{r.stdout[-1500:]}\n\nSTDERR:\n{r.stderr[-1500:]}"
    )
