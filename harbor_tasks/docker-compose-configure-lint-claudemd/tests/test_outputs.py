"""
Task: docker-compose-configure-lint-claudemd
Repo: docker/compose @ 27d9d506306e808965d99b70c1f59308dcabca13
PR:   13656

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
from pathlib import Path

REPO = "/workspace/compose"

# Ensure GOTOOLCHAIN=auto is set for all go commands
os.environ["GOTOOLCHAIN"] = "auto"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


def test_go_syntax_valid():
    """Modified Go files parse without errors."""
    files = [
        Path(REPO) / "pkg/compose/publish.go",
        Path(REPO) / "pkg/e2e/compose_run_build_once_test.go",
    ]
    for f in files:
        r = subprocess.run(
            ["gofmt", "-e", str(f)],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"gofmt error in {f}: {r.stderr}"


def test_go_vet_compose():
    """Go vet passes for pkg/compose (pass_to_pass)."""
    r = subprocess.run(
        ["go", "vet", "./pkg/compose/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env={**os.environ, "GOTOOLCHAIN": "auto"},
    )
    assert r.returncode == 0, f"go vet failed: {r.stderr}"


def test_unit_test_publish():
    """Unit test for publish functionality passes (pass_to_pass)."""
    r = subprocess.run(
        ["go", "test", "-run", "Test_createLayers", "./pkg/compose/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env={**os.environ, "GOTOOLCHAIN": "auto"},
    )
    assert r.returncode == 0, f"Unit test failed: {r.stderr[-500:]}"


def test_gofmt_check():
    """Modified Go files are properly formatted (pass_to_pass)."""
    files = ["pkg/compose/publish.go", "pkg/e2e/compose_run_build_once_test.go"]
    for f in files:
        r = subprocess.run(
            ["gofmt", "-l", f],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.stdout.strip() == "", f"File {f} is not properly formatted"


def test_go_build():
    """Go build compiles successfully (pass_to_pass)."""
    r = subprocess.run(
        ["go", "build", "./cmd/..."],
        capture_output=True, text=True, timeout=300, cwd=REPO,
        env={**os.environ, "GOTOOLCHAIN": "auto"},
    )
    assert r.returncode == 0, f"Go build failed: {r.stderr[-500:]}"


def test_unit_tests_compose():
    """Unit tests for pkg/compose pass (pass_to_pass)."""
    r = subprocess.run(
        ["go", "test", "-count=1", "./pkg/compose/"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
        env={**os.environ, "GOTOOLCHAIN": "auto"},
    )
    assert r.returncode == 0, f"Unit tests failed: {r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code style tests
# ---------------------------------------------------------------------------


def test_publish_uses_fprintf():
    """publish.go must use fmt.Fprintf instead of WriteString(fmt.Sprintf(...))."""
    publish = Path(REPO) / "pkg/compose/publish.go"
    r = subprocess.run(
        ["grep", "-n", "WriteString(fmt.Sprintf(", str(publish)],
        capture_output=True, text=True,
    )
    assert r.returncode != 0, f"Found WriteString(fmt.Sprintf anti-pattern: {r.stdout}"
    r2 = subprocess.run(
        ["grep", "-c", "fmt.Fprintf(", str(publish)],
        capture_output=True, text=True,
    )
    assert r2.returncode == 0, "No fmt.Fprintf calls found in publish.go"
    assert int(r2.stdout.strip()) >= 3, f"Expected >= 3 fmt.Fprintf calls, found {r2.stdout.strip()}"


def test_no_unnecessary_nolint():
    """Test file must not have unnecessary //nolint:errcheck directive."""
    content = (Path(REPO) / "pkg/e2e/compose_run_build_once_test.go").read_text()
    assert "//nolint:errcheck" not in content, "Found unnecessary //nolint:errcheck"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------


def test_claude_md_documents_build():
    """CLAUDE.md must exist and document build/test commands."""
    claude_md = Path(REPO) / "CLAUDE.md"
    assert claude_md.exists(), "CLAUDE.md does not exist"
    content = claude_md.read_text()
    assert "make build" in content, "CLAUDE.md should document 'make build'"
    assert "go test" in content, "CLAUDE.md should document 'go test' commands"


def test_claude_md_documents_lint_style():
    """CLAUDE.md must document linting setup and code style conventions."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()
    assert "golangci-lint" in content.lower(), "CLAUDE.md should mention golangci-lint"
    assert "fmt.Fprintf" in content, "CLAUDE.md should document the fmt.Fprintf preference"
    assert ".golangci.yml" in content, "CLAUDE.md should reference the linter config file"
