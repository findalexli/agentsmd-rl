"""
Task: dagger-fix-telemetry-tests
Repo: dagger/dagger @ 02b858d8f7368cb107374df899af3a90ffff9bbd
PR:   11939

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/dagger"


# ---------------------------------------------------------------------------
# Helper: build a standalone Go module from exit.go and run tests against it
# ---------------------------------------------------------------------------

def _run_go_test(test_source: str) -> subprocess.CompletedProcess:
    """Copy exit.go into a temp Go module, add a test, and run it."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Minimal go.mod (no external deps needed — exit.go only imports "fmt")
        (tmpdir / "go.mod").write_text("module exittest\n\ngo 1.21\n")

        # Copy exit.go, rename package
        src = Path(REPO) / "dagql" / "idtui" / "exit.go"
        content = src.read_text().replace("package idtui", "package exittest")
        (tmpdir / "exit.go").write_text(content)

        # Write test file
        (tmpdir / "exit_test.go").write_text(test_source)

        r = subprocess.run(
            ["go", "test", "-v", "-count=1", "."],
            cwd=str(tmpdir),
            capture_output=True,
            timeout=60,
        )
        return r


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Go file must compile without errors."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        (tmpdir / "go.mod").write_text("module exittest\n\ngo 1.21\n")
        src = Path(REPO) / "dagql" / "idtui" / "exit.go"
        content = src.read_text().replace("package idtui", "package exittest")
        (tmpdir / "exit.go").write_text(content)
        r = subprocess.run(
            ["go", "build", "."],
            cwd=str(tmpdir),
            capture_output=True,
            timeout=60,
        )
        assert r.returncode == 0, (
            f"exit.go failed to compile:\n{r.stderr.decode()}"
        )


# [repo_tests] pass_to_pass - Repo CI/CD: go build on dagql/idtui
def test_repo_build_idtui():
    """Repo's go build ./dagql/idtui passes (pass_to_pass)."""
    r = subprocess.run(
        ["go", "build", "./dagql/idtui"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"go build ./dagql/idtui failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - Repo CI/CD: go vet on dagql/idtui
def test_repo_vet_idtui():
    """Repo's go vet ./dagql/idtui passes (pass_to_pass)."""
    r = subprocess.run(
        ["go", "vet", "./dagql/idtui"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"go vet ./dagql/idtui failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - Repo CI/CD: gofmt check on dagql/idtui
def test_repo_gofmt_idtui():
    """Repo's gofmt check on dagql/idtui passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "gofmt -d dagql/idtui/*.go"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    # gofmt -d returns empty output if files are properly formatted
    assert r.stdout == "", f"gofmt found formatting issues:\n{r.stdout[:500]}"
    assert r.returncode == 0, f"gofmt command failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - Repo CI/CD: go mod verify
def test_repo_go_mod_verify():
    """Repo's go mod verify passes (pass_to_pass)."""
    r = subprocess.run(
        ["go", "mod", "verify"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"go mod verify failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - Repo CI/CD: go test compile for dagql/idtui
def test_repo_go_test_compile_idtui():
    """Repo's go test compile for dagql/idtui passes (pass_to_pass)."""
    r = subprocess.run(
        ["go", "test", "-c", "./dagql/idtui"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    assert r.returncode == 0, f"go test compile for dagql/idtui failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_error_includes_original():
    """ExitError.Error() must include the original error message when Original is set."""
    test_src = '''\
package exittest

import (
    "errors"
    "strings"
    "testing"
)

func TestErrorIncludesOriginal(t *testing.T) {
    orig := errors.New("parser: unexpected token at line 42")
    e := ExitError{Code: 1, Original: orig}
    msg := e.Error()
    if !strings.Contains(msg, "parser: unexpected token at line 42") {
        t.Fatalf("Error() = %q, want it to contain the original error message", msg)
    }
}
'''
    r = _run_go_test(test_src)
    assert r.returncode == 0, (
        f"ExitError.Error() does not include original error:\n"
        f"{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_error_includes_original_varied():
    """ExitError.Error() preserves the full original message for different errors."""
    test_src = '''\
package exittest

import (
    "errors"
    "strings"
    "testing"
)

func TestErrorIncludesOriginalVaried(t *testing.T) {
    cases := []struct {
        code int
        orig string
    }{
        {2, "connection refused: dial tcp 127.0.0.1:8080"},
        {1, "module not found: github.com/foo/bar"},
        {127, "exec: command not found"},
    }
    for _, tc := range cases {
        e := ExitError{Code: tc.code, Original: errors.New(tc.orig)}
        msg := e.Error()
        if !strings.Contains(msg, tc.orig) {
            t.Errorf("ExitError{Code: %d, Original: %q}.Error() = %q, missing original", tc.code, tc.orig, msg)
        }
    }
}
'''
    r = _run_go_test(test_src)
    assert r.returncode == 0, (
        f"ExitError.Error() fails with varied inputs:\n"
        f"{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_error_without_original():
    """ExitError.Error() still works when Original is nil (no regression)."""
    test_src = '''\
package exittest

import (
    "strings"
    "testing"
)

func TestErrorWithoutOriginal(t *testing.T) {
    e := ExitError{Code: 42}
    msg := e.Error()
    if !strings.Contains(msg, "42") {
        t.Fatalf("Error() = %q, should contain exit code 42", msg)
    }
    // Must not panic or include garbage when Original is nil
    if strings.Contains(msg, "nil") {
        t.Fatalf("Error() = %q, should not contain 'nil' when Original is unset", msg)
    }
}
'''
    r = _run_go_test(test_src)
    assert r.returncode == 0, (
        f"ExitError.Error() broken without Original:\n"
        f"{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Config edit tests (config_edit) — SKILL.md update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
