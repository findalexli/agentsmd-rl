"""
Tests for quickwit-ingester-status-default task.

Verifies that when an ingester doesn't broadcast its status, it defaults to Ready.
"""
import subprocess
import os
import pytest
import re

# The git repo root
REPO = os.environ.get("REPO", "/workspace/quickwit-repo")
# The cargo workspace root (where Cargo.toml is)
WORKSPACE = os.path.join(REPO, "quickwit")


def test_ingester_status_fix_in_member_rs():
    """
    Fail-to-pass: Verify that the fix is in place by checking that
    unwrap_or(IngesterStatus::Ready) replaces unwrap_or_default() in the
    ingester_status function.

    On base commit:
        .unwrap_or_default()  # Returns protobuf default (Unknown/0)
    On fixed commit:
        .unwrap_or(IngesterStatus::Ready)  # Returns Ready/1

    This is a fail-to-pass test because:
    - Base commit: The pattern unwrap_or(IngesterStatus::Ready) is NOT present
    - Fixed commit: The pattern unwrap_or(IngesterStatus::Ready) IS present
    """
    member_rs_path = os.path.join(REPO, "quickwit/quickwit-cluster/src/member.rs")
    with open(member_rs_path, "r") as f:
        content = f.read()

    # The fix uses unwrap_or(IngesterStatus::Ready)
    assert "unwrap_or(IngesterStatus::Ready)" in content, (
        "Expected to find 'unwrap_or(IngesterStatus::Ready)' in member.rs. "
        "The fix should replace .unwrap_or_default() with .unwrap_or(IngesterStatus::Ready) "
        "in the ingester_status() function."
    )

    # Verify the fix is in the ingester_status function inside impl NodeStateExt for NodeState
    lines = content.split('\n')
    found_impl = False
    found_correct_impl = False

    for i, line in enumerate(lines):
        # Look for impl NodeStateExt for NodeState block
        if 'impl NodeStateExt for NodeState' in line:
            found_impl = True
            # Now find the ingester_status function within this impl block
            # It should come after this line
            impl_region = '\n'.join(lines[i:])  # Rest of the impl block
            # Find the ingester_status function in this region
            if 'fn ingester_status(&self)' in impl_region:
                # Get the function implementation
                func_start = impl_region.find('fn ingester_status(&self)')
                if func_start != -1:
                    func_region = impl_region[func_start:func_start+300]
                    if 'unwrap_or(IngesterStatus::Ready)' in func_region:
                        found_correct_impl = True
                    # Check that the old buggy code is not there
                    if 'unwrap_or_default()' in func_region:
                        raise AssertionError(
                            "Found .unwrap_or_default() still present in ingester_status function. "
                            "The fix should replace it with unwrap_or(IngesterStatus::Ready)."
                        )
            break

    assert found_impl, "Could not find impl NodeStateExt for NodeState"
    assert found_correct_impl, (
        "Found unwrap_or(IngesterStatus::Ready) but not in ingester_status function in impl NodeStateExt. "
        "The fix should be in the ingester_status() function inside the impl block."
    )


def test_cargo_check_quickwit_cluster():
    """
    Pass-to-pass: The quickwit-cluster crate should compile without errors.
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "quickwit-cluster", "--features=testsuite"],
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        timeout=300
    )
    print(f"STDOUT:\n{result.stdout}")
    print(f"STDERR:\n{result.stderr}")
    assert result.returncode == 0, f"Cargo check failed:\n{result.stderr[-1000:]}"


def test_cargo_test_quickwit_cluster_testsuite():
    """
    Pass-to-pass: Run the existing testsuite for quickwit-cluster to ensure no regressions.
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "quickwit-cluster", "--features=testsuite"],
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        timeout=600
    )
    print(f"STDOUT:\n{result.stdout}")
    print(f"STDERR:\n{result.stderr}")
    assert result.returncode == 0, f"Tests failed:\n{result.stderr[-1000:]}"


def test_cargo_clippy_quickwit_cluster():
    """
    Pass-to-pass: Run clippy on quickwit-cluster to catch common mistakes and improve code quality.
    """
    result = subprocess.run(
        ["cargo", "clippy", "-p", "quickwit-cluster", "--features=testsuite", "--", "-D", "warnings"],
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        timeout=600
    )
    print(f"STDOUT:\n{result.stdout}")
    print(f"STDERR:\n{result.stderr}")
    assert result.returncode == 0, f"Clippy failed:\n{result.stderr[-1000:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])