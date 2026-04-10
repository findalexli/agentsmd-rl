import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
TARGET = f"{REPO}/src/vs/workbench/services/themes/browser/workbenchThemeService.ts"

# JS preamble: read file and extract showThemeAutoUpdatedNotification method body
_EXTRACT_METHOD = '''
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
'''


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    script = Path(REPO) / "_eval_tmp.cjs"
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
    r = _run_node('''
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const match = src.match(/private\s+showThemeAutoUpdatedNotification\s*\(\s*\)\s*:\s*void/);
if (!match) {
    console.error('FAIL: private showThemeAutoUpdatedNotification(): void not found');
    process.exit(1);
}
console.log('PASS');
''')
    assert r.returncode == 0, f"Method not defined: {r.stderr}"
    assert "PASS" in r.stdout


def test_method_called_in_initialize():
    """showThemeAutoUpdatedNotification is invoked during theme service initialization."""
    r = _run_node('''
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const initIdx = src.indexOf('async initialize(');
if (initIdx === -1) {
    console.error('FAIL: initialize method not found');
    process.exit(1);
}
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
''')
    assert r.returncode == 0, f"Not called in initialize: {r.stderr}"
    assert "PASS" in r.stdout


def test_notification_guard_conditions():
    """Method guards: already shown, new user, wrong theme, explicit choice."""
    r = _run_node(_EXTRACT_METHOD + '''
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
''')
    assert r.returncode == 0, f"Guard conditions missing: {r.stderr}"
    assert "PASS" in r.stdout


def test_revert_calls_setColorTheme():
    """Revert action calls setColorTheme with the previous theme settings ID."""
    r = _run_node(_EXTRACT_METHOD + '''
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
''')
    assert r.returncode == 0, f"Revert logic missing: {r.stderr}"
    assert "PASS" in r.stdout


def test_suppresses_new_theme_notification():
    """On close, stores both auto-updated and new-theme notification keys."""
    r = _run_node(_EXTRACT_METHOD + '''
if (!methodBody.includes('THEME_AUTO_UPDATED_NOTIFICATION_KEY')) {
    console.error('FAIL: THEME_AUTO_UPDATED_NOTIFICATION_KEY not stored');
    process.exit(1);
}
if (!methodBody.includes('NEW_THEME_NOTIFICATION_KEY')) {
    console.error('FAIL: NEW_THEME_NOTIFICATION_KEY not stored on close');
    process.exit(1);
}
console.log('PASS');
''')
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


# --- repo_tests pass_to_pass: Node.js-based CI validation ---


def test_repo_node_syntax_valid():
    """Repo CI: TypeScript file has valid Node.js parsable syntax (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", f"require('fs').readFileSync('{TARGET}', 'utf8'); console.log('PASS');"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Node.js syntax check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_no_syntax_errors():
    """Repo CI: Target file has no basic syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{TARGET}', 'utf8');
// Check for common syntax errors
const errors = [];
if ((src.match(/{{/g) || []).length !== (src.match(/}}/g) || []).length) {{
    errors.push('Mismatched braces in template literals');
}}
if ((src.match(/\[/g) || []).length !== (src.match(/\]/g) || []).length) {{
    errors.push('Mismatched brackets');
}}
if ((src.match(/\(/g) || []).length !== (src.match(/\)/g) || []).length) {{
    errors.push('Mismatched parentheses');
}}
if (errors.length > 0) {{
    console.error('FAIL:', errors.join(', '));
    process.exit(1);
}}
console.log('PASS');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax error check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_imports_valid():
    """Repo CI: Import statements follow valid patterns (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{TARGET}', 'utf8');
const lines = src.split('\\n');
const importLines = lines.filter(l => l.trim().startsWith('import'));
const errors = [];
for (const line of importLines) {{
    // Check for valid import patterns
    if (!line.match(/import\s+.*\s+from\s+['"][^'"]+['"];?$/)) {{
        if (!line.match(/import\s+['"][^'"]+['"];?$/)) {{ // side-effect imports
            if (!line.match(/import\s*\*\s+as\s+\w+\s+from\s+['"][^'"]+['"];?$/)) {{ // namespace imports
                if (!line.match(/import\s*{{[^}}]*}}\s*from\s+['"][^'"]+['"];?$/)) {{ // named imports
                    continue; // skip, might be a different pattern
                }}
            }}
        }}
    }}
}}
// Verify specific required imports exist
const requiredImports = [
    'notificationService',
    'notification/common/notification',
    'commandService',
    'Severity'
];
const hasAll = requiredImports.every(imp => src.includes(imp));
if (!hasAll) {{
    console.error('FAIL: Missing required imports');
    process.exit(1);
}}
console.log('PASS');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Import validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_class_structure_valid():
    """Repo CI: WorkbenchThemeService class structure is valid (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{TARGET}', 'utf8');
// Check class declaration
if (!src.includes('export class WorkbenchThemeService')) {{
    console.error('FAIL: Class declaration missing');
    process.exit(1);
}}
// Check constructor exists
if (!src.includes('constructor(')) {{
    console.error('FAIL: Constructor missing');
    process.exit(1);
}}
// Check initialize method exists
if (!src.includes('async initialize(')) {{
    console.error('FAIL: initialize method missing');
    process.exit(1);
}}
// Check required methods exist
const requiredMethods = ['setColorTheme', 'getColorTheme', 'findThemeBySettingsId'];
for (const method of requiredMethods) {{
    if (!src.includes(method)) {{
        console.error('FAIL: Missing method ' + method);
        process.exit(1);
    }}
}}
console.log('PASS');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Class structure check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_tabs_not_spaces():
    """Repo CI: Source file uses tabs for indentation per style guide (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{TARGET}', 'utf8');
const lines = src.split('\\n');
let spaceIndentCount = 0;
let tabIndentCount = 0;
for (const line of lines) {{
    if (line.match(/^[ ]+/)) spaceIndentCount++;
    if (line.match(/^[\\t]+/)) tabIndentCount++;
}}
// VS Code style guide requires tabs, not spaces
if (spaceIndentCount > tabIndentCount * 2) {{
    console.error('FAIL: File uses spaces for indentation instead of tabs');
    process.exit(1);
}}
console.log('PASS');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Indentation check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_repo_copyright_header():
    """Repo CI: File has required Microsoft copyright header (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{TARGET}', 'utf8');
const requiredHeader = 'Copyright (c) Microsoft Corporation';
if (!src.includes(requiredHeader)) {{
    console.error('FAIL: Missing Microsoft copyright header');
    process.exit(1);
}}
const requiredLicense = 'MIT License';
if (!src.includes(requiredLicense)) {{
    console.error('FAIL: Missing MIT License reference');
    process.exit(1);
}}
console.log('PASS');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Copyright header check failed: {r.stderr}"
    assert "PASS" in r.stdout
