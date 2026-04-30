"""Behavioral checks for docker/compose#13684 Tar.Sync() stat-error handling.

The buggy `Tar.Sync()` checks only for `fs.ErrNotExist` and silently treats
every other stat error (EACCES, EIO, ENOTDIR, ...) as a copyable path. The
correct three-way branch is:
    err == nil           → add to copy list
    fs.ErrNotExist       → add to delete list
    any other error      → return immediately, wrapping the original cause

Tests are executed by invoking `go test` on the upstream repo at
/workspace/compose. The Go test file (tar_test.go) content is embedded
below and written into the repo before each invocation, so behavior is
exercised on both the unfixed base commit and the fixed gold image.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/compose")
SYNC_PKG = REPO / "internal" / "sync"
GO_TEST_FILE_DST = SYNC_PKG / "tar_test.go"


# ── Upstream Go unit tests (PR #13684) ──────────────────────────────────────
# Embedded here so the tests/ directory contains only the harness files.
TAR_TEST_GO = r'''/*
   Copyright 2023 Docker Compose CLI authors

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

package sync

import (
	"context"
	"io"
	"os"
	"path/filepath"
	"runtime"
	"testing"

	"github.com/moby/moby/api/types/container"
	"gotest.tools/v3/assert"
	"gotest.tools/v3/assert/cmp"
)

// fakeLowLevelClient records calls made to it for test assertions.
type fakeLowLevelClient struct {
	containers []container.Summary
	execCmds   [][]string
	untarCount int
}

func (f *fakeLowLevelClient) ContainersForService(_ context.Context, _ string, _ string) ([]container.Summary, error) {
	return f.containers, nil
}

func (f *fakeLowLevelClient) Exec(_ context.Context, _ string, cmd []string, _ io.Reader) error {
	f.execCmds = append(f.execCmds, cmd)
	return nil
}

func (f *fakeLowLevelClient) Untar(_ context.Context, _ string, _ io.ReadCloser) error {
	f.untarCount++
	return nil
}

func TestSync_ExistingPath(t *testing.T) {
	tmpDir := t.TempDir()
	existingFile := filepath.Join(tmpDir, "exists.txt")
	assert.NilError(t, os.WriteFile(existingFile, []byte("data"), 0o644))

	client := &fakeLowLevelClient{
		containers: []container.Summary{{ID: "ctr1"}},
	}
	tar := NewTar("proj", client)

	err := tar.Sync(t.Context(), "svc", []*PathMapping{
		{HostPath: existingFile, ContainerPath: "/app/exists.txt"},
	})

	assert.NilError(t, err)
	assert.Equal(t, client.untarCount, 1, "existing path should be copied via Untar")
	assert.Equal(t, len(client.execCmds), 0, "no delete command expected for existing path")
}

func TestSync_NonExistentPath(t *testing.T) {
	client := &fakeLowLevelClient{
		containers: []container.Summary{{ID: "ctr1"}},
	}
	tar := NewTar("proj", client)

	err := tar.Sync(t.Context(), "svc", []*PathMapping{
		{HostPath: "/no/such/file", ContainerPath: "/app/gone.txt"},
	})

	assert.NilError(t, err)
	assert.Equal(t, len(client.execCmds), 1, "should issue a delete command")
	assert.DeepEqual(t, client.execCmds[0], []string{"rm", "-rf", "/app/gone.txt"})
}

func TestSync_StatPermissionError(t *testing.T) {
	if runtime.GOOS == "windows" {
		t.Skip("permission-based test not reliable on Windows")
	}
	if os.Getuid() == 0 {
		t.Skip("test requires non-root to trigger EACCES")
	}

	tmpDir := t.TempDir()
	restrictedDir := filepath.Join(tmpDir, "noaccess")
	assert.NilError(t, os.Mkdir(restrictedDir, 0o700))
	targetFile := filepath.Join(restrictedDir, "secret.txt")
	assert.NilError(t, os.WriteFile(targetFile, []byte("data"), 0o644))
	// Remove all permissions on the parent directory so stat on the child fails with EACCES.
	assert.NilError(t, os.Chmod(restrictedDir, 0o000))
	t.Cleanup(func() {
		// Restore permissions so t.TempDir() cleanup can remove it.
		_ = os.Chmod(restrictedDir, 0o700)
	})

	client := &fakeLowLevelClient{
		containers: []container.Summary{{ID: "ctr1"}},
	}
	tar := NewTar("proj", client)

	err := tar.Sync(t.Context(), "svc", []*PathMapping{
		{HostPath: targetFile, ContainerPath: "/app/secret.txt"},
	})

	assert.ErrorContains(t, err, "permission denied")
	assert.ErrorContains(t, err, "secret.txt")
	assert.Equal(t, client.untarCount, 0, "should not attempt copy on stat error")
	assert.Equal(t, len(client.execCmds), 0, "should not attempt delete on stat error")
}

func TestSync_MixedPaths(t *testing.T) {
	tmpDir := t.TempDir()
	existingFile := filepath.Join(tmpDir, "keep.txt")
	assert.NilError(t, os.WriteFile(existingFile, []byte("data"), 0o644))

	client := &fakeLowLevelClient{
		containers: []container.Summary{{ID: "ctr1"}},
	}
	tar := NewTar("proj", client)

	err := tar.Sync(t.Context(), "svc", []*PathMapping{
		{HostPath: existingFile, ContainerPath: "/app/keep.txt"},
		{HostPath: "/no/such/path", ContainerPath: "/app/removed.txt"},
	})

	assert.NilError(t, err)
	assert.Equal(t, client.untarCount, 1, "existing path should be copied")
	assert.Equal(t, len(client.execCmds), 1)
	assert.Check(t, cmp.Contains(client.execCmds[0][len(client.execCmds[0])-1], "removed.txt"))
}
'''


def _ensure_test_file_in_repo() -> None:
    """Write the upstream tar_test.go into the repo (idempotent)."""
    GO_TEST_FILE_DST.parent.mkdir(parents=True, exist_ok=True)
    GO_TEST_FILE_DST.write_text(TAR_TEST_GO)


def _go_test(run_pattern: str, timeout: int = 300) -> subprocess.CompletedProcess:
    _ensure_test_file_in_repo()
    return subprocess.run(
        ["go", "test", "-count=1", "-v", "-run", run_pattern, "./internal/sync/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ─────────────────────────── fail_to_pass ────────────────────────────────


def test_stat_permission_error_returned() -> None:
    """Permission stat errors must surface, not be silently treated as copy.

    On the buggy base, Sync() returns nil and the path is added to the copy
    list; on the fix, Sync() returns an error wrapping the original syscall
    error. The Go test asserts the error contains "permission denied" and
    that no copy/delete was attempted.
    """
    r = _go_test("^TestSync_StatPermissionError$", timeout=180)
    assert r.returncode == 0, (
        "TestSync_StatPermissionError failed.\n"
        f"--- stdout ---\n{r.stdout}\n--- stderr ---\n{r.stderr}"
    )
    # Defensive: the test contains skip-guards (root / windows). If it
    # skipped, returncode==0 is vacuous and the f2p is meaningless.
    combined = r.stdout + r.stderr
    assert "--- SKIP" not in combined, (
        f"TestSync_StatPermissionError was skipped — must run as non-root.\n"
        f"output:\n{combined}"
    )
    assert "--- PASS: TestSync_StatPermissionError" in combined, (
        f"expected explicit PASS marker for TestSync_StatPermissionError, got:\n{combined}"
    )


def test_sync_returns_error_via_runtime_check() -> None:
    """Independent runtime check via a one-shot Go program.

    Builds a tiny program that calls Sync() with a path whose parent
    directory has been chmod 0o000 and verifies that Sync returns a non-nil
    error. This exercises the same behavior as TestSync_StatPermissionError
    but doesn't depend on the test file copy mechanism — it imports the
    package directly. Reduces the risk of the suite passing trivially via a
    bad test-file copy.
    """
    _ensure_test_file_in_repo()  # ensure repo builds with tests too
    progdir = REPO / "_scratch_stat_check"
    progdir.mkdir(exist_ok=True)
    main_go = progdir / "main_test.go"
    main_go.write_text(
        '''
package sync

import (
	"context"
	"io"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/moby/moby/api/types/container"
)

type _runtimeFakeClient struct{}

func (f *_runtimeFakeClient) ContainersForService(_ context.Context, _ string, _ string) ([]container.Summary, error) {
	return []container.Summary{{ID: "x"}}, nil
}
func (f *_runtimeFakeClient) Exec(_ context.Context, _ string, _ []string, _ io.Reader) error {
	return nil
}
func (f *_runtimeFakeClient) Untar(_ context.Context, _ string, _ io.ReadCloser) error {
	return nil
}

func TestRuntimeStatErrorPropagated(t *testing.T) {
	if os.Getuid() == 0 {
		t.Skip("must run as non-root")
	}
	tmp := t.TempDir()
	d := filepath.Join(tmp, "noperm")
	if err := os.Mkdir(d, 0o700); err != nil { t.Fatal(err) }
	target := filepath.Join(d, "f.txt")
	if err := os.WriteFile(target, []byte("x"), 0o644); err != nil { t.Fatal(err) }
	if err := os.Chmod(d, 0o000); err != nil { t.Fatal(err) }
	t.Cleanup(func(){ _ = os.Chmod(d, 0o700) })

	tar := NewTar("p", &_runtimeFakeClient{})
	err := tar.Sync(t.Context(), "svc", []*PathMapping{
		{HostPath: target, ContainerPath: "/c/f.txt"},
	})
	if err == nil {
		t.Fatalf("expected non-nil error from Sync, got nil (bug: stat error silently swallowed)")
	}
	if !strings.Contains(err.Error(), "permission denied") {
		t.Fatalf("error %q does not contain 'permission denied'", err.Error())
	}
}
'''
    )
    # Place this file alongside the package source so it compiles in-package.
    runtime_test = SYNC_PKG / "runtime_stat_check_test.go"
    shutil.copyfile(main_go, runtime_test)
    try:
        r = subprocess.run(
            [
                "go",
                "test",
                "-count=1",
                "-v",
                "-run",
                "^TestRuntimeStatErrorPropagated$",
                "./internal/sync/...",
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=180,
        )
        combined = r.stdout + r.stderr
        assert r.returncode == 0, (
            f"runtime stat-propagation check failed.\n--- stdout ---\n{r.stdout}\n"
            f"--- stderr ---\n{r.stderr}"
        )
        assert "--- SKIP" not in combined, (
            f"runtime stat check was skipped — must run as non-root.\n{combined}"
        )
    finally:
        try:
            runtime_test.unlink()
        except FileNotFoundError:
            pass
        shutil.rmtree(progdir, ignore_errors=True)


# ─────────────────────────── pass_to_pass ────────────────────────────────


def test_existing_path_still_copied() -> None:
    """Existing host paths must continue to be added to the copy list.

    Regression guard: the fix must not break the err == nil branch.
    """
    r = _go_test("^TestSync_ExistingPath$", timeout=180)
    assert r.returncode == 0, (
        f"TestSync_ExistingPath failed.\n--- stdout ---\n{r.stdout}\n"
        f"--- stderr ---\n{r.stderr}"
    )


def test_missing_path_still_deletes() -> None:
    """ErrNotExist paths must continue to map to a delete command.

    Regression guard for the fs.ErrNotExist branch.
    """
    r = _go_test("^TestSync_NonExistentPath$", timeout=180)
    assert r.returncode == 0, (
        f"TestSync_NonExistentPath failed.\n--- stdout ---\n{r.stdout}\n"
        f"--- stderr ---\n{r.stderr}"
    )


def test_mixed_paths_classified_correctly() -> None:
    """Mixed existing+missing paths in one call: copy + delete simultaneously."""
    r = _go_test("^TestSync_MixedPaths$", timeout=180)
    assert r.returncode == 0, (
        f"TestSync_MixedPaths failed.\n--- stdout ---\n{r.stdout}\n"
        f"--- stderr ---\n{r.stderr}"
    )


def test_sync_package_compiles() -> None:
    """internal/sync builds (compile gate)."""
    _ensure_test_file_in_repo()
    r = subprocess.run(
        ["go", "build", "./internal/sync/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"go build failed:\n--- stdout ---\n{r.stdout}\n--- stderr ---\n{r.stderr}"
    )


def test_sync_package_vets() -> None:
    """`go vet ./internal/sync/...` reports no issues."""
    _ensure_test_file_in_repo()
    r = subprocess.run(
        ["go", "vet", "./internal/sync/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"go vet failed:\n--- stdout ---\n{r.stdout}\n--- stderr ---\n{r.stderr}"
    )


def test_sync_package_lints_clean() -> None:
    """golangci-lint v2 reports no issues for internal/sync.

    The repo's CLAUDE.md mandates that the linter must be run and pass on
    every Go change. This is a p2p check from the repo's own CI.
    """
    _ensure_test_file_in_repo()
    r = subprocess.run(
        [
            "golangci-lint",
            "run",
            "--timeout=300s",
            "./internal/sync/...",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"golangci-lint failed:\n--- stdout ---\n{r.stdout}\n"
        f"--- stderr ---\n{r.stderr}"
    )


def test_no_testify_imported_in_sync_tests() -> None:
    """CLAUDE.md / .golangci.yml depguard ban: no stretchr/testify imports.

    The repo blocks testify in favor of gotest.tools/v3. Verified by golangci
    via depguard, but checked here too as a fast guard for the test file we
    inject.
    """
    _ensure_test_file_in_repo()
    text = GO_TEST_FILE_DST.read_text()
    assert "stretchr/testify" not in text, (
        "tar_test.go must not import github.com/stretchr/testify — "
        "use gotest.tools/v3 (CLAUDE.md / .golangci.yml depguard rule)"
    )


def test_no_context_background_in_sync_tests() -> None:
    """CLAUDE.md / forbidigo rule: tests use t.Context(), not context.Background().

    Repo policy: in test files use t.Context() instead of context.Background()
    or context.TODO(). Enforced via the forbidigo linter; checked here as a
    direct programmatic gate.
    """
    _ensure_test_file_in_repo()
    text = GO_TEST_FILE_DST.read_text()
    assert "context.Background()" not in text, (
        "tar_test.go must use t.Context() instead of context.Background() "
        "(CLAUDE.md test convention)"
    )
    assert "context.TODO()" not in text, (
        "tar_test.go must use t.Context() instead of context.TODO() "
        "(CLAUDE.md test convention)"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_e2e_check_docker_version():
    """pass_to_pass | CI job 'e2e' → step 'Check Docker Version'"""
    r = subprocess.run(
        ["bash", "-lc", 'docker --version'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check Docker Version' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_build_example_provider():
    """pass_to_pass | CI job 'e2e' → step 'Build example provider'"""
    r = subprocess.run(
        ["bash", "-lc", 'make example-provider'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build example provider' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_test_plugin_mode():
    """pass_to_pass | CI job 'e2e' → step 'Test plugin mode'"""
    r = subprocess.run(
        ["bash", "-lc", 'make e2e-compose GOCOVERDIR=bin/coverage/e2e TEST_FLAGS="-v"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test plugin mode' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_test_standalone_mode():
    """pass_to_pass | CI job 'e2e' → step 'Test standalone mode'"""
    r = subprocess.run(
        ["bash", "-lc", 'make e2e-compose-standalone'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test standalone mode' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_and_test_unit_tests():
    """pass_to_pass | CI job 'Build and test' → step 'Unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'make test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_and_test_build_binaries():
    """pass_to_pass | CI job 'Build and test' → step 'Build binaries'"""
    r = subprocess.run(
        ["bash", "-lc", 'make'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build binaries' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_and_test_check_arch_of_go_compose_binary():
    """pass_to_pass | CI job 'Build and test' → step 'Check arch of go compose binary'"""
    r = subprocess.run(
        ["bash", "-lc", 'file ./bin/build/docker-compose'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check arch of go compose binary' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_and_test_test_plugin_mode():
    """pass_to_pass | CI job 'Build and test' → step 'Test plugin mode'"""
    r = subprocess.run(
        ["bash", "-lc", 'make e2e-compose'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test plugin mode' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")