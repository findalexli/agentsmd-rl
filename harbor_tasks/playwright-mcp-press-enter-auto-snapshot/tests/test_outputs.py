"""
Task: playwright-mcp-press-enter-auto-snapshot
Repo: microsoft/playwright @ 3cdf7ca18324b9a0aa0ec80d818c2f9602b0ef60
PR:   38934

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
KEYBOARD_TS = Path(REPO) / "packages/playwright/src/mcp/browser/tools/keyboard.ts"
SKILL_MD = Path(REPO) / "packages/playwright/src/mcp/terminal/SKILL.md"

# Node.js script that extracts the press tool's handle function, creates mocks,
# executes it with the given key, and returns the call log as JSON.
_NODE_PRESS_TEST = r"""
import { readFileSync } from 'fs';

const key = process.argv[2];
const src = readFileSync('packages/playwright/src/mcp/browser/tools/keyboard.ts', 'utf8');

const m = src.match(/const\s+press\s*=\s*defineTabTool\(\{[\s\S]*?handle:\s*async\s*\([^)]*\)\s*=>\s*\{([\s\S]*?)\n\s*\},\n\}\);/);
if (!m) {
  console.log(JSON.stringify({ error: 'Could not find press handle function' }));
  process.exit(0);
}

const body = m[1];
const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
const handle = new AsyncFunction('tab', 'params', 'response', body);

const calls = [];
const tab = {
  page: { keyboard: { press: async (k) => calls.push('keyboard.press:' + k) } },
  waitForCompletion: async (fn) => { calls.push('waitForCompletion'); await fn(); }
};
const response = {
  addCode: () => {},
  setIncludeSnapshot: () => calls.push('setIncludeSnapshot')
};

try {
  await handle(tab, { key }, response);
  console.log(JSON.stringify({ calls }));
} catch (e) {
  console.log(JSON.stringify({ error: e.message }));
}
"""


def _run_press_key(key: str) -> list:
    """Execute the press tool's handle function with mocks and return the call log."""
    script = Path(REPO) / "_eval_press_test.mjs"
    script.write_text(_NODE_PRESS_TEST)
    try:
        r = subprocess.run(
            ["node", str(script), key],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)
    assert r.returncode == 0, f"Node execution failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "error" not in data, f"Handle extraction error: {data['error']}"
    return data["calls"]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified TypeScript and Markdown files exist and are non-empty."""
    for f in [KEYBOARD_TS, SKILL_MD]:
        assert f.exists(), f"{f.name} does not exist"
        content = f.read_text()
        assert len(content) > 100, f"{f.name} appears truncated or empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via Node.js execution
# ---------------------------------------------------------------------------

def test_enter_key_waits_for_completion():
    """Pressing Enter must trigger waitForCompletion to wait for navigation."""
    calls = _run_press_key("Enter")
    assert "waitForCompletion" in calls, \
        f"Enter key must trigger waitForCompletion, got calls: {calls}"


def test_enter_key_auto_snapshots():
    """Pressing Enter must call setIncludeSnapshot for automatic page state capture."""
    calls = _run_press_key("Enter")
    assert "setIncludeSnapshot" in calls, \
        f"Enter key must trigger setIncludeSnapshot, got calls: {calls}"


def test_skill_md_no_separate_snapshot_step():
    """SKILL.md core workflow should not list Snapshot as a separate numbered step."""
    content = SKILL_MD.read_text()
    workflow_match = re.search(
        r"## Core workflow\s*\n(.*?)\n(\n## |\Z)",
        content,
        re.DOTALL,
    )
    assert workflow_match, "Could not find '## Core workflow' section in SKILL.md"
    workflow = workflow_match.group(1)
    numbered_lines = re.findall(r"^\d+\.\s+(.*)$", workflow, re.MULTILINE)
    for line in numbered_lines:
        assert not re.match(r"Snapshot:", line, re.IGNORECASE), \
            f"Core workflow should not have a separate Snapshot step, found: '{line}'"


def test_skill_md_workflow_step_count():
    """Core workflow should have at most 3 steps after removing the manual snapshot step."""
    content = SKILL_MD.read_text()
    workflow_match = re.search(
        r"## Core workflow\s*\n(.*?)\n(\n## |\Z)",
        content,
        re.DOTALL,
    )
    assert workflow_match, "Could not find '## Core workflow' section in SKILL.md"
    workflow = workflow_match.group(1)
    numbered_steps = re.findall(r"^\d+\.", workflow, re.MULTILINE)
    assert len(numbered_steps) <= 3, \
        f"Core workflow should have at most 3 steps, found {len(numbered_steps)}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression / anti-stub checks
# ---------------------------------------------------------------------------

def test_non_enter_keys_press_directly():
    """Non-Enter keys should call keyboard.press directly without waitForCompletion."""
    calls = _run_press_key("Tab")
    assert "waitForCompletion" not in calls, \
        f"Non-Enter key should not trigger waitForCompletion, got calls: {calls}"
    assert "keyboard.press:Tab" in calls, \
        f"Non-Enter key should call keyboard.press directly, got calls: {calls}"


def test_press_tool_still_exported():
    """The press tool must still be part of the default export array."""
    src = KEYBOARD_TS.read_text()
    export_match = re.search(r"export default\s*\[([^\]]+)\]", src)
    assert export_match, "keyboard.ts must have a default export array"
    exports = export_match.group(1)
    assert "press" in exports, "press tool must be in the default export"


def test_press_sequentially_submit_unchanged():
    """pressSequentially with submit:true should still waitForCompletion + setIncludeSnapshot."""
    src = KEYBOARD_TS.read_text()
    ps_match = re.search(
        r"const pressSequentially\s*=\s*defineTabTool\(\{[\s\S]*?handle:\s*async\s*\([^)]*\)\s*=>\s*\{([\s\S]*?)\n\s*\},\n\}\);",
        src,
    )
    assert ps_match, "Could not find pressSequentially handle function"
    ps_body = ps_match.group(1)
    assert "waitForCompletion" in ps_body, \
        "pressSequentially must still use waitForCompletion for submit"
    assert "setIncludeSnapshot" in ps_body, \
        "pressSequentially must still call setIncludeSnapshot for submit"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — file structure regression checks
# ---------------------------------------------------------------------------

def test_keyboard_file_structure():
    """Keyboard.ts has valid structure with required exports (pass_to_pass)."""
    content = KEYBOARD_TS.read_text()
    assert "import { z }" in content, "Missing z import"
    assert "import { defineTabTool }" in content, "Missing defineTabTool import"
    assert "const press = defineTabTool" in content, "Missing press tool definition"
    assert "const pressSequentially = defineTabTool" in content, "Missing pressSequentially tool definition"
    assert "export default" in content, "Missing default export"


def test_skill_md_structure():
    """SKILL.md has valid structure with required sections (pass_to_pass)."""
    content = SKILL_MD.read_text()
    assert "## Core workflow" in content, "Missing Core workflow section"
    assert "## Commands" in content, "Missing Commands section"
    assert "name: playwright-cli" in content, "Missing header frontmatter"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression checks (actual subprocess tests)
# ---------------------------------------------------------------------------

def test_repo_npm_install():
    """Repo npm install succeeds (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "--include=dev"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"npm install failed: {r.stderr[-500:]}"


def test_repo_eslint_keyboard():
    """ESLint passes on keyboard.ts (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "--include=dev"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"npm install failed: {r.stderr[-500:]}"
    r = subprocess.run(
        ["npm", "run", "eslint", "--", "packages/playwright/src/mcp/browser/tools/keyboard.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed: {r.stderr[-500:]}"


def test_repo_build():
    """Repo build succeeds (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "--include=dev"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"npm install failed: {r.stderr[-500:]}"
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed: {r.stderr[-500:]}"


def test_repo_check_deps():
    """Repo dependency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "--include=dev"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"npm install failed: {r.stderr[-500:]}"
    r = subprocess.run(
        ["npm", "run", "check-deps"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"check-deps failed: {r.stderr[-500:]}"


def test_repo_lint_packages():
    """Repo package linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "--include=dev"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"npm install failed: {r.stderr[-500:]}"
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"lint-packages failed: {r.stderr[-500:]}"


def test_repo_test_types():
    """Repo test types check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "--include=dev"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"npm install failed: {r.stderr[-500:]}"
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed: {r.stderr[-500:]}"
    r = subprocess.run(
        ["npm", "run", "test-types"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"test-types failed: {r.stderr[-500:]}"


def test_repo_tsc():
    """TypeScript compilation passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "--include=dev"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"npm install failed: {r.stderr[-500:]}"
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed: {r.stderr[-500:]}"
    r = subprocess.run(
        ["npm", "run", "tsc"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"tsc failed: {r.stderr[-500:]}"


def test_repo_lint_tests():
    """Test file linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "--include=dev"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"npm install failed: {r.stderr[-500:]}"
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed: {r.stderr[-500:]}"
    r = subprocess.run(
        ["npm", "run", "lint-tests"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"lint-tests failed: {r.stderr[-500:]}"
