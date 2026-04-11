"""
Task: opencode-terminal-e2e-probe-driver
Repo: anomalyco/opencode @ c9c0318e0e5c2fcd80fc1c32a1ccfe360f182f90
PR:   17144

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/opencode")
APP = REPO / "packages" / "app"


def _run_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a TypeScript snippet to a temp file and run it with node."""
    script_path = APP / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(APP),
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """testing/terminal.ts must exist and be valid TypeScript."""
    terminal_path = APP / "src" / "testing" / "terminal.ts"
    assert terminal_path.exists(), "packages/app/src/testing/terminal.ts must exist"
    content = terminal_path.read_text()
    assert "terminalAttr" in content, "terminal.ts must export terminalAttr"
    assert "terminalProbe" in content, "terminal.ts must export terminalProbe"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_terminal_attr_constant():
    """testing/terminal.ts exports terminalAttr as 'data-pty-id'."""
    result = _run_ts(
        'import { terminalAttr } from "./src/testing/terminal.ts"\n'
        'console.log(JSON.stringify({ attr: terminalAttr }))\n'
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["attr"] == "data-pty-id", f"Expected 'data-pty-id', got {data['attr']}"


# [pr_diff] fail_to_pass
def test_terminal_probe_state_tracking():
    """terminalProbe tracks connected, rendered, and settled state correctly."""
    result = _run_ts(
        'globalThis.window = {\n'
        '  __opencode_e2e: { terminal: { enabled: true, terminals: {} } },\n'
        '}\n'
        'const { terminalProbe } = await import("./src/testing/terminal.ts")\n'
        'const probe = terminalProbe(\'test-1\')\n'
        'probe.init()\n'
        'probe.connect()\n'
        'probe.render(\'hello \')\n'
        'probe.render(\'world\')\n'
        'probe.settle()\n'
        'const state = globalThis.window.__opencode_e2e.terminal.terminals[\'test-1\']\n'
        'console.log(JSON.stringify(state))\n'
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data.get("connected") is True, f"Expected connected=true, got {data}"
    assert data.get("rendered") == "hello world", (
        f"Expected rendered='hello world', got '{data.get('rendered')}'"
    )
    assert data.get("settled") == 1, f"Expected settled=1, got {data.get('settled')}"


# [pr_diff] fail_to_pass
def test_terminal_probe_drop():
    """terminalProbe.drop() removes the terminal entry from state."""
    result = _run_ts(
        'globalThis.window = {\n'
        '  __opencode_e2e: { terminal: { enabled: true, terminals: {} } },\n'
        '}\n'
        'const { terminalProbe } = await import("./src/testing/terminal.ts")\n'
        'const probe = terminalProbe(\'test-drop\')\n'
        'probe.init()\n'
        'probe.connect()\n'
        'probe.drop()\n'
        'const exists = \'test-drop\' in globalThis.window.__opencode_e2e.terminal.terminals\n'
        'console.log(JSON.stringify({ exists }))\n'
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["exists"] is False, "drop() should remove the terminal entry"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_terminal_probe_noop_without_window():
    """Probe methods are safe no-ops when window is undefined (Node env)."""
    result = _run_ts(
        "delete globalThis.window\n"
        'const { terminalProbe } = await import("./src/testing/terminal.ts")\n'
        'const probe = terminalProbe(\'test-noop\')\n'
        'probe.init()\n'
        'probe.connect()\n'
        'probe.render(\'data\')\n'
        'probe.settle()\n'
        'probe.drop()\n'
        'console.log("ok")\n'
    )
    assert result.returncode == 0, f"Probe should not throw without window: {result.stderr}"
    assert "ok" in result.stdout


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass tests — verify base commit health
# ---------------------------------------------------------------------------


def _ensure_system_deps():
    """Ensure system dependencies (unzip) are installed."""
    try:
        subprocess.run(
            ["unzip", "-v"],
            capture_output=True,
            timeout=5,
        )
    except FileNotFoundError:
        subprocess.run(
            ["apt-get", "update", "-qq"],
            capture_output=True,
            timeout=30,
        )
        subprocess.run(
            ["apt-get", "install", "-y", "-qq", "unzip"],
            capture_output=True,
            timeout=60,
        )


def _get_bun_path() -> Path:
    """Get bun path, installing if necessary."""
    _ensure_system_deps()
    bun_bin = Path.home() / ".bun" / "bin"
    bun_path = bun_bin / "bun"

    if not bun_path.exists():
        install_result = subprocess.run(
            "curl -fsSL https://bun.sh/install | bash",
            capture_output=True,
            text=True,
            timeout=120,
            shell=True,
        )
        if install_result.returncode != 0:
            raise RuntimeError(f"Failed to install bun: {install_result.stderr}")

    return bun_path


def _bun_env() -> dict:
    """Get environment with bun in PATH."""
    bun_bin = Path.home() / ".bun" / "bin"
    return {**os.environ, "PATH": f"{bun_bin}:{os.environ.get('PATH', '')}"}


# [repo_tests] pass_to_pass
def test_repo_typecheck_app():
    """Repo's packages/app typecheck passes (pass_to_pass)."""
    bun_path = _get_bun_path()
    env = _bun_env()

    r = subprocess.run(
        [str(bun_path), "install"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
        env=env,
    )
    assert r.returncode == 0, f"bun install failed: {r.stderr[-500:]}"

    r = subprocess.run(
        [str(bun_path), "run", "typecheck"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(APP),
        env=env,
    )
    assert r.returncode == 0, f"packages/app typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typecheck_turbo():
    """Repo's turbo typecheck passes (pass_to_pass)."""
    bun_path = _get_bun_path()
    env = _bun_env()

    r = subprocess.run(
        [str(bun_path), "install"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
        env=env,
    )
    assert r.returncode == 0, f"bun install failed: {r.stderr[-500:]}"

    r = subprocess.run(
        [str(bun_path), "run", "typecheck"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
        env=env,
    )
    assert r.returncode == 0, f"turbo typecheck failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests for packages/app pass (pass_to_pass)."""
    bun_path = _get_bun_path()
    env = _bun_env()

    r = subprocess.run(
        [str(bun_path), "install"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
        env=env,
    )
    assert r.returncode == 0, f"bun install failed: {r.stderr[-500:]}"

    r = subprocess.run(
        [str(bun_path), "test", "--preload", "./happydom.ts", "./src"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(APP),
        env=env,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_check():
    """Repo's prettier check for packages/app/src passes (pass_to_pass)."""
    bun_path = _get_bun_path()
    env = _bun_env()

    r = subprocess.run(
        [str(bun_path), "install"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
        env=env,
    )
    assert r.returncode == 0, f"bun install failed: {r.stderr[-500:]}"

    r = subprocess.run(
        [str(bun_path), "run", "prettier", "--check", "packages/app/src"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO),
        env=env,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Config/documentation update tests (pr_diff) — AGENTS.md
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_agents_md_documents_helpers():
    """e2e/AGENTS.md must document waitTerminalReady and runTerminal helpers."""
    agents_md = APP / "e2e" / "AGENTS.md"
    assert agents_md.exists(), "packages/app/e2e/AGENTS.md must exist"
    content = agents_md.read_text()
    assert "waitTerminalReady" in content, "AGENTS.md should document waitTerminalReady helper"
    assert "runTerminal" in content, "AGENTS.md should document runTerminal helper"


# [pr_diff] fail_to_pass
def test_agents_md_terminal_testing_section():
    """e2e/AGENTS.md must include a terminal testing guidelines section."""
    agents_md = APP / "e2e" / "AGENTS.md"
    content = agents_md.read_text()
    lower = content.lower()
    assert "terminal test" in lower, "AGENTS.md should have a Terminal Tests section"
    assert "type through the browser" in lower or "type through" in lower, "Terminal testing section should advise typing through the browser"
    assert "waitTerminalReady" in content and "runTerminal" in content, "Terminal testing section should reference both helpers"
