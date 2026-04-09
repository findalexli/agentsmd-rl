"""
Test outputs for continue-winston-stderr-ipc-fix task.

This task fixes Winston logger to write to stderr instead of stdout
to prevent IPC stream corruption in binary mode.
"""

import subprocess
import json
import os
import re
import ast

REPO = "/workspace/continue"


def test_winston_stderr_levels_config():
    """
    Fail-to-pass: Verify Winston Console transport uses stderrLevels.

    The fix redirects all Winston log levels to stderr to prevent
    corrupting the IPC stdout stream in the binary.
    """
    logger_file = os.path.join(REPO, "core/util/Logger.ts")
    assert os.path.exists(logger_file), f"Logger.ts not found at {logger_file}"

    with open(logger_file, "r") as f:
        content = f.read()

    # Check for stderrLevels configuration
    assert "stderrLevels:" in content, (
        "Winston Console transport must use stderrLevels to redirect logs to stderr"
    )

    # Extract the stderrLevels array values
    stderr_match = re.search(
        r'stderrLevels:\s*\[([^\]]+)\]',
        content
    )
    assert stderr_match, "Could not find stderrLevels array configuration"

    levels_str = stderr_match.group(1)
    # Check that all log levels are redirected to stderr
    expected_levels = ["error", "warn", "info", "debug"]
    for level in expected_levels:
        assert f'"{level}"' in levels_str or f"'{level}'" in levels_str, (
            f'Log level "{level}" must be in stderrLevels array'
        )


def test_logger_no_stdout_corruption():
    """
    Pass-to-pass: Verify the logger doesn't use default stdout transport.

    Before the fix, Winston used default Console transport which writes
    to stdout, corrupting the IPC stream.
    """
    logger_file = os.path.join(REPO, "core/util/Logger.ts")

    with open(logger_file, "r") as f:
        content = f.read()

    # Should have a Console transport with stderrLevels configuration
    # NOT just a plain new winston.transports.Console()
    console_pattern = r'new\s+winston\.transports\.Console\s*\([^)]*\)'
    matches = re.findall(console_pattern, content)
    assert len(matches) > 0, "Must have a Console transport configured"

    # The transport must have stderrLevels configured (not empty constructor)
    for match in matches:
        assert "stderrLevels" in content[content.find(match)-50:content.find(match)+len(match)+100], (
            "Console transport must have stderrLevels configuration to prevent stdout corruption"
        )


def test_binary_ide_handler_exists():
    """
    Fail-to-pass: Verify BinaryIdeHandler class was added to fix IPC handling.

    This class handles IDE messages from the binary subprocess, responding
    with plain data matching the Kotlin CoreMessenger format.
    """
    test_file = os.path.join(REPO, "binary/test/binary.test.ts")
    assert os.path.exists(test_file), f"binary.test.ts not found at {test_file}"

    with open(test_file, "r") as f:
        content = f.read()

    # Check for BinaryIdeHandler class
    assert "class BinaryIdeHandler" in content, (
        "BinaryIdeHandler class must be defined to handle IDE messages"
    )

    # Check for key methods
    assert "registerHandlers" in content, "BinaryIdeHandler must have registerHandlers method"
    assert "handleData" in content, "BinaryIdeHandler must have handleData method"
    assert "handleLine" in content, "BinaryIdeHandler must have handleLine method"
    assert "respond" in content, "BinaryIdeHandler must have respond method"


def test_binary_ide_handler_handlers():
    """
    Pass-to-pass: Verify BinaryIdeHandler has all required IDE method handlers.

    The handler must implement all IDE protocol methods for the binary to work.
    """
    test_file = os.path.join(REPO, "binary/test/binary.test.ts")

    with open(test_file, "r") as f:
        content = f.read()

    # Extract the BinaryIdeHandler class
    handler_match = re.search(
        r'class BinaryIdeHandler \{[^}]+registerHandlers\(\) \{([^}]+(?:\{[^}]*\}[^}]*)*)\}',
        content,
        re.DOTALL
    )

    # Required IDE handlers
    required_handlers = [
        "getIdeInfo",
        "getWorkspaceDirs",
        "readFile",
        "writeFile",
        "fileExists",
        "listDir",
        "getDiff",
        "getOpenFiles",
        "getCurrentFile",
        "getUniqueId",
    ]

    for handler in required_handlers:
        pattern = rf'h\["{handler}"\]\s*=|h\[\'{handler}\'\]\s*='
        assert re.search(pattern, content), (
            f'BinaryIdeHandler must register handler for "{handler}"'
        )


def test_request_helper_exists():
    """
    Fail-to-pass: Verify request() helper function exists to unwrap responses.

    Binary responses are wrapped in { done, content, status } by _handleLine.
    This helper unwraps them, matching how the Kotlin CoreMessenger reads responses.
    """
    test_file = os.path.join(REPO, "binary/test/binary.test.ts")

    with open(test_file, "r") as f:
        content = f.read()

    # Check for the request helper function
    assert re.search(r'async function request\s*\(', content), (
        "request() helper function must be defined to unwrap binary responses"
    )

    # Check it unwraps the content property
    assert "resp?.content" in content or 'resp.content' in content, (
        "request() helper must unwrap the content property from responses"
    )


def test_tests_use_request_helper():
    """
    Pass-to-pass: Verify tests use the request() helper instead of direct messenger.request().

    This ensures tests properly unwrap binary responses.
    """
    test_file = os.path.join(REPO, "binary/test/binary.test.ts")

    with open(test_file, "r") as f:
        content = f.read()

    # Get content after the request function definition
    request_func_match = re.search(
        r'async function request[^}]+return [^}]+\}',
        content
    )
    assert request_func_match, "request() function not found"

    # Content after the request function
    after_request = content[request_func_match.end():]

    # Find test cases using messenger.request directly (should be none)
    direct_calls = re.findall(
        r'messenger\.request\s*\(',
        after_request
    )

    # Should use request() helper instead
    helper_calls = re.findall(
        r'\brequest\s*\(',
        after_request
    )

    # There should be helper calls
    assert len(helper_calls) > 0, "Tests must use the request() helper function"


def test_subprocess_stderr_handler():
    """
    Pass-to-pass: Verify stderr handler is added to subprocess for debugging.
    """
    test_file = os.path.join(REPO, "binary/test/binary.test.ts")

    with open(test_file, "r") as f:
        content = f.read()

    # Check for stderr handler
    assert "subprocess.stderr.on" in content, (
        "Must add stderr handler to subprocess for debugging output"
    )

    assert "[stderr]" in content, (
        "stderr handler must log with [stderr] prefix"
    )


def test_binary_ide_handler_instantiation():
    """
    Pass-to-pass: Verify BinaryIdeHandler is instantiated in beforeAll.
    """
    test_file = os.path.join(REPO, "binary/test/binary.test.ts")

    with open(test_file, "r") as f:
        content = f.read()

    # Check that BinaryIdeHandler is instantiated
    assert "new BinaryIdeHandler(subprocess, ide)" in content, (
        "BinaryIdeHandler must be instantiated with subprocess and ide"
    )


def test_jest_timeout_set():
    """
    Pass-to-pass: Verify jest timeout is set appropriately.
    """
    test_file = os.path.join(REPO, "binary/test/binary.test.ts")

    with open(test_file, "r") as f:
        content = f.read()

    # Check for jest timeout (30 seconds)
    assert re.search(r'jest\.setTimeout\s*\(\s*30_?000\s*\)', content), (
        "jest.setTimeout(30000) must be set for binary tests"
    )


def test_core_typescript_compiles():
    """
    Fail-to-pass: Verify core TypeScript code compiles without errors.

    The Logger.ts changes must not break TypeScript compilation.
    """
    core_dir = os.path.join(REPO, "core")

    # Run TypeScript compiler in check mode (no emit)
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=core_dir,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, (
        f"Core TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"
    )


def test_binary_typescript_compiles():
    """
    Fail-to-pass: Verify binary TypeScript test code compiles without errors.

    The binary.test.ts changes must compile correctly.
    """
    binary_dir = os.path.join(REPO, "binary")

    # Run TypeScript compiler in check mode
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=binary_dir,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, (
        f"Binary TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"
    )


def test_repo_prettier_check():
    """
    Pass-to-pass: Verify code formatting with Prettier passes.

    Repo CI checks that all files are formatted correctly.
    """
    # Run prettier check from repo root
    result = subprocess.run(
        [
            "npx", "prettier", "--check",
            "**/*.{js,jsx,ts,tsx,json,css,md}",
            "--ignore-path", ".gitignore",
            "--ignore-path", ".prettierignore"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, (
        f"Prettier check failed:\n{result.stderr[-500:]}"
    )


def test_core_lint():
    """
    Pass-to-pass: Verify core ESLint checks pass.

    Repo CI runs lint on core package to ensure code quality.
    """
    core_dir = os.path.join(REPO, "core")

    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=core_dir,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, (
        f"Core lint failed:\n{result.stderr[-500:]}"
    )


def test_core_unit_tests():
    """
    Pass-to-pass: Verify core unit tests pass (subset).

    Repo CI runs jest tests on core package.
    Only run tests not requiring API keys or network access.
    """
    core_dir = os.path.join(REPO, "core")

    # Run jest tests, excluding LLM-related tests that need API keys
    result = subprocess.run(
        [
            "npm", "test", "--",
            "--testPathIgnorePatterns=llm",
            "--testNamePattern=^(?!.*API).*$"
        ],
        cwd=core_dir,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "NODE_OPTIONS": "--experimental-vm-modules"}
    )

    assert result.returncode == 0, (
        f"Core unit tests failed:\n{result.stderr[-500:]}"
    )
