"""
Task: react-devtools-disable-log-dimming-strict
Repo: facebook/react @ ba5b843692519a226347aecfb789d90fcb24b4bc
PR:   35207

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"


def _run_shell(cmd: list, cwd: str = REPO, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )


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
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base AND after fix
# ---------------------------------------------------------------------------

def test_repo_eslint_hook_files():
    """ESLint passes on modified DevTools hook files (pass_to_pass)."""
    files = [
        "packages/react-devtools-shared/src/backend/types.js",
        "packages/react-devtools-shared/src/hook.js",
        "packages/react-devtools-shared/src/devtools/views/Settings/DebuggingSettings.js",
        "packages/react-devtools-extensions/src/contentScripts/hookSettingsInjector.js",
        "packages/react-devtools-inline/src/backend.js",
    ]
    r = _run_shell(["node", "./scripts/tasks/eslint.js"] + files)
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_flow_dom_node():
    """Flow typecheck passes for dom-node renderer (pass_to_pass)."""
    r = _run_shell(["yarn", "flow", "dom-node"])
    assert r.returncode == 0, f"Flow check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using Node.js execution
# ---------------------------------------------------------------------------

def test_hook_settings_type_has_dimming_field():
    """DevToolsHookSettings Flow type includes disableSecondConsoleLogDimmingInStrictMode: boolean."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const content = readFileSync('packages/react-devtools-shared/src/backend/types.js', 'utf8');

// Find the DevToolsHookSettings type definition
const typeMatch = content.match(/DevToolsHookSettings\s*=\s*\{([^}]*)\}/s);
if (!typeMatch) {
    console.error('Could not find DevToolsHookSettings type definition');
    process.exit(1);
}

const typeBody = typeMatch[1];

// Verify the field is declared as boolean
const fieldMatch = typeBody.match(/disableSecondConsoleLogDimmingInStrictMode\s*:\s*boolean/);
if (!fieldMatch) {
    console.error('disableSecondConsoleLogDimmingInStrictMode not found as boolean in DevToolsHookSettings');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Test did not pass: {r.stdout}"


def test_hook_checks_dimming_setting():
    """hook.js uses settings.disableSecondConsoleLogDimmingInStrictMode in conditional to gate dimming."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const content = readFileSync('packages/react-devtools-shared/src/hook.js', 'utf8');

// The setting must be accessed on the settings object in conditional checks
if (!content.includes('settings.disableSecondConsoleLogDimmingInStrictMode')) {
    console.error('hook.js does not access settings.disableSecondConsoleLogDimmingInStrictMode');
    process.exit(1);
}

// Count references — need at least 3: one default value + two conditional checks
// (there are two separate console patching paths in installHook)
const refs = (content.match(/disableSecondConsoleLogDimmingInStrictMode/g) || []);
if (refs.length < 3) {
    console.error('Expected >= 3 references, found ' + refs.length);
    process.exit(1);
}

// Verify the setting appears in a conditional that gates dimming behavior:
// it should be near 'originalMethod' (the non-dimmed path)
const lines = content.split('\n');
let foundConditionalGate = false;
for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('disableSecondConsoleLogDimmingInStrictMode') &&
        (lines[i].includes('if') || (i > 0 && lines[i-1].includes('if')))) {
        const nearby = lines.slice(i, Math.min(lines.length, i + 8)).join('\n');
        if (nearby.includes('originalMethod')) {
            foundConditionalGate = true;
            break;
        }
    }
}

if (!foundConditionalGate) {
    console.error('No conditional gate connects the setting to dimming/originalMethod');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Test did not pass: {r.stdout}"


def test_hook_default_settings_include_dimming():
    """Extract and evaluate default settings object from hook.js — field exists with default false."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const content = readFileSync('packages/react-devtools-shared/src/hook.js', 'utf8');

// Extract the default settings object literal (contains appendComponentStack)
const match = content.match(/settings\s*=\s*\{([^}]*appendComponentStack[^}]*)\}/s);
if (!match) {
    console.error('Could not find default settings object in hook.js');
    process.exit(1);
}

// Evaluate the settings object as JavaScript
const objSource = 'const settings = {' + match[1] + '}; return settings;';
let settings;
try {
    settings = new Function(objSource)();
} catch (e) {
    console.error('Failed to evaluate settings object: ' + e.message);
    process.exit(1);
}

// Verify the field exists and defaults to false
if (!('disableSecondConsoleLogDimmingInStrictMode' in settings)) {
    console.error('disableSecondConsoleLogDimmingInStrictMode missing from default settings');
    process.exit(1);
}
if (settings.disableSecondConsoleLogDimmingInStrictMode !== false) {
    console.error('Expected default false, got: ' + settings.disableSecondConsoleLogDimmingInStrictMode);
    process.exit(1);
}

console.log(JSON.stringify(settings));
console.log('PASS');
""")
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Test did not pass: {r.stdout}"


def test_debugging_settings_ui_has_dimming_control():
    """DebuggingSettings component manages state for the dimming setting and passes it to hook settings."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const content = readFileSync(
    'packages/react-devtools-shared/src/devtools/views/Settings/DebuggingSettings.js',
    'utf8'
);

// Must reference the setting
if (!content.includes('disableSecondConsoleLogDimmingInStrictMode')) {
    console.error('DebuggingSettings does not reference disableSecondConsoleLogDimmingInStrictMode');
    process.exit(1);
}

// Must have a setter from useState
if (!content.includes('setDisableSecondConsoleLogDimmingInStrictMode')) {
    console.error('Missing setter setDisableSecondConsoleLogDimmingInStrictMode');
    process.exit(1);
}

// The setting must be included in the updateHookSettings call arguments
// It should appear in the object passed to updateHookSettings
const updateBlock = content.match(/updateHookSettings\s*\(\s*\{([^}]*)\}/s);
if (!updateBlock || !updateBlock[1].includes('disableSecondConsoleLogDimmingInStrictMode')) {
    console.error('disableSecondConsoleLogDimmingInStrictMode not passed to updateHookSettings');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Test did not pass: {r.stdout}"


def test_hook_settings_injector_validates_dimming():
    """hookSettingsInjector validates disableSecondConsoleLogDimmingInStrictMode as boolean, defaults to false."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const content = readFileSync(
    'packages/react-devtools-extensions/src/contentScripts/hookSettingsInjector.js',
    'utf8'
);

// Must validate typeof as boolean
if (!content.includes("typeof settings.disableSecondConsoleLogDimmingInStrictMode")) {
    console.error('No typeof check for disableSecondConsoleLogDimmingInStrictMode');
    process.exit(1);
}

// Must set default to false when validation fails
if (!content.includes('disableSecondConsoleLogDimmingInStrictMode = false')) {
    console.error('No default false assignment for disableSecondConsoleLogDimmingInStrictMode');
    process.exit(1);
}

// Simulate the validation logic to verify correctness
let settings = {};
if (typeof settings.disableSecondConsoleLogDimmingInStrictMode !== 'boolean') {
    settings.disableSecondConsoleLogDimmingInStrictMode = false;
}
if (settings.disableSecondConsoleLogDimmingInStrictMode !== false) {
    console.error('Validation logic: missing field should default to false');
    process.exit(1);
}

// Valid boolean should not be overwritten
settings = { disableSecondConsoleLogDimmingInStrictMode: true };
if (typeof settings.disableSecondConsoleLogDimmingInStrictMode !== 'boolean') {
    settings.disableSecondConsoleLogDimmingInStrictMode = false;
}
if (settings.disableSecondConsoleLogDimmingInStrictMode !== true) {
    console.error('Validation logic: valid boolean should be preserved');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Test did not pass: {r.stdout}"


def test_inline_backend_passes_dimming_setting():
    """react-devtools-inline backend.js destructures setting and assigns it to window global."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const content = readFileSync('packages/react-devtools-inline/src/backend.js', 'utf8');

// Must destructure the setting from data
if (!content.includes('disableSecondConsoleLogDimmingInStrictMode')) {
    console.error('backend.js does not reference disableSecondConsoleLogDimmingInStrictMode');
    process.exit(1);
}

// Must set the window global
const globalName = '__REACT_DEVTOOLS_DISABLE_SECOND_CONSOLE_LOG_DIMMING_IN_STRICT_MODE__';
if (!content.includes(globalName)) {
    console.error('backend.js does not set window global ' + globalName);
    process.exit(1);
}

// Verify the assignment connects the global to the setting value
const lines = content.split('\n');
let foundAssignment = false;
for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes(globalName)) {
        const nearby = lines.slice(i, Math.min(lines.length, i + 3)).join(' ');
        if (nearby.includes('disableSecondConsoleLogDimmingInStrictMode')) {
            foundAssignment = true;
            break;
        }
    }
}

if (!foundAssignment) {
    console.error('No assignment connecting ' + globalName + ' to the setting');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Test did not pass: {r.stdout}"
