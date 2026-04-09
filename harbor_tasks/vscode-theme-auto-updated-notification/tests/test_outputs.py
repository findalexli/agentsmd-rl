"""
Task: vscode-theme-auto-updated-notification
Repo: microsoft/vscode @ 9d3144bf84f54ab1e886fca20608dd3ddc296f64

Fix: Add one-time notification for existing users whose color theme
changed because the product default was updated (e.g. Dark Modern to
VS Code: Dark). Offers browse themes or revert options.

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
    script = Path(REPO) / "_eval_tmp.cjs"  # Use .cjs to force CommonJS mode
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


def test_target_file_valid_typescript():
    """Target file has valid TypeScript structure (pass_to_pass)."""
    src = Path(TARGET).read_text()
    # Basic structure checks
    assert "class WorkbenchThemeService" in src, "Missing WorkbenchThemeService class"
    assert "export class" in src or "class WorkbenchThemeService" in src, "Missing class export"
    # Check for balanced braces
    open_count = src.count('{')
    close_count = src.count('}')
    assert open_count > 0 and close_count > 0, "File appears to be empty or malformed"
    assert open_count == close_count, f"Unbalanced braces: {open_count} open vs {close_count} close"


def test_no_duplicate_method_definitions():
    """No duplicate definitions of showThemeAutoUpdatedNotification (pass_to_pass)."""
    src = Path(TARGET).read_text()
    # Count occurrences of the method definition
    count = src.count("private showThemeAutoUpdatedNotification")
    assert count <= 1, f"Method defined {count} times, expected 0 or 1"


def test_initialize_method_exists():
    """Theme service has an initialize method (pass_to_pass)."""
    src = Path(TARGET).read_text()
    assert "async initialize(" in src, "Missing initialize method"


def test_workbench_theme_service_class_valid():
    """WorkbenchThemeService class is well-formed (pass_to_pass)."""
    src = Path(TARGET).read_text()
    # Check class declaration
    assert "export class WorkbenchThemeService extends Disposable implements IWorkbenchThemeService" in src
    # Check constructor exists
    assert "constructor(" in src
    # Check the class is properly closed (no structural issues)
    open_braces = src.count('{')
    close_braces = src.count('}')
    assert open_braces > 50, "File appears truncated or malformed"
    assert open_braces == close_braces, f"Unbalanced braces: {open_braces} open vs {close_braces} close"


def test_existing_notification_method_intact():
    """Existing showNewDefaultThemeNotification method is preserved (pass_to_pass)."""
    src = Path(TARGET).read_text()
    # Check the existing method is present
    assert "private showNewDefaultThemeNotification(): void" in src, \
        "Existing showNewDefaultThemeNotification method missing"
    # Check the notification key constant
    assert "NEW_THEME_NOTIFICATION_KEY" in src, \
        "NEW_THEME_NOTIFICATION_KEY constant missing"


def test_required_imports_present():
    """Required imports for theme notifications are present (pass_to_pass)."""
    src = Path(TARGET).read_text()
    # Check for notification-related imports
    assert "Severity" in src, "Severity import missing for notifications"
    assert "INotificationService" in src, "INotificationService import missing"
    assert "ICommandService" in src, "ICommandService import missing"
    # Check nls for localization
    assert "nls.localize" in src, "nls.localize for localization missing"


def test_initialize_method_calls_notification():
    """Initialize method calls showNewDefaultThemeNotification (pass_to_pass - verifies hook point exists)."""
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
if (!initBody.includes('showNewDefaultThemeNotification()')) {
    console.error('FAIL: showNewDefaultThemeNotification() not called in initialize');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Notification call missing in initialize: {r.stderr}"
    assert "PASS" in r.stdout


# --- Additional repo_tests pass_to_pass checks ---


def test_repo_no_syntax_errors():
    """Repo target file has no obvious syntax errors - structural pass_to_pass check."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
// Check for balanced braces
let openCount = 0;
let closeCount = 0;
for (let i = 0; i < src.length; i++) {
    if (src[i] === '{') openCount++;
    if (src[i] === '}') closeCount++;
}
if (openCount === 0 || closeCount === 0) {
    console.error('FAIL: File appears empty or has no code blocks');
    process.exit(1);
}
if (openCount !== closeCount) {
    console.error('FAIL: Unbalanced braces - open: ' + openCount + ', close: ' + closeCount);
    process.exit(1);
}
// Check for basic TypeScript structure
if (!src.includes('export class WorkbenchThemeService')) {
    console.error('FAIL: Missing WorkbenchThemeService class export');
    process.exit(1);
}
// Check for common structural issues
const parenOpen = (src.match(/\\(/g) || []).length;
const parenClose = (src.match(/\\)/g) || []).length;
if (parenOpen !== parenClose) {
    console.error('FAIL: Unbalanced parentheses - open: ' + parenOpen + ', close: ' + parenClose);
    process.exit(1);
}
console.log('PASS: File structure valid - ' + openCount + ' braces balanced, ' + parenOpen + ' parens balanced');
""")
    assert r.returncode == 0, f"Syntax error check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_types_basic():
    """Basic TypeScript structure validation - repo pass_to_pass check."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
// Check class structure
const classMatch = src.match(/export class WorkbenchThemeService extends Disposable implements IWorkbenchThemeService/);
if (!classMatch) {
    console.error('FAIL: WorkbenchThemeService class declaration invalid');
    process.exit(1);
}
// Check constructor exists
if (!src.includes('constructor(')) {
    console.error('FAIL: Missing constructor');
    process.exit(1);
}
// Check initialize method exists
if (!src.includes('async initialize(')) {
    console.error('FAIL: Missing initialize method');
    process.exit(1);
}
// Check for common TypeScript patterns that indicate valid code
const hasImports = src.match(/^import\\s+/m);
const hasExports = src.match(/^export\\s+/m);
if (!hasImports) {
    console.error('FAIL: No imports found');
    process.exit(1);
}
if (!hasExports) {
    console.error('FAIL: No exports found');
    process.exit(1);
}
console.log('PASS: TypeScript structure valid');
""")
    assert r.returncode == 0, f"TypeScript structure check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_imports_valid():
    """All required imports for workbench theme service - repo pass_to_pass check."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
// Extract imports section (everything before first class/function export)
const importSection = src.substring(0, src.indexOf('export class'));
const requiredImports = [
    { pattern: /import.*Severity/, name: 'Severity' },
    { pattern: /import.*INotificationService/, name: 'INotificationService' },
    { pattern: /import.*ICommandService/, name: 'ICommandService' },
    { pattern: /import.*IWorkbenchThemeService/, name: 'IWorkbenchThemeService' },
    { pattern: /import.*Disposable/, name: 'Disposable' },
    { pattern: /import.*nls/, name: 'nls localization' },
    { pattern: /import.*StorageScope/, name: 'StorageScope' },
    { pattern: /import.*StorageTarget/, name: 'StorageTarget' }
];
const missing = [];
for (const imp of requiredImports) {
    if (!imp.pattern.test(importSection)) {
        missing.push(imp.name);
    }
}
if (missing.length > 0) {
    console.error('FAIL: Missing required imports: ' + missing.join(', '));
    process.exit(1);
}
console.log('PASS: All required imports present');
""")
    assert r.returncode == 0, f"Imports validation failed: {r.stderr}"
    assert "PASS" in r.stdout
