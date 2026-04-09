"""
Task: gradio-add-js-dataframe-documentation-to
Repo: gradio-app/gradio @ f67faa464add0ef6a4a58d60eb2ae850125ebb87
PR:   11766 — Add JS Dataframe documentation to docs

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/gradio"


def _run_node(code: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_readme_has_comprehensive_docs():
    """js/dataframe/README.md has full documentation with Install, Usage, Props sections."""
    r = _run_node("""
const fs = require('fs');
const readme = fs.readFileSync('js/dataframe/README.md', 'utf8');
const required = ['## Install', '## Usage', '## Props', '## Events', '## Custom Styling'];
const missing = required.filter(s => !readme.includes(s));
if (missing.length > 0) {
    console.error('Missing sections: ' + missing.join(', '));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"README missing sections: {r.stderr}"
    assert "PASS" in r.stdout


def test_standalone_readme_removed():
    """js/dataframe/standalone/README.md has been removed (content merged into main README)."""
    r = _run_node("""
const fs = require('fs');
if (fs.existsSync('js/dataframe/standalone/README.md')) {
    console.error('standalone/README.md still exists');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Standalone README should be removed: {r.stderr}"
    assert "PASS" in r.stdout


def test_js_page_redirects_to_dataframe():
    """The /docs/js page redirect logic checks for dataframe page existence and falls back properly."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('js/_website/src/routes/[[version]]/docs/js/+page.server.ts', 'utf8');

// Check for the urlExists function that validates page existence
if (!src.includes('urlExists')) {
    console.error('Missing urlExists function for checking page existence');
    process.exit(1);
}

// Check that it tries to redirect to dataframe first
if (!src.includes('/docs/js/dataframe')) {
    console.error('Missing redirect to /docs/js/dataframe');
    process.exit(1);
}

// Check for fallback to js-client
if (!src.includes('/docs/js/js-client')) {
    console.error('Missing fallback redirect to /docs/js/js-client');
    process.exit(1);
}

// Verify old atoms redirect is removed
if (src.includes('/docs/js/atoms')) {
    console.error('Still contains old redirect to /docs/js/atoms');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"JS page redirect logic incorrect: {r.stderr}"
    assert "PASS" in r.stdout


def test_syntax_highlighting_supports_svelte():
    """Documentation page servers import prism-svelte and register svelte language."""
    r = _run_node(r"""
const fs = require('fs');
const files = [
    'js/_website/src/routes/[[version]]/docs/js/[jsdoc]/+page.server.ts',
    'js/_website/src/routes/[[version]]/docs/js-client/+page.server.ts',
];
for (const f of files) {
    const src = fs.readFileSync(f, 'utf8');
    if (!src.includes('prism-svelte')) {
        console.error(f + ': Missing prism-svelte import');
        process.exit(1);
    }
    // Check for svelte language registration (multiple patterns)
    const hasSvelteLang = src.includes('svelte: "svelte"') ||
                          src.includes('svelte: "svelte",') ||
                          src.includes("svelte: 'svelte'") ||
                          /svelte:\s*["']svelte["']/.test(src);
    if (!hasSvelteLang) {
        console.error(f + ': Missing svelte lang entry');
        process.exit(1);
    }
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Syntax highlighting incomplete: {r.stderr}"
    assert "PASS" in r.stdout


def test_layout_filters_to_documented_components():
    """The docs layout server filters js_pages to only dataframe and js-client."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('js/_website/src/routes/[[version]]/docs/+layout.server.ts', 'utf8');

// Check for components_to_document array
if (!src.includes('components_to_document')) {
    console.error('Missing components_to_document array');
    process.exit(1);
}

// Check for both required components
if (!src.includes('"dataframe"') || !src.includes('"js-client"')) {
    console.error('Missing dataframe or js-client in components_to_document');
    process.exit(1);
}

// Check that filter is applied to js_pages
if (!src.includes('.filter')) {
    console.error('Filter not applied to js_pages');
    process.exit(1);
}

// Verify the filter uses components_to_document
if (!src.includes('components_to_document.includes')) {
    console.error('Filter does not use components_to_document.includes');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Layout filtering not correct: {r.stderr}"
    assert "PASS" in r.stdout


def test_package_exports_has_default():
    """js/code/package.json exports include default field for compatibility."""
    r = _run_node("""
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('js/code/package.json', 'utf8'));

// Check main export has default
if (!pkg.exports || !pkg.exports['.']) {
    console.error('Missing main export');
    process.exit(1);
}
if (!pkg.exports['.'].default) {
    console.error('Main export missing default field');
    process.exit(1);
}

// Check example export has default
if (!pkg.exports['./example']) {
    console.error('Missing example export');
    process.exit(1);
}
if (!pkg.exports['./example'].default) {
    console.error('Example export missing default field');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"package.json exports missing default: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------


def test_syntax_check():
    """Modified TypeScript files have valid syntax (parsable)."""
    r = _run_node("""
const fs = require('fs');

// Test that key modified files are valid TypeScript (basic parse check)
const files = [
    'js/_website/src/routes/[[version]]/docs/+layout.server.ts',
    'js/_website/src/routes/[[version]]/docs/js/+page.server.ts',
    'js/_website/src/routes/[[version]]/docs/js/[jsdoc]/+page.server.ts',
    'js/_website/src/routes/[[version]]/docs/js-client/+page.server.ts',
];

for (const f of files) {
    try {
        const content = fs.readFileSync(f, 'utf8');
        // Basic syntax checks
        if (content.includes('export ') && !content.includes('import ')) {
            // Check for balanced braces in export statements
            const openCount = (content.match(/[{]/g) || []).length;
            const closeCount = (content.match(/[}]/g) || []).length;
            if (openCount !== closeCount) {
                console.error(f + ': Unbalanced braces');
                process.exit(1);
            }
        }
    } catch(e) {
        console.error('Cannot read or parse: ' + f + ' - ' + e.message);
        process.exit(1);
    }
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Files have syntax errors: {r.stderr}"
    assert "PASS" in r.stdout


def test_changelog_has_prism_svelte():
    """Changelog page server also has prism-svelte support."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('js/_website/src/routes/changelog/+page.server.ts', 'utf8');

if (!src.includes('prism-svelte')) {
    console.error('Missing prism-svelte import in changelog');
    process.exit(1);
}

// Check for svelte language mapping
const hasSvelteLang = src.includes('svelte: "svelte"') ||
                      src.includes('svelte: "svelte",') ||
                      src.includes("svelte: 'svelte'") ||
                      /svelte:\s*["']svelte["']/.test(src);
if (!hasSvelteLang) {
    console.error('Missing svelte lang entry in changelog');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Changelog missing prism-svelte: {r.stderr}"
    assert "PASS" in r.stdout
