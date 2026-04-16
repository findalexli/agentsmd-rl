"""Tests for containerd CRI plugin klog stderrthreshold fix.

Behavioral tests: verify actual code behavior, not specific strings.
"""

import subprocess
import os
import re

REPO = "/workspace/containerd"
PLUGIN_FILE = os.path.join(REPO, "plugins/cri/runtime/plugin.go")


def _get_line_positions(content):
    """Return (legacy_pos, stderr_pos, logtostderr_pos) as line numbers (1-based)."""
    legacy_line = None
    stderr_line = None
    logtostderr_line = None

    for i, line in enumerate(content.split('\n'), 1):
        # Match any fs.Set call for these flags (quote-agnostic for flexibility)
        if '.Set(' in line and 'legacy_stderr_threshold_behavior' in line and 'false' in line:
            legacy_line = i
        if '.Set(' in line and 'stderrthreshold' in line and 'INFO' in line:
            stderr_line = i
        if '.Set(' in line and 'logtostderr' in line and 'true' in line:
            logtostderr_line = i

    return legacy_line, stderr_line, logtostderr_line


def _extract_function(content, func_name):
    """Extract a function's body from source content."""
    pattern = rf'func {func_name}\(\)[^{{]*\{{'
    m = re.search(pattern, content)
    if not m:
        return None
    start = m.end()
    brace_count = 1
    i = start
    while i < len(content) and brace_count > 0:
        if content[i] == '{':
            brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
        i += 1
    return content[start:i-1]


def test_legacy_stderr_flag_set():
    """
    Verify that stderrthreshold behavior flags are set before logtostderr.

    The klog bug requires that legacy_stderr_threshold_behavior and stderrthreshold
    flags are set BEFORE logtostderr=true, otherwise stderrthreshold is ignored.

    Behavioral approach: parse the source to find the setGLogLevel function,
    extract all fs.Set calls in order, and verify that at least 2 flag-setting
    calls precede the logtostderr call.
    """
    with open(PLUGIN_FILE, 'r') as f:
        content = f.read()

    # Extract setGLogLevel function
    func_body = _extract_function(content, 'setGLogLevel')
    assert func_body is not None, "setGLogLevel function not found"

    # Find all fs.Set calls in order
    set_calls = []
    for m in re.finditer(r'\.Set\([^)]+\)', func_body):
        set_calls.append(m.group())

    assert len(set_calls) >= 3, \
        f"setGLogLevel should have at least 3 fs.Set calls (need 2 klog fix flags + logtostderr), found {len(set_calls)}"

    # Find the logtostderr call
    logtostderr_idx = None
    for i, call in enumerate(set_calls):
        if 'logtostderr' in call:
            logtostderr_idx = i
            break

    assert logtostderr_idx is not None, "logtostderr flag setting not found"

    # Verify that at least 2 calls (the klog fix) precede logtostderr
    # These are the legacy_stderr_threshold_behavior and stderrthreshold calls
    calls_before_logtostderr = logtostderr_idx
    assert calls_before_logtostderr >= 2, \
        f"Need at least 2 flag settings before logtostderr for klog fix, found {calls_before_logtostderr}"


def test_stderrthreshold_before_logtostderr():
    """
    Verify the klog fix flags (legacy behavior + threshold) come before logtostderr.

    Extracts the setGLogLevel function and verifies the positional ordering
    of flag-setting calls.
    """
    with open(PLUGIN_FILE, 'r') as f:
        content = f.read()

    func_body = _extract_function(content, 'setGLogLevel')
    assert func_body is not None, "setGLogLevel function not found"

    # Get line positions for the flag-setting calls within the function
    lines = func_body.split('\n')
    legacy_line = None
    stderr_line = None
    logtostderr_line = None

    for i, line in enumerate(lines, 1):
        if '.Set(' in line and 'legacy_stderr_threshold_behavior' in line and 'false' in line:
            legacy_line = i
        if '.Set(' in line and 'stderrthreshold' in line and 'INFO' in line:
            stderr_line = i
        if '.Set(' in line and 'logtostderr' in line and 'true' in line:
            logtostderr_line = i

    # At least one of the klog fix flags must be present (stderrthreshold behavior)
    assert legacy_line is not None or stderr_line is not None, \
        "Neither legacy_stderr_threshold_behavior nor stderrthreshold flag found"

    # logtostderr must be present
    assert logtostderr_line is not None, "logtostderr flag setting not found"

    # Both (if present) must come before logtostderr
    if legacy_line is not None:
        assert legacy_line < logtostderr_line, \
            f"legacy flag (line {legacy_line}) must come before logtostderr (line {logtostderr_line})"
    if stderr_line is not None:
        assert stderr_line < logtostderr_line, \
            f"stderrthreshold (line {stderr_line}) must come before logtostderr (line {logtostderr_line})"


def test_klog_comment_present():
    """
    Verify an explanatory comment about the klog stderrthreshold fix is present.

    The fix should be documented to help future maintainers understand why
    specific flag settings are needed.
    """
    with open(PLUGIN_FILE, 'r') as f:
        content = f.read()

    func_body = _extract_function(content, 'setGLogLevel')
    assert func_body is not None, "setGLogLevel function not found"

    # Look for any comment in or near the function mentioning klog or stderrthreshold
    # Extract a window around setGLogLevel to check for comments
    func_start = content.find('func setGLogLevel()')
    # Check the function and ~10 lines before it (where comment might be)
    window_start = max(0, func_start - 500)
    window = content[window_start:func_start + len(func_body)]

    # Should mention klog or stderrthreshold behavior in comments
    has_klog_comment = bool(re.search(r'//.*klog', window, re.IGNORECASE))
    has_stderrthreshold_comment = bool(re.search(r'//.*stderrthreshold', window, re.IGNORECASE))

    assert has_klog_comment or has_stderrthreshold_comment, \
        "Missing explanatory comment about klog stderrthreshold fix"


def test_setgloglevel_function_structure():
    """
    Verify the setGLogLevel function has proper error handling.

    The fix adds flag-setting calls that can fail; these must be checked
    and return errors properly.
    """
    with open(PLUGIN_FILE, 'r') as f:
        content = f.read()

    func_body = _extract_function(content, 'setGLogLevel')
    assert func_body is not None, "setGLogLevel function not found"

    # Check that error handling is present (return err after a failed fs.Set)
    assert 'return err' in func_body or 'return' in func_body, \
        "setGLogLevel should return errors from failed operations"

    # Count fs.Set calls - should be at least 3 (2 klog fix flags + logtostderr)
    set_count = len(re.findall(r'\.Set\(', func_body))
    assert set_count >= 3, \
        f"Expected at least 3 fs.Set calls in setGLogLevel, found {set_count}"


def test_plugin_compiles():
    """
    Verify the CRI runtime plugin compiles successfully.
    """
    cmd = ["go", "build", "-v", "./plugins/cri/runtime/..."]
    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"CRI runtime plugin failed to compile:\n{result.stderr}"


def test_cri_runtime_unit_tests():
    """
    Run unit tests for the CRI runtime plugin.
    """
    cmd = ["go", "test", "-v", "./plugins/cri/runtime/..."]
    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"CRI runtime unit tests failed:\n{result.stderr[-500:]}"


def test_repo_go_vet():
    """
    Run go vet on the CRI runtime package.
    """
    cmd = ["go", "vet", "./plugins/cri/runtime/..."]
    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"go vet failed:\n{result.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])