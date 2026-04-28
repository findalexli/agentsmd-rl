"""
Task: opencode-terminal-e2e-probe-driver
Repo: anomalyco/opencode @ c9c0318e0e5c2fcd80fc1c32a1ccfe360f182f90
PR:   17144

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import re
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
def test_terminal_module_exists():
    """testing/terminal.ts must exist and be valid TypeScript."""
    terminal_path = APP / "src" / "testing" / "terminal.ts"
    assert terminal_path.exists(), "packages/app/src/testing/terminal.ts must exist"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_terminal_attr_value():
    """The module exports a constant with value 'data-pty-id'."""
    result = _run_ts(
        'const mod = await import("./src/testing/terminal.ts")\n'
        'for (const [name, value] of Object.entries(mod)) {\n'
        '  if (value === "data-pty-id") {\n'
        '    console.log(JSON.stringify({ found: name, value }))\n'
        '    break\n'
        '  }\n'
        '}\n'
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"
    # Should find something that exports the value "data-pty-id"
    assert '"data-pty-id"' in result.stdout, f"No export with value 'data-pty-id' found: {result.stdout}"


# [pr_diff] fail_to_pass
def test_terminal_probe_tracks_state():
    """A probe function tracks connected, rendered, and settled state correctly."""
    result = _run_ts(
        'globalThis.window = {\n'
        '  __opencode_e2e: { terminal: { enabled: true, terminals: {} } },\n'
        '}\n'
        'const mod = await import("./src/testing/terminal.ts")\n'
        '// Find the probe function (any name)\n'
        'const probeFn = Object.values(mod).find(\n'
        '  v => typeof v === "function" && v.toString().includes("id")\n'
        ')\n'
        'if (!probeFn) throw new Error("No probe function found")\n'
        'const probe = probeFn("test-1")\n'
        '// Call lifecycle methods (any names)\n'
        'const methods = Object.entries(probe)\n'
        'const init = methods.find(([k]) => k.toLowerCase().includes("init"))?.[1] ||\n'
        '             methods.find(([k, v]) => typeof v === "function")?.[1]\n'
        'const connect = methods.find(([k]) => k.toLowerCase().includes("connect"))?.[1] ||\n'
        '                methods.find(([k, v]) => typeof v === "function" && k !== "init")?.[1]\n'
        'const render = methods.find(([k]) => k.toLowerCase().includes("render"))?.[1]\n'
        'const settle = methods.find(([k]) => k.toLowerCase().includes("settle"))?.[1]\n'
        'if (init) init()\n'
        'if (connect) connect()\n'
        'if (render) render("hello ")\n'
        'if (render) render("world")\n'
        'if (settle) settle()\n'
        'const state = globalThis.window.__opencode_e2e.terminal.terminals["test-1"]\n'
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
def test_terminal_probe_cleanup():
    """A probe has a cleanup method that removes the terminal entry from state."""
    result = _run_ts(
        'globalThis.window = {\n'
        '  __opencode_e2e: { terminal: { enabled: true, terminals: {} } },\n'
        '}\n'
        'const mod = await import("./src/testing/terminal.ts")\n'
        'const probeFn = Object.values(mod).find(\n'
        '  v => typeof v === "function" && v.toString().includes("id")\n'
        ')\n'
        'if (!probeFn) throw new Error("No probe function found")\n'
        'const probe = probeFn("test-drop")\n'
        '// Initialize first\n'
        'const methods = Object.entries(probe)\n'
        'const init = methods.find(([k, v]) => typeof v === "function")?.[1]\n'
        'const connect = methods.find(([k, v]) => typeof v === "function")?.[1]\n'
        'if (init) init()\n'
        'if (connect) connect()\n'
        '// Find cleanup method (drop, cleanup, remove, dispose, etc.)\n'
        'const cleanup = methods.find(([k]) =>\n'
        '  ["drop", "cleanup", "remove", "dispose", "destroy", "delete", "clear"].some(\n'
        '    name => k.toLowerCase().includes(name)\n'
        '  )\n'
        ')?.[1] || methods.find(([k, v]) => typeof v === "function" && k !== "init" && k !== "connect")?.[1]\n'
        'if (cleanup) cleanup()\n'
        'const exists = "test-drop" in globalThis.window.__opencode_e2e.terminal.terminals\n'
        'console.log(JSON.stringify({ exists }))\n'
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["exists"] is False, "Cleanup should remove the terminal entry"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_terminal_probe_noop_without_window():
    """Probe methods are safe no-ops when window is undefined (Node env)."""
    result = _run_ts(
        "delete globalThis.window\n"
        'const mod = await import("./src/testing/terminal.ts")\n'
        'const probeFn = Object.values(mod).find(\n'
        '  v => typeof v === "function" && v.toString().includes("id")\n'
        ')\n'
        'if (!probeFn) throw new Error("No probe function found")\n'
        'const probe = probeFn("test-noop")\n'
        '// Call all methods - should not throw\n'
        'for (const [name, fn] of Object.entries(probe)) {\n'
        '  if (typeof fn === "function") {\n'
        '    if (name.toLowerCase().includes("render")) {\n'
        '      fn("data")\n'
        '    } else {\n'
        '      fn()\n'
        '    }\n'
        '  }\n'
        '}\n'
        'console.log("ok")\n'
    )
    assert result.returncode == 0, f"Probe should not throw without window: {result.stderr}"
    assert "ok" in result.stdout


# ---------------------------------------------------------------------------
# Integration tests — verify actual behavior in integrated files
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_terminal_component_integration():
    """terminal.tsx imports and uses the testing module's attribute value."""
    terminal_tsx = APP / "src" / "components" / "terminal.tsx"
    assert terminal_tsx.exists(), "terminal.tsx must exist"
    content = terminal_tsx.read_text()
    # Check that terminal.tsx imports from testing/terminal
    assert "testing/terminal" in content, "terminal.tsx must import from testing/terminal"
    # Check that it uses the attribute in JSX (spread or direct attribute)
    has_attr_usage = "data-pty-id" in content or "...{ [" in content or "{...{" in content
    assert has_attr_usage, "terminal.tsx must use data-pty-id attribute on terminal element"


# [pr_diff] fail_to_pass
def test_actions_helpers_exported():
    """actions.ts exports waitTerminalReady and runTerminal functions."""
    actions_ts = APP / "e2e" / "actions.ts"
    assert actions_ts.exists(), "actions.ts must exist"
    content = actions_ts.read_text()
    # Look for exported functions with terminal-related names
    # Match patterns like: export async function waitTerminalReady
    # or: export function runTerminal
    # or: export const waitTerminalReady
    export_pattern = r'export\s+(?:async\s+)?(?:function|const|let|var)\s+(\w+)'
    exports = re.findall(export_pattern, content)
    # Check for terminal-related helper functions
    has_wait = any("wait" in e.lower() and "terminal" in e.lower() for e in exports)
    has_run = any("run" in e.lower() and "terminal" in e.lower() for e in exports)
    assert has_wait, f"actions.ts must export a wait-terminal helper, found: {exports}"
    assert has_run, f"actions.ts must export a run-terminal helper, found: {exports}"


# [pr_diff] fail_to_pass
def test_fixtures_integration():
    """fixtures.ts sets up window.__opencode_e2e.terminal via addInitScript."""
    fixtures_ts = APP / "e2e" / "fixtures.ts"
    assert fixtures_ts.exists(), "fixtures.ts must exist"
    content = fixtures_ts.read_text()
    # Check for the integration
    has_window_setup = "__opencode_e2e" in content and "terminal" in content
    has_init_script = "addInitScript" in content
    assert has_window_setup, "fixtures.ts must set up window.__opencode_e2e.terminal"
    assert has_init_script, "fixtures.ts must use addInitScript"


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
def test_agents_md_documents_terminal_helpers():
    """e2e/AGENTS.md must document terminal testing helpers."""
    agents_md = APP / "e2e" / "AGENTS.md"
    assert agents_md.exists(), "packages/app/e2e/AGENTS.md must exist"
    content = agents_md.read_text()
    # Check for terminal testing section with helpers
    has_wait_helper = "waitTerminalReady" in content
    has_run_helper = "runTerminal" in content
    has_terminal_section = "Terminal Tests" in content
    assert has_wait_helper, "AGENTS.md should document a wait-for-terminal helper"
    assert has_run_helper, "AGENTS.md should document a run-terminal helper"
    assert has_terminal_section, "AGENTS.md should have a terminal testing section"


# [pr_diff] fail_to_pass
def test_agents_md_terminal_testing_guidelines():
    """e2e/AGENTS.md must include terminal testing guidelines."""
    agents_md = APP / "e2e" / "AGENTS.md"
    content = agents_md.read_text()
    lower = content.lower()
    # Must have a dedicated terminal tests section
    assert "terminal test" in lower or "terminal tests" in lower, \
        "AGENTS.md should have a 'Terminal Tests' section"
    # Must advise typing through the browser
    assert "type" in lower and "browser" in lower, \
        "Terminal testing section should advise typing through the browser"
    # Must warn against waitForTimeout
    assert "waitfortimeout" in lower, \
        "Terminal testing section should mention avoiding waitForTimeout"
    # Must warn against custom DOM readiness checks
    assert "dom" in lower or "data-" in content, \
        "Terminal testing section should warn against custom DOM checks"

# === Scoped CI-mined test (taskforge.ci_check_miner) ===
# Only tests scoped to the affected package (packages/app)
def test_ci_app_unit_tests():
    """pass_to_pass | CI job 'unit tests' scoped to packages/app"""
    bun_path = _get_bun_path()
    env = _bun_env()
    r = subprocess.run(
        [str(bun_path), "run", "test"],
        capture_output=True, text=True, timeout=120, cwd=str(APP), env=env,
    )
    assert r.returncode == 0, (
        f"CI step 'unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")