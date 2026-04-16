"""Test outputs for containerd/containerd#13138 - CRI UsageNanoCores semantics fix.

This PR mirrors cAdvisor's CpuInst behavior:
- getUsageNanoCores now returns *uint64 instead of uint64
- Returns nil when there's not enough data to compute an instantaneous rate
- Instead of returning 0, the UsageNanoCores field is left unset (nil)
"""

import subprocess
import sys
import os
import re
import ast

REPO = "/workspace/containerd"


# =============================================================================
# PASS_TO_PASS TESTS (these verify the environment is sane)
# =============================================================================

def test_go_build():
    """Go code compiles successfully (pass_to_pass)."""
    r = subprocess.run(
        ["go", "build", "./internal/cri/server/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Go build failed:\n{r.stderr}"


def test_cri_server_tests_compile():
    """CRI server test file compiles (pass_to_pass)."""
    r = subprocess.run(
        ["go", "test", "-c", "./internal/cri/server/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Test compilation failed:\n{r.stderr}"


def test_go_mod_verify():
    """Go modules verify successfully (pass_to_pass)."""
    r = subprocess.run(
        ["go", "mod", "verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert r.returncode == 0, f"Go mod verify failed:\n{r.stderr}"


def test_go_vet():
    """Go vet passes for CRI server package (pass_to_pass)."""
    r = subprocess.run(
        ["go", "vet", "./internal/cri/server/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Go vet failed:\n{r.stderr}"


def test_gofmt_check():
    """Go code is properly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "test -z \"$(gofmt -l internal/cri/server/)\""],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert r.returncode == 0, f"gofmt check failed - unformatted files in internal/cri/server/"


def test_cri_server_core_unit_tests():
    """CRI server core unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["go", "test", "-v", "./internal/cri/server", "-run", "TestContainer|TestGetWorkingSet|TestSandbox"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"CRI server core unit tests failed:\n{r.stderr}\n{r.stdout}"


# =============================================================================
# FAIL_TO_PASS TESTS (these verify the bug fix via behavior)
# =============================================================================

def test_getUsageNanoCores_returns_pointer():
    """getUsageNanoCores function returns *uint64 instead of uint64 (fail_to_pass).

    This is the key API change - returning a pointer allows distinguishing between
    "zero usage" and "no data available".
    """
    source_file = os.path.join(REPO, "internal/cri/server/container_stats_list.go")

    with open(source_file, "r") as f:
        content = f.read()

    # Look for the function signature: func (...) getUsageNanoCores(...) (*uint64, error)
    func_pattern = r"func\s+\([^)]+\)\s+getUsageNanoCores\s*\([^)]+\)\s*\(\s*(\S+)\s*,\s*error\s*\)"
    match = re.search(func_pattern, content)
    assert match is not None, "Could not find getUsageNanoCores function signature"

    return_type = match.group(1)
    assert return_type == "*uint64", f"Expected return type *uint64, got {return_type}"


def test_cri_server_unit_test_passes():
    """Unit test for CPU nano core usage passes (fail_to_pass).

    The existing unit test TestContainerMetricsCPUNanoCoreUsage validates the
    expected behavior. If the fix is correct, this test passes.
    """
    r = subprocess.run(
        ["go", "test", "-v", "-run", "TestContainerMetricsCPUNanoCoreUsage", "./internal/cri/server/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Unit test TestContainerMetricsCPUNanoCoreUsage failed:\n{r.stderr}\n{r.stdout}"


def test_uint64Ptr_helper_exists():
    """uint64Ptr helper function exists for test expectations (fail_to_pass).

    A helper function uint64Ptr should exist to create *uint64 values in tests.
    """
    test_file = os.path.join(REPO, "internal/cri/server/container_stats_list_test.go")
    with open(test_file, "r") as f:
        content = f.read()

    # Look for uint64Ptr function definition (any variable name, any body)
    helper_pattern = r"func\s+uint64Ptr\s*\(\s*\w+\s+uint64\s*\)\s*\*\s*uint64"
    match = re.search(helper_pattern, content)
    assert match is not None, "uint64Ptr helper function should exist in test file"


def test_test_expects_nil_for_first_sample():
    """Tests expect nil (not 0) for first sample (fail_to_pass).

    The test should have nil expectations for cases where insufficient data
    is available to compute a rate.
    """
    test_file = os.path.join(REPO, "internal/cri/server/container_stats_list_test.go")
    with open(test_file, "r") as f:
        content = f.read()

    # The test struct fields for first sample expectation should be *uint64 (pointer type)
    first_sample_field_pattern = r"expectedNanoCoreUsageFirst\s+\*uint64"
    match = re.search(first_sample_field_pattern, content)
    assert match is not None, "expectedNanoCoreUsageFirst field should be *uint64 type (pointer to allow nil)"


def test_callers_handle_nil_return():
    """Callers of getUsageNanoCores handle nil pointer return (fail_to_pass).

    At least one caller uses the returned pointer with nil checking before
    dereferencing (the container_stats_list.go caller).
    """
    source_file = os.path.join(REPO, "internal/cri/server/container_stats_list.go")
    with open(source_file, "r") as f:
        content = f.read()

    # Look for: if <var> != nil { followed at some point by *<var> and UsageNanoCores
    lines = content.split('\n')
    nil_guard_count = 0
    for i, line in enumerate(lines):
        if re.match(r'\s*if\s+\w+\s*!=\s*nil\s*\{', line):
            # Look ahead up to 5 lines for dereference of same variable
            var_match = re.match(r'\s*if\s+(\w+)\s*!=\s*nil', line)
            if var_match:
                var_name = var_match.group(1)
                # Check next 5 lines for *<var> in context of UsageNanoCores
                for j in range(i+1, min(i+6, len(lines))):
                    if f'*{var_name}' in lines[j] and 'UsageNanoCores' in lines[j]:
                        nil_guard_count += 1
                        break

    assert nil_guard_count >= 1, f"Expected at least 1 nil-guard dereference pattern in container_stats callers, found {nil_guard_count}"


def test_sandbox_caller_handles_nil():
    """Sandbox caller handles nil pointer from getUsageNanoCores (fail_to_pass).

    podSandboxStats in sandbox_stats_linux.go should use the pointer safely.
    """
    source_file = os.path.join(REPO, "internal/cri/server/sandbox_stats_linux.go")
    if not os.path.exists(source_file):
        # Skip on non-Linux platforms
        return

    with open(source_file, "r") as f:
        content = f.read()

    # Check for nil check pattern in sandbox stats
    # Look for: if <var> != nil { ... *<var> (within ~5 lines)
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if re.match(r'\s*if\s+\w+\s*!=\s*nil\s*\{', line):
            var_match = re.match(r'\s*if\s+(\w+)\s*!=\s*nil', line)
            if var_match:
                var_name = var_match.group(1)
                for j in range(i+1, min(i+6, len(lines))):
                    if f'*{var_name}' in lines[j] and 'UsageNanoCores' in lines[j]:
                        return  # Found the pattern

    assert False, "Should check returned pointer is non-nil before assigning UsageNanoCores in sandbox_stats_linux.go"


def test_error_paths_return_nil():
    """Error return paths use nil instead of 0 (fail_to_pass).

    When returning an error, the function should return nil, error instead of 0, error.
    """
    source_file = os.path.join(REPO, "internal/cri/server/container_stats_list.go")
    with open(source_file, "r") as f:
        content = f.read()

    # Check that error returns use "return nil," not "return 0,"
    error_return_pattern = r"return\s+nil,\s*fmt\.Errorf"
    matches = list(re.finditer(error_return_pattern, content))
    assert len(matches) >= 2, f"Error returns should use 'nil' not '0', found {len(matches)} occurrences"


def test_stats_collector_returns_pointer_type():
    """Stats collector path returns pointer to uint64 (fail_to_pass).

    The caller must wrap the returned uint64 value in a pointer when
    returning from getUsageNanoCores.
    """
    source_file = os.path.join(REPO, "internal/cri/server/container_stats_list.go")
    with open(source_file, "r") as f:
        content = f.read()

    # Look for a return statement where a value is returned as a pointer
    pointer_return_pattern = r"return\s+&\w+,\s*nil"
    match = re.search(pointer_return_pattern, content)
    assert match is not None, "Stats collector path should return a pointer (&variable, nil)"


def test_no_zero_returns_for_missing_data():
    """No returns of 0 for missing data conditions (fail_to_pass).

    The function should return nil (not 0) when:
    - No previous stats data exists (first sample)
    - Time interval is zero or negative
    - Counter goes backwards
    """
    source_file = os.path.join(REPO, "internal/cri/server/container_stats_list.go")
    with open(source_file, "r") as f:
        content = f.read()

    # Extract just the getUsageNanoCores function body
    func_match = re.search(
        r"func\s+\([^)]+\)\s+getUsageNanoCores\s*\([^)]+\)\s*\([^)]+\)\s*\{(.*?)^\}",
        content,
        re.MULTILINE | re.DOTALL
    )
    assert func_match is not None, "Could not find getUsageNanoCores function body"

    func_body = func_match.group(1)

    # Check that "return 0, nil" does NOT appear in the function body
    bad_pattern = r"return\s+0\s*,\s*nil"
    bad_matches = list(re.finditer(bad_pattern, func_body))
    assert len(bad_matches) == 0, f"Function should not return 0, nil for missing data; found {len(bad_matches)} occurrences"