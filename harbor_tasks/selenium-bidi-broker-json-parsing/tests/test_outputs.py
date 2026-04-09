"""Tests for Selenium BiDi Broker JSON parsing optimization.

This PR refactors the ProcessReceivedMessage method in Broker.cs to:
1. Use ValueTextEquals() with UTF-8 byte literals for property name comparison (more efficient)
2. Fix type inconsistencies (paramsStartIndex/paramsEndIndex from long to int)
3. Add proper handling for unknown message types
"""

import subprocess
import os
import sys

REPO = "/workspace/selenium"
BROKER_PATH = f"{REPO}/dotnet/src/webdriver/BiDi/Broker.cs"


def test_bazel_assembly_info_build():
    """Bazel can build assembly-info target (pass_to_pass).

    Verifies that the Bazel build system is properly configured and can
    generate assembly info for the .NET WebDriver project. This is a
    lightweight compile check that completes in ~12 seconds.
    """
    r = subprocess.run(
        ["bazel", "build", "//dotnet/src/webdriver:assembly-info"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Bazel assembly-info build failed:\n{r.stderr[-500:]}"


def test_broker_cs_exists():
    """Broker.cs file exists and is readable (pass_to_pass).

    Verifies that the main source file being modified exists in the
    expected location within the repository.
    """
    assert os.path.exists(BROKER_PATH), f"Broker.cs not found at {BROKER_PATH}"
    with open(BROKER_PATH, 'r') as f:
        content = f.read()
    assert len(content) > 0, "Broker.cs is empty"
    assert "ProcessReceivedMessage" in content, "Broker.cs missing expected method"


def test_uses_valuetextequals_for_properties():
    """Uses ValueTextEquals() with UTF-8 byte literals for JSON property parsing (f2p).

    The optimized code uses reader.ValueTextEquals("property"u8) instead of
    reader.GetString() == "property" for more efficient UTF-8 property name comparison.
    """
    with open(BROKER_PATH, 'r') as f:
        content = f.read()

    # Check for the optimized parsing pattern - ValueTextEquals with u8 suffix
    assert 'ValueTextEquals("id"u8)' in content, \
        "Should use ValueTextEquals('id'u8) for efficient property name comparison"
    assert 'ValueTextEquals("type"u8)' in content, \
        "Should use ValueTextEquals('type'u8) for efficient property name comparison"
    assert 'ValueTextEquals("method"u8)' in content, \
        "Should use ValueTextEquals('method'u8) for efficient property name comparison"


def test_int_indices_for_params():
    """Uses int type for params indices instead of long (f2p).

    The fix corrects the type inconsistency where paramsStartIndex and paramsEndIndex
    were declared as long but should be int for consistency with ReadOnlyMemory<byte> constructor.
    """
    with open(BROKER_PATH, 'r') as f:
        content = f.read()

    # Check that params indices are declared as int, not long
    # The base commit uses: long paramsStartIndex = 0; long paramsEndIndex = 0;
    # The fix uses: int paramsStartIndex = 0; int paramsEndIndex = 0;

    lines = content.split('\n')

    for i, line in enumerate(lines):
        if 'paramsStartIndex' in line and 'long paramsStartIndex' in line:
            assert False, "paramsStartIndex should be int, not long"
        if 'paramsEndIndex' in line and 'long paramsEndIndex' in line:
            assert False, "paramsEndIndex should be int, not long"

    # Verify int declarations exist
    int_start_found = False
    int_end_found = False
    for line in lines:
        if 'int paramsStartIndex' in line:
            int_start_found = True
        if 'int paramsEndIndex' in line:
            int_end_found = True

    assert int_start_found, "paramsStartIndex should be declared as int"
    assert int_end_found, "paramsEndIndex should be declared as int"


def test_message_type_constants():
    """Uses int constants for message types instead of string comparison (f2p).

    The optimization converts string type comparison to int constants:
    - TypeSuccess = 1 (was "success")
    - TypeEvent = 2 (was "event")
    - TypeError = 3 (was "error")
    """
    with open(BROKER_PATH, 'r') as f:
        content = f.read()

    # Check for the message type constants
    assert 'const int TypeSuccess = 1' in content, \
        "Should define TypeSuccess constant"
    assert 'const int TypeEvent = 2' in content, \
        "Should define TypeEvent constant"
    assert 'const int TypeError = 3' in content, \
        "Should define TypeError constant"

    # Check that switch uses the int variable, not string
    assert 'switch (messageType)' in content, \
        "Should switch on int messageType variable, not string type"


def test_unknown_message_type_handling():
    """Handles unknown message types with warning logging (f2p).

    The fix adds a default case to the message type switch that logs a warning
    when an unrecognized message type is received.
    """
    with open(BROKER_PATH, 'r') as f:
        content = f.read()

    # Check for default case in switch statement
    assert 'default:' in content, \
        "Should have a default case for unknown message types"

    # Check for warning log
    assert 'unknown message type' in content.lower() or \
           'IsEnabled(LogEventLevel.Warn)' in content, \
        "Should log warning for unknown message types"
