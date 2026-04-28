"""Tests for hugo PR #14544 — modules: include JSON error info from go mod download.

The agent must modify modules/client.go so that when ``go mod download -json``
fails, the JSON-encoded error written to stdout is surfaced in the wrapping
``error`` returned from ``Client.downloadModuleVersion``. Without the fix, the
JSON ``Error`` field is silently dropped and only a generic execution error is
shown.
"""

from __future__ import annotations

import os
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/hugo")

PRIVATE_REPO_TEST = textwrap.dedent('''
    package hugolib

    import (
    \t"testing"

    \tqt "github.com/frankban/quicktest"
    )

    func TestModulePrivateRepoPR14544(t *testing.T) {
    \tt.Parallel()

    \tfiles := `
    -- hugo.toml --
    baseURL = "https://example.com/"
    [module]
    [[module.imports]]
    path = "github.com/bep/this-is-a-non-existing-repo"
    version = "main"
    [[module.imports.mounts]]
    source = "content"
    target = "content"
    -- layouts/all.html --
    Title: {{ .Title }}|
    List: {{ .Title }}
    `

    \tb, err := TestE(t, files, TestOptOsFs())
    \tb.Assert(err, qt.ErrorMatches, `(?s).*mod download.*invalid version.*repository.*`)
    }
''').strip() + "\n"

SNAPSHOT_TEST = textwrap.dedent('''
    package hugolib

    import (
    \t"strings"
    \t"testing"
    )

    func TestModulePrivateRepoPR14544Snapshot(t *testing.T) {
    \tt.Parallel()

    \tfiles := `
    -- hugo.toml --
    baseURL = "https://example.com/"
    [module]
    [[module.imports]]
    path = "github.com/bep/this-is-a-non-existing-repo"
    version = "main"
    [[module.imports.mounts]]
    source = "content"
    target = "content"
    -- layouts/all.html --
    x
    `

    \t_, err := TestE(t, files, TestOptOsFs())
    \tif err == nil {
    \t\tt.Fatalf("expected an error from TestE, got nil")
    \t}
    \tmsg := err.Error()
    \tfor _, want := range []string{"mod download", "invalid version", "repository", "github.com/bep/this-is-a-non-existing-repo"} {
    \t\tif !strings.Contains(msg, want) {
    \t\t\tt.Fatalf("error message missing %q; got:\\n%s", want, msg)
    \t\t}
    \t}
    }
''').strip() + "\n"


def _write_check(name: str, body: str) -> Path:
    p = REPO / "hugolib" / name
    p.write_text(body)
    return p


def _go_test(run_pattern: str, package: str, timeout: int = 240) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["go", "test", "-count=1", "-timeout", "180s", "-run", run_pattern, "-v", package],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "GOFLAGS": "-mod=mod"},
    )


# ---------------------------------------------------------------------------
# Fail-to-pass behaviour test (the PR's behaviour)
# ---------------------------------------------------------------------------

def test_module_private_repo_error_matches_regex():
    """f2p: when ``go mod download -json`` fails for a non-existing module the
    error returned by Hugo must include the JSON ``Error`` field — at minimum
    the substrings ``mod download``, ``invalid version`` and ``repository``
    must all appear, in that order, in the surfaced error message.
    """
    test_path = _write_check("check_pr14544_test.go", PRIVATE_REPO_TEST)
    try:
        result = _go_test("^TestModulePrivateRepoPR14544$", "./hugolib")
    finally:
        test_path.unlink(missing_ok=True)

    print("STDOUT:", result.stdout[-2000:])
    print("STDERR:", result.stderr[-1000:])
    assert result.returncode == 0, (
        "Hugo's surfaced error does NOT match the regex "
        "`(?s).*mod download.*invalid version.*repository.*`. The JSON `Error` "
        "field from `go mod download -json` is being dropped."
    )


def test_module_private_repo_error_contains_json_payload():
    """f2p: the error message must include both the requested module path and
    the JSON ``Error`` field's distinctive substrings (``invalid version`` and
    ``repository``). A stub that hard-codes only the regex tokens but does not
    actually parse the JSON output would be missing the module path that lives
    inside the JSON payload, so this complements the regex check.
    """
    test_path = _write_check("check_pr14544_snapshot_test.go", SNAPSHOT_TEST)
    try:
        result = _go_test("^TestModulePrivateRepoPR14544Snapshot$", "./hugolib")
    finally:
        test_path.unlink(missing_ok=True)

    print("STDOUT:", result.stdout[-2000:])
    print("STDERR:", result.stderr[-1000:])
    assert result.returncode == 0, (
        "Hugo's surfaced error is missing one or more of the substrings emitted"
        " in the JSON `Error` payload from `go mod download -json`."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass tests (repo CI commands and fast unit tests)
# ---------------------------------------------------------------------------

def test_modules_package_unit_tests():
    """p2p: fast unit tests in the modules package keep passing."""
    result = subprocess.run(
        [
            "go", "test", "-count=1", "-timeout", "60s",
            "-run",
            "^(TestPathKey|TestFilterUnwantedMounts|TestDecodeConfig|"
            "TestDecodeConfigBothOldAndNewProvided|TestDecodeConfigTheme|"
            "TestConfigHugoVersionIsValid|TestGetModlineSplitter|"
            "TestClientConfigToEnv)$",
            "./modules/",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    print(result.stdout[-1000:])
    print(result.stderr[-500:])
    assert result.returncode == 0, "modules unit tests failed"


def test_go_vet_modules_and_hugolib():
    """p2p: go vet must stay clean on the affected packages."""
    result = subprocess.run(
        ["go", "vet", "./modules/...", "./hugolib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=240,
    )
    print(result.stdout[-1000:])
    print(result.stderr[-1000:])
    assert result.returncode == 0, f"go vet failed:\n{result.stderr}"


def test_go_build_modules_and_hugolib():
    """p2p: the modified packages still compile."""
    result = subprocess.run(
        ["go", "build", "./modules/...", "./hugolib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    print(result.stdout[-1000:])
    print(result.stderr[-1000:])
    assert result.returncode == 0, f"go build failed:\n{result.stderr}"


def test_gofmt_clean_on_client_go():
    """p2p: gofmt is clean on modules/client.go.

    Hugo's AGENTS.md and check.sh enforce a gofmt-clean tree. Restricting the
    check to the file the agent is expected to modify makes the test specific
    to the agent's edits rather than to unrelated repo state.
    """
    result = subprocess.run(
        ["gofmt", "-l", "modules/client.go"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"gofmt errored: {result.stderr}"
    assert result.stdout.strip() == "", (
        f"modules/client.go is not gofmt-clean:\n{result.stdout}"
    )


def test_no_hdebug_left_behind():
    """p2p: per AGENTS.md, hdebug.Printf must not be left in committed code.

    CI fails if the agent forgets to remove debug printing. We enforce the
    same rule on the file the agent edits.
    """
    content = (REPO / "modules" / "client.go").read_text()
    assert "hdebug.Printf" not in content, (
        "hdebug.Printf found in modules/client.go — temporary debug printing "
        "must be removed before submission (see AGENTS.md)."
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_brew():
    """pass_to_pass | CI job 'test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'brew install pandoc'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_choco():
    """pass_to_pass | CI job 'test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'choco install pandoc'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_pandoc():
    """pass_to_pass | CI job 'test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pandoc -v'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_choco():
    """pass_to_pass | CI job 'test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'choco install mingw'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_staticcheck():
    """pass_to_pass | CI job 'test' → step 'Run staticcheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'export STATICCHECK_CACHE="${{ runner.temp }}/staticcheck"\nstaticcheck ./...\nrm -rf ${{ runner.temp }}/staticcheck'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Run staticcheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_check():
    """pass_to_pass | CI job 'test' → step 'Check'"""
    r = subprocess.run(
        ["bash", "-lc", 'sass --version;\nmage -v check;'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_test():
    """pass_to_pass | CI job 'test' → step 'Test'"""
    r = subprocess.run(
        ["bash", "-lc", 'mage -v test'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_build_for_dragonfly():
    """pass_to_pass | CI job 'test' → step 'Build for dragonfly'"""
    r = subprocess.run(
        ["bash", "-lc", 'go install\ngo clean -i -cache'], cwd=REPO,
        capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        f"CI step 'Build for dragonfly' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_TestModulePrivateRepo():
    """fail_to_pass | PR added test 'TestModulePrivateRepo' in 'hugolib/hugo_modules_test.go' (go_test)"""
    r = subprocess.run(
        ["bash", "-lc", 'go test ./hugolib -run "^TestModulePrivateRepo$" -count=1 -v 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'TestModulePrivateRepo' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
