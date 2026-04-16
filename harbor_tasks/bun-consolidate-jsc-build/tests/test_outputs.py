#!/usr/bin/env python3
"""
Test suite for bun#28863: consolidate jsc:build into build.ts, add BUN_WEBKIT_PATH

This task validates:
1. TypeScript syntax for modified files
2. package.json scripts updated to use build.ts
3. scripts/build-jsc.ts is deleted
4. scripts/build/clean.ts removes WebKitBuild references
5. scripts/build/deps/webkit.ts adds $BUN_WEBKIT_PATH support
6. scripts/build/source.ts adds path and hint options
7. scripts/build/CLAUDE.md table is reformatted
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/bun")


def _run_ts_check(file_path: Path, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run TypeScript compiler on a single file for syntax checking."""
    return subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "--target", "ES2022", "--module", "ESNext", str(file_path)],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


def _run_bun_check(file_path: Path, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run bun to check TypeScript file."""
    return subprocess.run(
        ["bun", "--check", str(file_path)],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


# =============================================================================
# Pass-to-Pass Tests (syntax validation)
# =============================================================================


def test_clean_ts_syntax():
    """scripts/build/clean.ts must have valid TypeScript syntax."""
    file_path = REPO / "scripts" / "build" / "clean.ts"
    assert file_path.exists(), f"File not found: {file_path}"

    # Try TypeScript compiler first
    result = _run_ts_check(file_path)
    if result.returncode != 0:
        # Fallback to bun --check
        result2 = _run_bun_check(file_path)
        assert result2.returncode == 0, f"TypeScript syntax error in clean.ts: {result2.stderr}"


def test_webkit_ts_syntax():
    """scripts/build/deps/webkit.ts must have valid TypeScript syntax."""
    file_path = REPO / "scripts" / "build" / "deps" / "webkit.ts"
    assert file_path.exists(), f"File not found: {file_path}"

    result = _run_ts_check(file_path)
    if result.returncode != 0:
        result2 = _run_bun_check(file_path)
        assert result2.returncode == 0, f"TypeScript syntax error in webkit.ts: {result2.stderr}"


def test_source_ts_syntax():
    """scripts/build/source.ts must have valid TypeScript syntax."""
    file_path = REPO / "scripts" / "build" / "source.ts"
    assert file_path.exists(), f"File not found: {file_path}"

    result = _run_ts_check(file_path)
    if result.returncode != 0:
        result2 = _run_bun_check(file_path)
        assert result2.returncode == 0, f"TypeScript syntax error in source.ts: {result2.stderr}"


def test_claude_md_exists():
    """scripts/build/CLAUDE.md must exist and have content."""
    file_path = REPO / "scripts" / "build" / "CLAUDE.md"
    assert file_path.exists(), f"File not found: {file_path}"
    content = file_path.read_text()
    assert len(content) > 1000, "CLAUDE.md should have substantial content"


# =============================================================================
# Fail-to-Pass Tests (functional fixes)
# =============================================================================


def test_build_jsc_ts_deleted():
    """scripts/build-jsc.ts must be deleted (was replaced by build.ts)."""
    file_path = REPO / "scripts" / "build-jsc.ts"
    assert not file_path.exists(), f"build-jsc.ts should be deleted but still exists at {file_path}"


def test_package_json_uses_build_ts():
    """package.json jsc:build* scripts must use build.ts, not build-jsc.ts."""
    package_json_path = REPO / "package.json"
    assert package_json_path.exists(), "package.json not found"

    content = package_json_path.read_text()
    pkg = json.loads(content)

    scripts = pkg.get("scripts", {})

    # Check jsc:build scripts use build.ts
    for script_name in ["jsc:build", "jsc:build:debug", "jsc:build:lto"]:
        assert script_name in scripts, f"Missing script: {script_name}"
        script_value = scripts[script_name]
        assert "build-jsc.ts" not in script_value, \
            f"{script_name} should not reference build-jsc.ts"
        assert "build.ts" in script_value, \
            f"{script_name} should reference build.ts"
        assert "--target=WebKit" in script_value, \
            f"{script_name} should have --target=WebKit"


def test_clean_ts_no_webkit_build():
    """scripts/build/clean.ts must not reference vendor/WebKit/WebKitBuild."""
    file_path = REPO / "scripts" / "build" / "clean.ts"
    assert file_path.exists(), f"File not found: {file_path}"

    content = file_path.read_text()

    # Should NOT have WebKitBuild references
    assert "WebKitBuild" not in content, \
        "clean.ts should not reference WebKitBuild (now builds in build/<profile>/deps/WebKit/)"

    # The profile descriptions should not mention WebKitBuild
    assert "vendor/WebKit" not in content, \
        "clean.ts should not reference vendor/WebKit in preset descriptions"


def test_webkit_ts_has_env_var():
    """scripts/build/deps/webkit.ts must support $BUN_WEBKIT_PATH."""
    file_path = REPO / "scripts" / "build" / "deps" / "webkit.ts"
    assert file_path.exists(), f"File not found: {file_path}"

    content = file_path.read_text()

    # Should have BUN_WEBKIT_PATH environment variable handling
    assert "BUN_WEBKIT_PATH" in content, \
        "webkit.ts must reference BUN_WEBKIT_PATH environment variable"

    # Should have webkitSrcDir function
    assert "webkitSrcDir" in content, \
        "webkit.ts must have webkitSrcDir function for path resolution"

    # Should import homedir for tilde expansion
    assert "homedir" in content, \
        "webkit.ts must import homedir from node:os for ~ expansion"

    # Should mention worktree sharing
    assert "worktree" in content.lower(), \
        "webkit.ts should mention worktree sharing in comments or hints"


def test_webkit_ts_local_source_with_path():
    """webkit.ts must return local source with path and hint."""
    file_path = REPO / "scripts" / "build" / "deps" / "webkit.ts"
    content = file_path.read_text()

    # Should return a local source with path property
    assert "kind: \"local\"" in content, \
        "webkit.ts must return kind: 'local'"
    assert "path:" in content, \
        "webkit.ts must return path property for local source"
    assert "hint:" in content, \
        "webkit.ts must return hint property for better error messages"


def test_source_ts_has_path_hint():
    """scripts/build/source.ts must have path and hint for local sources."""
    file_path = REPO / "scripts" / "build" / "source.ts"
    assert file_path.exists(), f"File not found: {file_path}"

    content = file_path.read_text()

    # Source type definition should have path and hint for local
    # Check for the path property documentation
    assert "path?:" in content or "path?: string" in content, \
        "source.ts must have optional path property for local sources"

    # Check for hint property
    assert "hint?:" in content or "hint?: string" in content, \
        "source.ts must have optional hint property for local sources"

    # Should use path when resolving source dir for local deps
    assert "source.path" in content, \
        "source.ts must use source.path when resolving local deps"

    # Should use hint in error messages
    assert "source.hint" in content, \
        "source.ts must use source.hint in error messages"


def test_claude_md_table_reformatted():
    """scripts/build/CLAUDE.md module inventory table should be reformatted."""
    file_path = REPO / "scripts" / "build" / "CLAUDE.md"
    assert file_path.exists(), f"File not found: {file_path}"

    content = file_path.read_text()

    # The PR reformats the table to have wider columns
    # Check for specific reformatted lines that are unique to this PR
    # The table column separator should be wider
    table_section = content[content.find("## Module inventory"):content.find("## Key types")]

    # The reformatted table has specific alignment markers
    # Check for the wider separator line
    assert "--- | --" in table_section or "File" in table_section, \
        "CLAUDE.md should have module inventory table"

    # Check that the table still has expected entries
    assert "`build.ts`" in table_section, \
        "CLAUDE.md table should reference build.ts"
    assert "`clean.ts`" in table_section, \
        "CLAUDE.md table should reference clean.ts"
    assert "`source.ts`" in table_section, \
        "CLAUDE.md table should reference source.ts"
    assert "`deps/*.ts`" in table_section, \
        "CLAUDE.md table should reference deps/*.ts"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
