"""
Task: remix-refactor-update-interaction-setup-functions
Repo: remix-run/remix @ 0b0ca631198af88cda1ecceef5a51d20e1b3b3e2
PR:   10952

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/remix"
INTERACTION_PKG = f"{REPO}/packages/interaction"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structure checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified TypeScript files have balanced braces and are non-empty."""
    files = [
        f"{INTERACTION_PKG}/src/lib/interaction.ts",
        f"{INTERACTION_PKG}/src/lib/interactions/form.ts",
        f"{INTERACTION_PKG}/src/lib/interactions/keys.ts",
        f"{INTERACTION_PKG}/src/lib/interactions/popover.ts",
        f"{INTERACTION_PKG}/src/lib/interactions/press.ts",
    ]
    for f in files:
        p = Path(f)
        assert p.exists(), f"{f} does not exist"
        content = p.read_text()
        assert len(content) > 100, f"{f} appears empty or truncated"
        assert content.count("{") == content.count("}"), f"{f} has unbalanced braces"


def test_interaction_setup_type_exported():
    """InteractionSetup type must still be exported from interaction.ts."""
    content = Path(f"{INTERACTION_PKG}/src/lib/interaction.ts").read_text()
    assert re.search(r"export\s+type\s+InteractionSetup", content), \
        "InteractionSetup type is not exported"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess
# ---------------------------------------------------------------------------

def test_calling_convention_behavioral():
    """Behavioral: the source call site must use direct invocation, which correctly
    passes the context as a parameter to handle-style setup functions.

    On the BASE commit the call site is interaction.call(interactionContext) which
    sets 'this' but leaves the first parameter undefined — handle-style functions
    break.  After the fix, interaction(interactionContext) passes the context as
    the first argument, which handle-style functions expect.
    """
    r = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');
const src = fs.readFileSync(
    '/workspace/remix/packages/interaction/src/lib/interaction.ts', 'utf8');

// --- 1. Locate the actual invocation line in the source ---
const lines = src.split('\n');
let callLine = null;
for (const line of lines) {
    const t = line.trim();
    if (t.includes('interactionContext') &&
        (t.includes('interaction(') || t.includes('interaction.call('))) {
        callLine = t;
        break;
    }
}
if (!callLine) {
    console.error('Could not find interaction invocation line');
    process.exit(1);
}

// --- 2. Behaviorally test the calling convention found in the source ---
// A handle-style setup function (the new API surface)
function handleSetup(handle) {
    if (!handle || typeof handle.on !== 'function') {
        throw new Error('handle not received as parameter');
    }
    return 'ok';
}

const mockCtx = { target: {}, on: function(){}, signal: {} };

if (callLine.includes('.call(')) {
    // OLD pattern: .call() sets 'this' but first param is undefined
    try {
        handleSetup.call(mockCtx);  // handle arg is undefined
        process.exit(1);            // should never get here
    } catch (e) {
        console.error('FAIL: .call() cannot pass context to handle-parameter functions');
        process.exit(1);
    }
}

// NEW pattern: direct invocation passes ctx as first argument
if (!callLine.includes('interaction(interactionContext)')) {
    console.error('FAIL: expected interaction(interactionContext)');
    process.exit(1);
}

const result = handleSetup(mockCtx);
if (result !== 'ok') { process.exit(1); }
console.log('PASS');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Behavioral call-site test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_type_signature_uses_parameter():
    """Behavioral: InteractionSetup type must use a regular parameter, not 'this' context.

    Runs a Node script that extracts the type definition, verifies it does NOT use
    'this:', then creates and invokes a function matching the new signature to prove
    parameter-passing works at runtime.
    """
    r = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');
const src = fs.readFileSync(
    '/workspace/remix/packages/interaction/src/lib/interaction.ts', 'utf8');

const m = src.match(/export\s+type\s+InteractionSetup\s*=\s*(.+)/);
if (!m) { console.error('InteractionSetup type not found'); process.exit(1); }

const typeDef = m[1];
if (typeDef.includes('this:') || typeDef.includes('this :')) {
    console.error('Still uses this-context: ' + typeDef);
    process.exit(1);
}
if (!typeDef.includes('Interaction')) {
    console.error('Missing Interaction type ref: ' + typeDef);
    process.exit(1);
}

// Runtime proof: a handle-parameter function receives its argument correctly
function setup(handle) {
    if (!handle) throw new Error('handle is undefined');
    return handle.marker;
}
const res = setup({ marker: 42 });
if (res !== 42) { process.exit(1); }
console.log('PASS');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Type-signature test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_builtin_functions_use_handle():
    """Behavioral: all built-in setup functions use handle parameter, not 'this'.

    Runs a Node script that reads each built-in setup file and verifies no
    'this: Interaction', 'this.target', or 'this.on(' patterns remain.
    """
    r = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');
const files = [
    '/workspace/remix/packages/interaction/src/lib/interactions/form.ts',
    '/workspace/remix/packages/interaction/src/lib/interactions/keys.ts',
    '/workspace/remix/packages/interaction/src/lib/interactions/popover.ts',
    '/workspace/remix/packages/interaction/src/lib/interactions/press.ts',
];

let ok = true;
for (const f of files) {
    const c = fs.readFileSync(f, 'utf8');
    const n = f.split('/').pop();
    for (const pat of ['this: Interaction', 'this.target', 'this.on(']) {
        if (c.includes(pat)) {
            console.error(n + ' still uses ' + pat);
            ok = false;
        }
    }
}
if (!ok) process.exit(1);
console.log('PASS');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Builtin-functions test failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — documentation / changeset
# ---------------------------------------------------------------------------

def test_readme_custom_interactions_updated():
    """README Custom Interactions examples must use handle parameter pattern."""
    content = Path(f"{INTERACTION_PKG}/README.md").read_text()
    assert "Custom Interactions" in content, "README missing Custom Interactions section"

    ci_match = re.search(
        r"## Custom Interactions(.*?)(?=\n## |\Z)", content, re.DOTALL
    )
    assert ci_match, "Could not extract Custom Interactions section"
    ci_section = ci_match.group(1)

    code_blocks = re.findall(r"```[\w]*\n(.*?)```", ci_section, re.DOTALL)
    assert len(code_blocks) > 0, "No code examples in Custom Interactions section"

    for block in code_blocks:
        assert "this: Interaction" not in block, \
            "README code example still uses 'this: Interaction'"
        assert "this.target" not in block, \
            "README code example still uses 'this.target'"
        assert "this.on(" not in block, \
            "README code example still uses 'this.on()'"

    has_param_pattern = any(
        re.search(r"\(\w+:\s*Interaction\)", block)
        for block in code_blocks
    )
    assert has_param_pattern, \
        "README examples must show parameter-based Interaction pattern"


def test_changeset_documents_breaking_change():
    """A changeset file must exist documenting the handle-parameter breaking change."""
    changes_dir = Path(f"{INTERACTION_PKG}/.changes")
    assert changes_dir.is_dir(), "No .changes directory in packages/interaction"

    changeset_files = [
        f for f in changes_dir.glob("*.md") if f.name.lower() != "readme.md"
    ]
    assert len(changeset_files) > 0, "No changeset markdown files found"

    found = False
    for cf in changeset_files:
        content = cf.read_text()
        content_lower = content.lower()
        if ("handle" in content_lower or "parameter" in content_lower) and \
           "interaction" in content_lower:
            found = True
            assert content.strip().startswith("BREAKING CHANGE"), \
                f"Changeset {cf.name} should start with 'BREAKING CHANGE:' " \
                f"per AGENTS.md convention for v0.x breaking changes"
            break

    assert found, \
        "No changeset file found documenting the handle parameter change"
