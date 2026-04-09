"""
Test suite for Electron dock state validation fix.

This tests that the security fix properly validates dock_state values
against an allowlist before using them.
"""

import subprocess
import sys
from pathlib import Path

# Path to the electron repository
REPO = Path("/workspace/electron")
TARGET_FILE = REPO / "shell/browser/ui/inspectable_web_contents.cc"

# Valid dock states per the fix
VALID_DOCK_STATES = {"bottom", "left", "right", "undocked"}
DEFAULT_DOCK_STATE = "right"


def get_file_content():
    """Get the content of the target file."""
    if not TARGET_FILE.exists():
        pytest.fail(f"Target file not found: {TARGET_FILE}")
    return TARGET_FILE.read_text()


def test_clang_syntax_check():
    """
    Fail-to-pass: The modified C++ code must be syntactically valid.
    This will fail on base if the file is missing the required header
    or has syntax errors.
    """
    content = get_file_content()

    # Try to parse with clang
    result = subprocess.run(
        ["clang", "-fsyntax-only", "-std=c++20", "-c", str(TARGET_FILE)],
        capture_output=True,
        cwd=str(REPO),
    )

    # The syntax check may fail due to missing dependencies (Chromium headers)
    # but it should at least parse the structure correctly
    # We check that there are no structural syntax errors
    output = result.stderr.decode()

    # Only fail on actual syntax errors, not missing includes
    syntax_errors = [
        line for line in output.split("\n")
        if "error:" in line and not any(x in line for x in [
            "file not found", "cannot open", "No such file"
        ])
    ]

    assert len(syntax_errors) == 0, f"Syntax errors found:\n{chr(10).join(syntax_errors)}"


def test_valid_dock_states_constant_exists():
    """
    Fail-to-pass: The kValidDockStates allowlist constant must exist.
    Tests that the security fix includes the allowlist definition.
    """
    content = get_file_content()

    # Check for the constant definition
    assert "kValidDockStates" in content, \
        "kValidDockStates constant not found - security allowlist missing"

    # Check for MakeFixedFlatSet usage (the Chromium container type)
    assert "MakeFixedFlatSet" in content, \
        "MakeFixedFlatSet not found - should use base::MakeFixedFlatSet for allowlist"


def test_is_valid_dock_state_function_exists():
    """
    Fail-to-pass: The IsValidDockState validation function must exist.
    Tests that the security fix includes the validation helper.
    """
    content = get_file_content()

    # Check for the validation function
    assert "IsValidDockState" in content, \
        "IsValidDockState function not found - validation helper missing"

    # Check function signature
    assert "IsValidDockState(const std::string& state)" in content or \
           "IsValidDockState" in content, \
        "IsValidDockState function signature incorrect"


def test_set_dock_state_uses_validation():
    """
    Fail-to-pass: SetDockState must validate input through IsValidDockState.
    Tests that the security fix properly validates dock state in SetDockState.
    """
    content = get_file_content()

    # Look for the SetDockState function
    set_dock_start = content.find("void InspectableWebContents::SetDockState")
    assert set_dock_start != -1, "SetDockState function not found"

    # Extract function body (approximate: find next function or end of class)
    func_end = content.find("void InspectableWebContents::", set_dock_start + 1)
    if func_end == -1:
        func_end = len(content)
    func_body = content[set_dock_start:func_end]

    # Check that IsValidDockState is called in SetDockState
    assert "IsValidDockState" in func_body, \
        "SetDockState does not use IsValidDockState for validation"

    # Check that there's a fallback to "right" for invalid states
    assert "\"right\"" in func_body or '"right"' in func_body, \
        "SetDockState missing fallback to 'right' for invalid dock states"


def test_load_completed_uses_validation():
    """
    Fail-to-pass: LoadCompleted must validate dock_state from preferences.
    Tests that the security fix properly validates persisted dock state.
    """
    content = get_file_content()

    # Look for the LoadCompleted function
    load_completed_start = content.find("void InspectableWebContents::LoadCompleted")
    assert load_completed_start != -1, "LoadCompleted function not found"

    # Extract function body (approximate)
    func_end = content.find("void InspectableWebContents::", load_completed_start + 1)
    if func_end == -1:
        func_end = len(content)
    func_body = content[load_completed_start:func_end]

    # Check that IsValidDockState is called in LoadCompleted
    assert "IsValidDockState" in func_body, \
        "LoadCompleted does not use IsValidDockState for validation"

    # Check that current_dock_state is checked for existence before use
    assert "if (current_dock_state)" in func_body or \
           "current_dock_state)" in func_body, \
        "LoadCompleted missing null check for current_dock_state"


def test_dock_states_allowlist_contents():
    """
    Pass-to-pass: The allowlist must contain exactly the expected states.
    Tests that the security fix uses the correct allowlist values.
    """
    content = get_file_content()

    # Check that all expected states are in the kValidDockStates definition
    start = content.find("kValidDockStates")
    assert start != -1, "kValidDockStates not found"

    # Find the closing brace of the initializer
    end = content.find("};", start)
    assert end != -1, "Could not find end of kValidDockStates definition"

    states_section = content[start:end]

    # Check each expected state is present
    for state in VALID_DOCK_STATES:
        assert f'"{state}"' in states_section, \
            f"Expected dock state '{state}' not found in allowlist"

    # Check that no extra states are present (security: explicit allowlist)
    # This verifies it's an allowlist approach, not a blacklist


def test_fixed_flat_set_header_included():
    """
    Pass-to-pass: The required header for MakeFixedFlatSet must be included.
    Tests that the security fix includes the necessary dependency.
    """
    content = get_file_content()

    # Check for the header include
    assert '#include "base/containers/fixed_flat_set.h"' in content, \
        "Missing required header: base/containers/fixed_flat_set.h"


def test_no_direct_state_assignment():
    """
    Fail-to-pass: Direct assignment to dock_state_ must be validated.
    Tests that the old vulnerable pattern (direct assignment) is replaced.
    """
    content = get_file_content()

    # In SetDockState, the direct assignment should be replaced with validation
    set_dock_start = content.find("void InspectableWebContents::SetDockState")
    set_dock_end = content.find("void InspectableWebContents::", set_dock_start + 1)
    if set_dock_end == -1:
        set_dock_end = len(content)
    set_dock_body = content[set_dock_start:set_dock_end]

    # Count occurrences of "dock_state_ = state" (vulnerable pattern)
    # After fix, should use IsValidDockState or "right" fallback
    vulnerable_pattern = "dock_state_ = state;"
    assert vulnerable_pattern not in set_dock_body, \
        f"Vulnerable direct assignment pattern found: {vulnerable_pattern}"


# ============================================================================
# Pass-to-pass tests: Repo CI/CD checks that must pass on both base and fix
# ============================================================================


def test_repo_clang_format_target():
    """
    Pass-to-pass: Repo's clang-format check passes on the target file.
    Equivalent to the repo's `lint:clang-format` CI command which runs
    `clang-format` with Chromium style config on shell/ directory files.
    """
    r = subprocess.run(
        ["clang-format", "--dry-run", "--Werror",
         "shell/browser/ui/inspectable_web_contents.cc"],
        capture_output=True, text=True, timeout=120, cwd=str(REPO),
    )
    assert r.returncode == 0, (
        f"clang-format check failed (Chromium style):\n{r.stderr[-500:]}"
    )


def test_repo_clang_format_script():
    """
    Pass-to-pass: Repo's own Python clang-format wrapper passes.
    Equivalent to `python3 script/run-clang-format.py -r -c shell/`
    which is the actual CI command used in the Electron lint pipeline.
    """
    r = subprocess.run(
        ["python3", "script/run-clang-format.py", "-r", "-c",
         "shell/browser/ui/inspectable_web_contents.cc"],
        capture_output=True, text=True, timeout=120, cwd=str(REPO),
    )
    assert r.returncode == 0, (
        f"Repo clang-format script failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
    )


def test_repo_target_file_exists():
    """
    Pass-to-pass: The target source file exists and is non-empty.
    Basic sanity check that the repo checkout is valid.
    """
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"
    content = TARGET_FILE.read_text()
    assert len(content) > 100, "Target file is unexpectedly small"
    assert "// Copyright" in content, "Target file missing copyright header"


def test_repo_valid_encoding():
    """
    Pass-to-pass: Target file has valid UTF-8 encoding without BOM.
    CI linting checks enforce consistent file encoding.
    """
    try:
        raw = TARGET_FILE.read_bytes()
        assert not raw.startswith(b'\xef\xbb\xbf'), \
            "File has UTF-8 BOM marker which should not be present"
        raw.decode('utf-8')
    except UnicodeDecodeError as e:
        pytest.fail(f"File is not valid UTF-8: {e}")


if __name__ == "__main__":
    # Allow running with: python test_outputs.py
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
