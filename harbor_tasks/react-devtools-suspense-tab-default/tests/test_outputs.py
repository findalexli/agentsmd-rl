"""
Task: react-devtools-suspense-tab-default
Repo: facebook/react @ 8374c2abf13fa803233025192b8d7e87de70b087
PR:   35768

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Node.js script in the repo directory."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_required_files_exist():
    """All five modified files must exist in the repo."""
    for f in [
        "packages/react-devtools-extensions/src/main/index.js",
        "packages/react-devtools-shared/src/backend/agent.js",
        "packages/react-devtools-shared/src/bridge.js",
        "packages/react-devtools-shared/src/devtools/store.js",
        "packages/react-devtools-shared/src/devtools/views/DevTools.js",
    ]:
        assert (Path(REPO) / f).exists(), f"{f} not found"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral checks via Node subprocess
# ---------------------------------------------------------------------------

def test_suspense_panel_created_eagerly():
    """createSuspensePanel() is called directly inside mountReactDevTools, not via event listener."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/react-devtools-extensions/src/main/index.js', 'utf8');

// Find the mountReactDevTools function and extract its body
const funcStart = src.indexOf('function mountReactDevTools');
if (funcStart === -1) {
    console.error('mountReactDevTools function not found');
    process.exit(1);
}

// Scan forward to find the function body (opening brace to closing brace)
let braceDepth = 0;
let bodyStart = -1;
let bodyEnd = -1;
for (let i = funcStart; i < src.length; i++) {
    if (src[i] === '{') {
        if (bodyStart === -1) bodyStart = i;
        braceDepth++;
    } else if (src[i] === '}') {
        braceDepth--;
        if (braceDepth === 0) {
            bodyEnd = i;
            break;
        }
    }
}

if (bodyStart === -1 || bodyEnd === -1) {
    console.error('Could not parse mountReactDevTools function body');
    process.exit(1);
}

const body = src.slice(bodyStart, bodyEnd + 1);

if (!body.includes('createSuspensePanel()')) {
    console.error('createSuspensePanel() not called directly in mountReactDevTools');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_enable_suspense_tab_listener_removed_from_index():
    """The dynamic enableSuspenseTab event listener is removed from index.js."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/react-devtools-extensions/src/main/index.js', 'utf8');

// Check that the store.addListener('enableSuspenseTab', ...) call is gone
const patterns = [
    "store.addListener('enableSuspenseTab'",
    'store.addListener("enableSuspenseTab"',
];

for (const pat of patterns) {
    if (src.includes(pat)) {
        console.error(`enableSuspenseTab listener still present: found "${pat}"`);
        process.exit(1);
    }
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_static_tabs_array_in_devtools():
    """DevTools.js uses a static tabs array with suspenseTab instead of conditional logic."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync(
    'packages/react-devtools-shared/src/devtools/views/DevTools.js', 'utf8'
);

// useIsSuspenseTabEnabled hook must be fully removed
if (src.includes('useIsSuspenseTabEnabled')) {
    console.error('useIsSuspenseTabEnabled hook still present');
    process.exit(1);
}

// Must have a single static tabs array at module scope including suspenseTab
const tabsRegex = /^const\s+tabs\s*=\s*\[([^\]]+)\]/m;
const match = src.match(tabsRegex);
if (!match) {
    console.error('Static module-level "const tabs = [...]" not found');
    process.exit(1);
}

// Evaluate the array contents to verify suspenseTab is included
const items = match[1].split(',').map(s => s.trim());
if (!items.includes('suspenseTab')) {
    console.error('suspenseTab not in static tabs array. Found: ' + items.join(', '));
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_suspense_tab_rendered_unconditionally():
    """Suspense tab JSX is rendered unconditionally — no enableSuspenseTab && guard."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync(
    'packages/react-devtools-shared/src/devtools/views/DevTools.js', 'utf8'
);

// The conditional wrapper {enableSuspenseTab && (...)} must be removed
if (src.includes('enableSuspenseTab &&')) {
    console.error('Conditional enableSuspenseTab && guard still wraps SuspenseTab');
    process.exit(1);
}

// The SuspenseTab component itself must still be present (unconditionally)
if (!src.includes('<SuspenseTab')) {
    console.error('SuspenseTab component not found in DevTools.js');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_enable_suspense_tab_removed_from_bridge():
    """enableSuspenseTab event type is removed from BackendEvents in bridge.js."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/react-devtools-shared/src/bridge.js', 'utf8');

// The enableSuspenseTab event must be removed from the BackendEvents type
if (/enableSuspenseTab\s*:/.test(src)) {
    console.error('enableSuspenseTab event type still present in bridge.js BackendEvents');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_version_check_removed_from_agent():
    """Version-based Suspense tab feature detection is removed from agent.js."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/react-devtools-shared/src/backend/agent.js', 'utf8');

// All enableSuspenseTab references must be gone
if (src.includes('enableSuspenseTab')) {
    console.error('enableSuspenseTab references still in agent.js');
    process.exit(1);
}

// The gte import from ./utils should be removed (was only used for version check)
const utilsImport = src.match(/import\s*\{([^}]+)\}\s*from\s*['"]\.\/utils['"]/);
if (utilsImport && /\bgte\b/.test(utilsImport[1])) {
    console.error('gte still imported from ./utils in agent.js');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_enable_suspense_tab_removed_from_store():
    """enableSuspenseTab listener, getter, and _supportsSuspenseTab field removed from store.js."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/react-devtools-shared/src/devtools/store.js', 'utf8');

const forbidden = [
    'enableSuspenseTab',
    '_supportsSuspenseTab',
    'onEnableSuspenseTab',
    'supportsSuspenseTab',
];

for (const term of forbidden) {
    if (src.includes(term)) {
        console.error(`"${term}" still present in store.js`);
        process.exit(1);
    }
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that should pass on base and fix
# ---------------------------------------------------------------------------

def test_repo_eslint():
    """Repo's ESLint passes on all files (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/eslint.js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_version_check():
    """Repo's version check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/version-check.js"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Version check failed:\n{r.stderr[-500:]}"


def test_repo_print_warnings():
    """Repo's print warnings test passes (pass_to_pass)."""
    r = subprocess.run(
        ["./scripts/ci/test_print_warnings.sh"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Print warnings test failed:\n{r.stderr[-500:]}"


def test_repo_modified_files_syntax():
    """Modified files have valid JavaScript syntax (pass_to_pass)."""
    files_to_check = [
        "packages/react-devtools-extensions/src/main/index.js",
        "packages/react-devtools-shared/src/backend/agent.js",
        "packages/react-devtools-shared/src/bridge.js",
        "packages/react-devtools-shared/src/devtools/store.js",
        "packages/react-devtools-shared/src/devtools/views/DevTools.js",
    ]
    for f in files_to_check:
        path = Path(REPO) / f
        r = subprocess.run(
            ["node", "--check", str(path)],
            capture_output=True, text=True, timeout=10, cwd=REPO,
        )
        assert r.returncode == 0, f"Syntax error in {f}:\n{r.stderr[-500:]}"
