"""
Task: react-devtools-apply-component-filters-on
Repo: facebook/react @ 2c30ebc4e397d57fe75f850e32aa44e353052944
PR:   35587

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"


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
# Fail-to-pass (pr_diff) — behavioral tests via Node subprocess
# ---------------------------------------------------------------------------

def test_initialize_accepts_component_filters():
    """initialize() in backend.js accepts a componentFilters parameter."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const src = readFileSync('packages/react-devtools-core/src/backend.js', 'utf8');
const match = src.match(/export\s+function\s+initialize\s*\(([\s\S]*?)\)\s*(?::\s*\w+)?\s*\{/);
if (!match) {
    console.error('Could not find initialize function');
    process.exit(1);
}
const params = match[1];
if (!/[Cc]omponent[Ff]ilter/.test(params)) {
    console.error('initialize() does not accept a componentFilters parameter');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_install_hook_accepts_component_filters():
    """installHook() in hook.js accepts a componentFilters parameter."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const src = readFileSync('packages/react-devtools-shared/src/hook.js', 'utf8');
const match = src.match(/export\s+function\s+installHook\s*\(([\s\S]*?)\)\s*(?::\s*\w+)?\s*\{/);
if (!match) {
    console.error('Could not find installHook function');
    process.exit(1);
}
const params = match[1];
if (!/[Cc]omponent[Ff]ilter/.test(params)) {
    console.error('installHook() does not accept a componentFilters parameter');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_renderer_attach_accepts_component_filters():
    """Fiber renderer attach() accepts component filters for initial load."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const src = readFileSync('packages/react-devtools-shared/src/backend/fiber/renderer.js', 'utf8');
const match = src.match(/export\s+function\s+attach\s*\(([\s\S]*?)\)\s*(?::\s*\w+)?\s*\{/);
if (!match) {
    console.error('Could not find attach function');
    process.exit(1);
}
const params = match[1];
if (!/[Cc]omponent[Ff]ilter/.test(params)) {
    console.error('attach() does not accept a componentFilters parameter');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_no_global_component_filters_mechanism():
    """__REACT_DEVTOOLS_COMPONENT_FILTERS__ global removed from backend and renderer."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const files = [
    'packages/react-devtools-core/src/backend.js',
    'packages/react-devtools-shared/src/backend/fiber/renderer.js',
];
const violations = [];
for (const f of files) {
    const src = readFileSync(f, 'utf8');
    if (src.includes('__REACT_DEVTOOLS_COMPONENT_FILTERS__')) {
        violations.push(f);
    }
}
if (violations.length > 0) {
    console.error('Still references __REACT_DEVTOOLS_COMPONENT_FILTERS__: ' + violations.join(', '));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_standalone_passes_filters_via_initialize_arg():
    """standalone.js passes component filters as initialize() argument, not as global."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const src = readFileSync('packages/react-devtools-core/src/standalone.js', 'utf8');

// After the fix, standalone should NOT set window.__REACT_DEVTOOLS_COMPONENT_FILTERS__
if (src.includes('__REACT_DEVTOOLS_COMPONENT_FILTERS__')) {
    console.error('standalone.js still uses __REACT_DEVTOOLS_COMPONENT_FILTERS__ global');
    process.exit(1);
}

// The fix passes componentFilters as an argument to initialize():
// ReactDevToolsBackend.initialize(undefined, undefined, undefined, ${componentFiltersString})
if (!/initialize\([^)]*componentFilter/i.test(src)) {
    console.error('standalone.js does not pass componentFilters to initialize()');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_readme_documents_component_filters_parameter():
    """README.md documents the componentFilters parameter for initialize()."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const readme = readFileSync('packages/react-devtools-core/README.md', 'utf8');

if (!/componentFilters/.test(readme)) {
    console.error('README does not document componentFilters parameter');
    process.exit(1);
}

// Check for component filter type documentation (the filter spec table)
if (!/ComponentFilterElementType|ComponentFilterDisplayName/.test(readme)) {
    console.error('README does not document component filter types');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout
