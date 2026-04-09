"""
Test outputs for sui-indexer-alt-framework pipeline state validation fix.

This tests that the WatermarkPart struct properly panics on invalid state:
1. When batch_rows exceeds total_rows after add()
2. When trying to take more rows than available

Before the fix, these used debug_assert! which is ignored in release builds.
After the fix, they use assert! which always panics.
"""

import subprocess
import sys

REPO = "/workspace/sui"
TARGET_FILE = "crates/sui-indexer-alt-framework/src/pipeline/mod.rs"


def run_cargo_test(test_pattern: str, timeout: int = 120) -> tuple[int, str, str]:
    """Run cargo test for the indexer-alt-framework crate."""
    cmd = [
        "cargo", "test", "-p", "sui-indexer-alt-framework",
        test_pattern, "--", "--nocapture"
    ]
    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        timeout=timeout
    )
    return result.returncode, result.stdout.decode(), result.stderr.decode()


def test_assert_prevents_batch_rows_exceeding_total():
    """
    Test that add() panics when batch_rows would exceed total_rows.
    This is a fail-to-pass test - it should fail before the fix.
    """
    # Run the test that triggers the assertion
    code, stdout, stderr = run_cargo_test("test_watermark_part_batch_rows_exceeds_total")
    output = stdout + stderr

    # The test should pass (return 0) on the fixed code
    assert code == 0, f"Test failed with code {code}:\n{output}"

    # Verify we saw the assertion message format in the test output
    # (The test itself validates this)
    assert "batch_rows" in output.lower() or "PASSED" in output or "ok" in output, \
        f"Expected test to validate assertion behavior:\n{output}"


def test_assert_prevents_taking_more_than_available():
    """
    Test that take() panics when trying to take more rows than available.
    This is a fail-to-pass test - it should fail before the fix.
    """
    code, stdout, stderr = run_cargo_test("test_watermark_part_take_too_many")
    output = stdout + stderr

    # The test should pass (return 0) on the fixed code
    assert code == 0, f"Test failed with code {code}:\n{output}"

    assert "PASSED" in output or "ok" in output or "panicked" in output.lower(), \
        f"Expected test to validate assertion behavior:\n{output}"


def test_checkpoint_mismatch_assertion():
    """
    Test that add() panics when checkpoint values don't match.
    """
    code, stdout, stderr = run_cargo_test("test_watermark_part_checkpoint_mismatch")
    output = stdout + stderr

    assert code == 0, f"Test failed with code {code}:\n{output}"


def test_compilation_succeeds():
    """
    Verify the crate compiles without errors.
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-indexer-alt-framework"],
        cwd=REPO,
        capture_output=True,
        timeout=180
    )

    assert result.returncode == 0, \
        f"Compilation failed:\n{result.stderr.decode()}"


def test_assertions_are_present():
    """
    P2P test: Verify the fix is present by checking source code.
    This is a pass-to-pass test on the fix.
    """
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Check that assert! is used (not debug_assert!)
    # The fix should have:
    # 1. assert_eq! for checkpoint check in add()
    # 2. assert! for batch_rows <= total_rows
    # 3. assert! for batch_rows >= rows in take()

    # Find the add() method - look for assert! not debug_assert! for checkpoint
    # and the batch_rows <= total_rows assertion
    assert "assert_eq!(self.checkpoint(), other.checkpoint())" in content, \
        "Missing assert_eq! for checkpoint check in add()"

    assert 'assert!(\n            self.batch_rows <= self.total_rows,' in content, \
        "Missing batch_rows <= total_rows assertion"

    assert 'assert!(\n            self.batch_rows >= rows,' in content, \
        "Missing batch_rows >= rows assertion in take()"

    # Make sure debug_assert! was replaced (not still present in these spots)
    # We check there are no debug_assert! for these specific conditions
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'fn add' in line:
            # Check next ~15 lines for debug_assert_eq
            for j in range(i, min(i+15, len(lines))):
                if 'debug_assert_eq!(self.checkpoint()' in lines[j]:
                    assert False, "Found debug_assert_eq! in add() - should be assert_eq!"
                if 'debug_assert!(' in lines[j] and j < i + 15:
                    # Check if this is about batch_rows/total_rows
                    context = '\n'.join(lines[j:min(j+5, len(lines))])
                    if 'checkpoint' in context.lower():
                        assert False, "Found debug_assert! for checkpoint check"

        if 'fn take' in line:
            # Check next ~10 lines for debug_assert! about batch_rows >= rows
            for j in range(i, min(i+10, len(lines))):
                if 'debug_assert!(' in lines[j] and 'batch_rows' in lines[j]:
                    assert False, "Found debug_assert! for batch_rows check in take()"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
