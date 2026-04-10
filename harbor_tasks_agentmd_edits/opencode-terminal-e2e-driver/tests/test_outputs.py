"""
Task: opencode-terminal-e2e-driver
Repo: anomalyco/opencode @ c9c0318e0e5c2fcd80fc1a32a1ccfe360f182f90
PR:   17144

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/opencode"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax_check():
    """New and modified TypeScript files must parse without errors."""
    # Check that terminal.ts exists and is valid TypeScript
    terminal_ts = Path(f"{REPO}/packages/app/src/testing/terminal.ts")
    assert terminal_ts.exists(), "terminal.ts must exist"

    # Verify TypeScript syntax by running tsc --noEmit on the new file
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "--target", "ES2022", str(terminal_ts)],
        cwd=f"{REPO}/packages/app",
        capture_output=True,
        timeout=60,
    )
    # If tsc is not available, fall back to basic parsing check via bun
    if r.returncode != 0 and b"command not found" in r.stderr:
        r2 = subprocess.run(
            ["bun", "run", "--hot", "typecheck"],
            cwd=f"{REPO}/packages/app",
            capture_output=True,
            timeout=120,
        )
        # Just check that files parse - typecheck errors are OK for syntax validation
        assert b"SyntaxError" not in r2.stderr, f"Syntax error in modified files: {r2.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_terminal_probe_file_exists():
    """The terminal probe/driver file must be created with proper exports."""
    terminal_ts = Path(f"{REPO}/packages/app/src/testing/terminal.ts")
    assert terminal_ts.exists(), "packages/app/src/testing/terminal.ts must exist"

    content = terminal_ts.read_text()
    # Check for key exports
    assert "export const terminalAttr" in content, "terminalAttr must be exported"
    assert "export type TerminalProbeState" in content, "TerminalProbeState type must be exported"
    assert "export type E2EWindow" in content, "E2EWindow type must be exported"
    assert "export const terminalProbe" in content, "terminalProbe function must be exported"


# [pr_diff] fail_to_pass
def test_actions_has_terminal_helpers():
    """actions.ts must export waitTerminalReady and runTerminal helpers."""
    actions_ts = Path(f"{REPO}/packages/app/e2e/actions.ts")
    assert actions_ts.exists(), "actions.ts must exist"

    content = actions_ts.read_text()
    # Check for the new helper functions
    assert "export async function waitTerminalReady" in content, "waitTerminalReady must be exported"
    assert "export async function runTerminal" in content, "runTerminal must be exported"
    # Check it imports from terminal.ts
    assert 'from "../src/testing/terminal"' in content or 'from "@/testing/terminal"' in content, \
        "actions.ts must import from terminal.ts"


# [pr_diff] fail_to_pass
def test_terminal_component_integrates_probe():
    """Terminal component must integrate the terminal probe system."""
    terminal_tsx = Path(f"{REPO}/packages/app/src/components/terminal.tsx")
    assert terminal_tsx.exists(), "terminal.tsx must exist"

    content = terminal_tsx.read_text()
    # Check for probe integration
    assert 'import { terminalAttr, terminalProbe }' in content or \
           'from "@/testing/terminal"' in content, \
        "terminal.tsx must import terminal probe"
    assert "terminalProbe(id)" in content or "const probe = terminalProbe" in content, \
        "terminal.tsx must create a probe instance"
    assert "probe.init()" in content or "probe.connect()" in content, \
        "terminal.tsx must use probe methods"
    assert "[terminalAttr]: id" in content or 'terminalAttr: id' in content or "data-pty-id" in content, \
        "terminal.tsx must set data-pty-id attribute"


# [pr_diff] fail_to_pass
def test_fixtures_enables_terminal_driver():
    """fixtures.ts must enable the test-only terminal driver in init script."""
    fixtures_ts = Path(f"{REPO}/packages/app/e2e/fixtures.ts")
    assert fixtures_ts.exists(), "fixtures.ts must exist"

    content = fixtures_ts.read_text()
    # Check for terminal driver initialization
    assert "terminal: { enabled: true" in content or '__opencode_e2e: { ...win.__opencode_e2e, terminal:' in content.replace("\n", "").replace(" ", "").replace("...", ""), \
        "fixtures.ts must enable terminal driver"
    assert 'import type { E2EWindow }' in content or 'import { E2EWindow }' in content, \
        "fixtures.ts must import E2EWindow type"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — config documentation update tests
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — packages/app/e2e/AGENTS.md:170-175 @ c9c0318e0e5c2fcd80fc1a32a1ccfe360f182f90
def test_agents_md_documents_terminal_testing():
    """AGENTS.md must document the terminal testing pattern with waitTerminalReady and runTerminal."""
    agents_md = Path(f"{REPO}/packages/app/e2e/AGENTS.md")
    assert agents_md.exists(), "packages/app/e2e/AGENTS.md must exist"

    content = agents_md.read_text()
    # Check for terminal testing section
    assert "### Terminal Tests" in content, "AGENTS.md must have a Terminal Tests section"
    assert "waitTerminalReady" in content, "AGENTS.md must document waitTerminalReady helper"
    assert "runTerminal" in content, "AGENTS.md must document runTerminal helper"
    assert "type through the browser" in content.lower() or "Do not write to the PTY" in content, \
        "AGENTS.md must document that terminal tests should type through browser"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_terminal_probe_not_stub():
    """Terminal probe implementation must have real logic, not just empty functions."""
    terminal_ts = Path(f"{REPO}/packages/app/src/testing/terminal.ts")
    content = terminal_ts.read_text()

    # Count function implementations with actual logic (not just pass/empty)
    # The probe has multiple methods: init, connect, render, settle, focus, step, control, drop
    # set() is called in init() and focus(); state[id] is used directly in other methods
    assert content.count("set(") >= 2 or "state[id]" in content, \
        "terminalProbe must have real implementation with state management"
    assert "rendered:" in content and "settled:" in content, \
        "TerminalProbeState must track rendered and settled state"


# [static] pass_to_pass
def test_run_terminal_not_stub():
    """runTerminal helper must have real implementation with typing and waiting logic."""
    actions_ts = Path(f"{REPO}/packages/app/e2e/actions.ts")
    content = actions_ts.read_text()

    # Find the runTerminal function and check it has real implementation
    assert "page.keyboard.type" in content, "runTerminal must type via keyboard"
    assert "page.keyboard.press" in content and "Enter" in content, "runTerminal must press Enter"
    assert "terminalHas" in content or "poll" in content, "runTerminal must poll for output"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI checks from the repository
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (bun typecheck in packages/app)."""
    r = subprocess.run(
        ["bun", "typecheck"],
        cwd=f"{REPO}/packages/app",
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit test suite passes (bun test:ci in packages/app)."""
    r = subprocess.run(
        ["bun", "test:ci"],
        cwd=f"{REPO}/packages/app",
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"
