"""
Test suite for shell injection fix in create-github-release.mjs
PR: https://github.com/TanStack/router/pull/6965

This tests that the security vulnerability has been fixed by replacing
execSync with execFileSync to prevent shell injection via malicious
path names.
"""

import subprocess
import os
import re
import ast
import sys

REPO = "/workspace/router"
TARGET_FILE = os.path.join(REPO, "scripts/create-github-release.mjs")


def test_execfilesync_imported():
    """execFileSync must be imported from node:child_process (f2p)."""
    content = open(TARGET_FILE).read()
    # Check that execFileSync is imported
    assert "execFileSync" in content, "execFileSync must be imported"
    # Check the import line specifically
    import_match = re.search(
        r"import\s*\{\s*execSync\s*,\s*execFileSync\s*\}\s*from\s*['\"]node:child_process['\"]",
        content,
    )
    assert import_match is not None, (
        "execFileSync must be imported alongside execSync from node:child_process"
    )


def test_git_show_uses_execfilesync():
    """git show command must use execFileSync with array arguments (f2p)."""
    content = open(TARGET_FILE).read()

    # Find the git show usage - it should use execFileSync now
    # The pattern should be: execFileSync('git', ['show', ...], options)
    git_show_pattern = re.compile(
        r"execFileSync\(\s*['\"]git['\"]\s*,\s*\[\s*['\"]show['\"]",
        re.MULTILINE | re.DOTALL,
    )

    assert git_show_pattern.search(content) is not None, (
        "git show command must use execFileSync with array arguments to prevent shell injection"
    )

    # Make sure the old vulnerable pattern is NOT present
    # The old pattern: execSync(`git show ${previousRelease}:packages/${relPath}`, ...)
    vulnerable_pattern = re.compile(
        r"execSync\(\s*`git show \$\{previousRelease\}:packages/\$\{relPath\}`",
        re.MULTILINE,
    )

    assert vulnerable_pattern.search(content) is None, (
        "Vulnerable execSync pattern with template literal must be removed"
    )


def test_no_shell_injection_in_rel_path():
    """relPath from glob must not be passed to shell command via template literal (f2p)."""
    content = open(TARGET_FILE).read()

    # Specifically check for the vulnerable pattern with relPath
    # The PR fixes: execSync(`git show ${previousRelease}:packages/${relPath}`, ...)
    # This is the core vulnerability: relPath from glob could contain shell metacharacters
    vulnerable_relPath_pattern = re.compile(
        r"execSync\(\s*`[^`]*\$\{relPath\}",
        re.MULTILINE,
    )

    match = vulnerable_relPath_pattern.search(content)
    if match:
        # Check if the match is using the safe execFileSync pattern instead
        line_start = content.rfind("\n", 0, match.start()) + 1
        line_end = content.find("\n", match.end())
        line = content[line_start:line_end]
        assert "execFileSync" in line, (
            f"Dangerous shell interpolation with relPath found: {line.strip()}. "
            "Use execFileSync with array arguments to prevent shell injection."
        )


def test_execfilesync_has_array_args():
    """execFileSync must be called with array arguments, not string (f2p)."""
    content = open(TARGET_FILE).read()

    # Find execFileSync calls
    execfile_calls = re.findall(
        r"execFileSync\((.*?)\)", content, re.MULTILINE | re.DOTALL
    )

    assert len(execfile_calls) > 0, "At least one execFileSync call must exist"

    for call in execfile_calls:
        # The second argument should be an array (square brackets)
        # Pattern: 'git', ['show', ...]
        array_arg_pattern = r"['\"]git['\"]\s*,\s*\["
        assert re.search(array_arg_pattern, call) is not None, (
            f"execFileSync must be called with array arguments, not shell string: {call}"
        )


def test_file_is_valid_javascript():
    """File must be syntactically valid JavaScript (p2p)."""
    # Use node to check syntax
    result = subprocess.run(
        ["node", "--check", TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"JavaScript syntax error: {result.stderr}"


def test_import_statement_valid():
    """Import statement must be valid JavaScript (p2p)."""
    # Use node to parse the file and verify it has no syntax errors
    result = subprocess.run(
        ["node", "--check", TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Import statement or file has syntax error: {result.stderr}"


def test_repo_eslint_scripts():
    """ESLint passes on scripts directory (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "eslint", "--max-warnings=0", "scripts/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stderr[-500:]}"


def test_repo_prettier_scripts():
    """Prettier formatting check passes on scripts (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "prettier", "--experimental-cli", "--check", "scripts/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stderr[-500:]}"


def test_repo_pnpm_version():
    """pnpm is available and functional (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "--version"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"pnpm version check failed: {result.stderr}"
    assert "10." in result.stdout, "pnpm version 10.x expected"
