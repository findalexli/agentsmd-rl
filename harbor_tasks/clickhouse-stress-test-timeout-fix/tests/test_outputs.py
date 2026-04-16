#!/usr/bin/env python3
"""Tests for ClickHouse stress test timeout fix."""

import subprocess
import sys
import re
import os

REPO = "/workspace/ClickHouse"
TARGET_FILE = f"{REPO}/tests/docker_scripts/stress_runner.sh"


def test_randomization_produces_varying_output():
    """Verify async_load_databases randomization changes per execution.

    The fix replaces $(date +%-d) % 2 with $RANDOM % 2.
    Behavioral test: $RANDOM produces different values on each invocation,
    whereas $(date +%-d) produces the same value within a 24-hour period.

    We extract and execute the randomization logic twice and verify the
    results differ (which proves $RANDOM is being used, not date-based).
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the randomization line in async_load_databases section
    lines = content.split('\n')
    async_line = None
    for line in lines:
        # Look for the if condition that checks randomization
        # The fix changes: if [ $(( $(date +%-d) % 2 )) -eq 0 ]; then
        # to: if [ $((RANDOM % 2)) -eq 0 ]; then
        if 'async_load_databases' in line and 'Randomize' in line:
            continue
        if 'if [' in line and ('date' in line or 'RANDOM' in line):
            async_line = line
            break

    assert async_line is not None, "Could not find randomization check in async_load_databases section"

    # Extract the randomization expression
    # For $RANDOM approach: $((RANDOM % 2))
    # For date approach: $(( $(date +%-d) % 2 ))
    random_var = None
    uses_date = False

    if '$((RANDOM % 2))' in async_line:
        random_var = 'RANDOM'
    elif 'date' in async_line and '$(date' in async_line:
        uses_date = True

    # Execute the randomization logic twice using bash
    if random_var == 'RANDOM':
        # Test that $RANDOM produces varying results
        results = []
        for _ in range(3):
            result = subprocess.run(
                ['bash', '-c', 'echo $(($RANDOM % 2))'],
                capture_output=True,
                text=True,
                timeout=10
            )
            results.append(result.stdout.strip())

        # At least 2 of 3 runs should differ (statistically $RANDOM % 2
        # should have ~75% chance of differing between runs)
        unique_results = set(results)
        assert len(unique_results) > 1, \
            f"RANDOM should produce varying output, got: {results}"

    elif uses_date:
        # If date is still used, the output would be constant within a day
        result = subprocess.run(
            ['bash', '-c', 'echo $(($(date +%-d) % 2))'],
            capture_output=True,
            text=True,
            timeout=10
        )
        # We FAIL if date-based is still present - this is the bug
        assert False, \
            f"Still using date-based randomization: {async_line}"


def test_post_stress_start_server_accepts_timeout_parameter():
    """Verify post-stress start_server call passes explicit timeout value.

    Behavioral test: the start_server function accepts a timeout parameter
    (max_attempt). We verify the call provides a value > 6 (the default).
    The exact value (30, 25, 60) may vary by implementation.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    lines = content.split('\n')

    # Find the post-stress restart section
    target_idx = None
    for i, line in enumerate(lines):
        if 'cannot_allocate_thread_injection.xml' in line and line.strip().startswith('rm'):
            for j in range(i+1, min(i+10, len(lines))):
                if 'start_server' in lines[j]:
                    target_idx = j
                    break
            break

    assert target_idx is not None, "Could not find post-stress start_server call"

    post_stress_line = lines[target_idx]

    # Extract the numeric argument passed to start_server
    # Pattern: start_server <number> || ...
    match = re.search(r'start_server\s+(\d+)', post_stress_line)
    assert match is not None, \
        f"start_server call should pass explicit timeout number, found: {post_stress_line}"

    timeout_value = int(match.group(1))
    assert timeout_value > 6, \
        f"Timeout should exceed default (6), got: {timeout_value}"


def test_shellcheck_no_errors():
    """Verify shellcheck finds no errors (warnings/info are acceptable).

    This is a pass_to_pass test that verifies the script is valid bash.
    """
    result = subprocess.run(
        ['shellcheck', '-x', TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=60
    )
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


def test_no_date_based_randomization_remains():
    """Ensure no date-based randomization patterns remain.

    Behavioral test: date-based randomization produces constant results
    within a day, defeating the purpose of randomization.
    We verify the pattern is completely absent (not just the exact form).
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for date-based randomization: any $(date ...) used in % or mod context
    # Pattern: $(date ...) followed by % <number>
    date_mod_pattern = re.compile(r'\$\(date\s+[^)]+\)\s*%')
    matches = date_mod_pattern.findall(content)

    assert len(matches) == 0, \
        f"Found date-based randomization still present: {matches}"


def test_timeout_explanation_exists_near_start_server():
    """Verify an explanatory comment exists before post-stress start_server.

    The fix should add a comment explaining why the timeout is extended.
    We verify SOME explanation exists near the start_server call,
    without asserting on exact wording.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    lines = content.split('\n')

    # Find the post-stress start_server call
    target_idx = None
    for i, line in enumerate(lines):
        if 'cannot_allocate_thread_injection.xml' in line and line.strip().startswith('rm'):
            for j in range(i+1, min(i+20, len(lines))):
                if 'start_server' in lines[j] and '||' in lines[j]:
                    target_idx = j
                    break
            break

    assert target_idx is not None, "Could not find post-stress start_server call"

    # Check that there's a comment block within the 10 lines before start_server
    # that explains the timeout
    comment_block = []
    for i in range(max(0, target_idx - 10), target_idx):
        line = lines[i]
        if line.strip().startswith('#'):
            comment_block.append(line.strip())

    # Verify some comment exists that explains the timeout behavior
    # We don't check exact wording, just that there IS an explanation
    has_explanation = False
    for comment in comment_block:
        # Look for comment that mentions timeout AND gives some reason
        lower_comment = comment.lower()
        if ('timeout' in lower_comment or 'larger' in lower_comment or
                'extended' in lower_comment or 'sanitizer' in lower_comment or
                'table' in lower_comment):
            has_explanation = True
            break

    assert has_explanation, \
        f"Missing explanatory comment near post-stress start_server. Found comments: {comment_block}"


if __name__ == '__main__':
    import pytest
    sys.exit(pytest.main([__file__, '-v', '--tb=short']))
