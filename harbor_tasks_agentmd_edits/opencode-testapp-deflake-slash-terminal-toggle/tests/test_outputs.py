"""
Task: opencode-testapp-deflake-slash-terminal-toggle
Repo: anomalyco/opencode @ cb69501098c603ccd7d3e3dbe6655d401c1d815c
PR:   17881

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"


def _run_bun(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a temp .ts file and execute it with bun."""
    script_path = Path(REPO) / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["bun", "run", str(script_path)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass) — existing terminal probe APIs still work
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_terminal_settle_api():
    """Existing terminal probe connect/render/settle APIs still work."""
    result = _run_bun("""
Object.assign(globalThis, { window: globalThis });
(globalThis as any).__opencode_e2e = {
  terminal: { enabled: true, terminals: {} }
};

const { terminalProbe } = await import("./packages/app/src/testing/terminal.ts");
const probe = terminalProbe("t1");

probe.connect();
const s1 = (globalThis as any).__opencode_e2e.terminal.terminals["t1"];

probe.render("hello world");
const s2 = (globalThis as any).__opencode_e2e.terminal.terminals["t1"];

probe.settle();
const s3 = (globalThis as any).__opencode_e2e.terminal.terminals["t1"];

console.log(JSON.stringify({
  connects: s1.connects,
  rendered: s2.rendered,
  settled: s3.settled,
}));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["connects"] == 1, f"connect() should increment connects, got {data['connects']}"
    assert data["rendered"] == "hello world", f"render() should set rendered, got {data['rendered']}"
    assert data["settled"] == 1, f"settle() should increment settled, got {data['settled']}"


# [repo_tests] pass_to_pass
def test_repo_terminal_ts_transpiles():
    """Terminal probe module transpiles without errors (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "build", "--transpile-only", f"{REPO}/packages/app/src/testing/terminal.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"terminal.ts transpile failed:\n{r.stderr[-500:]}"
    assert len(r.stdout) > 100, "terminal.ts transpile should produce output"


# [repo_tests] pass_to_pass
def test_repo_terminal_panel_label_test_transpiles():
    """Terminal panel label tests transpile without errors (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "build", "--target=bun", "--transpile-only", f"{REPO}/packages/app/src/pages/session/terminal-panel.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"terminal-panel.test.ts transpile failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_bun_version_available():
    """Bun runtime is available and functional (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "--version"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"bun --version failed:\n{r.stderr}"
    assert "1." in r.stdout, f"Expected bun version 1.x, got: {r.stdout}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_terminal_probe_focus_tracking():
    """Terminal probe must support focus(count) and step() for tracking focus retries."""
    result = _run_bun("""
Object.assign(globalThis, { window: globalThis });
(globalThis as any).__opencode_e2e = {
  terminal: { enabled: true, terminals: {} }
};

const { terminalProbe } = await import("./packages/app/src/testing/terminal.ts");
const probe = terminalProbe("t1");

probe.focus(3);
const f1 = (globalThis as any).__opencode_e2e.terminal.terminals["t1"].focusing;

probe.step();
const f2 = (globalThis as any).__opencode_e2e.terminal.terminals["t1"].focusing;

probe.step();
const f3 = (globalThis as any).__opencode_e2e.terminal.terminals["t1"].focusing;

probe.focus(0);
const f4 = (globalThis as any).__opencode_e2e.terminal.terminals["t1"].focusing;

console.log(JSON.stringify({ f1, f2, f3, f4 }));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["f1"] == 3, f"focus(3) should set focusing=3, got {data['f1']}"
    assert data["f2"] == 2, f"step() should decrement to 2, got {data['f2']}"
    assert data["f3"] == 1, f"step() should decrement to 1, got {data['f3']}"
    assert data["f4"] == 0, f"focus(0) should reset to 0, got {data['f4']}"


# [pr_diff] fail_to_pass
def test_prompt_probe_selection():
    """Prompt probe must track popover state and selection counts."""
    result = _run_bun("""
Object.assign(globalThis, { window: globalThis });
(globalThis as any).__opencode_e2e = {
  prompt: { enabled: true },
  terminal: { enabled: false }
};

const { promptProbe, promptEnabled } = await import("./packages/app/src/testing/prompt.ts");

if (!promptEnabled()) throw new Error("promptEnabled should be true when enabled");

promptProbe.set({
  popover: "slash",
  slash: { active: "terminal.toggle", ids: ["terminal.toggle", "help"] },
});

const s1 = (globalThis as any).__opencode_e2e.prompt.current;

promptProbe.select("terminal.toggle");
const s2 = (globalThis as any).__opencode_e2e.prompt.current;

promptProbe.select("help");
const s3 = (globalThis as any).__opencode_e2e.prompt.current;

console.log(JSON.stringify({
  popover: s1.popover,
  active: s1.slash.active,
  ids: s1.slash.ids,
  selected1: s2.selected,
  selects1: s2.selects,
  selected2: s3.selected,
  selects2: s3.selects,
}));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["popover"] == "slash", f"popover should be 'slash', got {data['popover']}"
    assert data["active"] == "terminal.toggle", \
        f"active should be 'terminal.toggle', got {data['active']}"
    assert data["ids"] == ["terminal.toggle", "help"], \
        f"ids mismatch: {data['ids']}"
    assert data["selected1"] == "terminal.toggle", \
        f"first select should be 'terminal.toggle', got {data['selected1']}"
    assert data["selects1"] == 1, f"first select count should be 1, got {data['selects1']}"
    assert data["selected2"] == "help", \
        f"second select should be 'help', got {data['selected2']}"
    assert data["selects2"] == 2, f"second select count should be 2, got {data['selects2']}"


# [pr_diff] fail_to_pass
def test_actions_exports_new_helpers():
    """actions.ts must export waitTerminalFocusIdle, showPromptSlash, and runPromptSlash."""
    actions = Path(REPO) / "packages" / "app" / "e2e" / "actions.ts"
    content = actions.read_text()
    assert "export async function waitTerminalFocusIdle" in content, \
        "actions.ts must export waitTerminalFocusIdle"
    assert "export async function showPromptSlash" in content, \
        "actions.ts must export showPromptSlash"
    assert "export async function runPromptSlash" in content, \
        "actions.ts must export runPromptSlash"


# ---------------------------------------------------------------------------
# Config update tests (fail_to_pass, pr_diff) — AGENTS.md additions
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agents_md_focus_idle_guidance():
    """AGENTS.md must document waitTerminalFocusIdle usage for terminal focus handling."""
    agents = Path(REPO) / "packages" / "app" / "e2e" / "AGENTS.md"
    content = agents.read_text()
    assert "waitTerminalFocusIdle" in content, \
        "AGENTS.md should document waitTerminalFocusIdle helper"
    lines = content.split("\n")
    has_context = any(
        "waitTerminalFocusIdle" in l and ("keyboard" in l.lower() or "focus" in l.lower())
        for l in lines
    )
    assert has_context, \
        "AGENTS.md should explain when to use waitTerminalFocusIdle (focus/keyboard context)"


# [pr_diff] fail_to_pass
def test_agents_md_semantic_state_guidance():
    """AGENTS.md must advise preferring semantic app state over transient DOM visibility."""
    agents = Path(REPO) / "packages" / "app" / "e2e" / "AGENTS.md"
    content = agents.read_text()
    lines = content.lower().split("\n")
    has_semantic = any("semantic" in l and ("transient" in l or "dom" in l) for l in lines)
    assert has_semantic, \
        "AGENTS.md should advise preferring semantic state over transient DOM"
    has_routing_warning = any("visible" in l and ("route" in l or "proof" in l) for l in lines)
    assert has_routing_warning, \
        "AGENTS.md should warn that visibility does not imply routing readiness"


# [pr_diff] fail_to_pass
def test_agents_md_helper_composition_guidance():
    """AGENTS.md must warn against redundant helper composition."""
    agents = Path(REPO) / "packages" / "app" / "e2e" / "AGENTS.md"
    content = agents.read_text()
    assert "redundant" in content.lower(), \
        "AGENTS.md should warn against redundant helper composition"
    lines = content.lower().split("\n")
    has_perform_verify = any("action" in l and "verify" in l for l in lines)
    assert has_perform_verify, \
        "AGENTS.md should recommend helpers that both perform action and verify result"


# ---------------------------------------------------------------------------
# Agent config compliance (fail_to_pass, agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — packages/app/e2e/AGENTS.md:190 @ cb6950109
def test_prompt_probe_inert_unless_enabled():
    """Prompt probe must be inert when e2e testing is not enabled (AGENTS.md rule)."""
    result = _run_bun("""
Object.assign(globalThis, { window: globalThis });
// Intentionally do NOT set __opencode_e2e — probe must be inert

const { promptEnabled, promptProbe } = await import("./packages/app/src/testing/prompt.ts");

const enabled = promptEnabled();

// set(), select(), clear() should silently no-op
promptProbe.set({
  popover: "slash",
  slash: { active: "test", ids: ["test"] },
});
promptProbe.select("test");
promptProbe.clear();

console.log(JSON.stringify({ enabled, noError: true }));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["enabled"] is False, "promptEnabled() should return false when not configured"
    assert data["noError"] is True, "probe methods should no-op without error when disabled"
