"""Tests for Selenium Grid VNC capabilities fix.

This test module verifies that VNC capabilities are properly propagated
for session requests that don't include a browserName capability.
"""

import os
import subprocess
import sys

REPO = "/workspace/selenium"


def write_reward(value):
    """Write the reward value to the expected location."""
    os.makedirs("/logs/verifier", exist_ok=True)
    with open("/logs/verifier/reward.txt", "w") as f:
        f.write(str(value))


def test_vnc_caps_propagated_for_no_browser_name():
    """F2P: VNC capabilities should be present for sessions without browserName.

    When a session request arrives without a browserName capability (e.g. proxy-only
    configuration), the Grid should still propagate VNC capabilities (se:vncEnabled,
    se:noVncPort) from the slot stereotype to the session capabilities.

    This test creates a temporary Java test file that directly tests the behavior
    and runs it via Bazel, verifying the fix is present.
    """
    # Create a temporary Java test file that tests the specific bug
    java_test_code = '''
package org.openqa.selenium.grid.node.config;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.openqa.selenium.Capabilities;
import org.openqa.selenium.ImmutableCapabilities;

public class VncCapabilityTest {
    @Test
    void vncCapsShouldBePropagatedForRequestWithoutBrowserName() {
        // Create a stereotype with VNC enabled (like a node with VNC configured)
        Capabilities stereotype = new ImmutableCapabilities(
            "browserName", "chrome",
            "se:vncEnabled", true,
            "se:noVncPort", 7900
        );

        SessionCapabilitiesMutator mutator = new SessionCapabilitiesMutator(stereotype);

        // Create a request WITHOUT browserName (e.g., proxy-only config)
        Capabilities request = new ImmutableCapabilities("proxy", "direct");

        // Apply the mutator
        Capabilities result = mutator.apply(request);

        // The VNC capabilities from the stereotype should be present in the result
        // This is the bug: on base commit, these will be null because the code
        // returns early when browserNames don't match (request has null browserName)
        assertThat(result.getCapability("se:vncEnabled"))
            .as("se:vncEnabled should be propagated from stereotype even when request has no browserName")
            .isEqualTo(true);
        assertThat(result.getCapability("se:noVncPort"))
            .as("se:noVncPort should be propagated from stereotype even when request has no browserName")
            .isEqualTo(7900);
    }
}
'''

    # Write the test file
    test_file_path = f"{REPO}/java/test/org/openqa/selenium/grid/node/config/VncCapabilityTest.java"
    import os
    os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
    with open(test_file_path, 'w') as f:
        f.write(java_test_code)

    # Run the test via Bazel
    result = subprocess.run(
        [
            "bazel",
            "test",
            "//java/test/org/openqa/selenium/grid/node/config:VncCapabilityTest",
            "--test_output=all",
            "--cache_test_results=no",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode != 0:
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

    assert result.returncode == 0, (
        "VNC capabilities are not being propagated for sessions without browserName. "
        "The bug is that SessionCapabilitiesMutator.apply() returns early when "
        "browserNames don't match, before propagating VNC capabilities from the stereotype."
    )


def test_existing_functionality_still_works():
    """P2P: Existing SessionCapabilitiesMutator functionality should remain intact.

    The fix should not break any existing functionality - tests like browser name
    matching, stereotype merging, and capability propagation for normal browser requests
    should still pass.
    """
    # Run all tests in the SessionCapabilitiesMutatorTest class except the new one
    result = subprocess.run(
        [
            "bazel",
            "test",
            "//java/test/org/openqa/selenium/grid/node/config:SessionCapabilitiesMutatorTest",
            "--test_filter=-shouldPropagateVncCapsWhenRequestHasNoBrowserName",
            "--test_output=errors",
            "--cache_test_results=no",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode != 0:
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

    assert result.returncode == 0, (
        "Existing SessionCapabilitiesMutatorTest tests failed. "
        "The fix broke existing functionality."
    )


def test_vnc_caps_with_normal_browser_request():
    """P2P: Normal browser requests with matching stereotype still work.

    When a normal browser request (with browserName) is matched to a slot,
    VNC capabilities should still be propagated correctly along with
    browser-specific capabilities.
    """
    result = subprocess.run(
        [
            "bazel",
            "test",
            "//java/test/org/openqa/selenium/grid/node/config:SessionCapabilitiesMutatorTest",
            "--test_filter=shouldMergeTopLevelStereotypeAndCaps",
            "--test_output=errors",
            "--cache_test_results=no",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert result.returncode == 0, (
        "Normal browser requests should still receive proper capability merging "
        "including VNC capabilities when the stereotype has them."
    )


def test_code_compiles():
    """P2P: The Java code should compile without errors."""
    result = subprocess.run(
        [
            "bazel",
            "build",
            "//java/src/org/openqa/selenium/grid/node/config:config",
            "--compilation_mode=fastbuild",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode != 0:
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

    assert result.returncode == 0, "Java code failed to compile"


def test_repo_grid_config_tests():
    """P2P: Repo grid config tests pass (pass_to_pass).

    The repo's own grid config tests should pass on the base commit.
    These tests validate basic grid configuration functionality.
    """
    result = subprocess.run(
        [
            "bazel",
            "test",
            "//java/test/org/openqa/selenium/grid/config:AnnotatedConfigTest",
            "//java/test/org/openqa/selenium/grid/config:ConfigTest",
            "//java/test/org/openqa/selenium/grid/data:DefaultSlotMatcherTest",
            "--test_output=errors",
            "--cache_test_results=no",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode != 0:
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

    assert result.returncode == 0, "Repo grid config tests failed"


def test_repo_format_lint():
    """P2P: Repo format lint check passes (pass_to_pass).

    The repo's format lint check should pass on the base commit.
    This ensures code follows the repo's formatting standards.
    """
    result = subprocess.run(
        ["./scripts/format.sh", "--lint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

    assert result.returncode == 0, "Format lint check failed"


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
