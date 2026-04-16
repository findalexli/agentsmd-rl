"""
Test proxy bypass logic fix and skill documentation update.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/playwright")

def test_chromium_ts_compiles():
    """TypeScript files must compile without errors."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "packages/playwright-core"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stderr}"


def test_proxy_loopback_logic_fixed():
    """
    Proxy bypass logic must check for localhost, 127.0.0.1, and ::1.
    The fix adds a bypassesLoopback check that considers these addresses.
    """
    chromium_ts = REPO / "packages" / "playwright-core" / "src" / "server" / "chromium" / "chromium.ts"
    content = chromium_ts.read_text()

    # The fix adds a bypassesLoopback constant with expanded checks
    assert "bypassesLoopback" in content, \
        "chromium.ts must define bypassesLoopback constant for loopback detection"

    # Should check for localhost, 127.0.0.1, and ::1 in the some() call
    assert 'rule === \'localhost\'' in content, \
        "bypassesLoopback must check for 'localhost'"
    assert 'rule === \'127.0.0.1\'' in content, \
        "bypassesLoopback must check for '127.0.0.1'"
    assert 'rule === \'::1\'' in content, \
        "bypassesLoopback must check for '::1'"

    # Should use bypassesLoopback in the condition
    assert "!bypassesLoopback" in content, \
        "The proxy condition must use !bypassesLoopback"


def test_skill_md_documents_github_skill():
    """
    SKILL.md must reference the new github.md skill documentation.
    This is the config update that documents how to upload fixes.
    """
    skill_md = REPO / ".claude" / "skills" / "playwright-dev" / "SKILL.md"
    assert skill_md.exists(), "SKILL.md must exist"

    content = skill_md.read_text()

    # Must reference github.md for uploading fixes
    assert "github.md" in content, \
        "SKILL.md must reference github.md"
    assert "Uploading Fixes to GitHub" in content, \
        "SKILL.md must document 'Uploading Fixes to GitHub'"


def test_github_md_skill_file_exists():
    """
    The github.md skill file must exist with proper documentation.
    """
    github_md = REPO / ".claude" / "skills" / "playwright-dev" / "github.md"
    assert github_md.exists(), \
        "github.md skill file must be created"

    content = github_md.read_text()

    # Must document the key workflow steps
    assert "Branch naming" in content, \
        "github.md must document branch naming"
    assert "Committing changes" in content, \
        "github.md must document committing changes"
    assert "conventional commit format" in content.lower(), \
        "github.md must document conventional commit format"
    assert "Pushing" in content, \
        "github.md must document pushing"


def test_npm_run_check_deps_passes():
    """Dependency check must pass on the codebase."""
    result = subprocess.run(
        ["npm", "run", "check-deps"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Dependency check failed:\n{result.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
