#!/usr/bin/env python3
"""
Task harness for electric-sql-fast-loop-detection.
Runs pytest-style verification of task outputs.
"""

import subprocess
import os
import sys

REPO = "/workspace/electric/packages/elixir-client"
PATCH_APPLIED = os.path.exists(os.path.join(REPO, "lib/electric/client/shape_state.ex.bak")) or \
    os.path.exists(os.path.join(REPO, "lib/electric/client/stream.ex"))

def run_elixir_tests():
    """Run the Elixir client's test suite."""
    result = subprocess.run(
        ["mix", "test", "--trace"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    return result

def test_fast_loop_check_exists():
    """ShapeState has check_fast_loop/1 function."""
    shape_state = os.path.join(REPO, "lib/electric/client/shape_state.ex")
    with open(shape_state) as f:
        content = f.read()
    assert "def check_fast_loop" in content, "check_fast_loop/1 function not found in ShapeState"
    assert "@spec check_fast_loop(t())" in content, "check_fast_loop/1 spec not found"

def test_fast_loop_constants():
    """ShapeState has fast_loop detection constants."""
    shape_state = os.path.join(REPO, "lib/electric/client/shape_state.ex")
    with open(shape_state) as f:
        content = f.read()
    assert "@fast_loop_window_ms 500" in content
    assert "@fast_loop_threshold 5" in content
    assert "@fast_loop_max_count 5" in content

def test_fast_loop_struct_fields():
    """ShapeState struct has recent_requests and fast_loop_consecutive_count fields."""
    shape_state = os.path.join(REPO, "lib/electric/client/shape_state.ex")
    with open(shape_state) as f:
        content = f.read()
    assert "recent_requests: []" in content
    assert "fast_loop_consecutive_count: 0" in content

def test_clear_fast_loop_exists():
    """ShapeState has clear_fast_loop/1 function."""
    shape_state = os.path.join(REPO, "lib/electric/client/shape_state.ex")
    with open(shape_state) as f:
        content = f.read()
    assert "def clear_fast_loop" in content, "clear_fast_loop/1 function not found"

def test_stream_calls_check_fast_loop():
    """Stream module calls check_fast_loop in the fetch path."""
    stream = os.path.join(REPO, "lib/electric/client/stream.ex")
    with open(stream) as f:
        content = f.read()
    assert "check_fast_loop(stream)" in content, "Stream does not call check_fast_loop"

def test_stream_clears_fast_loop_on_live():
    """Stream clears fast-loop tracking when transitioning to live/up-to-date mode."""
    stream = os.path.join(REPO, "lib/electric/client/stream.ex")
    with open(stream) as f:
        content = f.read()
    assert "ShapeState.clear_fast_loop" in content, "Stream does not clear fast-loop on live mode"

def test_elixir_tests_pass():
    """ShapeState unit tests pass (pass_to_pass)."""
    shape_state_test = os.path.join(REPO, "test/electric/client/shape_state_test.exs")
    if not os.path.exists(shape_state_test):
        raise AssertionError(
            "test/electric/client/shape_state_test.exs not found. "
            "Fast-loop detection has not been implemented yet."
        )
    result = subprocess.run(
        ["mix", "test", "--trace", "test/electric/client/shape_state_test.exs"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    # shape_state_test.exs has 8 tests, all should pass
    assert result.returncode == 0, f"ShapeState tests failed:\n{result.stderr[-1000:]}"
    assert "8 tests" in result.stdout, f"Expected 8 tests in shape_state_test.exs, got: {result.stdout}"

def test_elixir_format_check():
    """Repo's Elixir formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["mix", "format", "--check-formatted"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"

def test_elixir_compile_warnings():
    """Repo compiles without warnings (pass_to_pass)."""
    r = subprocess.run(
        ["mix", "compile", "--force", "--all-warnings", "--warnings-as-errors"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"Compile with warnings failed:\n{r.stderr[-500:]}"

def test_elixir_fetch_unit_tests():
    """Fetch module unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["mix", "test", "test/electric/client/fetch/request_test.exs",
         "test/electric/client/fetch/response_test.exs",
         "test/electric/client/message_test.exs",
         "test/electric/client/poll_test.exs"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Fetch unit tests failed:\n{r.stderr[-500:]}"

def test_elixir_util_tests():
    """Util module tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["mix", "test", "test/electric/client/util_test.exs"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Util tests failed:\n{r.stderr[-500:]}"

def test_elixir_mock_and_http_tests():
    """Mock and HTTP fetch tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["mix", "test", "test/electric/client/mock_test.exs",
         "test/electric/client/fetch/http_test.exs"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Mock/HTTP tests failed:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    # Run all tests
    tests = [
        test_fast_loop_check_exists,
        test_fast_loop_constants,
        test_fast_loop_struct_fields,
        test_clear_fast_loop_exists,
        test_stream_calls_check_fast_loop,
        test_stream_clears_fast_loop_on_live,
        test_elixir_tests_pass,
        test_elixir_format_check,
        test_elixir_compile_warnings,
        test_elixir_fetch_unit_tests,
        test_elixir_util_tests,
        test_elixir_mock_and_http_tests,
    ]

    failed = []
    for test in tests:
        print(f"Running {test.__name__}...", end=" ")
        try:
            test()
            print("PASS")
        except Exception as e:
            print(f"FAIL: {e}")
            failed.append(test.__name__)

    if failed:
        print(f"\n{len(failed)} tests failed: {failed}")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)