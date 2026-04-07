"""
Task: docker-compose-configure-lint-claudemd
Repo: docker/compose @ 27d9d506306e808965d99b70c1f59308dcabca13
PR:   13656

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/compose"


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
    assert r.returncode != 0, f"Found WriteString(fmt.Sprintf anti-pattern at:\n{r.stdout}"
    r2 = subprocess.run(
        ["grep", "-c", "fmt.Fprintf(", str(publish)],
        capture_output=True, text=True,
    )
    assert r2.returncode == 0, "No fmt.Fprintf calls found in publish.go"
    assert int(r2.stdout.strip()) >= 3, \
        f"Expected >= 3 fmt.Fprintf calls, found {r2.stdout.strip()}"


def test_no_unnecessary_nolint():
    """Test file must not have unnecessary //nolint:errcheck directive."""
    content = (Path(REPO) / "pkg/e2e/compose_run_build_once_test.go").read_text()
    assert "//nolint:errcheck" not in content, \
        "Found unnecessary //nolint:errcheck in compose_run_build_once_test.go"


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
    assert "golangci-lint" in content.lower(), \
        "CLAUDE.md should mention golangci-lint"
    assert "fmt.Fprintf" in content, \
        "CLAUDE.md should document the fmt.Fprintf preference"
    assert ".golangci.yml" in content, \
        "CLAUDE.md should reference the linter config file"
