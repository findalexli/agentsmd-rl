"""
Test suite for Selenium Grid VNC capabilities fix.
Tests that VNC capabilities are propagated even for sessions without browserName.
"""

import subprocess
import os
import sys

REPO = "/workspace/selenium"
TEST_TARGET = "//java/test/org/openqa/selenium/grid/node/config:SessionCapabilitiesMutatorTest"
MUTATOR_PATH = "java/src/org/openqa/selenium/grid/node/config/SessionCapabilitiesMutator.java"
GRID_TEST_TARGET = "//java/test/org/openqa/selenium/grid/node/config:medium-tests"


def test_code_compiles():
    """
    Pass-to-pass: Verify the Java code compiles without errors.
    This is a basic syntax/compilation check.
    """
    result = subprocess.run(
        ["bazel", "build", "//java/src/org/openqa/selenium/grid/node/config:config"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Compilation failed:\n{result.stderr}"


def test_vnc_caps_propagated_for_no_browser_name():
    """
    Fail-to-pass test: VNC capabilities should be propagated even when
    the session request has no browserName (e.g., proxy-only capabilities).

    The bug: When browserName doesn't match, there's an early return that
    prevents VNC capabilities from being propagated.

    The fix: Move VNC capability handling BEFORE the browserName check.
    """
    source_path = os.path.join(REPO, MUTATOR_PATH)
    with open(source_path, 'r') as f:
        content = f.read()

    # Find the apply method
    apply_start = content.find("public Capabilities apply(Capabilities capabilities)")
    assert apply_start != -1, "apply method not found"

    # Look for where getCapability(SE_VNC_ENABLED) is called - this is the VNC handling
    vnc_get_capability = "slotStereotype.getCapability(SE_VNC_ENABLED)"
    vnc_idx = content.find(vnc_get_capability, apply_start)
    assert vnc_idx != -1, "VNC capability retrieval not found"

    # Find the browserName check
    browser_check_line = "slotStereotype.getBrowserName(), capabilities.getBrowserName()"
    browser_check_idx = content.find(browser_check_line, apply_start)
    assert browser_check_idx != -1, "browserName check not found"

    # The fix: VNC handling must happen BEFORE the browser check
    # In the buggy code, the early return happens before VNC handling
    assert vnc_idx < browser_check_idx, \
        "VNC handling must come before browserName check - bug not fixed!"


def test_existing_tests_still_pass():
    """
    Pass-to-pass: Existing SessionCapabilitiesMutator tests should still pass.
    This ensures the fix doesn't break existing functionality.
    """
    result = subprocess.run(
        ["bazel", "test", TEST_TARGET,
         "--test_output=errors"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, f"Existing tests failed:\n{result.stderr}\n{result.stdout}"


def test_vnc_port_handled_before_browser_check():
    """
    Fail-to-pass: Verify that VNC port (SE_NO_VNC_PORT) is handled before the browserName check.
    This ensures that proxy-only sessions get the VNC port assigned.
    """
    source_path = os.path.join(REPO, MUTATOR_PATH)
    with open(source_path, 'r') as f:
        content = f.read()

    # Find the apply method
    apply_start = content.find("public Capabilities apply(Capabilities capabilities)")
    assert apply_start != -1, "apply method not found"

    # Look for where VNC port is retrieved inside the apply method
    vnc_port_get = "slotStereotype.getCapability(SE_NO_VNC_PORT)"
    vnc_port_idx = content.find(vnc_port_get, apply_start)

    # Find the browserName check inside the apply method
    browser_check_line = "slotStereotype.getBrowserName(), capabilities.getBrowserName()"
    browser_check_idx = content.find(browser_check_line, apply_start)

    assert vnc_port_idx != -1, "VNC port retrieval not found in apply method"
    assert browser_check_idx != -1, "browserName check not found in apply method"

    # VNC port handling should come before the browserName check (fix applied)
    assert vnc_port_idx < browser_check_idx, \
        "VNC port handling should come before browserName check - bug not fixed!"


def test_no_early_return_before_vnc_handling():
    """
    Fail-to-pass test: Ensure there is no early return statement
    before VNC capability handling.

    The bug: When browserName doesn't match, there's an early return that
    prevents VNC capabilities from being propagated.

    The fix: Move VNC handling before the browserName check/return.
    """
    source_path = os.path.join(REPO, MUTATOR_PATH)
    with open(source_path, 'r') as f:
        content = f.read()

    # Find the start of the apply method
    apply_method_start = content.find("public Capabilities apply(Capabilities capabilities)")
    assert apply_method_start != -1, "apply method not found"

    # Find the VNC handling inside the apply method
    vnc_section_start = content.find("slotStereotype.getCapability(SE_VNC_ENABLED)", apply_method_start)
    assert vnc_section_start != -1, "VNC handling not found in apply method"

    # Find the browserName check inside the apply method
    browser_check_idx = content.find("slotStereotype.getBrowserName(), capabilities.getBrowserName()", apply_method_start)
    assert browser_check_idx != -1, "browserName check not found in apply method"

    # Check that there's no return statement between VNC handling and browser check
    # (in the buggy code, the return is between them - actually, the return comes AFTER
    # the browser check, but the browser check itself comes BEFORE VNC handling)

    # In the fixed code:
    # 1. VNC handling comes first
    # 2. Then browser check
    # 3. Then return (if browser doesn't match)

    # In the buggy code:
    # 1. Browser check comes first
    # 2. Early return (if browser doesn't match)
    # 3. VNC handling (never reached if browser doesn't match)

    # So the assertion should be: VNC handling must come BEFORE browser check
    assert vnc_section_start < browser_check_idx, \
        "VNC handling must come before browserName check - early return bug not fixed!"


# ==============================================================================
# PASS-TO-PASS TESTS: Repository CI/CD checks
# These tests verify the repo's own CI/CD pipeline passes on the base commit.
# ==============================================================================


def test_repo_grid_java_tests():
    """
    Pass-to-pass: Grid node config tests pass.
    Runs the medium-tests target for grid node config (pass_to_pass).
    """
    result = subprocess.run(
        ["bazel", "test", GRID_TEST_TARGET,
         "--test_output=errors",
         "--test_size_filters=medium,small"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"Grid Java tests failed:\n{result.stderr[-1000:]}"


def test_repo_grid_build():
    """
    Pass-to-pass: Grid node config package builds successfully.
    Verifies the build target for grid node config compiles (pass_to_pass).
    """
    result = subprocess.run(
        ["bazel", "build", "//java/src/org/openqa/selenium/grid/node/config:all"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Grid build failed:\n{result.stderr[-500:]}"


def test_repo_bazel_query_grid():
    """
    Pass-to-pass: Bazel can query the grid package structure.
    Verifies the Bazel build files are valid and the package structure is correct (pass_to_pass).
    """
    result = subprocess.run(
        ["bazel", "query", "//java/src/org/openqa/selenium/grid/node/config:all"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Bazel query failed:\n{result.stderr[-500:]}"
    # Should return at least one target
    assert result.stdout.strip(), "Bazel query returned no targets"


def test_repo_node_options_test():
    """
    Pass-to-pass: NodeOptionsTest passes.
    This test covers grid node configuration options, which is related to the
    SessionCapabilitiesMutator component being fixed (pass_to_pass).
    """
    result = subprocess.run(
        ["bazel", "test", "//java/test/org/openqa/selenium/grid/node/config:NodeOptionsTest",
         "--test_output=errors"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"NodeOptionsTest failed:\n{result.stderr[-1000:]}"
