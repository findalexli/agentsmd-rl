"""
Task: opencode-model-variant-dialog
Repo: anomalyco/opencode @ 8ac2fbbd1262a9de1362beb6e29debc446ceea0e
PR:   19534

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess, json, re
from pathlib import Path

REPO = "/workspace/opencode"
APP_FILE = Path(REPO) / "packages/opencode/src/cli/cmd/tui/app.tsx"
VARIANT_FILE = Path(REPO) / "packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx"

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


_NODE_ANALYSIS = """
import { readFileSync } from 'fs';

const src = readFileSync('packages/opencode/src/cli/cmd/tui/app.tsx', 'utf8');
const lines = src.split('\\n');

// Check for DialogVariant import
const importLines = lines.filter(l => l.includes('import') && l.includes('DialogVariant'));
const hasImport = importLines.length > 0;

// Find variant_cycle keybind and extract surrounding context
const idx = lines.findIndex(l => l.includes('variant_cycle'));
let title = null;
let hasDialogCall = false;
let hasDialogVariant = false;
let hasBlindCycle = false;

if (idx >= 0) {
    const start = Math.max(0, idx - 12);
    const end = Math.min(lines.length, idx + 12);
    const context = lines.slice(start, end).join('\\n');

    hasDialogCall = context.includes('dialog.replace(') ||
                    context.includes('dialog.open(') ||
                    context.includes('dialog.show(') ||
                    context.includes('dialog.push(');

    hasDialogVariant = context.includes('DialogVariant');
    hasBlindCycle = context.includes('.variant.cycle(');

    for (let i = start; i < end; i++) {
        const m = lines[i].match(/title:\\s*["'`]([^"'`]+)["'`]/);
        if (m) {
            title = m[1];
            break;
        }
    }
}

console.log(JSON.stringify({
    found: idx >= 0,
    hasImport,
    hasDialogCall,
    hasDialogVariant,
    hasBlindCycle,
    title,
}));
"""

_analysis_cache = None


def _get_analysis():
    """Run the Node.js analysis script once and cache the result."""
    global _analysis_cache
    if _analysis_cache is None:
        r = _run_node(_NODE_ANALYSIS)
        assert r.returncode == 0, f"Node analysis script failed: {r.stderr}"
        _analysis_cache = json.loads(r.stdout.strip())
    return _analysis_cache


def _strip_comments(src: str) -> str:
    """Strip JS/TS single-line and multi-line comments."""
    src = re.sub(r"//.*$", "", src, flags=re.MULTILINE)
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)
    return src


def _read_app_stripped() -> str:
    return _strip_comments(APP_FILE.read_text())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via Node.js execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_handler_opens_dialog_variant():
    """variant_cycle handler must open DialogVariant via dialog API."""
    data = _get_analysis()
    assert data["found"], "variant_cycle keybind not found in app.tsx"
    assert data["hasDialogCall"], \
        "Handler does not call dialog.replace/open/show/push"
    assert data["hasDialogVariant"], \
        "Handler does not reference DialogVariant component"


# [pr_diff] fail_to_pass
def test_dialog_variant_imported():
    """DialogVariant must be imported in app.tsx."""
    data = _get_analysis()
    assert data["hasImport"], "DialogVariant is not imported in app.tsx"


# [pr_diff] fail_to_pass
def test_no_blind_cycle_in_handler():
    """The old .variant.cycle() call must be removed from the handler."""
    data = _get_analysis()
    assert data["found"], "variant_cycle keybind not found in app.tsx"
    assert not data["hasBlindCycle"], \
        "Handler still calls .variant.cycle() — should open dialog instead"


# [pr_diff] fail_to_pass
def test_title_not_variant_cycle():
    """Title for the variant action must not be the old 'Variant cycle'."""
    data = _get_analysis()
    assert data["found"], "variant_cycle keybind not found in app.tsx"
    assert data["title"] != "Variant cycle", \
        f"Title is still 'Variant cycle' — should be a selection-oriented label"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_variant_keybind_preserved():
    """variant_cycle keybind must still be registered."""
    stripped = _read_app_stripped()
    assert re.search(r'''["'`]variant[._]cycle["'`]''', stripped), \
        "variant_cycle keybind not found in app.tsx"


# [static] pass_to_pass
def test_other_dialogs_preserved():
    """DialogModel and App function must still exist (anti-stub)."""
    stripped = _read_app_stripped()
    assert "DialogModel" in stripped, "DialogModel reference missing — file may be gutted"
    assert re.search(r"function\s+App\s*\(", stripped), \
        "App function missing — file may be gutted"


# [static] pass_to_pass
def test_app_not_gutted():
    """app.tsx must have >150 meaningful lines."""
    stripped = _read_app_stripped()
    lines = [l for l in stripped.splitlines() if l.strip()]
    assert len(lines) > 150, f"Only {len(lines)} meaningful lines — file appears gutted"


# [pr_diff] pass_to_pass
def test_dialog_variant_component_exists():
    """dialog-variant.tsx must exist and export DialogVariant."""
    assert VARIANT_FILE.exists(), f"{VARIANT_FILE} does not exist"
    content = VARIANT_FILE.read_text()
    assert "DialogVariant" in content, "DialogVariant not found in dialog-variant.tsx"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:13 @ 8ac2fbbd1262a9de1362beb6e29debc446ceea0e
def test_no_any_type():
    """No 'any' type usage in app.tsx (AGENTS.md line 13: 'Avoid using the any type')."""
    stripped = _read_app_stripped()
    assert not re.search(r":\s*any\b|<any>|as\s+any\b", stripped), \
        "app.tsx contains 'any' type usage — violates AGENTS.md:13"


# [agent_config] pass_to_pass — AGENTS.md:84 @ 8ac2fbbd1262a9de1362beb6e29debc446ceea0e
def test_no_else_in_variant_area():
    """No else statements near variant handler (AGENTS.md line 84: 'Avoid else statements')."""
    stripped = _read_app_stripped()
    m = re.search(r"variant[._]cycle[\s\S]{0,500}", stripped)
    if m:
        assert not re.search(r"\belse\b", m.group(0)), \
            "else statement found near variant handler — violates AGENTS.md:84"


# [agent_config] pass_to_pass — AGENTS.md:12 @ 8ac2fbbd1262a9de1362beb6e29debc446ceea0e
def test_no_try_catch_in_variant_area():
    """No try/catch near variant handler (AGENTS.md line 12: 'Avoid try/catch where possible')."""
    stripped = _read_app_stripped()
    m = re.search(r"variant[._]cycle[\s\S]{0,500}", stripped)
    if m:
        assert not re.search(r"\btry\s*\{", m.group(0)), \
            "try/catch found near variant handler — violates AGENTS.md:12"


# [agent_config] pass_to_pass — AGENTS.md:70 @ 8ac2fbbd1262a9de1362beb6e29debc446ceea0e
def test_prefer_const_in_variant_area():
    """No let in variant handler area (AGENTS.md line 70: 'Prefer const over let')."""
    stripped = _read_app_stripped()
    m = re.search(r"variant[._]cycle[\s\S]{0,500}", stripped)
    if m:
        assert not re.search(r"\blet\s+\w", m.group(0)), \
            "let found near variant handler — use const instead (AGENTS.md:70)"
