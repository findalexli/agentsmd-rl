"""
Task: react-rn-global-event-dispatch
Repo: react @ a48e9e3f10fed06c813399ccae8a28db7dd76683
PR:   35913

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
EVENT_PLUGIN_UTILS = (
    "packages/react-native-renderer/src/legacy-events/EventPluginUtils.js"
)

# Shared preamble: extract executeDispatch from source and mock dependencies
_EXTRACT_PREAMBLE = """
const fs = require('fs');
const src = fs.readFileSync(
  '/workspace/react/packages/react-native-renderer/src/legacy-events/EventPluginUtils.js',
  'utf8'
);

// Locate executeDispatch function
const marker = 'export function executeDispatch(';
const start = src.indexOf(marker);
if (start === -1) {
  process.stderr.write('executeDispatch function not found in source');
  process.exit(1);
}

// Brace-counting to find matching close
let depth = 0, end = -1;
for (let i = src.indexOf('{', start); i < src.length; i++) {
  if (src[i] === '{') depth++;
  if (src[i] === '}') { depth--; if (depth === 0) { end = i + 1; break; } }
}

let funcSrc = src.substring(start, end).replace('export function', 'function');

// Mock module-level dependencies
let hasError = false;
let caughtError = null;
function getNodeFromInstance(inst) { return inst || {}; }

eval(funcSrc);
"""


def _run_node(test_js: str) -> subprocess.CompletedProcess:
    """Run a Node.js script that includes the extraction preamble + test code."""
    script = _EXTRACT_PREAMBLE + test_js
    return subprocess.run(
        ["node", "-e", script],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """EventPluginUtils.js must be valid JavaScript (no syntax errors)."""
    r = subprocess.run(
        ["node", "--check", "-e",
         f"require('fs').readFileSync('{EVENT_PLUGIN_UTILS}','utf8')"],
        cwd=REPO,
        capture_output=True,
        timeout=15,
    )
    # node --check validates stdin, so we use acorn-style parse via node
    # Simpler: just try to parse with Function constructor
    parse_script = f"""
const fs = require('fs');
const src = fs.readFileSync('{EVENT_PLUGIN_UTILS}', 'utf8');
// Strip ES module syntax for parsing check
const stripped = src
  .replace(/^import .+$/gm, '')
  .replace(/^export /gm, '');
try {{
  new Function(stripped);
  process.exit(0);
}} catch (e) {{
  process.stderr.write('Syntax error: ' + e.message);
  process.exit(1);
}}
"""
    r = subprocess.run(
        ["node", "-e", parse_script],
        cwd=REPO,
        capture_output=True,
        timeout=15,
    )
    assert r.returncode == 0, (
        f"EventPluginUtils.js has syntax errors:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_global_event_set_during_dispatch():
    """global.event must equal the dispatched event inside the listener callback."""
    r = _run_node("""
// Test with a click-like event
let captured1 = undefined;
const ev1 = { type: 'touchStart', target: 1 };
executeDispatch(ev1, function() { captured1 = global.event; }, {});
if (captured1 !== ev1) {
  process.stderr.write('Test 1 failed: global.event not set to ev1 during dispatch');
  process.exit(1);
}

// Test with a different event object
let captured2 = undefined;
const ev2 = { type: 'touchEnd', target: 2 };
executeDispatch(ev2, function() { captured2 = global.event; }, {});
if (captured2 !== ev2) {
  process.stderr.write('Test 2 failed: global.event not set to ev2 during dispatch');
  process.exit(1);
}

process.exit(0);
""")
    assert r.returncode == 0, (
        f"global.event not set during dispatch:\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_global_event_nested_dispatch():
    """Nested executeDispatch calls must properly save and restore global.event."""
    r = _run_node("""
let innerCaptured = undefined;
let outerAfterInner = undefined;

const outerEvent = { type: 'outerTouch', id: 'outer' };
const innerEvent = { type: 'innerTouch', id: 'inner' };

executeDispatch(outerEvent, function() {
  // Inside outer listener, global.event should be outerEvent
  if (global.event !== outerEvent) {
    process.stderr.write('outer: global.event != outerEvent');
    process.exit(1);
  }

  // Nested dispatch
  executeDispatch(innerEvent, function() {
    innerCaptured = global.event;
  }, {});

  // After inner dispatch returns, global.event should be restored to outerEvent
  outerAfterInner = global.event;
}, {});

if (innerCaptured !== innerEvent) {
  process.stderr.write('inner: global.event != innerEvent (got ' + JSON.stringify(innerCaptured) + ')');
  process.exit(1);
}

if (outerAfterInner !== outerEvent) {
  process.stderr.write('after inner: global.event not restored to outerEvent (got ' + JSON.stringify(outerAfterInner) + ')');
  process.exit(1);
}

process.exit(0);
""")
    assert r.returncode == 0, (
        f"Nested dispatch save/restore failed:\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_global_event_set_across_multiple_listeners():
    """Each dispatch sets global.event to its own event, not a stale reference."""
    r = _run_node("""
const results = [];
const events = [
  { type: 'press', id: 100 },
  { type: 'scroll', id: 200 },
  { type: 'focus', id: 300 },
];

for (const ev of events) {
  executeDispatch(ev, function() {
    results.push(global.event === ev);
  }, {});
}

const allCorrect = results.every(Boolean);
if (!allCorrect || results.length !== 3) {
  process.stderr.write('Not all dispatches set global.event correctly: ' + JSON.stringify(results));
  process.exit(1);
}

process.exit(0);
""")
    assert r.returncode == 0, (
        f"global.event not set correctly across multiple listeners:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_global_event_restored_after_dispatch():
    """After dispatch completes, global.event must be restored to its pre-existing value."""
    r = _run_node("""
const preexisting = { type: 'preexisting', sentinel: true };
global.event = preexisting;

executeDispatch({ type: 'touch' }, function() {}, {});

if (global.event !== preexisting) {
  process.stderr.write('global.event not restored to preexisting after dispatch');
  process.exit(1);
}

// Also test with undefined
global.event = undefined;
executeDispatch({ type: 'touch2' }, function() {}, {});

if (global.event !== undefined) {
  process.stderr.write('global.event not restored to undefined after dispatch');
  process.exit(1);
}

process.exit(0);
""")
    assert r.returncode == 0, (
        f"global.event not restored after dispatch:\n{r.stderr.decode()}"
    )


# [static] pass_to_pass
def test_current_target_set_and_cleared():
    """event.currentTarget is set during dispatch and cleared to null after."""
    r = _run_node("""
let currentTargetDuringDispatch = undefined;
const ev = { type: 'touch', currentTarget: null };
const mockNode = { nodeId: 42 };

// Override getNodeFromInstance to return a known node
getNodeFromInstance = function(inst) { return mockNode; };

executeDispatch(ev, function(e) {
  currentTargetDuringDispatch = e.currentTarget;
}, {});

if (currentTargetDuringDispatch !== mockNode) {
  process.stderr.write('currentTarget not set to node during dispatch');
  process.exit(1);
}

if (ev.currentTarget !== null) {
  process.stderr.write('currentTarget not cleared to null after dispatch');
  process.exit(1);
}

process.exit(0);
""")
    assert r.returncode == 0, (
        f"currentTarget handling failed:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint check passes (pass_to_pass)."""
    # Fix pre-existing lint error in base commit
    fabric_test = Path(REPO) / "packages/react-native-renderer/src/__tests__/ReactFabric-test.internal.js"
    if fabric_test.exists():
        content = fabric_test.read_text()
        # Remove unused ref3 variable at line 1183 (uses React.createRef())
        content = content.replace("const ref3 = React.createRef();", "// const ref3 = React.createRef(); // skipped for lint")
        content = content.replace("ref3.current = instance.ref3;", "// ref3.current = instance.ref3; // skipped for lint")
        fabric_test.write_text(content)

    r = subprocess.run(
        ["yarn", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flow_native():
    """Repo's Flow typecheck for native renderer passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "flow", "native"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Flow check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_tests_react_native_renderer():
    """Repo's react-native-renderer tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test", "--testPathPattern=react-native-renderer"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Tests failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"
