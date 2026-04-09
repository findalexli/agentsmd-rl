"""
Task: opencode-home-footer-plugin-slot
Repo: anomalyco/opencode @ 8e4bab51812fccf3b69713904159a4394b3a29ab
PR:   20057

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/opencode"
HOME_TSX = Path(REPO) / "packages/opencode/src/cli/cmd/tui/routes/home.tsx"
INTERNAL_TS = Path(REPO) / "packages/opencode/src/cli/cmd/tui/plugin/internal.ts"
SLOT_MAP = Path(REPO) / "packages/plugin/src/tui.ts"
FEATURE_PLUGINS = Path(REPO) / "packages/opencode/src/cli/cmd/tui/feature-plugins"

JS_FOOTER_LOGIC = r"""
const fs = require('fs');
const src = fs.readFileSync('packages/opencode/src/cli/cmd/tui/routes/home.tsx', 'utf8');
const forbidden = ['connectedMcpCount', 'mcpError', 'Installation.VERSION'];
const found = forbidden.filter(p => src.includes(p));
if (found.length > 0) {
    throw new Error('home.tsx still has: ' + found.join(', '));
}
console.log('PASS');
"""

JS_SLOT_USAGE = r"""
const fs = require('fs');
const src = fs.readFileSync('packages/opencode/src/cli/cmd/tui/routes/home.tsx', 'utf8');
if (!src.includes('home_footer')) throw new Error('home_footer slot not referenced');
if (!src.includes('Slot')) throw new Error('Slot component not used');
if (!src.includes('TuiPluginRuntime')) throw new Error('TuiPluginRuntime not referenced');
console.log('PASS');
"""

JS_FOOTER_EXISTS = r"""
const fs = require('fs');
const path = require('path');
const homeDir = 'packages/opencode/src/cli/cmd/tui/feature-plugins/home';
const candidates = ['footer.tsx', 'footer.ts', 'home-footer.tsx', 'home-footer.ts'];
let footerFile = null;
for (const name of candidates) {
    if (fs.existsSync(path.join(homeDir, name))) { footerFile = path.join(homeDir, name); break; }
}
if (!footerFile) {
    const files = fs.readdirSync(homeDir);
    const match = files.find(f => f.includes('footer') && (f.endsWith('.tsx') || f.endsWith('.ts')));
    if (match) footerFile = path.join(homeDir, match);
}
if (!footerFile) throw new Error('No footer plugin file found under feature-plugins/home/');
const src = fs.readFileSync(footerFile, 'utf8');
const codeLines = src.split('\n').filter(l => {
    const s = l.trim();
    return s && !s.startsWith('//') && !s.startsWith('*');
});
if (codeLines.length < 20) throw new Error('Footer plugin too short: ' + codeLines.length + ' lines');
if (!/<[A-Z][A-Za-z]*[\s/>]/.test(src)) throw new Error('No JSX components found');
const hasDir = /directory|cwd|\bdir\b|path/i.test(src);
const hasMcp = /mcp/i.test(src);
const hasVersion = /version/i.test(src);
const count = [hasDir, hasMcp, hasVersion].filter(Boolean).length;
if (count < 2) throw new Error('Only covers ' + count + '/3 footer concerns (need dir, mcp, version)');
console.log('PASS');
"""

JS_SLOT_REGISTRATION = r"""
const fs = require('fs');
const path = require('path');
const homeDir = 'packages/opencode/src/cli/cmd/tui/feature-plugins/home';
const candidates = ['footer.tsx', 'footer.ts', 'home-footer.tsx', 'home-footer.ts'];
let footerFile = null;
for (const name of candidates) {
    if (fs.existsSync(path.join(homeDir, name))) { footerFile = path.join(homeDir, name); break; }
}
if (!footerFile) {
    const files = fs.readdirSync(homeDir);
    const match = files.find(f => f.includes('footer') && (f.endsWith('.tsx') || f.endsWith('.ts')));
    if (match) footerFile = path.join(homeDir, match);
}
if (!footerFile) throw new Error('No footer plugin file found');
const src = fs.readFileSync(footerFile, 'utf8');
const hasDefault = /export\s+default/.test(src) || /export\s*\{[^}]*as\s+default/.test(src);
if (!hasDefault) throw new Error('Footer plugin missing default export');
if (!src.includes('home_footer')) throw new Error('home_footer slot not referenced in plugin');
if (!/register|slots|init\s*[:(]/.test(src)) throw new Error('No slot registration call');
console.log('PASS');
"""

JS_SLOT_MAP = r"""
const fs = require('fs');
const src = fs.readFileSync('packages/plugin/src/tui.ts', 'utf8');
if (!src.includes('home_footer')) throw new Error('home_footer not declared in TuiSlotMap');
console.log('PASS');
"""

JS_INTERNAL_FOOTER = r"""
const fs = require('fs');
const path = require('path');
const src = fs.readFileSync('packages/opencode/src/cli/cmd/tui/plugin/internal.ts', 'utf8');
const hasRef = /HomeFooter/.test(src) && /home\/footer/.test(src);
if (!hasRef) throw new Error('HomeFooter plugin not imported/registered in internal.ts from home/footer path');
// Also verify the import resolves to a real file
const importMatch = src.match(/from\s+['"]([^'"]*home\/footer[^'"]*)['"]/);
if (!importMatch) throw new Error('No home/footer import statement in internal.ts');
const importPath = importMatch[1];
const internalDir = path.dirname('packages/opencode/src/cli/cmd/tui/plugin/internal.ts');
const resolved = path.resolve(internalDir, importPath);
const extensions = ['', '.ts', '.tsx', '/index.ts', '/index.tsx'];
let found = false;
for (const ext of extensions) {
    if (fs.existsSync(resolved + ext)) { found = true; break; }
}
if (!found) throw new Error('Import does not resolve: ' + importPath);
console.log('PASS');
"""

JS_HINT_REMOVED = r"""
const fs = require('fs');
const src = fs.readFileSync('packages/opencode/src/cli/cmd/tui/routes/home.tsx', 'utf8');
if (/hint\s*=\s*\{/.test(src)) throw new Error('hint prop still passed to Prompt');
if (/useDirectory/.test(src)) throw new Error('useDirectory still imported');
console.log('PASS');
"""


def _find_footer_plugin() -> Path | None:
    """Locate the footer plugin file under feature-plugins/home/."""
    candidates = [
        FEATURE_PLUGINS / "home" / "footer.tsx",
        FEATURE_PLUGINS / "home" / "footer.ts",
        FEATURE_PLUGINS / "home" / "home-footer.tsx",
        FEATURE_PLUGINS / "home" / "home-footer.ts",
    ]
    for c in candidates:
        if c.exists():
            return c
    home_dir = FEATURE_PLUGINS / "home"
    if home_dir.is_dir():
        for f in home_dir.iterdir():
            if "footer" in f.name.lower() and f.suffix in (".tsx", ".ts"):
                return f
    return None


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via Node.js execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_home_tsx_footer_logic_extracted():
    """home.tsx must no longer contain inline MCP counting/display logic."""
    r = _run_node(JS_FOOTER_LOGIC)
    assert r.returncode == 0, f"Footer logic not extracted: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_home_tsx_uses_slot_for_footer():
    """home.tsx must render the footer via the plugin slot system."""
    r = _run_node(JS_SLOT_USAGE)
    assert r.returncode == 0, f"Slot not used for footer: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_footer_plugin_exists_with_content():
    """Footer plugin must exist with valid JSX rendering of directory, MCP, and version."""
    r = _run_node(JS_FOOTER_EXISTS)
    assert r.returncode == 0, f"Footer plugin content check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_footer_plugin_has_slot_registration():
    """Footer plugin must have default export and register home_footer slot."""
    r = _run_node(JS_SLOT_REGISTRATION)
    assert r.returncode == 0, f"Slot registration check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_slot_map_declares_home_footer():
    """TuiSlotMap in tui.ts must declare the home_footer slot."""
    r = _run_node(JS_SLOT_MAP)
    assert r.returncode == 0, f"Slot map check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_internal_registry_includes_footer():
    """internal.ts must import/register the home footer plugin and the import must resolve."""
    r = _run_node(JS_INTERNAL_FOOTER)
    assert r.returncode == 0, f"Internal registry check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_home_tsx_hint_removed():
    """home.tsx must not pass hint prop to Prompt (MCP hint moved to footer plugin)."""
    r = _run_node(JS_HINT_REMOVED)
    assert r.returncode == 0, f"Hint not removed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_home_tsx_preserves_core_components():
    """home.tsx must still render Logo and Prompt components."""
    src = HOME_TSX.read_text()
    assert re.search(r"Logo", src), "home.tsx missing Logo component"
    assert re.search(r"Prompt", src), "home.tsx missing Prompt component"


# [pr_diff] pass_to_pass
def test_existing_plugins_and_slots_preserved():
    """Existing internal plugins and TuiSlotMap slots must be preserved."""
    internal = INTERNAL_TS.read_text()
    assert re.search(r"Tips", internal, re.IGNORECASE), \
        "HomeTips plugin lost from internal.ts"
    assert re.search(r"Sidebar.*Footer|Footer.*Sidebar|SidebarFooter", internal, re.IGNORECASE), \
        "SidebarFooter plugin lost from internal.ts"
    slot_src = SLOT_MAP.read_text()
    for slot in ("home_logo", "home_prompt", "home_bottom"):
        assert slot in slot_src, f"Existing slot '{slot}' missing from TuiSlotMap"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:13 @ 8e4bab51812fccf3b69713904159a4394b3a29ab
def test_footer_plugin_no_any_type():
    """Footer plugin must not use the `any` type (AGENTS.md rule)."""
    footer = _find_footer_plugin()
    assert footer is not None, "No footer plugin file found"
    src = footer.read_text()
    lines = src.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        if re.search(r":\s*any\b|as\s+any\b|<any>", line):
            assert False, f"Footer plugin uses `any` type at line {i}: {line.strip()}"


# [agent_config] fail_to_pass — AGENTS.md:84 @ 8e4bab51812fccf3b69713904159a4394b3a29ab
def test_footer_plugin_no_else_statements():
    """Footer plugin must not use `else` statements — prefer early returns (AGENTS.md rule)."""
    footer = _find_footer_plugin()
    assert footer is not None, "No footer plugin file found"
    src = footer.read_text()
    lines = src.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        if re.search(r"\belse\b", line):
            assert False, f"Footer plugin uses `else` at line {i}: {line.strip()}"


# [agent_config] fail_to_pass — AGENTS.md:12 @ 8e4bab51812fccf3b69713904159a4394b3a29ab
def test_footer_plugin_no_try_catch():
    """Footer plugin must not use try/catch blocks (AGENTS.md rule)."""
    footer = _find_footer_plugin()
    assert footer is not None, "No footer plugin file found"
    src = footer.read_text()
    lines = src.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        if re.search(r"\btry\s*\{", line) or re.search(r"\bcatch\s*\(", line):
            assert False, f"Footer plugin uses try/catch at line {i}: {line.strip()} — avoid try/catch"


# [agent_config] fail_to_pass — AGENTS.md:17 @ 8e4bab51812fccf3b69713904159a4394b3a29ab
def test_footer_plugin_no_for_loops():
    """Footer plugin must prefer functional array methods over for loops (AGENTS.md rule)."""
    footer = _find_footer_plugin()
    assert footer is not None, "No footer plugin file found"
    src = footer.read_text()
    lines = src.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        if re.search(r"\bfor\s*\(", line):
            assert False, f"Footer plugin uses for loop at line {i}: {line.strip()} — prefer functional array methods"


# [agent_config] fail_to_pass — AGENTS.md:70 @ 8e4bab51812fccf3b69713904159a4394b3a29ab
def test_footer_plugin_const_over_let():
    """Footer plugin must prefer const over let (AGENTS.md rule)."""
    footer = _find_footer_plugin()
    assert footer is not None, "No footer plugin file found"
    src = footer.read_text()
    lines = src.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        if re.search(r"\blet\s+\w+", line):
            assert False, f"Footer plugin uses `let` at line {i}: {line.strip()} — prefer const"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo's own CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c",
         "export PATH=/root/.bun/bin:$PATH && cd /workspace/opencode && bun run typecheck"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c",
         "export PATH=/root/.bun/bin:$PATH && cd /workspace/opencode/packages/opencode && bun test"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"
