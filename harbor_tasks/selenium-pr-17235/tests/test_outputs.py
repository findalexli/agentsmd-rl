"""
Tests for SeleniumHQ/selenium#17235
Fix VNC caps not propagated for sessions without browserName

The bug: SessionCapabilitiesMutator.apply() checked browserName match BEFORE
propagating VNC capabilities. When a request has no browserName (e.g., proxy-only
caps), the method returned early without adding se:vncEnabled and se:noVncPort.

The fix: Move the browserName check AFTER VNC capability propagation, so VNC caps
are always propagated regardless of browserName.
"""

import subprocess
import re
from pathlib import Path

REPO = Path("/workspace/selenium")
MUTATOR_FILE = REPO / "java/src/org/openqa/selenium/grid/node/config/SessionCapabilitiesMutator.java"
TEST_FILE = REPO / "java/test/org/openqa/selenium/grid/node/config/SessionCapabilitiesMutatorTest.java"


def test_new_test_method_exists():
    """
    The test method shouldPropagateVncCapsWhenRequestHasNoBrowserName must exist (fail_to_pass).

    The fix includes a new unit test that verifies VNC caps propagation for
    requests without browserName.
    """
    content = TEST_FILE.read_text()

    # Check for the new test method
    assert "shouldPropagateVncCapsWhenRequestHasNoBrowserName" in content, (
        "Missing test method: shouldPropagateVncCapsWhenRequestHasNoBrowserName. "
        "The fix must include a unit test for VNC caps propagation without browserName."
    )

    # Verify it's a proper test method with @Test annotation
    test_pattern = re.search(
        r'@Test\s+void\s+shouldPropagateVncCapsWhenRequestHasNoBrowserName\s*\(',
        content
    )
    assert test_pattern, (
        "shouldPropagateVncCapsWhenRequestHasNoBrowserName must be a proper @Test method"
    )


def test_vnc_propagation_order_in_apply_method():
    """
    The browserName check must occur AFTER VNC capability handling (fail_to_pass).

    Verifies that the VNC capability block appears before the browserName early-return.
    """
    content = MUTATOR_FILE.read_text()

    # Find the apply method
    apply_match = re.search(r'public Capabilities apply\(Capabilities capabilities\)\s*\{', content)
    assert apply_match, "Could not find apply() method"

    apply_start = apply_match.end()

    # Find the position of VNC capability handling
    vnc_match = re.search(r'Object vncEnabled = slotStereotype\.getCapability\(SE_VNC_ENABLED\)', content[apply_start:])
    assert vnc_match, "Could not find VNC capability handling code"
    vnc_pos = vnc_match.start()

    # Find the position of browserName check with early return
    browser_check = re.search(
        r'if\s*\(\s*!Objects\.equals\(slotStereotype\.getBrowserName\(\),\s*capabilities\.getBrowserName\(\)\s*\)\s*\)\s*\{\s*return\s+capabilities;',
        content[apply_start:]
    )
    assert browser_check, "Could not find browserName check with early return"
    browser_pos = browser_check.start()

    # VNC handling must come BEFORE browserName check
    assert vnc_pos < browser_pos, (
        f"VNC capability handling (pos {vnc_pos}) must appear before browserName check (pos {browser_pos}). "
        "The fix moves the browserName check AFTER VNC propagation."
    )


def test_vnc_propagation_comment_exists():
    """
    The fix must include a comment explaining why VNC caps are always propagated (fail_to_pass).

    The comment documents that requests without browserName still route to VNC-enabled slots.
    """
    content = MUTATOR_FILE.read_text()

    # Check for the explanatory comment
    assert "Always propagate VNC capabilities from the stereotype" in content, (
        "Missing comment explaining VNC propagation behavior. "
        "The fix adds a comment explaining why VNC caps are always propagated."
    )


def test_session_capabilities_mutator_test_suite():
    """
    Full SessionCapabilitiesMutator test suite passes (pass_to_pass).

    Ensures fix doesn't break existing functionality.
    """
    result = subprocess.run(
        [
            "bazel", "test",
            "//java/test/org/openqa/selenium/grid/node/config:SessionCapabilitiesMutatorTest",
            "--test_output=errors",
            "--cache_test_results=no",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, f"Test suite failed:\n{result.stdout}\n{result.stderr}"


def test_existing_vnc_tests_still_pass():
    """
    Existing VNC capability tests continue to pass (pass_to_pass).

    Tests that the fix doesn't break VNC propagation for matching browserName cases.
    """
    result = subprocess.run(
        [
            "bazel", "test",
            "//java/test/org/openqa/selenium/grid/node/config:SessionCapabilitiesMutatorTest",
            "--test_filter=shouldCopyVncCapabilityFromStereotype",
            "--test_output=errors",
            "--cache_test_results=no",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, f"Existing VNC test failed:\n{result.stdout}\n{result.stderr}"


def test_build_source_module():
    """
    Source module compiles successfully (pass_to_pass).

    Verifies that the SessionCapabilitiesMutator source code compiles without errors.
    """
    result = subprocess.run(
        [
            "bazel", "build",
            "//java/src/org/openqa/selenium/grid/node/config:config",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr[-1000:]}"


def test_default_slot_matcher_vnc():
    """
    DefaultSlotMatcher VNC capability tests pass (pass_to_pass).

    Tests slot matching behavior with VNC capabilities, ensuring the fix
    doesn't break the overall VNC capability handling in the grid.
    """
    result = subprocess.run(
        [
            "bazel", "test",
            "//java/test/org/openqa/selenium/grid/data:DefaultSlotMatcherTest",
            "--test_output=errors",
            "--cache_test_results=no",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, f"DefaultSlotMatcher tests failed:\n{result.stdout}\n{result.stderr}"
