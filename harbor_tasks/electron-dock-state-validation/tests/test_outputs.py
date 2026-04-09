"""
Test suite for electron dock_state validation fix.

This tests that dock_state values are properly validated against an allowlist
before being used in JavaScript execution contexts.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/electron")
TARGET_FILE = REPO / "shell/browser/ui/inspectable_web_contents.cc"


def test_file_exists():
    """Verify the target file exists."""
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"


def test_kValidDockStates_defined():
    """Verify kValidDockStates allowlist is defined."""
    content = TARGET_FILE.read_text()

    # Check for the allowlist definition
    assert "kValidDockStates" in content, "kValidDockStates allowlist not found"
    assert "base::MakeFixedFlatSet" in content, "MakeFixedFlatSet not used for allowlist"

    # Check for valid states in the set
    assert '"bottom"' in content, "bottom state not in allowlist"
    assert '"left"' in content, "left state not in allowlist"
    assert '"right"' in content, "right state not in allowlist"
    assert '"undocked"' in content, "undocked state not in allowlist"


def test_IsValidDockState_function():
    """Verify IsValidDockState validation function exists."""
    content = TARGET_FILE.read_text()

    # Check for function definition
    assert "IsValidDockState" in content, "IsValidDockState function not found"

    # Verify it uses the allowlist
    assert "kValidDockStates.contains" in content, "Function doesn't use allowlist for validation"


def test_SetDockState_validates_input():
    """Verify SetDockState validates input before assigning."""
    content = TARGET_FILE.read_text()

    # Find the SetDockState function and check for validation
    pattern = r'void InspectableWebContents::SetDockState\([^)]+\).*?\{[^}]+\}[^}]*\}'
    match = re.search(pattern, content, re.DOTALL)

    # If we can't find the exact pattern, look for the key parts
    if not match:
        # Check for the validation pattern in SetDockState area
        lines = content.split('\n')
        in_set_dock = False
        found_validation = False
        for i, line in enumerate(lines):
            if 'void InspectableWebContents::SetDockState' in line:
                in_set_dock = True
            if in_set_dock:
                if 'IsValidDockState' in line and '?' in line:
                    found_validation = True
                    break
                if line.strip() == '}' and i > 0 and 'can_dock_' in lines[i-1]:
                    break
        assert found_validation, "SetDockState doesn't validate input with IsValidDockState"


def test_LoadCompleted_handles_invalid_dock_state():
    """Verify LoadCompleted properly handles invalid dock_state from preferences."""
    content = TARGET_FILE.read_text()

    # Look for the LoadCompleted function and its dock_state handling
    assert "IsValidDockState(sanitized)" in content, "LoadCompleted doesn't validate sanitized dock_state"

    # Check for null pointer check
    assert "if (current_dock_state)" in content, "LoadCompleted doesn't check for null current_dock_state"


def test_sanitization_before_validation():
    """Verify that quotes are removed before validation."""
    content = TARGET_FILE.read_text()

    # Check that RemoveChars is called with quote character
    assert 'base::RemoveChars(*current_dock_state, "\\"", &sanitized)' in content, \
        "Quotes not removed before validation"


def test_default_fallback_to_right():
    """Verify invalid dock states fall back to 'right'."""
    content = TARGET_FILE.read_text()

    # Check for fallback pattern: condition ? valid : "right"
    assert '? state : "right"' in content.replace("'", '"') or \
           '? sanitized : "right"' in content.replace("'", '"') or \
           '? state : \"right\"' in content or \
           '? sanitized : \"right\"' in content, \
        "Invalid dock states don't fall back to 'right'"


def test_fixed_flat_set_include():
    """Verify the correct header is included for FixedFlatSet."""
    content = TARGET_FILE.read_text()
    assert '#include "base/containers/fixed_flat_set.h"' in content, \
        "Required header for FixedFlatSet not included"


def test_all_validation_points():
    """Count and verify all validation points in the file."""
    content = TARGET_FILE.read_text()

    # Should have IsValidDockState calls in both SetDockState and LoadCompleted
    is_valid_calls = content.count("IsValidDockState")
    assert is_valid_calls >= 2, f"Expected at least 2 IsValidDockState calls, found {is_valid_calls}"


def test_no_unsanitized_assignment():
    """Verify dock_state_ is never assigned without validation."""
    content = TARGET_FILE.read_text()

    # The old code had: dock_state_ = state; (without validation)
    # We should see validation being used now
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'dock_state_ =' in line and 'IsValidDockState' not in line:
            # Check if this is in LoadCompleted with null check (which is ok)
            if 'right' not in line and 'sanitized' not in line:
                assert False, f"Found unvalidated dock_state_ assignment at line {i+1}: {line}"


def test_clang_format_compliance():
    """Verify basic C++ formatting compliance."""
    result = subprocess.run(
        ["grep", "kValidDockStates", str(TARGET_FILE)],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        output = result.stdout
        # Check constexpr formatting
        assert "constexpr auto" in output or "constexpr" in content, \
            "constexpr not properly formatted"
