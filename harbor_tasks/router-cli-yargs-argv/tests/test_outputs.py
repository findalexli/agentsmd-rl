"""Tests for TanStack Router CLI yargs fix.

This tests that the router-cli properly passes process.argv to yargs,
fixing the silent CLI failure where commands were not being recognized.
"""

import subprocess
import sys
import os

REPO = "/workspace/router"
CLI_INDEX = f"{REPO}/packages/router-cli/src/index.ts"
CLI_DIST = f"{REPO}/packages/router-cli/dist/esm/index.js"
CLI_PKG = f"{REPO}/packages/router-cli"


def run_tsr(args: list, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run the tsr CLI with given arguments using node directly."""
    # Run via node directly on the dist file
    cmd = ["node", CLI_DIST] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def test_cli_help_shows_usage():
    """CLI --help should show usage information (fail-to-pass).

    Without the fix, yargs() is called without arguments, so --help is not
    parsed and the CLI silently exits with empty output.
    """
    result = run_tsr(["--help"])

    # Should exit 0 and show help text
    assert result.returncode == 0, f"--help failed with exit code {result.returncode}\nstderr: {result.stderr}"
    assert "tsr" in result.stdout, f"Expected 'tsr' in help output, got: {result.stdout[:500]}"
    assert "generate" in result.stdout, f"Expected 'generate' command in help, got: {result.stdout[:500]}"
    assert "watch" in result.stdout, f"Expected 'watch' command in help, got: {result.stdout[:500]}"


def test_cli_recognizes_generate_command():
    """CLI should recognize 'generate' command and show error without config (fail-to-pass).

    Without the fix, the 'generate' command is never registered because
    yargs doesn't receive process.argv. With the fix, it tries to run but
    fails due to missing config - which is the expected behavior.
    """
    result = run_tsr(["generate"])

    # With the fix, the generate command should be recognized.
    # It will likely fail or exit non-zero due to missing config,
    # but it should NOT silently exit with code 0 and empty output.

    # Without the fix: exit code 0 with empty output (commands not parsed)
    # With the fix: non-zero exit OR output about processing routes

    silently_exits = result.returncode == 0 and len(result.stdout) < 10 and len(result.stderr) < 10

    assert not silently_exits, \
        f"Command 'generate' silently did nothing. " \
        f"Got exit={result.returncode}, stdout='{result.stdout}', stderr='{result.stderr}'"

    # Also verify it's actually processing the command (not just failing for other reasons)
    has_meaningful_output = (
        "generate" in result.stdout.lower() or
        "generate" in result.stderr.lower() or
        "route" in result.stdout.lower() or
        "route" in result.stderr.lower() or
        "config" in result.stdout.lower() or
        "config" in result.stderr.lower()
    )

    assert has_meaningful_output or result.returncode != 0, \
        f"Expected generate command to be processed. " \
        f"Got exit={result.returncode}, stdout={result.stdout[:500]}, stderr={result.stderr[:500]}"


def test_cli_recognizes_watch_command():
    """CLI should recognize 'watch' command (fail-to-pass).

    Similar to generate - watch command should be parsed and processed.
    Note: watch command starts a continuous process, so we just check it doesn't
    silently exit immediately (which indicates the bug).
    """
    import subprocess

    # Start the watch command - it should either process the command or hang (waiting for changes)
    # With the bug: silently exits with code 0 immediately
    # Without the bug: either errors about config OR starts watching (doesn't return immediately)
    proc = subprocess.Popen(
        ["node", CLI_DIST, "watch"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        # Wait for a short time to see if the process exits immediately (bug behavior)
        # or continues running (correct behavior - it's watching for changes)
        proc.wait(timeout=2)
        # If we get here, the process exited
        stdout, stderr = proc.stdout.read(), proc.stderr.read()
        silently_exits = proc.returncode == 0 and len(stdout) < 10 and len(stderr) < 10

        assert not silently_exits, \
            f"Command 'watch' silently did nothing. " \
            f"Got exit={proc.returncode}, stdout='{stdout}', stderr='{stderr}'"

        # Process exited but with some output or error - that's fine (might be missing config)
        has_meaningful_output = (
            "watch" in stdout.lower() or "watch" in stderr.lower() or
            "route" in stdout.lower() or "route" in stderr.lower() or
            "config" in stdout.lower() or "config" in stderr.lower()
        )
        assert has_meaningful_output or proc.returncode != 0, \
            f"Expected watch command to be processed. " \
            f"Got exit={proc.returncode}, stdout={stdout[:500]}, stderr={stderr[:500]}"
    except subprocess.TimeoutExpired:
        # Process is still running - this is expected for watch command
        # It means the command was recognized and is watching for changes
        proc.kill()
        proc.wait()
        # Timeout = success, the command was recognized and is watching


def test_router_cli_builds():
    """Router CLI package should build successfully (pass-to-pass).

    This verifies the TypeScript compiles without errors.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-cli:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"Build failed:\nstdout: {result.stdout[-1000:]}\nstderr: {result.stderr[-1000:]}"


def test_router_cli_lint():
    """Router CLI package passes ESLint checks (pass_to_pass).

    Verifies the modified code follows the project's linting rules.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-cli:test:eslint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stderr[-500:]}"


def test_router_cli_types():
    """Router CLI package passes TypeScript type checks (pass_to_pass).

    Verifies the modified code has no type errors across multiple TS versions.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-cli:test:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Type check failed:\n{result.stderr[-500:]}"


def test_router_cli_build_check():
    """Router CLI package passes build artifact checks (pass_to_pass).

    Verifies the package builds correctly and passes publint/attw checks.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-cli:test:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Build check failed:\n{result.stderr[-500:]}"


def test_yargs_import_exists():
    """Import statement for hideBin should exist (structural, gated).

    This is gated by behavioral tests - only checked if they pass.
    """
    with open(CLI_INDEX, 'r') as f:
        content = f.read()

    assert "hideBin" in content, "Expected 'hideBin' import in index.ts"
    assert "from 'yargs/helpers'" in content, "Expected import from 'yargs/helpers'"


def test_yargs_receives_argv():
    """yargs should be called with hideBin(process.argv) (structural, gated).

    Verifies the fix is applied correctly.
    """
    with open(CLI_INDEX, 'r') as f:
        content = f.read()

    # The fix: yargs(hideBin(process.argv))
    assert "yargs(hideBin(process.argv))" in content, \
        "Expected yargs to be called with hideBin(process.argv)"
