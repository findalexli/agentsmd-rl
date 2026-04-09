"""
Task: storybook-change-detection-flag
Repo: storybook @ 3f91f48ddcd1bb7cb7ee42a8b22229599317b796
PR:   34314

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/storybook"


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
# fail_to_pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_change_detection_type_declared():
    """changeDetection must be declared as optional boolean in StorybookConfigRaw.features."""
    src = Path(f"{REPO}/code/core/src/types/modules/core-common.ts").read_text()

    # Find the features block in StorybookConfigRaw interface.
    # The block is: features?: { ... };
    features_start = src.find("features?: {")
    assert features_start != -1, (
        "features?: { ... } block not found in StorybookConfigRaw interface"
    )

    # Find the matching closing brace — scan forward counting braces
    brace_depth = 0
    features_body = ""
    for i in range(features_start, len(src)):
        ch = src[i]
        if ch == "{":
            brace_depth += 1
        elif ch == "}":
            brace_depth -= 1
            if brace_depth == 0:
                features_body = src[features_start:i + 1]
                break

    assert features_body, "Could not extract features type block"

    # changeDetection must be declared as optional boolean
    assert re.search(r"changeDetection\??\s*:\s*boolean", features_body), (
        "changeDetection?: boolean not found in features type declaration"
    )


# [pr_diff] fail_to_pass
def test_change_detection_preset_evaluated():
    """Features preset must evaluate to include changeDetection === false."""
    r = _run_node("""
import { readFileSync } from 'node:fs';
const src = readFileSync('code/core/src/core-server/presets/common-preset.ts', 'utf-8');

// Extract the object literal body from the features function
const match = src.match(/export const features[\\s\\S]*?=>\\s*\\(\\{([\\s\\S]*?)\\}\\);/);
if (!match) {
    console.error('FAIL: could not extract features function body');
    process.exit(1);
}

// Reconstruct as a plain JS function and evaluate
// The body already contains ...existing spread
try {
    const fn = new Function('existing', `return ({${match[1]}});`);
    const result = fn({});

    if (result.changeDetection !== false) {
        console.error('FAIL: changeDetection should be false, got:', result.changeDetection);
        process.exit(1);
    }

    // Also verify with pre-existing value — preset should set the default
    const result2 = fn({ changeDetection: true });
    if (result2.changeDetection !== false) {
        console.error('FAIL: preset must set changeDetection to false as default');
        process.exit(1);
    }
} catch (e) {
    console.error('FAIL: could not evaluate features function:', e.message);
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Features preset evaluation failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_change_detection_in_docs():
    """Documentation must include changeDetection in the features reference."""
    docs_path = Path(f"{REPO}/docs/api/main-config/main-config-features.mdx")
    assert docs_path.exists(), "main-config-features.mdx not found"
    docs = docs_path.read_text()

    # changeDetection must appear in at least one type signature and as a section
    assert docs.count("changeDetection") >= 2, (
        "changeDetection should appear in the docs type signatures and as a section heading "
        f"(found {docs.count('changeDetection')} occurrences)"
    )

    # Must document the type as boolean
    assert re.search(r"changeDetection.*boolean", docs, re.DOTALL | re.IGNORECASE), (
        "changeDetection with boolean type not documented"
    )


# ---------------------------------------------------------------------------
# pass_to_pass (repo_tests) — repo CI checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_formatting():
    """Repo formatting check passes (oxfmt)."""
    r = subprocess.run(
        ["yarn", "fmt:check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Formatting check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typescript_syntax():
    """Modified TypeScript files have valid syntax (pass_to_pass)."""
    r = _run_node("""
import * as ts from 'typescript';
import * as fs from 'fs';

const files = [
    'code/core/src/core-server/presets/common-preset.ts',
    'code/core/src/types/modules/core-common.ts'
];

let hasErrors = false;
for (const file of files) {
    try {
        const content = fs.readFileSync(file, 'utf8');
        // Parse the file - throws if there are syntax errors
        ts.createSourceFile(file, content, ts.ScriptTarget.Latest, true);
        console.log('OK: ' + file);
    } catch (e) {
        console.error('ERROR: ' + file + ' - ' + e.message);
        hasErrors = true;
    }
}
process.exit(hasErrors ? 1 : 0);
""")
    assert r.returncode == 0, f"TypeScript syntax check failed:\n{r.stderr}\n{r.stdout}"


# ---------------------------------------------------------------------------
# pass_to_pass (static) — syntax / integrity checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must parse without syntax errors."""
    files = [
        "code/core/src/core-server/presets/common-preset.ts",
        "code/core/src/types/modules/core-common.ts",
    ]
    for f in files:
        fpath = Path(REPO) / f
        assert fpath.exists(), f"{f} does not exist"
        content = fpath.read_text()
        assert len(content) > 100, f"{f} appears to be empty or too short"
        opens = content.count("{")
        closes = content.count("}")
        assert abs(opens - closes) <= 3, (
            f"{f} has unbalanced braces ({opens} open, {closes} close)"
        )


# [static] pass_to_pass
def test_features_preset_integrity():
    """All pre-existing feature flags must still be present in the features preset."""
    r = _run_node("""
import { readFileSync } from 'node:fs';
const src = readFileSync('code/core/src/core-server/presets/common-preset.ts', 'utf-8');

const featMatch = src.match(/export const features[\\s\\S]*?=>\\s*\\(\\{([\\s\\S]*?)\\}\\);/);
if (!featMatch) {
    console.error('FAIL: features function not found');
    process.exit(1);
}
const body = featMatch[1];

// These flags must all still be present (they existed before the PR)
const requiredFlags = [
    'actions', 'argTypeTargetsV7', 'backgrounds', 'componentsManifest',
    'controls', 'disallowImplicitActionsInRenderV8', 'highlight',
    'interactions', 'legacyDecoratorFileOrder', 'measure', 'outline',
    'sidebarOnboardingChecklist', 'viewport'
];

const missing = requiredFlags.filter(flag => !new RegExp(flag + '\\s*:').test(body));
if (missing.length > 0) {
    console.error('FAIL: missing flags:', missing.join(', '));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Features integrity check failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout
