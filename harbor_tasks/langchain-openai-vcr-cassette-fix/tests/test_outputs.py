"""Tests for langchain-openai VCR cassette fix.

This task tests that the agent correctly fixes VCR cassette playback
by removing "uri" from match_on (since URIs are redacted during recording).
"""

import os
import subprocess
import sys
from pathlib import Path

# Path to the openai partner package
REPO = Path("/workspace/langchain")
OPENAI_PKG = REPO / "libs/partners/openai"
CONftest_PY = OPENAI_PKG / "tests/conftest.py"
TEST_FILE = OPENAI_PKG / "tests/integration_tests/chat_models/test_responses_api.py"


def test_vcr_config_excludes_uri():
    """VCR config must exclude 'uri' from match_on since URIs are redacted.

    This is a fail-to-pass test: on base commit, the config includes 'uri'
    in match_on but URIs are redacted to '**REDACTED**', causing playback failures.
    """
    assert CONftest_PY.exists(), f"conftest.py not found at {CONftest_PY}"

    content = CONftest_PY.read_text()

    # Check that the fix is present: "uri" is filtered out of match_on
    # The fixed code should have: if m != "uri"
    assert 'if m != "uri"' in content, (
        "VCR config does not exclude 'uri' from match_on. "
        "The fix should filter out 'uri' since before_record_request redacts URIs."
    )

    # Also verify the structure is correct: list comprehension with both conditions
    assert "for m in config.get(\"match_on\", [])" in content, (
        "match_on configuration not found or incorrectly structured"
    )


def test_vcr_config_structure():
    """VCR config has proper structure with json_body matcher and filters."""
    assert CONftest_PY.exists(), f"conftest.py not found at {CONftest_PY}"

    content = CONftest_PY.read_text()

    # Check base_vcr_config is called
    assert "base_vcr_config()" in content, "base_vcr_config() not called"

    # Check json_body matcher is used
    assert "json_body" in content, "json_body matcher not configured"

    # Check filter_headers are extended
    assert "filter_headers" in content, "filter_headers not configured"

    # Check before_record_request is set
    assert "before_record_request" in content, "before_record_request not configured"

    # Check before_record_response is set
    assert "before_record_response" in content, "before_record_response not configured"


def test_test_strings_match_cassettes():
    """Test strings must match the recorded cassettes.

    The cassettes were recorded with specific typos/intentional strings.
    Changing the test strings without re-recording breaks playback.
    """
    assert TEST_FILE.exists(), f"Test file not found at {TEST_FILE}"

    content = TEST_FILE.read_text()

    # These strings must match the cassettes exactly
    # The cassettes use "whats" (no apostrophe) and "buliding" (typo)
    assert 'bound_llm.invoke("whats 5 * 4")' in content, (
        "Test string 'whats 5 * 4' not found. "
        "The apostrophe-free version must be used to match cassettes."
    )

    assert 'bound_llm.stream("whats 5 * 4")' in content, (
        "Test stream string 'whats 5 * 4' not found. "
        "The apostrophe-free version must be used to match cassettes."
    )

    assert '"What was the third tallest buliding in the year 2000?"' in content, (
        "Test string with 'buliding' typo not found. "
        "The typo must be preserved to match cassettes."
    )


def test_vcr_tests_pass():
    """VCR cassette tests must pass in playback-only mode.

    Runs the VCR tests with --record-mode=none to verify cassettes work.
    This is the ultimate integration test for the fix.
    """
    # Set a fake API key for playback mode
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = "sk-fake"

    # Run VCR tests in playback-only mode
    result = subprocess.run(
        [
            "uv", "run", "--group", "test",
            "pytest",
            "--record-mode=none",
            "-m", "vcr",
            "--ignore=tests/integration_tests/chat_models/test_azure_standard.py",
            "tests/integration_tests/",
            "-v",
            "--tb=short",
        ],
        cwd=OPENAI_PKG,
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
    )

    # Check tests passed
    assert result.returncode == 0, (
        f"VCR tests failed:\nstdout: {result.stdout[-2000:]}\n"
        f"stderr: {result.stderr[-2000:]}"
    )


def test_repo_imports():
    """Repo package imports work correctly (pass-to-pass)."""
    result = subprocess.run(
        ["uv", "run", "--group", "test", "python", "-c", "import langchain_openai"],
        cwd=OPENAI_PKG,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"


def test_conftest_syntax():
    """conftest.py has valid Python syntax (pass-to-pass)."""
    result = subprocess.run(
        ["python", "-m", "py_compile", str(CONftest_PY)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Syntax error in conftest.py: {result.stderr}"


def test_repo_lint_package():
    """Repo's ruff linter passes on package code (pass-to-pass)."""
    result = subprocess.run(
        ["uv", "run", "--group", "lint", "ruff", "check", "langchain_openai"],
        cwd=OPENAI_PKG,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stderr[-500:]}"


def test_repo_lint_tests():
    """Repo's ruff linter passes on test code (pass-to-pass)."""
    result = subprocess.run(
        ["uv", "run", "--group", "lint", "ruff", "check", "tests"],
        cwd=OPENAI_PKG,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stderr[-500:]}"


def test_repo_unit_imports():
    """Repo's unit tests for imports and loading pass (pass-to-pass)."""
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = "sk-fake"
    result = subprocess.run(
        [
            "uv", "run", "--group", "test",
            "pytest", "tests/unit_tests/test_imports.py", "tests/unit_tests/test_load.py",
            "-v", "--disable-socket", "--allow-unix-socket",
        ],
        cwd=OPENAI_PKG,
        capture_output=True,
        text=True,
        timeout=180,
        env=env,
    )
    assert result.returncode == 0, f"Tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"


def test_repo_unit_secrets():
    """Repo's unit tests for secrets handling pass (pass-to-pass)."""
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = "sk-fake"
    result = subprocess.run(
        [
            "uv", "run", "--group", "test",
            "pytest", "tests/unit_tests/test_secrets.py",
            "-v", "--disable-socket", "--allow-unix-socket",
        ],
        cwd=OPENAI_PKG,
        capture_output=True,
        text=True,
        timeout=180,
        env=env,
    )
    assert result.returncode == 0, f"Tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"


if __name__ == "__main__":
    # Run with pytest if available
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
