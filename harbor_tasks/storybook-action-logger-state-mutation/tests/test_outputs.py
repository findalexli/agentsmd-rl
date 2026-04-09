"""
Task: storybook-action-logger-state-mutation
Repo: storybook @ ce8c743b04264c5e8010df1181c828171a04c33a
PR:   34286

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/storybook"
TARGET_FILE = "code/core/src/actions/containers/ActionLogger/index.tsx"

# ---------------------------------------------------------------------------
# Shared JS: extracts the state updater from the ActionLogger source
# and makes it callable as stateUpdater(prevActions, action, safeDeepEqual).
# ---------------------------------------------------------------------------
_EXTRACT_UPDATER_JS = r"""
'use strict';
const fs = require('fs');
const path = require('path');
const assert = require('assert');

const src = fs.readFileSync(
    path.join(process.cwd(), 'code/core/src/actions/containers/ActionLogger/index.tsx'),
    'utf8',
);

// Locate the setActions state-updater callback via regex (handles any param name)
const match = src.match(/setActions\(\(?(\w+)\)?\s*=>\s*\{/);
if (!match) {
    console.error('Could not find setActions callback in source');
    process.exit(2);
}
const paramName = match[1];
const bodyStart = match.index + match[0].length;

// Brace-counting to find the matching closing brace
let depth = 1;
let i = bodyStart;
while (i < src.length && depth > 0) {
    if (src[i] === '{') depth++;
    if (src[i] === '}') depth--;
    i++;
}
const body = src.slice(bodyStart, i - 1);

// Build a callable function. Strict mode ensures Object.freeze violations throw.
const stateUpdater = new Function(
    paramName, 'action', 'safeDeepEqual',
    '"use strict";\n' + body,
);

function safeDeepEqual(a, b) {
    try { return JSON.stringify(a) === JSON.stringify(b); }
    catch (e) { return false; }
}

function makeAction(name, args, id, limit) {
    return {
        id: id,
        data: { name: name, args: args },
        count: 0,
        options: { limit: limit !== undefined ? limit : 50, clearOnStoryChange: true },
    };
}
"""


def _run_node_script(script):
    """Write a JS script to a temp file and execute it with node."""
    fd, fpath = tempfile.mkstemp(suffix=".js")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(script)
        r = subprocess.run(
            ["node", fpath],
            capture_output=True,
            timeout=30,
            cwd=REPO,
        )
        return r
    finally:
        os.unlink(fpath)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript file has valid structure."""
    content = Path(f"{REPO}/{TARGET_FILE}").read_text()
    assert "export default function ActionLogger" in content, (
        "ActionLogger default export not found"
    )
    assert "setActions" in content, "setActions call not found"
    assert "addAction" in content, "addAction callback not found"
    assert content.count("{") == content.count("}"), "Unbalanced braces"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_limit_retains_newest():
    """When actions exceed the limit, the newest actions must be kept."""
    script = _EXTRACT_UPDATER_JS + r"""

// --- Test 1: limit=3 with 5 actions -> keep last 3 ---
let state = [];
for (let i = 0; i < 5; i++) {
    state = stateUpdater(state, makeAction('a' + i, [i], 'id-' + i, 3), safeDeepEqual);
}
assert.strictEqual(state.length, 3, 'Expected 3 with limit=3, got ' + state.length);
assert.strictEqual(state[0].data.name, 'a2',
    'First should be a2, got ' + state[0].data.name);
assert.strictEqual(state[1].data.name, 'a3',
    'Second should be a3, got ' + state[1].data.name);
assert.strictEqual(state[2].data.name, 'a4',
    'Third should be a4, got ' + state[2].data.name);

// --- Test 2: limit=2 with 4 actions -> keep last 2 ---
state = [];
for (let i = 0; i < 4; i++) {
    state = stateUpdater(state, makeAction('b' + i, [i * 10], 'bid-' + i, 2), safeDeepEqual);
}
assert.strictEqual(state.length, 2, 'Expected 2 with limit=2, got ' + state.length);
assert.strictEqual(state[0].data.name, 'b2',
    'First should be b2, got ' + state[0].data.name);
assert.strictEqual(state[1].data.name, 'b3',
    'Second should be b3, got ' + state[1].data.name);

// --- Test 3: limit=1 with 3 actions -> keep last 1 ---
state = [];
for (let i = 0; i < 3; i++) {
    state = stateUpdater(state, makeAction('c' + i, [i * 100], 'cid-' + i, 1), safeDeepEqual);
}
assert.strictEqual(state.length, 1, 'Expected 1 with limit=1, got ' + state.length);
assert.strictEqual(state[0].data.name, 'c2',
    'Only item should be c2, got ' + state[0].data.name);

console.log('PASS');
"""
    r = _run_node_script(script)
    assert r.returncode == 0, (
        f"Limit-retains-newest failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_no_state_mutation_on_duplicate():
    """Adding a duplicate action must not mutate previous state objects."""
    script = _EXTRACT_UPDATER_JS + r"""

// Build an initial state with one action (frozen to detect mutation)
const initial = { ...makeAction('click', [1], 'id-1', 50), count: 1 };
Object.freeze(initial);
Object.freeze(initial.data);
Object.freeze(initial.options);
const prevState = Object.freeze([initial]);

// Add a duplicate (same data shape)
const dup = makeAction('click', [1], 'id-2', 50);

let newState;
try {
    newState = stateUpdater(prevState, dup, safeDeepEqual);
} catch (e) {
    // TypeError from Object.freeze means the code tried to mutate state
    console.error('State mutation detected: ' + e.message);
    process.exit(1);
}

// Count should be incremented immutably
const last = newState[newState.length - 1];
assert.strictEqual(last.count, 2,
    'Count should be 2 after duplicate, got ' + last.count);

// Original frozen object must be unchanged
assert.strictEqual(initial.count, 1,
    'Original state count should still be 1, got ' + initial.count);

console.log('PASS');
"""
    r = _run_node_script(script)
    assert r.returncode == 0, (
        f"Mutation-on-duplicate failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_new_action_immutable():
    """Adding a new (non-duplicate) action must not mutate the input object."""
    script = _EXTRACT_UPDATER_JS + r"""

// Freeze the input action to detect any mutation
const action = Object.freeze({
    id: 'id-1',
    data: Object.freeze({ name: 'click', args: Object.freeze([1]) }),
    count: 0,
    options: Object.freeze({ limit: 50, clearOnStoryChange: true }),
});

let newState;
try {
    newState = stateUpdater([], action, safeDeepEqual);
} catch (e) {
    console.error('Input action mutation detected: ' + e.message);
    process.exit(1);
}

// Result should contain one action with count=1
assert.strictEqual(newState.length, 1, 'Should have 1 action, got ' + newState.length);
assert.strictEqual(newState[0].count, 1, 'Count should be 1, got ' + newState[0].count);
assert.strictEqual(newState[0].data.name, 'click',
    'Name should be click, got ' + newState[0].data.name);

// Original frozen input must be unchanged
assert.strictEqual(action.count, 0,
    'Original action count should still be 0, got ' + action.count);

console.log('PASS');
"""
    r = _run_node_script(script)
    assert r.returncode == 0, (
        f"New-action-immutability failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config / static)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:246
def test_explicit_ts_extensions():
    """Relative imports use explicit .ts/.tsx extensions per AGENTS.md convention."""
    content = Path(f"{REPO}/{TARGET_FILE}").read_text()
    imports = re.findall(r"from\s+['\"](\.[^'\"]+)['\"]", content)
    assert len(imports) > 0, "No relative imports found"
    for imp in imports:
        if imp.endswith((".css", ".json", ".svg")):
            continue
        assert imp.endswith((".ts", ".tsx", ".js", ".jsx", ".mjs")), (
            f"Import '{imp}' lacks explicit file extension (AGENTS.md line 246)"
        )


# [static] pass_to_pass
def test_not_stub():
    """The addAction handler contains real state-update logic, not a stub."""
    content = Path(f"{REPO}/{TARGET_FILE}").read_text()
    idx = content.find("setActions")
    assert idx != -1, "setActions call missing"
    region = content[idx : idx + 600]
    assert "if" in region and "else" in region, (
        "addAction should have conditional deduplication logic"
    )
    assert "count" in region, "addAction should manage action counts"
    assert "slice" in region, "addAction should enforce the limit via slice"
