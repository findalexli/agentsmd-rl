#!/usr/bin/env python3
"""Tests for ClickHouse stress test timeout fix."""

import subprocess
import sys

REPO = "/workspace/ClickHouse"
TARGET_FILE = f"{REPO}/tests/docker_scripts/stress_runner.sh"

def test_randomization_uses_random_not_date():
    """Verify async_load_databases uses $RANDOM for proper per-run randomization.

    The fix replaces $(date +%-d) % 2 with $RANDOM % 2 for proper randomization.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the async_load_databases section
    lines = content.split('\n')
    in_async_section = False
    async_line = None

    for i, line in enumerate(lines):
        if 'async_load_databases' in line and 'Randomize' in line:
            in_async_section = True
            continue
        if in_async_section and line.strip().startswith('if ['):
            async_line = line
            break

    assert async_line is not None, "Could not find async_load_databases randomization check"

    # Should use $RANDOM % 2, not $(date +%-d) % 2
    assert '$((RANDOM % 2))' in async_line, \
        f"Should use $RANDOM for randomization, found: {async_line}"
    assert 'date +%-d' not in async_line, \
        f"Should not use date-based randomization, found: {async_line}"


def test_post_stress_start_server_has_timeout():
    """Verify post-stress start_server call has timeout argument of 30.

    After stress test, server restart needs extended timeout (30 attempts ~10 min)
    because under TSan with async_load_databases=false, loading tables takes longer.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the post-stress restart section - after "rm cannot_allocate_thread_injection.xml"
    lines = content.split('\n')

    # Find the line after rm ...cannot_allocate_thread_injection.xml
    target_idx = None
    for i, line in enumerate(lines):
        if 'cannot_allocate_thread_injection.xml' in line and line.strip().startswith('rm'):
            # Look for start_server in the next few lines
            for j in range(i+1, min(i+10, len(lines))):
                if 'start_server' in lines[j]:
                    target_idx = j
                    break
            break

    assert target_idx is not None, "Could not find post-stress start_server call"

    post_stress_line = lines[target_idx]

    # Should have timeout argument of 30
    assert 'start_server 30' in post_stress_line, \
        f"Post-stress start_server should have timeout 30, found: {post_stress_line}"


def test_shellcheck_no_errors():
    """Verify shellcheck finds no errors (warnings/info are acceptable).

    This is a pass_to_pass test that verifies the script is valid bash.
    We only fail on actual errors (exit code > 1), not warnings/info.
    """
    result = subprocess.run(
        ['shellcheck', '-x', TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=60
    )
    # Shellcheck exit codes:
    # 0 = no issues
    # 1 = warnings/info (acceptable)
    # 2+ = errors (not acceptable)
    assert result.returncode <= 1, \
        f"Shellcheck found errors:\n{result.stdout}\n{result.stderr}"


def test_script_syntax_valid():
    """Verify bash syntax is valid (pass_to_pass)."""
    result = subprocess.run(
        ['bash', '-n', TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, \
        f"Bash syntax check failed:\n{result.stderr}"


def test_stress_tests_lib_shellcheck():
    """Verify stress_tests.lib passes shellcheck (pass_to_pass)."""
    lib_file = f"{REPO}/tests/docker_scripts/stress_tests.lib"
    result = subprocess.run(
        ['shellcheck', '-x', lib_file],
        capture_output=True,
        text=True,
        timeout=60
    )
    # Allow warnings/info (exit code <= 1)
    assert result.returncode <= 1, \
        f"Shellcheck found errors in stress_tests.lib:\n{result.stdout}\n{result.stderr}"


def test_stress_tests_lib_syntax():
    """Verify stress_tests.lib bash syntax is valid (pass_to_pass)."""
    lib_file = f"{REPO}/tests/docker_scripts/stress_tests.lib"
    result = subprocess.run(
        ['bash', '-n', lib_file],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, \
        f"Bash syntax check failed for stress_tests.lib:\n{result.stderr}"


def test_utils_lib_shellcheck():
    """Verify utils.lib passes shellcheck (pass_to_pass)."""
    lib_file = f"{REPO}/tests/docker_scripts/utils.lib"
    result = subprocess.run(
        ['shellcheck', '-x', lib_file],
        capture_output=True,
        text=True,
        timeout=60
    )
    # Allow warnings/info (exit code <= 1)
    assert result.returncode <= 1, \
        f"Shellcheck found errors in utils.lib:\n{result.stdout}\n{result.stderr}"


def test_utils_lib_syntax():
    """Verify utils.lib bash syntax is valid (pass_to_pass)."""
    lib_file = f"{REPO}/tests/docker_scripts/utils.lib"
    result = subprocess.run(
        ['bash', '-n', lib_file],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, \
        f"Bash syntax check failed for utils.lib:\n{result.stderr}"


def test_upgrade_runner_shellcheck():
    """Verify upgrade_runner.sh passes shellcheck (pass_to_pass)."""
    upgrade_file = f"{REPO}/tests/docker_scripts/upgrade_runner.sh"
    result = subprocess.run(
        ['shellcheck', '-x', upgrade_file],
        capture_output=True,
        text=True,
        timeout=60
    )
    # Allow warnings/info (exit code <= 1)
    assert result.returncode <= 1, \
        f"Shellcheck found errors in upgrade_runner.sh:\n{result.stdout}\n{result.stderr}"


def test_upgrade_runner_syntax():
    """Verify upgrade_runner.sh bash syntax is valid (pass_to_pass)."""
    upgrade_file = f"{REPO}/tests/docker_scripts/upgrade_runner.sh"
    result = subprocess.run(
        ['bash', '-n', upgrade_file],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, \
        f"Bash syntax check failed for upgrade_runner.sh:\n{result.stderr}"


def test_create_tpcds_shellcheck():
    """Verify create_tpcds.sh passes shellcheck (pass_to_pass)."""
    script_file = f"{REPO}/tests/docker_scripts/create_tpcds.sh"
    result = subprocess.run(
        ['shellcheck', '-x', script_file],
        capture_output=True,
        text=True,
        timeout=60
    )
    # Allow warnings/info (exit code <= 1)
    assert result.returncode <= 1, \
        f"Shellcheck found errors in create_tpcds.sh:\n{result.stdout}\n{result.stderr}"


def test_create_tpcds_syntax():
    """Verify create_tpcds.sh bash syntax is valid (pass_to_pass)."""
    script_file = f"{REPO}/tests/docker_scripts/create_tpcds.sh"
    result = subprocess.run(
        ['bash', '-n', script_file],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, \
        f"Bash syntax check failed for create_tpcds.sh:\n{result.stderr}"


def test_create_tpch_shellcheck():
    """Verify create_tpch.sh passes shellcheck (pass_to_pass)."""
    script_file = f"{REPO}/tests/docker_scripts/create_tpch.sh"
    result = subprocess.run(
        ['shellcheck', '-x', script_file],
        capture_output=True,
        text=True,
        timeout=60
    )
    # Allow warnings/info (exit code <= 1)
    assert result.returncode <= 1, \
        f"Shellcheck found errors in create_tpch.sh:\n{result.stdout}\n{result.stderr}"


def test_create_tpch_syntax():
    """Verify create_tpch.sh bash syntax is valid (pass_to_pass)."""
    script_file = f"{REPO}/tests/docker_scripts/create_tpch.sh"
    result = subprocess.run(
        ['bash', '-n', script_file],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, \
        f"Bash syntax check failed for create_tpch.sh:\n{result.stderr}"


def test_attach_gdb_lib_shellcheck():
    """Verify attach_gdb.lib passes shellcheck (pass_to_pass)."""
    lib_file = f"{REPO}/tests/docker_scripts/attach_gdb.lib"
    result = subprocess.run(
        ['shellcheck', '-x', lib_file],
        capture_output=True,
        text=True,
        timeout=60
    )
    # Allow warnings/info (exit code <= 1)
    assert result.returncode <= 1, \
        f"Shellcheck found errors in attach_gdb.lib:\n{result.stdout}\n{result.stderr}"


def test_attach_gdb_lib_syntax():
    """Verify attach_gdb.lib bash syntax is valid (pass_to_pass)."""
    lib_file = f"{REPO}/tests/docker_scripts/attach_gdb.lib"
    result = subprocess.run(
        ['bash', '-n', lib_file],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, \
        f"Bash syntax check failed for attach_gdb.lib:\n{result.stderr}"


def test_no_date_based_randomization_anywhere():
    """Ensure no other date-based randomization patterns remain in the file."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for date +%-d pattern used for randomization
    import re
    date_random_pattern = re.compile(r'date\s+\+%-d\s*\)\s*\%\s*2')
    matches = date_random_pattern.findall(content)

    assert len(matches) == 0, \
        f"Found date-based randomization remaining: {matches}"


def test_start_server_timeout_has_comment():
    """Verify the timeout change has explanatory comment.

    The fix adds a comment explaining why larger timeout is needed.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for comment about larger timeout before start_server 30
    assert 'larger timeout for the post-stress restart' in content, \
        "Missing explanatory comment for timeout increase"
    assert 'under sanitizers with' in content, \
        "Missing mention of sanitizers in comment"


if __name__ == '__main__':
    import pytest
    sys.exit(pytest.main([__file__, '-v', '--tb=short']))
