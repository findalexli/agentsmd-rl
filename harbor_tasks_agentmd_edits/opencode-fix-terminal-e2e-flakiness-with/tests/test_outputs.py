"""
Task: Fix terminal e2e flakiness with a real terminal driver
Repo: anomalyco/opencode @ c9c0318e0e5c2fcd80fc1c32a1ccfe360f182f90
PR: 17144

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
def test_typescript_syntax_valid():
    """Modified TypeScript files must parse without errors."""
    # Check terminal.ts exists and is valid TypeScript
    terminal_ts = Path(f"{REPO}/packages/app/src/testing/terminal.ts")
    assert terminal_ts.exists(), "terminal.ts not created"

    # Check actions.ts imports are valid
    actions_ts = Path(f"{REPO}/packages/app/e2e/actions.ts")
    content = actions_ts.read_text()
    assert "terminalAttr" in content, "actions.ts missing terminalAttr import"
    assert "E2EWindow" in content, "actions.ts missing E2EWindow import"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_terminal_testing_module_created():
    """Terminal testing module exists with proper exports."""
    terminal_ts = Path(f"{REPO}/packages/app/src/testing/terminal.ts")
    assert terminal_ts.exists(), "packages/app/src/testing/terminal.ts not created"

    content = terminal_ts.read_text()

    # Check for required exports
    assert "export const terminalAttr" in content, "terminalAttr not exported"
    assert "export type TerminalProbeState" in content, "TerminalProbeState not exported"
    assert "export type E2EWindow" in content, "E2EWindow not exported"
    assert "export const terminalProbe" in content, "terminalProbe not exported"

    # Check for required state fields
    assert "connected: boolean" in content, "connected field missing"
    assert "rendered: string" in content, "rendered field missing"
    assert "settled: number" in content, "settled field missing"

    # Check for required methods
    assert "init()" in content, "init method missing"
    assert "connect()" in content, "connect method missing"
    assert "render(data: string)" in content, "render method missing"
    assert "settle()" in content, "settle method missing"
    assert "drop()" in content, "drop method missing"


# [pr_diff] fail_to_pass
def test_wait_terminal_ready_helper_exists():
    """waitTerminalReady helper exported from actions.ts."""
    actions_ts = Path(f"{REPO}/packages/app/e2e/actions.ts")
    content = actions_ts.read_text()

    # Check function is exported
    assert "export async function waitTerminalReady" in content, "waitTerminalReady not exported"

    # Check it uses the terminal probe
    assert "terminalReady" in content, "waitTerminalReady doesn't use terminalReady helper"
    assert "terminalSelector" in content, "waitTerminalReady doesn't use terminalSelector"


# [pr_diff] fail_to_pass
def test_run_terminal_helper_exists():
    """runTerminal helper exported from actions.ts."""
    actions_ts = Path(f"{REPO}/packages/app/e2e/actions.ts")
    content = actions_ts.read_text()

    # Check function is exported
    assert "export async function runTerminal" in content, "runTerminal not exported"

    # Check it uses waitTerminalReady
    assert "waitTerminalReady" in content, "runTerminal doesn't call waitTerminalReady"

    # Check it types via keyboard
    assert "page.keyboard.type" in content, "runTerminal doesn't use page.keyboard.type"
    assert "page.keyboard.press" in content, "runTerminal doesn't use page.keyboard.press"


# [pr_diff] fail_to_pass
def test_terminal_component_integrates_probe():
    """Terminal component integrates the terminal probe."""
    terminal_tsx = Path(f"{REPO}/packages/app/src/components/terminal.tsx")
    content = terminal_tsx.read_text()

    # Check imports
    assert 'import { terminalAttr, terminalProbe } from "@/testing/terminal"' in content, \
        "terminal.tsx missing terminal probe import"

    # Check probe is initialized
    assert "const probe = terminalProbe(id)" in content, "terminal probe not initialized"

    # Check probe methods are called
    assert "probe.init()" in content, "probe.init() not called"
    assert "probe.connect()" in content, "probe.connect() not called"
    assert "probe.render(data)" in content, "probe.render() not called"
    assert "probe.settle()" in content, "probe.settle() not called"
    assert "probe.drop()" in content, "probe.drop() not called"

    # Check terminal attribute is set on DOM element
    assert "{...{ [terminalAttr]: id }}" in content, "terminalAttr not set on DOM element"


# [pr_diff] fail_to_pass
def test_fixtures_initializes_terminal_state():
    """Fixtures initialize terminal testing state in seedStorage."""
    fixtures_ts = Path(f"{REPO}/packages/app/e2e/fixtures.ts")
    content = fixtures_ts.read_text()

    # Check import
    assert 'import type { E2EWindow } from "../src/testing/terminal"' in content, \
        "fixtures.ts missing E2EWindow import"

    # Check terminal state is initialized
    assert "win.__opencode_e2e = {" in content, "__opencode_e2e not initialized"
    assert "terminal: {" in content, "terminal state not initialized"
    assert "enabled: true" in content, "terminal.enabled not set to true"
    assert "terminals: {}" in content, "terminal.terminals not initialized"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_agents_md_documents_terminal_testing():
    """AGENTS.md documents terminal testing patterns."""
    agents_md = Path(f"{REPO}/packages/app/e2e/AGENTS.md")
    content = agents_md.read_text()

    # Check for terminal testing section
    assert "### Terminal Tests" in content, "Terminal Tests section not in AGENTS.md"

    # Check for helper documentation
    assert "waitTerminalReady" in content, "waitTerminalReady not documented"
    assert "runTerminal" in content, "runTerminal not documented"

    # Check for key patterns
    assert "type through the browser" in content, "browser typing pattern not documented"
    assert "Do not write to the PTY through the SDK" in content, "PTY warning not documented"
    assert "Avoid `waitForTimeout`" in content, "waitForTimeout warning not documented"


# [static] pass_to_pass
def test_terminal_tests_use_new_helpers():
    """Existing terminal tests use new waitTerminalReady helper."""
    # Check terminal.spec.ts
    terminal_spec = Path(f"{REPO}/packages/app/e2e/terminal/terminal.spec.ts")
    if terminal_spec.exists():
        content = terminal_spec.read_text()
        assert "waitTerminalReady" in content, "terminal.spec.ts doesn't use waitTerminalReady"

    # Check terminal-init.spec.ts
    terminal_init = Path(f"{REPO}/packages/app/e2e/terminal/terminal-init.spec.ts")
    if terminal_init.exists():
        content = terminal_init.read_text()
        assert "waitTerminalReady" in content, "terminal-init.spec.ts doesn't use waitTerminalReady"

    # Check terminal-tabs.spec.ts uses runTerminal
    terminal_tabs = Path(f"{REPO}/packages/app/e2e/terminal/terminal-tabs.spec.ts")
    if terminal_tabs.exists():
        content = terminal_tabs.read_text()
        assert "runTerminal" in content, "terminal-tabs.spec.ts doesn't use runTerminal"
        assert "waitTerminalReady" in content, "terminal-tabs.spec.ts doesn't use waitTerminalReady"


# [static] pass_to_pass
def test_slash_terminal_test_updated():
    """Slash terminal test uses waitTerminalReady instead of toBeVisible."""
    slash_terminal = Path(f"{REPO}/packages/app/e2e/prompt/prompt-slash-terminal.spec.ts")
    if slash_terminal.exists():
        content = slash_terminal.read_text()
        assert "waitTerminalReady" in content, "prompt-slash-terminal.spec.ts doesn't use waitTerminalReady"


# [static] pass_to_pass
def test_settings_keybinds_test_updated():
    """Settings keybinds test uses waitTerminalReady."""
    settings_keybinds = Path(f"{REPO}/packages/app/e2e/settings/settings-keybinds.spec.ts")
    if settings_keybinds.exists():
        content = settings_keybinds.read_text()
        assert "waitTerminalReady" in content, "settings-keybinds.spec.ts doesn't use waitTerminalReady"



# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base AND after fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    # Install bun and dependencies, then run typecheck
    r = subprocess.run(
        ["bash", "-c", """
            set -e
            apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null
            curl -fsSL https://bun.sh/install 2>/dev/null | bash 2>/dev/null
            mv ~/.bun/bin/bun /usr/local/bin/
            cd /workspace/opencode
            bun install 2>&1 | tail -1
            npx turbo typecheck 2>&1
        """],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
            set -e
            apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null
            curl -fsSL https://bun.sh/install 2>/dev/null | bash 2>/dev/null
            mv ~/.bun/bin/bun /usr/local/bin/
            cd /workspace/opencode
            bun install 2>&1 | tail -1
            cd packages/app
            bun run test:unit 2>&1
        """],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_build():
    """Repo's app package builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
            set -e
            apt-get update -qq && apt-get install -y -qq unzip 2>/dev/null
            curl -fsSL https://bun.sh/install 2>/dev/null | bash 2>/dev/null
            mv ~/.bun/bin/bun /usr/local/bin/
            cd /workspace/opencode
            bun install 2>&1 | tail -1
            cd packages/app
            bun run build 2>&1
        """],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"
