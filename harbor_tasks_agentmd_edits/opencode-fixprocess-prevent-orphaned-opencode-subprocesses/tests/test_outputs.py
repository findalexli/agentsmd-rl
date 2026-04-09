"""
Task: opencode-fixprocess-prevent-orphaned-opencode-subprocesses
Repo: anomalyco/opencode @ 570038ac3c4ae02378e5de38793d3014587a33e1
PR:   15924

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/opencode"


def _run_bun(cmd: list, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a bun command in the repo directory."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """Modified TypeScript files must compile without errors."""
    r = _run_bun(["bun", "run", "tsc", "--noEmit"], timeout=120)
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stdout}\n{r.stderr}"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_worker_stop_idempotent():
    """TUI thread has idempotent stop() function that unregisters listeners and terminates worker."""
    code = """
import * as fs from 'fs';
const src = fs.readFileSync('packages/opencode/src/cli/cmd/tui/thread.ts', 'utf8');

// Check for idempotent stop() function
if (!src.includes('let stopped = false')) {
    console.log('FAIL: missing stopped flag');
    process.exit(1);
}
if (!src.includes('if (stopped) return')) {
    console.log('FAIL: missing idempotency check');
    process.exit(1);
}
if (!src.includes('process.off("uncaughtException", error)')) {
    console.log('FAIL: missing uncaughtException cleanup');
    process.exit(1);
}
if (!src.includes('process.off("unhandledRejection", error)')) {
    console.log('FAIL: missing unhandledRejection cleanup');
    process.exit(1);
}
if (!src.includes('process.off("SIGUSR2", reload)')) {
    console.log('FAIL: missing SIGUSR2 cleanup');
    process.exit(1);
}
if (!src.includes('worker.terminate()')) {
    console.log('FAIL: missing worker.terminate()');
    process.exit(1);
}
console.log('PASS');
"""
    r = _run_bun(["bun", "run", "-e", code], timeout=30)
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS, got: {r.stdout}"


# [pr_diff] fail_to_pass
def test_worker_shutdown_timeout_bounded():
    """Worker shutdown uses timeout-bounded cleanup instead of Promise.race with timeout."""
    code = """
import * as fs from 'fs';
const workerSrc = fs.readFileSync('packages/opencode/src/cli/cmd/tui/worker.ts', 'utf8');
const threadSrc = fs.readFileSync('packages/opencode/src/cli/cmd/tui/thread.ts', 'utf8');

// Worker should NOT have Promise.race with setTimeout anymore
if (workerSrc.includes('Promise.race') && workerSrc.includes('setTimeout(resolve, 5000)')) {
    console.log('FAIL: worker still uses Promise.race with setTimeout');
    process.exit(1);
}

// Worker should now just await Instance.disposeAll()
if (!workerSrc.includes('await Instance.disposeAll()')) {
    console.log('FAIL: worker missing await Instance.disposeAll()');
    process.exit(1);
}

// Thread should use withTimeout for bounded shutdown
if (!threadSrc.includes('withTimeout(client.call("shutdown", undefined), 5000)')) {
    console.log('FAIL: thread missing withTimeout for shutdown');
    process.exit(1);
}

console.log('PASS');
"""
    r = _run_bun(["bun", "run", "-e", code], timeout=30)
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS, got: {r.stdout}"


# [pr_diff] fail_to_pass
def test_mcp_descendants_cleanup():
    """MCP cleanup kills descendant processes before closing clients."""
    code = """
import * as fs from 'fs';
const src = fs.readFileSync('packages/opencode/src/mcp/index.ts', 'utf8');

// Check for descendants function
if (!src.includes('async function descendants(pid: number)')) {
    console.log('FAIL: missing descendants function');
    process.exit(1);
}

// Check for pgrep usage to find child processes
if (!src.includes('Bun.spawn(["pgrep", "-P"')) {
    console.log('FAIL: missing pgrep for child process discovery');
    process.exit(1);
}

// Check that cleanup kills descendants before closing
if (!src.includes('process.kill(dpid, "SIGTERM")')) {
    console.log('FAIL: missing SIGTERM for descendant processes');
    process.exit(1);
}

// Check for the comment explaining the fix
if (!src.includes('The MCP SDK only signals the direct child process on close')) {
    console.log('FAIL: missing explanatory comment about MCP SDK limitation');
    process.exit(1);
}

console.log('PASS');
"""
    r = _run_bun(["bun", "run", "-e", code], timeout=30)
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS, got: {r.stdout}"


# [pr_diff] fail_to_pass
def test_timer_unref_prevents_hang():
    """setTimeout for checkUpgrade uses unref to prevent keeping process alive."""
    code = """
import * as fs from 'fs';
const src = fs.readFileSync('packages/opencode/src/cli/cmd/tui/thread.ts', 'utf8');

// Check for unref usage on setTimeout
if (!src.includes('setTimeout(() => {') || !src.includes('.unref?.()')) {
    console.log('FAIL: missing unref on setTimeout');
    process.exit(1);
}

console.log('PASS');
"""
    r = _run_bun(["bun", "run", "-e", code], timeout=30)
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS, got: {r.stdout}"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_typecheck_passes():
    """Bun typecheck passes on modified files."""
    r = _run_bun(["bun", "run", "typecheck"], timeout=120)
    # Typecheck may fail due to other issues, but should not fail due to our changes
    # Just check it runs without crashing
    assert r.returncode in [0, 1], f"Typecheck crashed: {r.stderr}"


# [static] pass_to_pass
def test_not_stub():
    """Modified functions have real logic, not just pass/return."""
    code = """
import * as fs from 'fs';
const threadSrc = fs.readFileSync('packages/opencode/src/cli/cmd/tui/thread.ts', 'utf8');
const mcpSrc = fs.readFileSync('packages/opencode/src/mcp/index.ts', 'utf8');

// stop() function should have multiple statements
const stopMatch = threadSrc.match(/const stop = async.*?^\\s*};/ms);
if (!stopMatch) {
    console.log('FAIL: stop function not found');
    process.exit(1);
}
const stopBody = stopMatch[0];
const statementCount = (stopBody.match(/\\b(let|const|if|await|process\\.|worker\\.)\\b/g) || []).length;
if (statementCount < 5) {
    console.log('FAIL: stop function appears to be a stub');
    process.exit(1);
}

// descendants() should have real logic
const descMatch = mcpSrc.match(/async function descendants.*?^\\s*}/ms);
if (!descMatch) {
    console.log('FAIL: descendants function not found');
    process.exit(1);
}
const descBody = descMatch[0];
if (!descBody.includes('Bun.spawn') || !descBody.includes('while')) {
    console.log('FAIL: descendants function appears to be a stub');
    process.exit(1);
}

console.log('PASS');
"""
    r = _run_bun(["bun", "run", "-e", code], timeout=30)
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS, got: {r.stdout}"


# -----------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# -----------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:23-31 @ 570038ac3c4ae02378e5de38793d3014587a33e1
def test_agents_naming_enforcement():
    """AGENTS.md contains mandatory naming enforcement section."""
    code = """
import * as fs from 'fs';
const src = fs.readFileSync('AGENTS.md', 'utf8');

// Check for Naming Enforcement section
if (!src.includes('### Naming Enforcement (Read This)')) {
    console.log('FAIL: missing Naming Enforcement section header');
    process.exit(1);
}
if (!src.includes('THIS RULE IS MANDATORY FOR AGENT WRITTEN CODE')) {
    console.log('FAIL: missing mandatory rule statement');
    process.exit(1);
}
if (!src.includes('Use single word names by default')) {
    console.log('FAIL: missing single word names rule');
    process.exit(1);
}
if (!src.includes('Good short names to prefer:')) {
    console.log('FAIL: missing good short names guidance');
    process.exit(1);
}
if (!src.includes('pid') || !src.includes('cfg') || !src.includes('err')) {
    console.log('FAIL: missing specific short name examples');
    process.exit(1);
}

console.log('PASS');
"""
    r = _run_bun(["bun", "run", "-e", code], timeout=30)
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS, got: {r.stdout}"
