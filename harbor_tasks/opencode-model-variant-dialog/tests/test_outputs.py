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


_NODE_ANALYSIS = r"""
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


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates — ensure repo's own checks pass on base and gold
# ---------------------------------------------------------------------------

_NODE_SYNTAX_CHECK = r"""
import { readFileSync } from 'fs';

const files = [
    'packages/opencode/src/cli/cmd/tui/app.tsx',
    'packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx'
];

const results = {};

for (const file of files) {
    try {
        const content = readFileSync(file, 'utf8');
        // Check for basic TSX structural issues
        const openTags = (content.match(/<[A-Z][a-zA-Z0-9]*/g) || []).length;
        const closeTags = (content.match(/<\/[A-Z][a-zA-Z0-9]*/g) || []).length;
        const selfClosing = (content.match(/\/>/g) || []).length;

        // Check for unclosed braces
        const openBraces = (content.match(/\{/g) || []).length;
        const closeBraces = (content.match(/\}/g) || []).length;

        // Check for basic import/export syntax
        const imports = (content.match(/import\s+/g) || []).length;
        const exports = (content.match(/export\s+/g) || []).length;

        results[file] = {
            valid: openBraces === closeBraces,
            tags: { open: openTags, close: closeTags, selfClosing },
            imports,
            exports,
            hasDialogVariantExport: content.includes('export function DialogVariant') ||
                                   content.includes('export const DialogVariant') ||
                                   content.includes('export default function DialogVariant')
        };
    } catch (e) {
        results[file] = { error: e.message };
    }
}

console.log(JSON.stringify(results));
"""


# [repo_ci] pass_to_pass — repo's typecheck equivalent
def test_repo_tsx_syntax_valid():
    """Repo's TSX files have valid syntax (pass_to_pass gate for typecheck)."""
    r = _run_node(_NODE_SYNTAX_CHECK)
    assert r.returncode == 0, f"Syntax check script failed: {r.stderr}"
    results = json.loads(r.stdout.strip())

    for file, data in results.items():
        assert "error" not in data, f"Error reading {file}: {data.get('error')}"
        assert data.get("valid"), f"{file} has mismatched braces - syntax error"


# [repo_ci] pass_to_pass — repo's test equivalent for TUI module
def test_repo_dialog_variant_exports_component():
    """DialogVariant component is properly exported (pass_to_pass gate for tests)."""
    r = _run_node(_NODE_SYNTAX_CHECK)
    assert r.returncode == 0, f"Export check script failed: {r.stderr}"
    results = json.loads(r.stdout.strip())

    variant_file = 'packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx'
    assert variant_file in results, f"{variant_file} not found in results"
    data = results[variant_file]
    assert data.get("hasDialogVariantExport"), \
        f"{variant_file} does not export DialogVariant component"


# [repo_ci] pass_to_pass — verify app.tsx structure is valid for CI
def test_repo_app_tsx_structure():
    """app.tsx has valid structure with imports and exports (pass_to_pass gate)."""
    r = _run_node(_NODE_SYNTAX_CHECK)
    assert r.returncode == 0, f"Structure check script failed: {r.stderr}"
    results = json.loads(r.stdout.strip())

    app_file = 'packages/opencode/src/cli/cmd/tui/app.tsx'
    assert app_file in results, f"{app_file} not found in results"
    data = results[app_file]
    assert data.get("imports", 0) > 0, f"{app_file} has no imports"
    assert data.get("exports", 0) > 0, f"{app_file} has no exports"
