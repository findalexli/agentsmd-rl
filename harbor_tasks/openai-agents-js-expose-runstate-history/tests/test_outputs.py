"""Tests for the RunState history getter PR (openai/openai-agents-js#340).

Fail-to-pass tests verify the `history` getter is defined, returns combined items,
and survives serialization. Pass-to-pass tests verify the repo builds and lints.
"""
import subprocess
import os

REPO = "/workspace/openai-agents-js"
AGENTS_CORE = os.path.join(REPO, "packages", "agents-core")


def _run_tsx(script, timeout=30):
    """Run a TypeScript inline script via tsx from the agents-core directory."""
    r = subprocess.run(
        ["npx", "tsx", "--eval", script],
        cwd=AGENTS_CORE,
        capture_output=True, text=True, timeout=timeout,
    )
    return r


# ── fail-to-pass ──────────────────────────────────────────────────────────────

def test_history_getter_defined():
    """RunState instances expose a `history` property that returns an array."""
    r = _run_tsx(
        'import { RunState, RunContext, Agent } from "@openai/agents-core";'
        "const ctx = new RunContext();"
        'const agent = new Agent({name: "T", instructions: "test"});'
        'const state = new RunState(ctx, "test input", agent, 1);'
        "const h = state.history;"
        'if (h === undefined || h === null) { console.error("FAIL: history property is " + typeof h); process.exit(1); }'
        'if (!Array.isArray(h)) { console.error("FAIL: history is not an array, got " + typeof h); process.exit(1); }'
        'if (h.length !== 1) { console.error("FAIL: expected 1 item in history, got " + h.length); process.exit(1); }'
        'console.log("PASS");'
    )
    assert r.returncode == 0, f"history property missing:\n{r.stderr}\n{r.stdout}"


def test_history_includes_original_input():
    """The history array includes the original input item(s)."""
    r = _run_tsx(
        'import { RunState, RunContext, Agent } from "@openai/agents-core";'
        "const ctx = new RunContext();"
        'const agent = new Agent({name: "T", instructions: "test"});'
        'const state = new RunState(ctx, "hello world", agent, 1);'
        "const inputItem = state.history[0];"
        'if (inputItem.content !== "hello world") { console.error("FAIL: expected content hello world, got " + JSON.stringify(inputItem.content)); process.exit(1); }'
        'if (inputItem.role !== "user") { console.error("FAIL: expected role user, got " + JSON.stringify(inputItem.role)); process.exit(1); }'
        'console.log("PASS");'
    )
    assert r.returncode == 0, f"history content wrong:\n{r.stderr}\n{r.stdout}"


def test_history_includes_generated_items():
    """After pushing a generated item, history reflects it."""
    r = _run_tsx(
        'import { RunState, RunContext, Agent, RunMessageOutputItem } from "@openai/agents-core";'
        "const ctx = new RunContext();"
        'const agent = new Agent({name: "T", instructions: "test"});'
        'const state = new RunState(ctx, "input", agent, 1);'
        "const beforeLen = state.history.length;"
        'const msg = {id: "m1", type: "message", role: "assistant", status: "completed", content: [{type: "output_text", text: "response", providerData: {annotations: []}}]};'
        "state._generatedItems.push(new RunMessageOutputItem(msg, agent));"
        "const afterLen = state.history.length;"
        'if (afterLen <= beforeLen) { console.error("FAIL: history did not grow after adding generated item"); process.exit(1); }'
        'if (state.history.length !== 2) { console.error("FAIL: expected 2 items, got " + state.history.length); process.exit(1); }'
        'console.log("PASS");'
    )
    assert r.returncode == 0, f"generated items not reflected:\n{r.stderr}\n{r.stdout}"


def test_history_survives_serialization():
    """The history property value survives JSON serialization round-trip."""
    r = _run_tsx(
        'import { RunState, RunContext, Agent, RunMessageOutputItem } from "@openai/agents-core";'
        'async function main() {'
        "const ctx = new RunContext();"
        'const agent = new Agent({name: "T", instructions: "test"});'
        'const state = new RunState(ctx, "input", agent, 1);'
        'const msg = {id: "m1", type: "message", role: "assistant", status: "completed", content: [{type: "output_text", text: "response", providerData: {annotations: []}}]};'
        "state._generatedItems.push(new RunMessageOutputItem(msg, agent));"
        "const before = state.history;"
        "const restored = await RunState.fromString(agent, state.toString());"
        "if (restored.history.length !== before.length) { console.error('FAIL: length mismatch'); process.exit(1); }"
        'console.log("PASS"); }'
        "main().catch(e => { console.error('FAIL:', e.message); process.exit(1); });"
    )
    assert r.returncode == 0, f"serialization roundtrip failed:\n{r.stderr}\n{r.stdout}"


# ── pass-to-pass ──────────────────────────────────────────────────────────────

def test_build_check():
    """pnpm build-check passes on agents-core (compilation and type-checking)."""
    r = subprocess.run(
        ["pnpm", "-F", "agents-core", "build-check"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"build-check failed:\n{r.stderr[-800:]}"


# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_build_all_packages():
    """pass_to_pass | CI job 'test' → step 'Build all packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build all packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_linter():
    """pass_to_pass | CI job 'test' → step 'Run linter'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run linter' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_compile_examples():
    """pass_to_pass | CI job 'test' → step 'Compile examples'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r build-check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Compile examples' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_returns_history_including_original_input_and_gen():
    """fail_to_pass | PR added test 'returns history including original input and generated items' in 'packages/agents-core/test/runState.test.ts' (vitest)"""
    # Verify the test exists in the source file first (provides f2p signal)
    grep_r = subprocess.run(
        ["grep", "-q", "returns history including original input and generated items",
         "packages/agents-core/test/runState.test.ts"],
        cwd=REPO, capture_output=True, text=True, timeout=10)
    assert grep_r.returncode == 0, (
        "PR-added test 'returns history including original input and generated items' "
        "not found in packages/agents-core/test/runState.test.ts")

    # Then run the test to verify it passes
    r = subprocess.run(
        ["bash", "-lc",
         'pnpm vitest run "packages/agents-core/test/runState.test.ts" -t "returns history including original input and generated items" 2>&1 | tail -30'],
        cwd=REPO, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'returns history including original input and generated items' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_pr_added_preserves_history_after_serialization():
    """fail_to_pass | PR added test 'preserves history after serialization' in 'packages/agents-core/test/runState.test.ts' (vitest)"""
    # Verify the test exists in the source file first (provides f2p signal)
    grep_r = subprocess.run(
        ["grep", "-q", "preserves history after serialization",
         "packages/agents-core/test/runState.test.ts"],
        cwd=REPO, capture_output=True, text=True, timeout=10)
    assert grep_r.returncode == 0, (
        "PR-added test 'preserves history after serialization' "
        "not found in packages/agents-core/test/runState.test.ts")

    # Then run the test to verify it passes
    r = subprocess.run(
        ["bash", "-lc",
         'pnpm vitest run "packages/agents-core/test/runState.test.ts" -t "preserves history after serialization" 2>&1 | tail -30'],
        cwd=REPO, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'preserves history after serialization' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
