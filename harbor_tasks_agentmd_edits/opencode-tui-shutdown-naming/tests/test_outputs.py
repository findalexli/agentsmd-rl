"""
Task: opencode-tui-shutdown-naming
Repo: opencode @ 2a0be8316be7ae6ec78f5d221851fc1cc0cdddb2
PR:   anomalyco/opencode#15924

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = Path("/workspace/opencode")


def _run_bun(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a TypeScript snippet with bun."""
    script_path = REPO / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["bun", "run", str(script_path)],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(REPO),
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) — actual CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """TypeScript files parse correctly using Bun transpiler (lightweight typecheck)."""
    script = '''
const transpiler = new Bun.Transpiler({ loader: "ts" });
const files = [
  "packages/opencode/src/cli/cmd/tui/thread.ts",
  "packages/opencode/src/cli/cmd/tui/worker.ts"
];
for (const f of files) {
  const content = await Bun.file(f).text();
  try {
    await transpiler.transform(content);
    console.log("OK: " + f);
  } catch(e) {
    console.error("FAIL: " + f + " - " + e.message);
    process.exit(1);
  }
}
console.log("All files passed syntax check");
'''
    r = subprocess.run(
        ["bun", "-e", script],
        capture_output=True, text=True, timeout=60, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}\n{r.stdout}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """Modified TypeScript files are syntactically well-formed."""
    thread = REPO / "packages/opencode/src/cli/cmd/tui/thread.ts"
    worker = REPO / "packages/opencode/src/cli/cmd/tui/worker.ts"
    for path in [thread, worker]:
        content = path.read_text()
        opens = content.count("{")
        closes = content.count("}")
        assert abs(opens - closes) <= 1, f"Unbalanced braces in {path.name}: {opens} open vs {closes} close"
        parens_open = content.count("(")
        parens_close = content.count(")")
        assert abs(parens_open - parens_close) <= 1, f"Unbalanced parens in {path.name}"


# [static] pass_to_pass
def test_with_timeout_behavior():
    """withTimeout utility resolves within timeout and rejects on timeout."""
    result = _run_bun("""
import { withTimeout } from './packages/opencode/src/util/timeout.ts'

// Test 1: resolves normally
const val = await withTimeout(Promise.resolve("ok"), 5000)
console.log(JSON.stringify({ step: "resolved", value: val }))
""")
    assert result.returncode == 0, f"withTimeout failed: {result.stderr}"
    data = json.loads(result.stdout.strip().split("\n")[-1])
    assert data["step"] == "resolved"
    assert data["value"] == "ok"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_thread_imports_with_timeout():
    """thread.ts must import withTimeout from @/util/timeout for bounded shutdown."""
    thread = REPO / "packages/opencode/src/cli/cmd/tui/thread.ts"
    content = thread.read_text()
    assert "import { withTimeout }" in content, \
        "thread.ts must import withTimeout"
    assert "@/util/timeout" in content, \
        "withTimeout must be imported from @/util/timeout"


# [pr_diff] fail_to_pass
def test_thread_idempotent_stop():
    """thread.ts must have an idempotent stop() function with stopped guard."""
    thread = REPO / "packages/opencode/src/cli/cmd/tui/thread.ts"
    content = thread.read_text()
    assert "let stopped = false" in content, \
        "Must declare stopped flag for idempotent shutdown"
    assert "if (stopped) return" in content, \
        "stop() must guard against double invocation"
    assert "stopped = true" in content, \
        "stop() must set stopped flag"
    assert "worker.terminate()" in content, \
        "stop() must always terminate the worker"


# [pr_diff] fail_to_pass
def test_thread_helpers_extracted():
    """thread.ts must extract target() and input() as standalone helper functions."""
    thread = REPO / "packages/opencode/src/cli/cmd/tui/thread.ts"
    content = thread.read_text()
    # target() helper — resolves the worker path
    assert "async function target(" in content, \
        "Must have async function target() to resolve worker path"
    assert "OPENCODE_WORKER_PATH" in content, \
        "target() must check OPENCODE_WORKER_PATH env var"
    # input() helper — handles piped stdin and prompt arg
    assert "async function input(" in content, \
        "Must have async function input() to handle stdin/prompt"
    assert "Bun.stdin" in content, \
        "input() must read from Bun.stdin"


# [pr_diff] fail_to_pass
def test_worker_shutdown_simplified():
    """worker.ts shutdown must call Instance.disposeAll directly without Promise.race."""
    worker = REPO / "packages/opencode/src/cli/cmd/tui/worker.ts"
    content = worker.read_text()
    shutdown_idx = content.find("async shutdown()")
    assert shutdown_idx != -1, "Must have async shutdown() function"
    shutdown_body = content[shutdown_idx:shutdown_idx + 500]
    assert "Promise.race" not in shutdown_body, \
        "shutdown should not wrap disposeAll in Promise.race"
    assert "Instance.disposeAll()" in shutdown_body, \
        "shutdown must call Instance.disposeAll()"


# ---------------------------------------------------------------------------
# Config-derived (agent_config / pr_diff) — AGENTS.md naming convention
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:21 @ base_commit
def test_short_variable_names():
    """thread.ts must use short single-word names per AGENTS.md naming convention."""
    thread = REPO / "packages/opencode/src/cli/cmd/tui/thread.ts"
    content = thread.read_text()
    # These multi-word identifiers from the old code must be removed
    assert "workerPath" not in content, \
        "Use 'file' instead of 'workerPath' per naming convention"
    assert "baseCwd" not in content, \
        "Use 'root' instead of 'baseCwd' per naming convention"
    assert "shouldStartServer" not in content, \
        "Use 'external' instead of 'shouldStartServer' per naming convention"
    assert "networkOpts" not in content, \
        "Use 'network' instead of 'networkOpts' per naming convention"


# [pr_diff] fail_to_pass
def test_agents_md_naming_enforcement():
    """AGENTS.md must contain the Naming Enforcement section with mandatory rule."""
    agents = REPO / "AGENTS.md"
    content = agents.read_text()
    assert "Naming Enforcement" in content, \
        "AGENTS.md must have Naming Enforcement section"
    assert "THIS RULE IS MANDATORY" in content, \
        "Naming enforcement must be declared as mandatory"
    # Must specify single-word preference
    assert "single word names" in content, \
        "Must specify single-word naming preference"
    # Must list preferred short names as examples
    for name in ["pid", "cfg", "err", "opts", "dir", "root"]:
        assert name in content, \
            f"Must list '{name}' as a preferred short name"
    # Must list examples to avoid
    assert "workerPath" in content, \
        "Must list 'workerPath' as an example to avoid"
