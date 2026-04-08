"""
Task: vscode-theme-auto-updated-notification
Repo: microsoft/vscode @ 9d3144bf84f54ab1e886fca20608dd3ddc296f64

Fix: Add one-time notification for existing users whose color theme
changed because the product default was updated (e.g. Dark Modern to
VS Code Dark). Offers browse themes or revert options.

All checks must pass for reward = 1. Any failure = reward 0.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
TARGET = f"{REPO}/src/vs/workbench/services/themes/browser/workbenchThemeService.ts"

# JS preamble: read file and extract showThemeAutoUpdatedNotification method body
_EXTRACT_METHOD = """
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const methodDefIdx = src.indexOf('private showThemeAutoUpdatedNotification');
if (methodDefIdx === -1) { console.error('FAIL: method definition not found'); process.exit(1); }
let braceStart = src.indexOf('{', methodDefIdx);
let depth = 0;
let bodyEnd = braceStart;
for (let i = braceStart; i < src.length; i++) {
    if (src[i] === '{') depth++;
    if (src[i] === '}') depth--;
    if (depth === 0) { bodyEnd = i; break; }
}
const methodBody = src.substring(braceStart, bodyEnd + 1);
"""


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script), TARGET],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# --- fail_to_pass ---


def test_method_defined():
    """showThemeAutoUpdatedNotification is defined as a private void method."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const match = src.match(/private\\s+showThemeAutoUpdatedNotification\\s*\\(\\s*\\)\\s*:\\s*void/);
if (!match) {
    console.error('FAIL: private showThemeAutoUpdatedNotification(): void not found');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Method not defined: {r.stderr}"
    assert "PASS" in r.stdout


def test_method_called_in_initialize():
    """showThemeAutoUpdatedNotification is invoked during theme service initialization."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
// Find the initialize method
const initIdx = src.indexOf('async initialize(');
if (initIdx === -1) {
    console.error('FAIL: initialize method not found');
    process.exit(1);
}
// Find the opening brace and extract body via brace counting
let braceStart = src.indexOf('{', initIdx);
let depth = 0;
let bodyEnd = braceStart;
for (let i = braceStart; i < src.length; i++) {
    if (src[i] === '{') depth++;
    if (src[i] === '}') depth--;
    if (depth === 0) { bodyEnd = i; break; }
}
const initBody = src.substring(braceStart, bodyEnd + 1);
if (!initBody.includes('this.showThemeAutoUpdatedNotification()')) {
    console.error('FAIL: showThemeAutoUpdatedNotification() not called in initialize');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Not called in initialize: {r.stderr}"
    assert "PASS" in r.stdout


def test_notification_guard_conditions():
    """Method guards: already shown, new user, wrong theme, explicit choice."""
    r = _run_node(_EXTRACT_METHOD + """
const guards = [
    ['getBoolean', 'already shown storage check'],
    ['isNew', 'new user check'],
    ['isDefaultColorTheme', 'explicit theme choice check'],
    ['COLOR_THEME_DARK', 'dark default theme constant'],
    ['COLOR_THEME_LIGHT', 'light default theme constant'],
];
for (const [pattern, desc] of guards) {
    if (!methodBody.includes(pattern)) {
        console.error('FAIL: missing ' + desc + ' (' + pattern + ')');
        process.exit(1);
    }
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Guard conditions missing: {r.stderr}"
    assert "PASS" in r.stdout


def test_revert_calls_setColorTheme():
    """Revert action calls setColorTheme with the previous theme settings ID."""
    r = _run_node(_EXTRACT_METHOD + """
if (!methodBody.includes('setColorTheme')) {
    console.error('FAIL: setColorTheme not called in revert action');
    process.exit(1);
}
if (!methodBody.includes('findThemeBySettingsId')) {
    console.error('FAIL: must look up previous theme by settings ID');
    process.exit(1);
}
if (!methodBody.includes('previousSettingsId') && !methodBody.includes('Dark Modern') && !methodBody.includes('Light Modern')) {
    console.error('FAIL: no previous theme settings ID reference');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Revert logic missing: {r.stderr}"
    assert "PASS" in r.stdout


def test_suppresses_new_theme_notification():
    """On close, stores both auto-updated and new-theme notification keys."""
    r = _run_node(_EXTRACT_METHOD + """
if (!methodBody.includes('THEME_AUTO_UPDATED_NOTIFICATION_KEY')) {
    console.error('FAIL: THEME_AUTO_UPDATED_NOTIFICATION_KEY not stored');
    process.exit(1);
}
if (!methodBody.includes('NEW_THEME_NOTIFICATION_KEY')) {
    console.error('FAIL: NEW_THEME_NOTIFICATION_KEY not stored on close');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Notification key storage missing: {r.stderr}"
    assert "PASS" in r.stdout


# --- pass_to_pass ---


def test_target_file_exists():
    """Target theme service file must exist."""
    assert Path(TARGET).exists()


def test_existing_notification_intact():
    """showNewDefaultThemeNotification must remain unchanged."""
    src = Path(TARGET).read_text()
    assert "showNewDefaultThemeNotification" in src, \
        "Existing notification method should be preserved"
