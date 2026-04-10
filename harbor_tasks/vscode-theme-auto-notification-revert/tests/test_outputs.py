"""
Task: vscode-theme-auto-notification-revert
Repo: microsoft/vscode @ d4b002af75f1878ead5b608beed470b9ae25b6f8
PR:   306341

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
THEME_FILE = f"{REPO}/src/vs/workbench/services/themes/browser/workbenchThemeService.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax():
    """Modified file has no obvious syntax errors (balanced braces, no stray tokens)."""
    content = Path(THEME_FILE).read_text()
    # Basic sanity: file is non-empty and braces are roughly balanced
    assert len(content) > 1000, "File appears truncated or empty"
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert abs(open_braces - close_braces) < 5, (
        f"Brace mismatch: {open_braces} open vs {close_braces} close — likely a syntax error"
    )
    # Check that the file still has the class declaration
    assert "class WorkbenchThemeService" in content, "WorkbenchThemeService class missing"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests (subprocess execution)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_notification_method_removed():
    """showThemeAutoUpdatedNotification method must not exist after the fix."""
    r = _run_node("""
import { readFileSync } from 'fs';
const content = readFileSync(
  'src/vs/workbench/services/themes/browser/workbenchThemeService.ts', 'utf8'
);
// Extract the class body
const classIdx = content.indexOf('class WorkbenchThemeService');
if (classIdx === -1) { console.error('Class not found'); process.exit(1); }
const classBody = content.slice(classIdx);
// Collect all method declarations (private/public/protected + optional static/readonly/async)
const methodRe = /(?:private|public|protected)\\s+(?:static\\s+)?(?:readonly\\s+)?(?:async\\s+)?(\\w+)\\s*\\(/g;
const methods = new Set();
let m;
while ((m = methodRe.exec(classBody)) !== null) methods.add(m[1]);
if (methods.has('showThemeAutoUpdatedNotification')) {
  console.error('showThemeAutoUpdatedNotification method still declared');
  process.exit(1);
}
// Also check no standalone call reference exists (e.g. this.showThemeAutoUpdatedNotification())
const callRe = /this\\.showThemeAutoUpdatedNotification\\s*\\(/;
if (callRe.test(content)) {
  console.error('this.showThemeAutoUpdatedNotification() call still present');
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Method or call still exists: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_notification_key_removed():
    """THEME_AUTO_UPDATED_NOTIFICATION_KEY constant must not exist after the fix."""
    r = _run_node("""
import { readFileSync } from 'fs';
const content = readFileSync(
  'src/vs/workbench/services/themes/browser/workbenchThemeService.ts', 'utf8'
);
// Collect all private static readonly constants declared in the class
const constRe = /private\\s+static\\s+readonly\\s+(\\w+)\\s*=/g;
const constants = new Set();
let m;
while ((m = constRe.exec(content)) !== null) constants.add(m[1]);
if (constants.has('THEME_AUTO_UPDATED_NOTIFICATION_KEY')) {
  console.error('THEME_AUTO_UPDATED_NOTIFICATION_KEY constant still exists');
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Constant still exists: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_notification_call_removed():
    """The call to showThemeAutoUpdatedNotification() must not exist in initialize()."""
    r = _run_node("""
import { readFileSync } from 'fs';
const content = readFileSync(
  'src/vs/workbench/services/themes/browser/workbenchThemeService.ts', 'utf8'
);
// Extract the initialize() method body — starts with 'async initialize(' and ends at next closing brace at column 0
const initRe = /async\\s+initialize\\s*\\([\\s\\S]*?\\n\\t\\}/;
const initMatch = content.match(initRe);
if (!initMatch) {
  console.error('initialize() method not found');
  process.exit(1);
}
const initBody = initMatch[0];
if (initBody.includes('showThemeAutoUpdatedNotification')) {
  console.error('initialize() still references showThemeAutoUpdatedNotification');
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Call still present in initialize(): {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_revert_notification_string_removed():
    """The notification localization string for auto-updated theme must be removed."""
    r = _run_node("""
import { readFileSync } from 'fs';
const content = readFileSync(
  'src/vs/workbench/services/themes/browser/workbenchThemeService.ts', 'utf8'
);
// The localization key 'newDefaultThemeAutoUpdated' should not appear anywhere
if (content.includes('newDefaultThemeAutoUpdated')) {
  console.error('newDefaultThemeAutoUpdated localization key still present');
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Localization key still exists: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_new_default_notification_preserved():
    """showNewDefaultThemeNotification must still exist (not accidentally removed)."""
    content = Path(THEME_FILE).read_text()
    assert "showNewDefaultThemeNotification" in content, \
        "showNewDefaultThemeNotification was incorrectly removed"


# [pr_diff] pass_to_pass
def test_new_theme_notification_key_preserved():
    """NEW_THEME_NOTIFICATION_KEY constant must still exist."""
    content = Path(THEME_FILE).read_text()
    assert "NEW_THEME_NOTIFICATION_KEY" in content, \
        "NEW_THEME_NOTIFICATION_KEY was incorrectly removed"


# [pr_diff] pass_to_pass
def test_initialize_method_intact():
    """The initialize() method must still call showNewDefaultThemeNotification."""
    content = Path(THEME_FILE).read_text()
    # Find the initialize method and verify it still has the new default notification call
    init_match = re.search(
        r'async\s+initialize\b.*?^\t\}',
        content,
        re.DOTALL | re.MULTILINE,
    )
    assert init_match, "Could not find initialize() method"
    init_body = init_match.group(0)
    assert "showNewDefaultThemeNotification" in init_body, \
        "initialize() no longer calls showNewDefaultThemeNotification()"
    assert "showThemeAutoUpdatedNotification" not in init_body, \
        "initialize() still calls showThemeAutoUpdatedNotification()"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:130 @ d4b002af75f1878ead5b608beed470b9ae25b6f8
def test_copyright_header():
    """All files must include Microsoft copyright header."""
    lines = Path(THEME_FILE).read_text().splitlines()
    header_region = "\n".join(lines[:5]).lower()
    assert "microsoft" in header_region, \
        "Missing Microsoft copyright header in first 5 lines of file"


# [agent_config] pass_to_pass — .github/copilot-instructions.md:72 @ d4b002af75f1878ead5b608beed470b9ae25b6f8
def test_tabs_indentation():
    """Use tabs, not spaces for indentation."""
    lines = Path(THEME_FILE).read_text().splitlines()
    # Count lines that start with 4+ spaces but no leading tab (space-indented)
    space_indented = sum(1 for l in lines if l.startswith("    ") and not l.startswith("\t"))
    assert space_indented < 20, \
        f"File has {space_indented} space-indented lines; tabs should be used instead of spaces"


# [agent_config] pass_to_pass — .github/copilot-instructions.md:138 @ d4b002af75f1878ead5b608beed470b9ae25b6f8
def test_no_duplicate_imports():
    """Never duplicate imports. Always reuse existing imports if they are present."""
    import_lines = [
        l.strip() for l in Path(THEME_FILE).read_text().splitlines()
        if l.strip().startswith("import ")
    ]
    duplicates = {l for l in import_lines if import_lines.count(l) > 1}
    assert not duplicates, f"Duplicate import statements found: {duplicates}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — VS Code CI: eslint check
def test_repo_eslint_theme_file():
    """Repo's eslint passes on the modified theme service file (pass_to_pass)."""
    r = subprocess.run(
        ["node", "build/eslint.ts", THEME_FILE],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — VS Code CI: stylelint check
def test_repo_stylelint():
    """Repo's stylelint passes on all CSS files (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "stylelint"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Stylelint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — VS Code CI: eslint on themes directory
def test_repo_eslint_themes_dir():
    """Repo's eslint passes on the themes directory (pass_to_pass)."""
    r = subprocess.run(
        ["node", "build/eslint.ts", "src/vs/workbench/services/themes/"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint on themes dir failed:\n{r.stderr[-500:]}"
