"""Tests for sentry-go MaxBreadcrumbs behavior change (PR #1106)."""
import os
import shutil
import subprocess
import textwrap
import pathlib

REPO = "/workspace/sentry-go"
PROBE_FILE = os.path.join(REPO, "breadcrumb_probe_test.go")


# A single Go test file that probes the user-observable behavior. It is dropped
# into the repo at test time and removed after.
PROBE_GO = textwrap.dedent(
    """
    package sentry

    import (
    \t"testing"
    )

    // probeMaxBreadcrumbsAboveOldHardLimit: when MaxBreadcrumbs is set above the
    // historical 100 cap, all of them must be retained (cap was removed).
    func TestProbeMaxBreadcrumbsAboveOldHardLimit(t *testing.T) {
    \tclient, err := NewClient(ClientOptions{MaxBreadcrumbs: 500})
    \tif err != nil {
    \t\tt.Fatalf("NewClient failed: %v", err)
    \t}
    \tscope := NewScope()
    \thub := NewHub(client, scope)
    \tfor i := 0; i < 600; i++ {
    \t\thub.AddBreadcrumb(&Breadcrumb{Message: "x"}, nil)
    \t}
    \tif got := len(scope.breadcrumbs); got != 500 {
    \t\tt.Fatalf("want 500 breadcrumbs retained, got %d", got)
    \t}
    }

    // probeMaxBreadcrumbsAt250: another value above 100 to vary the input.
    func TestProbeMaxBreadcrumbsAt250(t *testing.T) {
    \tclient, err := NewClient(ClientOptions{MaxBreadcrumbs: 250})
    \tif err != nil {
    \t\tt.Fatalf("NewClient failed: %v", err)
    \t}
    \tscope := NewScope()
    \thub := NewHub(client, scope)
    \tfor i := 0; i < 400; i++ {
    \t\thub.AddBreadcrumb(&Breadcrumb{Message: "y"}, nil)
    \t}
    \tif got := len(scope.breadcrumbs); got != 250 {
    \t\tt.Fatalf("want 250 breadcrumbs retained, got %d", got)
    \t}
    }

    // probeDefaultMaxBreadcrumbs: when MaxBreadcrumbs is unset (0), the SDK
    // must fall back to its default. The new default is 100 (was 30).
    func TestProbeDefaultMaxBreadcrumbsIs100(t *testing.T) {
    \tclient, err := NewClient(ClientOptions{})
    \tif err != nil {
    \t\tt.Fatalf("NewClient failed: %v", err)
    \t}
    \tscope := NewScope()
    \thub := NewHub(client, scope)
    \tfor i := 0; i < 150; i++ {
    \t\thub.AddBreadcrumb(&Breadcrumb{Message: "z"}, nil)
    \t}
    \tif got := len(scope.breadcrumbs); got != 100 {
    \t\tt.Fatalf("want default cap 100 breadcrumbs, got %d", got)
    \t}
    }
    """
).lstrip()


def _write_probe():
    pathlib.Path(PROBE_FILE).write_text(PROBE_GO)


def _run_probe(name: str) -> subprocess.CompletedProcess:
    _write_probe()
    return subprocess.run(
        ["go", "test", "-count=1", "-run", "^" + name + "$", "-timeout", "120s", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )


# ---------- fail_to_pass: behavioral tests ----------

def test_max_breadcrumbs_above_old_hard_limit():
    """MaxBreadcrumbs=500 must retain 500 (was capped at 100)."""
    r = _run_probe("TestProbeMaxBreadcrumbsAboveOldHardLimit")
    assert r.returncode == 0, (
        "probe failed:\nSTDOUT:\n" + r.stdout + "\nSTDERR:\n" + r.stderr
    )


def test_max_breadcrumbs_at_250():
    """MaxBreadcrumbs=250 must retain 250 (was capped at 100)."""
    r = _run_probe("TestProbeMaxBreadcrumbsAt250")
    assert r.returncode == 0, (
        "probe failed:\nSTDOUT:\n" + r.stdout + "\nSTDERR:\n" + r.stderr
    )


def test_default_max_breadcrumbs_is_100():
    """With no MaxBreadcrumbs option, default must be 100 (was 30)."""
    r = _run_probe("TestProbeDefaultMaxBreadcrumbsIs100")
    assert r.returncode == 0, (
        "probe failed:\nSTDOUT:\n" + r.stdout + "\nSTDERR:\n" + r.stderr
    )


# ---------- pass_to_pass: existing repo tests still pass ----------

def test_repo_unit_tests_pass():
    """Existing scope/hub breadcrumb tests pass after the change."""
    r = subprocess.run(
        [
            "go",
            "test",
            "-count=1",
            "-timeout",
            "300s",
            "-run",
            "TestAddBreadcrumb|TestScopeParentChangedInheritance|TestScopeChildOverrideInheritance|TestClearAndReconfigure",
            ".",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        "repo tests failed:\nSTDOUT:\n" + r.stdout + "\nSTDERR:\n" + r.stderr
    )


def test_repo_go_vet():
    """`go vet` passes on root package — sanity-check the patch compiles cleanly."""
    r = subprocess.run(
        ["go", "vet", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, "go vet failed:\n" + r.stderr


def test_repo_build():
    """Whole module builds (`go build ./...`)."""
    r = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, "go build failed:\n" + r.stderr


# ---------- agent_config: rules from .cursor/rules/changelog.mdc ----------

def test_changelog_pr_link_format():
    """Per .cursor/rules/changelog.mdc: PR links must use
    `([#NUMBER](https://github.com/getsentry/sentry-go/pull/NUMBER))` format."""
    import re

    text = pathlib.Path(REPO, "CHANGELOG.md").read_text()
    pattern = re.compile(
        r"\(\[#1106\]\(https://github\.com/getsentry/sentry-go/pull/1106\)\)"
    )
    assert pattern.search(text), (
        "CHANGELOG.md must contain a PR link for #1106 in the form "
        "([#1106](https://github.com/getsentry/sentry-go/pull/1106))"
    )


def test_changelog_breaking_changes_section():
    """Per .cursor/rules/changelog.mdc: breaking changes must be documented under
    a `### Breaking Changes` heading in CHANGELOG.md."""
    text = pathlib.Path(REPO, "CHANGELOG.md").read_text()
    # Must have a Breaking Changes section that mentions MaxBreadcrumbs.
    head, _, _ = text.partition("## 0.35.3")
    assert "### Breaking Changes" in head, (
        "CHANGELOG.md must contain a `### Breaking Changes` section "
        "in the new release block"
    )
    assert "MaxBreadcrumbs" in head, (
        "Breaking changes section must reference the MaxBreadcrumbs option"
    )

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_TestAddBreadcrumbAppendsBreadcrumb():
    """fail_to_pass | PR added test 'TestAddBreadcrumbAppendsBreadcrumb' in 'scope_test.go' (go_test)"""
    r = subprocess.run(
        ["bash", "-lc", 'go test ./ -run "^TestAddBreadcrumbAppendsBreadcrumb$" -count=1 -v 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'TestAddBreadcrumbAppendsBreadcrumb' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_TestAddBreadcrumbAddsTimestamp():
    """fail_to_pass | PR added test 'TestAddBreadcrumbAddsTimestamp' in 'scope_test.go' (go_test)"""
    r = subprocess.run(
        ["bash", "-lc", 'go test ./ -run "^TestAddBreadcrumbAddsTimestamp$" -count=1 -v 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'TestAddBreadcrumbAddsTimestamp' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_TestAddBreadcrumbDefaultLimit():
    """fail_to_pass | PR added test 'TestAddBreadcrumbDefaultLimit' in 'scope_test.go' (go_test)"""
    r = subprocess.run(
        ["bash", "-lc", 'go test ./ -run "^TestAddBreadcrumbDefaultLimit$" -count=1 -v 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'TestAddBreadcrumbDefaultLimit' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_TestAddBreadcrumbAddsBreadcrumb():
    """fail_to_pass | PR added test 'TestAddBreadcrumbAddsBreadcrumb' in 'scope_test.go' (go_test)"""
    r = subprocess.run(
        ["bash", "-lc", 'go test ./ -run "^TestAddBreadcrumbAddsBreadcrumb$" -count=1 -v 2>&1 | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'TestAddBreadcrumbAddsBreadcrumb' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
