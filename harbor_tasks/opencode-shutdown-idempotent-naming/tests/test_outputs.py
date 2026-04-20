"""
Task: opencode-shutdown-idempotent-naming
Repo: anomalyco/opencode @ 2a0be8316be7ae6ec78f5d221851fc1cc0cdddb2
PR: 15924

Tests verify both the functional shutdown fix and the AGENTS.md naming enforcement update.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/opencode"
THREAD_TS = Path(REPO) / "packages/opencode/src/cli/cmd/tui/thread.ts"
WORKER_TS = Path(REPO) / "packages/opencode/src/cli/cmd/tui/worker.ts"
AGENTS_MD = Path(REPO) / "AGENTS.md"


def _run_in_repo(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a command in the repo directory."""
    return subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _parse_ts_imports(content: str) -> list:
    """Parse TypeScript imports from file content."""
    imports = []
    for line in content.split("\n"):
        if line.strip().startswith("import "):
            imports.append(line.strip())
    return imports


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax / compilation checks
# -----------------------------------------------------------------------------

def test_typescript_compiles():
    """Modified TypeScript files must compile without errors.
    
    Uses bun turbo typecheck which is the actual CI check. The single-file tsc
    approach doesn't work with this project's tsconfig paths and moduleResolution.
    """
    result = _run_in_repo(["bun", "turbo", "typecheck"], timeout=60)
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_worker_typescript_compiles():
    """worker.ts must compile without errors.
    
    Uses bun turbo typecheck which is the actual CI check. The single-file tsc
    approach doesn't work with this project's tsconfig paths and moduleResolution.
    """
    result = _run_in_repo(["bun", "turbo", "typecheck"], timeout=60)
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI/CD checks that must pass on base and after fix
# -----------------------------------------------------------------------------

def test_repo_typecheck():
    """Repo's bun typecheck passes (pass_to_pass).
    
    Runs 'bun turbo typecheck' which is the same as 'bun typecheck' per package.json.
    This is a repo CI gate that must pass both before and after the fix.
    """
    r = _run_in_repo(["bun", "turbo", "typecheck"], timeout=120)
    assert r.returncode == 0, f"Typecheck failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# Note: test_repo_opencode_package_tests removed because it fails on the base commit
# (145 failures even before the fix), making it an invalid pass_to_pass test.
# The repo's own test suite has pre-existing failures at this commit.


def test_repo_cli_tests():
    """Repo's CLI tests pass (pass_to_pass).

    Runs 'bun test test/cli/' - tests CLI-related functionality including
    TUI transcript tests. These tests pass on the base commit.
    """
    r = subprocess.run(
        ["bun", "test", "test/cli/"],
        cwd=f"{REPO}/packages/opencode",
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, f"CLI tests failed:\n{r.stderr[-500:]}"


def test_repo_util_tests():
    """Repo's utility tests pass (pass_to_pass).

    Runs 'bun test test/util/' - tests utility functions including
    timeout, process, and wildcard matching. These tests pass on the base commit.
    """
    r = subprocess.run(
        ["bun", "test", "test/util/"],
        cwd=f"{REPO}/packages/opencode",
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, f"Util tests failed:\n{r.stderr[-500:]}"


def test_repo_prettier():
    """Repo's code formatting passes prettier check (pass_to_pass).

    Runs 'npx prettier --check packages/opencode/src/cli/cmd/tui/' to verify
    that modified files follow the repo's code style.
    """
    r = _run_in_repo(
        ["npx", "prettier", "--check", "packages/opencode/src/cli/cmd/tui/"],
        timeout=60,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests for shutdown fix
# -----------------------------------------------------------------------------

def test_stop_function_is_idempotent():
    """The stop() function must use a 'stopped' flag to ensure idempotency."""
    content = THREAD_TS.read_text()

    # Must have a stopped flag
    assert "stopped" in content, f"Variable stopped should be defined", "Missing 'stopped' flag variable"

    # Must check stopped flag at start of stop function
    assert "if (stopped) return" in content, "stop() function must check 'stopped' flag early"

    # Must set stopped = true
    assert "stopped = true" in content, "stop() function must set 'stopped = true'"


def test_stop_unregisters_process_listeners():
    """stop() must unregister process event listeners to prevent leaks."""
    content = THREAD_TS.read_text()

    # Must have process.off calls for all registered listeners
    assert 'process.off("uncaughtException"' in content, "Missing process.off for uncaughtException"
    assert 'process.off("unhandledRejection"' in content, "Missing process.off for unhandledRejection"
    assert 'process.off("SIGUSR2"' in content, "Missing process.off for SIGUSR2"


def test_stop_calls_worker_terminate():
    """stop() must call worker.terminate() to force worker shutdown."""
    content = THREAD_TS.read_text()

    # Must call worker.terminate() after shutdown attempt
    assert "worker.terminate()" in content, "Missing worker.terminate() call in stop()"


def test_worker_shutdown_simplified():
    """worker.ts shutdown() should not have Promise.race with timeout (moved to caller)."""
    content = WORKER_TS.read_text()

    # The old code had Promise.race with setTimeout - should be removed
    assert "Promise.race" not in content, "worker.ts should not use Promise.race (timeout moved to caller)"

    # Should directly await Instance.disposeAll()
    assert "await Instance.disposeAll()" in content, "worker.ts should directly await Instance.disposeAll()"


def test_helper_functions_extracted():
    """Helper functions target() and input() should be extracted from inline iife."""
    content = THREAD_TS.read_text()

    # Should have standalone target() function
    assert "async function target()" in content, "Missing target() helper function"

    # Should have standalone input() function
    assert "async function input(" in content, "Missing input() helper function"

    # Should NOT have iife calls for these anymore
    assert "iife(async ()" not in content, "Should not use iife pattern for target/input (extract to functions)"


def test_short_variable_names():
    """Code should use short variable names per AGENTS.md naming rules."""
    content = THREAD_TS.read_text()

    # Check that old long names are replaced with short ones
    assert "const root =" in content, "Should use 'root' instead of 'baseCwd'"
    assert "const file =" in content, "Should use 'file' instead of 'workerPath'"
    assert "const network =" in content, "Should use 'network' instead of 'networkOpts'"
    assert "const external =" in content, "Should use 'external' instead of 'shouldStartServer'"

    # Check that old names are NOT present
    assert "baseCwd" not in content, "Should not use 'baseCwd' (use 'root')"
    assert "workerPath" not in content, "Should not use 'workerPath' (use 'file')"
    assert "networkOpts" not in content, "Should not use 'networkOpts' (use 'network')"
    assert "shouldStartServer" not in content, "Should not use 'shouldStartServer' (use 'external')"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff / agent_config) - AGENTS.md update tests
# -----------------------------------------------------------------------------

def test_agents_md_has_naming_enforcement():
    """AGENTS.md must have the new Naming Enforcement section with mandatory rules."""
    content = AGENTS_MD.read_text()

    # Must have the Naming Enforcement section header
    assert "### Naming Enforcement (Read This)" in content, "Missing 'Naming Enforcement (Read This)' section header"

    # Must indicate this rule is mandatory
    assert "THIS RULE IS MANDATORY FOR AGENT WRITTEN CODE" in content, "Missing mandatory rule indicator"

    # Must list specific examples of good short names
    assert "pid" in content, "Should list 'pid' as good short name"
    assert "cfg" in content, "Should list 'cfg' as good short name"
    assert "err" in content, "Should list 'err' as good short name"

    # Must list examples to avoid
    assert "inputPID" in content, "Should list 'inputPID' as example to avoid"
    assert "existingClient" in content, "Should list 'existingClient' as example to avoid"
    assert "connectTimeout" in content, "Should list 'connectTimeout' as example to avoid"
    assert "workerPath" in content, "Should list 'workerPath' as example to avoid"


def test_agents_md_naming_rules_bullet_points():
    """AGENTS.md Naming Enforcement section must have clear bullet point rules."""
    content = AGENTS_MD.read_text()

    # Should have specific bullet points about naming conventions
    assert "Use single word names by default" in content, "Missing 'Use single word names by default' rule"
    assert "Multi-word names are allowed only when" in content, "Missing multi-word exception rule"
    assert "Do not introduce new camelCase compounds" in content, "Missing camelCase compound rule"
    assert "review touched lines and shorten" in content, "Missing review/shorten rule"


# -----------------------------------------------------------------------------
# Pass-to-pass (static) - anti-stub and validation
# -----------------------------------------------------------------------------

def test_import_with_timeout():
    """thread.ts must import withTimeout utility (used for bounded shutdown)."""
    content = THREAD_TS.read_text()

    # Should import withTimeout from @/util/timeout
    assert 'import { withTimeout } from "@/util/timeout"' in content, "Missing withTimeout import"

    # Should use withTimeout in stop() function
    assert 'withTimeout(client.call("shutdown"' in content, "Missing withTimeout around shutdown call"


def test_no_iife_import():
    """thread.ts should no longer import iife utility (replaced with helper functions)."""
    content = THREAD_TS.read_text()

    imports = _parse_ts_imports(content)
    iife_imports = [i for i in imports if "iife" in i]
    assert len(iife_imports) == 0, f"Should not import iife utility: {iife_imports}"


def test_error_handler_reused():
    """Error handler should be extracted as reusable function, not inline arrows."""
    content = THREAD_TS.read_text()

    # Should have a named error handler function
    assert "const error = (e: unknown)" in content, "Missing reusable error handler function"

    # Should use the error handler for both uncaughtException and unhandledRejection
    assert 'process.on("uncaughtException", error)' in content, "Should register error handler for uncaughtException"
    assert 'process.on("unhandledRejection", error)' in content, "Should register error handler for unhandledRejection"
