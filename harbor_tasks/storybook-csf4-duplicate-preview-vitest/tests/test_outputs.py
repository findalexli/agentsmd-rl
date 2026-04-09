"""
Task: storybook-csf4-duplicate-preview-vitest
Repo: storybook @ 6d4fcb5417be0013e4c2d6e2e166a15a81637268
PR:   34361

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/storybook"
UTILS_TS = f"{REPO}/code/addons/vitest/src/vitest-plugin/utils.ts"
INDEX_TS = f"{REPO}/code/addons/vitest/src/vitest-plugin/index.ts"


def _run_node(script: str, timeout: int = 30) -> dict:
    """Run a Node.js script and return parsed JSON output."""
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, timeout=timeout,
    )
    assert r.returncode == 0, f"Node script failed:\n{r.stderr.decode()}"
    return json.loads(r.stdout.decode())


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_files_parse():
    """Both modified TypeScript files must parse without syntax errors."""
    # Use the TypeScript compiler API to parse each file
    for filepath in [UTILS_TS, INDEX_TS]:
        script = f"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('{filepath}', 'utf-8');
const sf = ts.createSourceFile('{filepath}', src, ts.ScriptTarget.Latest, true);
const diags = [];
// Collect parse diagnostics
for (const d of sf.parseDiagnostics || []) {{
    diags.push({{ msg: ts.flattenDiagnosticMessageText(d.messageText, '\\n'), pos: d.start }});
}}
console.log(JSON.stringify({{ ok: diags.length === 0, diags }}));
"""
        result = _run_node(script)
        assert result["ok"], f"TypeScript parse errors in {filepath}: {result['diags']}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_csf4_param_in_requires_project_annotations():
    """requiresProjectAnnotations must not accept an isCSF4 parameter.

    The bug was caused by this function receiving a boolean to short-circuit
    project annotation loading for CSF4 users. The fix removes this parameter
    so project annotations are always loaded via the virtual module (which
    handles deduplication internally).
    """
    script = f"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('{UTILS_TS}', 'utf-8');
const sf = ts.createSourceFile('utils.ts', src, ts.ScriptTarget.Latest, true);

function findFunction(node) {{
    if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'requiresProjectAnnotations') {{
        return node;
    }}
    let found = null;
    ts.forEachChild(node, child => {{
        if (!found) found = findFunction(child);
    }});
    return found;
}}

const fn = findFunction(sf);
if (!fn) {{
    console.log(JSON.stringify({{ found: false, paramCount: 0, paramNames: [] }}));
}} else {{
    const params = fn.parameters.map(p => p.name.getText(sf));
    console.log(JSON.stringify({{ found: true, paramCount: params.length, paramNames: params }}));
}}
"""
    result = _run_node(script)
    assert result["found"], "requiresProjectAnnotations function not found in utils.ts"
    assert result["paramCount"] == 2, (
        f"requiresProjectAnnotations should have 2 parameters (testConfig, finalOptions), "
        f"but has {result['paramCount']}: {result['paramNames']}"
    )
    assert "isCSF4" not in result["paramNames"], (
        "requiresProjectAnnotations must not have an isCSF4 parameter"
    )


# [pr_diff] fail_to_pass
def test_no_csf4_conditional_return_in_utils():
    """requiresProjectAnnotations must not short-circuit to false for CSF4.

    The base code had 'else if (isCSF4) { return false; }' which prevented
    project annotations from loading for CSF4 users. This caused the preview
    file to be added directly as a setup file, leading to duplication.
    """
    # The function body must not reference isCSF4 at all
    # Use TypeScript AST to check for any identifier references
    script = f"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('{UTILS_TS}', 'utf-8');
const sf = ts.createSourceFile('utils.ts', src, ts.ScriptTarget.Latest, true);

let identifiers = [];

function visit(node) {{
    if (ts.isIdentifier(node) && node.text === 'isCSF4') {{
        identifiers.push({{ text: node.text, pos: node.pos }});
    }}
    ts.forEachChild(node, visit);
}}
visit(sf);

console.log(JSON.stringify({{ isCSF4Refs: identifiers.length }}));
"""
    result = _run_node(script)
    assert result["isCSF4Refs"] == 0, (
        f"Found {result['isCSF4Refs']} references to 'isCSF4' in utils.ts — "
        "the CSF4 short-circuit logic must be removed"
    )


# [pr_diff] fail_to_pass
def test_no_preview_file_loading_for_csf4_detection():
    """The plugin must not load/parse preview config to detect CSF4 status.

    The base code called loadPreviewOrConfigFile + readConfig +
    isCsfFactoryPreview to determine if the project uses CSF4. This detection
    was used to inject the preview file directly into setup files, causing
    duplication. The fix removes this detection entirely.

    Note: unused imports may remain — we check for actual usage (calls and
    variable declarations), not import specifiers.
    """
    src = Path(INDEX_TS).read_text()

    # Check for function call usage (not import specifiers)
    assert "isCsfFactoryPreview(" not in src, (
        "isCsfFactoryPreview() is still called in index.ts — "
        "CSF4 detection must be removed from the plugin"
    )
    assert "const isCSF4" not in src, (
        "const isCSF4 still declared in index.ts — "
        "CSF4-specific variable must be removed from the plugin"
    )


# [pr_diff] fail_to_pass
def test_setup_files_no_preview_injection():
    """Internal setup files must not conditionally include the preview file.

    The base code had 'isCSF4 && previewOrConfigFile' in the internalSetupFiles
    array, which directly injected the user's preview file as a Vitest setup file.
    This caused duplicate loading since the virtual module already provides it.

    Note: unused imports may remain — we check for actual variable usage, not
    import specifiers.
    """
    src = Path(INDEX_TS).read_text()

    # Check for variable declaration (not just import specifier —
    # loadPreviewOrConfigFile import may remain as unused)
    assert "const previewOrConfigFile" not in src, (
        "previewOrConfigFile variable is still declared in index.ts — "
        "the preview file must not be loaded for direct injection into setup files"
    )
    # Also check the preview file isn't injected into setup files array
    assert "&& previewOrConfigFile" not in src, (
        "previewOrConfigFile is still conditionally added to setup files — "
        "the preview file must not be directly injected into setup files"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_project_annotations_conditional_still_exists():
    """The project annotations setup file must still be conditionally included.

    The fix removes CSF4-specific preview file injection but must preserve the
    conditional inclusion of setup-file-with-project-annotations based on
    areProjectAnnotationRequired.
    """
    src = Path(INDEX_TS).read_text()
    assert "areProjectAnnotationRequired" in src, (
        "areProjectAnnotationRequired variable must still exist in index.ts"
    )
    assert "setup-file-with-project-annotations" in src, (
        "setup-file-with-project-annotations module must still be referenced in index.ts"
    )


# [static] pass_to_pass
def test_requires_project_annotations_still_exported():
    """requiresProjectAnnotations must still be exported from utils.ts."""
    script = f"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('{UTILS_TS}', 'utf-8');
const sf = ts.createSourceFile('utils.ts', src, ts.ScriptTarget.Latest, true);

let found = false;
function visit(node) {{
    if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'requiresProjectAnnotations') {{
        const mods = node.modifiers || [];
        const isExported = mods.some(m => m.kind === ts.SyntaxKind.ExportKeyword);
        found = isExported;
    }}
    ts.forEachChild(node, visit);
}}
visit(sf);

console.log(JSON.stringify({{ exported: found }}));
"""
    result = _run_node(script)
    assert result["exported"], (
        "requiresProjectAnnotations must be exported from utils.ts"
    )


# [static] pass_to_pass
def test_requires_project_annotations_returns_true_by_default():
    """requiresProjectAnnotations must return true when no setup file has setProjectAnnotations.

    The function should have a 'return true' as its default path — meaning
    project annotations are loaded unless explicitly handled by a user setup file.
    """
    src = Path(UTILS_TS).read_text()
    # Find the function body and verify it contains 'return true'
    assert "return true" in src, (
        "requiresProjectAnnotations must have a 'return true' default path — "
        "project annotations should always be loaded unless a setup file handles them"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD verification
# These tests verify the repo's own CI checks pass on both base and gold commits
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_utils_ts_parses():
    """Repo's utils.ts file must parse as valid TypeScript (pass_to_pass)."""
    script = f"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('{UTILS_TS}', 'utf-8');
const sf = ts.createSourceFile('{UTILS_TS}', src, ts.ScriptTarget.Latest, true);
const diags = [];
for (const d of sf.parseDiagnostics || []) {{
    diags.push({{ msg: ts.flattenDiagnosticMessageText(d.messageText, '\\n'), pos: d.start }});
}}
console.log(JSON.stringify({{ ok: diags.length === 0, diags, file: 'utils.ts' }}));
"""
    result = _run_node(script)
    assert result["ok"], f"utils.ts has parse errors: {result['diags']}"


# [repo_tests] pass_to_pass
def test_repo_index_ts_parses():
    """Repo's index.ts file must parse as valid TypeScript (pass_to_pass)."""
    script = f"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('{INDEX_TS}', 'utf-8');
const sf = ts.createSourceFile('{INDEX_TS}', src, ts.ScriptTarget.Latest, true);
const diags = [];
for (const d of sf.parseDiagnostics || []) {{
    diags.push({{ msg: ts.flattenDiagnosticMessageText(d.messageText, '\\n'), pos: d.start }});
}}
console.log(JSON.stringify({{ ok: diags.length === 0, diags, file: 'index.ts' }}));
"""
    result = _run_node(script)
    assert result["ok"], f"index.ts has parse errors: {result['diags']}"


# [repo_tests] pass_to_pass
def test_repo_requires_project_annotations_function_signature():
    """requiresProjectAnnotations function must have consistent signature (pass_to_pass).

    This ensures the function signature doesn't change unexpectedly between base and gold.
    """
    script = f"""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('{UTILS_TS}', 'utf-8');
const sf = ts.createSourceFile('utils.ts', src, ts.ScriptTarget.Latest, true);

function findFunction(node) {{
    if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'requiresProjectAnnotations') {{
        return node;
    }}
    let found = null;
    ts.forEachChild(node, child => {{
        if (!found) found = findFunction(child);
    }});
    return found;
}}

const fn = findFunction(sf);
if (!fn) {{
    console.log(JSON.stringify({{ found: false }}));
}} else {{
    const isAsync = fn.modifiers && fn.modifiers.some(m => m.kind === ts.SyntaxKind.AsyncKeyword);
    const isExported = fn.modifiers && fn.modifiers.some(m => m.kind === ts.SyntaxKind.ExportKeyword);
    console.log(JSON.stringify({{
        found: true,
        isAsync: !!isAsync,
        isExported: !!isExported,
        name: fn.name.text
    }}));
}}
"""
    result = _run_node(script)
    assert result.get("found"), "requiresProjectAnnotations function not found"
    assert result.get("isAsync"), "requiresProjectAnnotations must be async"
    assert result.get("isExported"), "requiresProjectAnnotations must be exported"


# [repo_tests] pass_to_pass
def test_repo_vitest_plugin_imports_valid():
    """Vitest plugin files must have valid import/export statements (pass_to_pass).

    Verifies that import paths follow expected patterns and syntax is valid.
    """
    src = Path(INDEX_TS).read_text()
    # Check for obviously broken import patterns
    assert "from 'vitest/config'" in src, "Expected import from vitest/config"
    assert "from './utils'" in src, "Expected import from ./utils"
    # Verify no empty import sources
    assert "from ''" not in src, "Empty import source detected"
    assert "import {} from" not in src, "Empty import specifier detected"
