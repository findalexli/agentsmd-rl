"""
Task: react-devtools-clone-nonexistent-node
Repo: facebook/react @ bb53387716e96912cbfb48d92655bc23882798ff

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
TARGET = Path(REPO) / "packages/react-devtools-shared/src/devtools/views/Profiler/CommitTreeBuilder.js"


def _run_node(code, timeout=30):
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


# JS preamble: extracts getClonedNode from source, compiles it as plain JS,
# and sets up a test node map. Exits non-zero if the function body contains
# Flow type-cast syntax (i.e. the unfixed version).
_SETUP = r"""
const fs = require('fs');
const source = fs.readFileSync(
  'packages/react-devtools-shared/src/devtools/views/Profiler/CommitTreeBuilder.js',
  'utf-8'
);

// Locate getClonedNode arrow function
const start = source.indexOf('const getClonedNode');
if (start === -1) {
  process.stderr.write('getClonedNode not found in source');
  process.exit(1);
}
const arrow = source.indexOf('=>', start);
const openBrace = source.indexOf('{', arrow);

// Brace-counting to find the matching closing brace
let depth = 0, closeBrace = openBrace;
for (let i = openBrace; i < source.length; i++) {
  if (source[i] === '{') depth++;
  if (source[i] === '}') { depth--; if (depth === 0) { closeBrace = i; break; } }
}
const body = source.slice(openBrace + 1, closeBrace);

// Compile as plain JavaScript — the unfixed version's Flow casts will fail here
const nodes = new Map();
nodes.set(1, { id: 1, children: [], displayName: 'Root', key: null, parentID: 0, treeBaseDuration: 10 });

let getClonedNode;
try {
  getClonedNode = (new Function('nodes', 'return function(id){' + body + '}'))(nodes);
} catch(e) {
  process.stderr.write('Function body is not valid JavaScript: ' + e.message);
  process.exit(1);
}
"""


# ---------------------------------------------------------------------------
# pass_to_pass — gates and regressions
# ---------------------------------------------------------------------------

def test_file_exists():
    """CommitTreeBuilder.js must be present in the workspace."""
    assert TARGET.exists(), f"Target file not found: {TARGET}"


def test_existing_fiber_collision_error_preserved():
    """'Commit tree already contains fiber' error must still be present."""
    source = TARGET.read_text()
    assert "Commit tree already contains fiber" in source, (
        "Regression: existing fiber collision error was removed"
    )


# ---------------------------------------------------------------------------
# fail_to_pass — behavioral checks via subprocess (Node.js)
# ---------------------------------------------------------------------------

def test_throws_error_for_nonexistent_node():
    """getClonedNode must throw a descriptive error for a missing fiber ID."""
    r = _run_node(_SETUP + r"""
try {
  getClonedNode(999);
  console.log('NO_ERROR');
} catch(e) {
  if (e.message.includes('Could not clone the node')) {
    console.log('PASS');
  } else {
    console.log('WRONG_ERROR:' + e.message);
  }
}
""")
    assert r.returncode == 0, f"Script failed (likely Flow syntax not removed): {r.stderr}"
    assert "PASS" in r.stdout, (
        f"getClonedNode(999) should throw 'Could not clone the node': {r.stdout.strip()}"
    )


def test_error_message_identifies_fiber():
    """Error message must include the specific missing fiber ID."""
    r = _run_node(_SETUP + r"""
try {
  getClonedNode(42);
  console.log('NO_ERROR');
} catch(e) {
  if (e.message.includes('42')) {
    console.log('PASS');
  } else {
    console.log('NO_ID:' + e.message);
  }
}
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    assert "PASS" in r.stdout, (
        f"Error message should include fiber ID 42: {r.stdout.strip()}"
    )


def test_clone_produces_correct_result():
    """Cloning an existing node returns a correct, independent copy."""
    r = _run_node(_SETUP + r"""
const original = { id: 1, children: [], displayName: 'Root', key: null, parentID: 0, treeBaseDuration: 10 };
const clone = getClonedNode(1);
const keysMatch = JSON.stringify(Object.keys(clone).sort()) === JSON.stringify(Object.keys(original).sort());
const valsMatch = Object.keys(original).every(k => JSON.stringify(clone[k]) === JSON.stringify(original[k]));
const storedInMap = nodes.get(1) === clone;
if (keysMatch && valsMatch && storedInMap) {
  console.log('PASS');
} else {
  console.log('FAIL keys=' + keysMatch + ' vals=' + valsMatch + ' stored=' + storedInMap);
}
""")
    assert r.returncode == 0, f"Script failed (likely Flow syntax not removed): {r.stderr}"
    assert "PASS" in r.stdout, (
        f"Clone should have same keys/values and be stored in map: {r.stdout.strip()}"
    )
