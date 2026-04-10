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




def test_repo_typescript_syntax_valid():
    """Repo CI: TypeScript file has valid syntax with balanced braces (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "const fs=require('fs');const src=fs.readFileSync('/workspace/vscode/src/vs/workbench/services/themes/browser/workbenchThemeService.ts','utf8');let openCount=0,closeCount=0;for(let i=0;i<src.length;i++){if(src[i]==='{')openCount++;if(src[i]==='}')closeCount++;}if(openCount===0||closeCount===0){console.error('FAIL:File empty');process.exit(1);}if(openCount!==closeCount){console.error('FAIL:Unbalanced braces');process.exit(1);}let parenOpen=0,parenClose=0;for(let i=0;i<src.length;i++){if(src[i]==='(')parenOpen++;if(src[i]===')')parenClose++;}if(parenOpen!==parenClose){console.error('FAIL:Unbalanced parens');process.exit(1);}console.log('PASS');"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed: {r.stderr}"


def test_repo_class_structure_valid():
    """Repo CI: WorkbenchThemeService class structure is valid (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "const fs=require('fs');const src=fs.readFileSync('/workspace/vscode/src/vs/workbench/services/themes/browser/workbenchThemeService.ts','utf8');if(!src.includes('export class WorkbenchThemeService extends Disposable implements IWorkbenchThemeService')){console.error('FAIL:Class declaration');process.exit(1);}if(!src.includes('constructor(')){console.error('FAIL:Missing constructor');process.exit(1);}if(!src.includes('async initialize(')){console.error('FAIL:Missing initialize');process.exit(1);}const required=['setColorTheme','getColorTheme','findThemeBySettingsId'];for(const m of required){if(!src.includes(m)){console.error('FAIL:Missing '+m);process.exit(1);}}console.log('PASS');"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Class structure check failed: {r.stderr}"


def test_repo_imports_complete():
    """Repo CI: Required imports are present (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "const fs=require('fs');const src=fs.readFileSync('/workspace/vscode/src/vs/workbench/services/themes/browser/workbenchThemeService.ts','utf8');const patterns=[{re:/import.*Severity/,name:'Severity'},{re:/import.*INotificationService/,name:'INotificationService'},{re:/import.*ICommandService/,name:'ICommandService'},{re:/import.*IWorkbenchThemeService/,name:'IWorkbenchThemeService'},{re:/import.*Disposable/,name:'Disposable'},{re:/import.*nls/,name:'nls'},{re:/import.*StorageScope/,name:'StorageScope'},{re:/import.*StorageTarget/,name:'StorageTarget'},{re:/import.*IStorageService/,name:'IStorageService'},{re:/import.*IConfigurationService/,name:'IConfigurationService'}];const missing=[];for(const p of patterns){if(!p.re.test(src))missing.push(p.name);}if(missing.length>0){console.error('FAIL:Missing '+missing.join(','));process.exit(1);}console.log('PASS');"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Imports check failed: {r.stderr}"


def test_repo_no_duplicate_definitions():
    """Repo CI: No duplicate method definitions (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "const fs=require('fs');const src=fs.readFileSync('/workspace/vscode/src/vs/workbench/services/themes/browser/workbenchThemeService.ts','utf8');const methods=['showThemeAutoUpdatedNotification','showNewDefaultThemeNotification'];for(const m of methods){if(src.split('private '+m).length>2){console.error('FAIL:Duplicate '+m);process.exit(1);}}console.log('PASS');"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Duplicate check failed: {r.stderr}"


def test_repo_theme_service_integration():
    """Repo CI: Theme service integrates with notification system (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "const fs=require('fs');const src=fs.readFileSync('/workspace/vscode/src/vs/workbench/services/themes/browser/workbenchThemeService.ts','utf8');const required=['notificationService','prompt','Severity','commandService','executeCommand'];for(const item of required){if(!src.includes(item)){console.error('FAIL:Missing '+item);process.exit(1);}}console.log('PASS');"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Integration check failed: {r.stderr}"
