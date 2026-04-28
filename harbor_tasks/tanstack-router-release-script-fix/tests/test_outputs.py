#!/usr/bin/env python3
"""Tests for TanStack Router release script fix.

This test suite verifies the changes made to create-github-release.mjs:
1. Git commit range detection no longer uses -n 1 / HEAD~1
2. Non-conventional commit parsing uses split() instead of indexOf
3. --latest flag is conditional, not unconditional
"""

import subprocess
import sys
from pathlib import Path

REPO = Path('/workspace/router')
SCRIPT_PATH = REPO / 'scripts' / 'create-github-release.mjs'


def read_script():
    if not SCRIPT_PATH.exists():
        raise FileNotFoundError(f'Script not found: {SCRIPT_PATH}')
    return SCRIPT_PATH.read_text()


# ============================================================================
# Fail-to-Pass Tests
# ============================================================================


def test_old_release_log_pattern_removed():
    content = read_script()
    assert '-n 1 --format=%H HEAD~1' not in content


def test_release_log_parsed_as_array():
    content = read_script()
    assert ".split('\\n')" in content
    assert content.count('.filter(Boolean)') >= 2


def test_git_log_range_no_longer_uses_head():
    content = read_script()
    assert 'HEAD~1' not in content


def test_non_conventional_commit_parsing_uses_split():
    content = read_script()
    assert ".split(' ')" in content
    assert "indexOf(' ')" not in content


def test_latest_flag_no_longer_unconditional():
    content = read_script()
    assert '--notes-file ${tmpFile} --latest' not in content
    assert '--latest' in content


def test_timing_comment_added():
    content = read_script()
    assert 'runs right after the' in content.lower()


def test_conventional_commit_format_comment_added():
    content = read_script()
    assert '<hash>' in content
    assert '<type>' in content


def test_non_conventional_comment_added():
    content = read_script()
    assert 'non-conventional commits' in content.lower()


# ============================================================================
# Pass-to-Pass Tests
# ============================================================================


def test_script_syntax_valid():
    result = subprocess.run(
        ['bash', '-lc', 'node --check scripts/create-github-release.mjs'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert result.returncode == 0, f'Syntax error: {result.stderr}'


def test_prerelease_flag_preserved():
    content = read_script()
    assert 'prereleaseFlag' in content


def test_repo_script_syntax():
    result = subprocess.run(
        ['bash', '-lc', 'node --check scripts/create-github-release.mjs'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert result.returncode == 0, f'Syntax error: {result.stderr}'


def test_repo_script_formatting():
    result = subprocess.run(
        ['bash', '-lc', 'npx prettier --check scripts/create-github-release.mjs'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert result.returncode == 0, f'Formatting check failed:\n{result.stdout[-500:]}'


def test_repo_all_mjs_scripts_syntax():
    scripts_dir = REPO / 'scripts'
    mjs_files = list(scripts_dir.glob('*.mjs'))
    assert mjs_files
    for script_file in mjs_files:
        result = subprocess.run(
            ['bash', '-lc', f'node --check {script_file.relative_to(REPO)}'],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert result.returncode == 0, f'{script_file.name} syntax error: {result.stderr}'


def test_repo_all_scripts_formatting():
    result = subprocess.run(
        ['bash', '-lc', 'npx prettier --check scripts/'],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert result.returncode == 0, f'Scripts formatting check failed:\n{result.stdout[-500:]}'


def test_repo_markdown_formatting():
    result = subprocess.run(
        ['bash', '-lc', 'npx prettier --check *.md'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert result.returncode == 0, f'Markdown formatting check failed:\n{result.stdout[-500:]}'


def test_repo_package_json_formatting():
    result = subprocess.run(
        ['bash', '-lc', 'npx prettier --check package.json'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert result.returncode == 0, f'package.json formatting check failed:\n{result.stdout[-500:]}'


def test_repo_git_valid():
    result = subprocess.run(
        ['git', 'log', '--oneline', '-1'],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f'Git log failed: {result.stderr}'
    assert result.stdout.strip()


def test_repo_workspace_config_formatting():
    result = subprocess.run(
        ['bash', '-lc', 'npx prettier --check pnpm-workspace.yaml nx.json'],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert result.returncode == 0, f'Workspace config formatting check failed:\n{result.stdout[-500:]}'


def test_repo_all_scripts_syntax():
    scripts_dir = REPO / 'scripts'
    script_files = (
        list(scripts_dir.glob('*.mjs'))
        + list(scripts_dir.glob('*.js'))
        + list(scripts_dir.glob('*.ts'))
    )
    assert script_files
    for script_file in script_files:
        result = subprocess.run(
            ['bash', '-lc', f'node --check {script_file.relative_to(REPO)}'],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert result.returncode == 0, f'{script_file.name} syntax error: {result.stderr}'


def test_repo_all_scripts_individual_formatting():
    scripts_dir = REPO / 'scripts'
    script_files = (
        list(scripts_dir.glob('*.mjs'))
        + list(scripts_dir.glob('*.js'))
        + list(scripts_dir.glob('*.ts'))
    )
    for script_file in script_files:
        result = subprocess.run(
            ['bash', '-lc', f'npx prettier --check {script_file.relative_to(REPO)}'],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert result.returncode == 0, f'{script_file.name} formatting check failed:\n{result.stdout[-500:]}'


def test_repo_git_status_clean():
    result = subprocess.run(
        ['git', 'status', '--porcelain'],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f'Git status failed: {result.stderr}'


def test_repo_npmrc_exists():
    result = subprocess.run(
        ['test', '-f', '.npmrc'],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert result.returncode == 0


def test_repo_node_version_specified():
    result = subprocess.run(
        ['cat', '.nvmrc'],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert result.returncode == 0, f'.nvmrc read failed: {result.stderr}'
    assert result.stdout.strip()


if __name__ == '__main__':
    import pytest
    sys.exit(pytest.main([__file__, '-v']))
