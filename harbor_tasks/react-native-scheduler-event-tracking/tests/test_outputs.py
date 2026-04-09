"""
Task: react-native-scheduler-event-tracking
Repo: react @ aac12ce597b49093a5add54b00deee3d8980f874
PR:   35947

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/react"
TARGET = "packages/react-native-renderer/src/ReactFiberConfigFabric.js"
TARGET_FULL = os.path.join(REPO, TARGET)


def _install_deps():
    """Install dependencies if not already installed."""
    node_modules = Path(REPO) / "node_modules"
    if not node_modules.exists():
        r = subprocess.run(
            ["yarn", "install", "--frozen-lockfile"],
            capture_output=True, text=True, timeout=180, cwd=REPO,
        )
        if r.returncode != 0:
            raise RuntimeError(f"Failed to install dependencies: {r.stderr[-500:]}")


# JS setup code: reads the source file, extracts the event tracking functions
# (trackSchedulerEvent through resolveEventTimeStamp), strips Flow type annotations,
# and wraps them in a Function constructor so they share a closure over schedulerEvent.
_SETUP_JS = r"""
'use strict';
const fs = require('fs');

const src = fs.readFileSync(process.env.TARGET_FILE, 'utf8');
const lines = src.split('\n');

// Find the block from schedulerEvent/trackSchedulerEvent to shouldAttemptEagerTransition
let start = -1, end = -1;
for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (start === -1 && (
        line.startsWith('let schedulerEvent') ||
        line.startsWith('var schedulerEvent') ||
        line.startsWith('export function trackSchedulerEvent') ||
        line.startsWith('function trackSchedulerEvent')
    )) {
        start = i;
    }
    if (start !== -1 && /^export\s+function\s+shouldAttemptEagerTransition/.test(line)) {
        end = i;
        break;
    }
}

if (start === -1 || end === -1) {
    process.stderr.write('Cannot find function block: start=' + start + ', end=' + end + '\n');
    process.exit(2);
}

let block = lines.slice(start, end).join('\n');

// Strip Flow type annotations and ES module syntax
block = block
    .replace(/: *void *\| *Event\b/g, '')
    .replace(/: *Event\b/g, '')
    .replace(/: *void\b/g, '')
    .replace(/: *null *\| *string\b/g, '')
    .replace(/: *number\b/g, '')
    .replace(/: *boolean\b/g, '')
    .replace(/\bexport +/g, '')
    .replace(/\/\/ *\$Flow[^\n]*/g, '');

// Build a factory function: the 'global' parameter shadows the real global,
// letting us control global.event. All inner functions share the closure.
const factory = new Function('global',
    block + '\nreturn { trackSchedulerEvent, resolveEventType, resolveEventTimeStamp };'
);
const mockGlobal = { event: undefined };
const api = factory(mockGlobal);
"""


def _run_js(test_js):
    """Run setup + test JS code via Node.js, return CompletedProcess."""
    script = _SETUP_JS + "\n" + test_js
    fd, path = tempfile.mkstemp(suffix=".js", dir="/tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(script)
        r = subprocess.run(
            ["node", path],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
            env={**os.environ, "TARGET_FILE": TARGET_FULL},
        )
        return r
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target file exists and declares the three required exported functions."""
    src = Path(TARGET_FULL).read_text()
    for fn_name in ["trackSchedulerEvent", "resolveEventType", "resolveEventTimeStamp"]:
        assert fn_name in src, f"Missing function declaration: {fn_name}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_resolve_event_type_modern():
    """resolveEventType returns event.type for modern events with a type property."""
    r = _run_js("""
    // Test with multiple different event types to prevent hardcoding
    const cases = [
        { input: { type: 'click', timeStamp: 100 }, expected: 'click' },
        { input: { type: 'keydown', timeStamp: 200 }, expected: 'keydown' },
        { input: { type: 'scroll', timeStamp: 300 }, expected: 'scroll' },
    ];
    for (const { input, expected } of cases) {
        mockGlobal.event = input;
        const result = api.resolveEventType();
        if (result !== expected) {
            process.stderr.write(
                'resolveEventType: expected ' + JSON.stringify(expected) +
                ', got ' + JSON.stringify(result) + ' for input type=' + input.type + '\\n'
            );
            process.exit(1);
        }
    }
    """)
    assert r.returncode == 0, f"Failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_resolve_event_type_legacy():
    """resolveEventType handles legacy RN events via dispatchConfig.phasedRegistrationNames."""
    r = _run_js("""
    // Legacy RN events use dispatchConfig instead of event.type
    const cases = [
        {
            input: {
                dispatchConfig: { phasedRegistrationNames: { bubbled: 'onTouchStart' } },
                timeStamp: 100,
            },
            expected: 'touchstart',
        },
        {
            input: {
                dispatchConfig: { phasedRegistrationNames: { captured: 'onPress' } },
                timeStamp: 200,
            },
            expected: 'press',
        },
        {
            input: {
                dispatchConfig: { phasedRegistrationNames: { bubbled: 'topChange' } },
                timeStamp: 300,
            },
            expected: 'topchange',
        },
    ];
    for (const { input, expected } of cases) {
        mockGlobal.event = input;
        const result = api.resolveEventType();
        if (result !== expected) {
            process.stderr.write(
                'resolveEventType legacy: expected ' + JSON.stringify(expected) +
                ', got ' + JSON.stringify(result) + '\\n'
            );
            process.exit(1);
        }
    }
    """)
    assert r.returncode == 0, f"Failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_resolve_event_timestamp():
    """resolveEventTimeStamp returns the actual event.timeStamp, not -1.1."""
    r = _run_js("""
    const cases = [
        { input: { type: 'click', timeStamp: 42.5 }, expected: 42.5 },
        { input: { type: 'scroll', timeStamp: 1000 }, expected: 1000 },
        { input: { type: 'keyup', timeStamp: 0 }, expected: 0 },
    ];
    for (const { input, expected } of cases) {
        mockGlobal.event = input;
        const result = api.resolveEventTimeStamp();
        if (result !== expected) {
            process.stderr.write(
                'resolveEventTimeStamp: expected ' + expected +
                ', got ' + result + ' for timeStamp=' + input.timeStamp + '\\n'
            );
            process.exit(1);
        }
    }
    """)
    assert r.returncode == 0, f"Failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_tracked_event_excluded():
    """After trackSchedulerEvent, the tracked event is excluded from type/timestamp resolution."""
    r = _run_js("""
    const eventA = { type: 'click', timeStamp: 100 };
    const eventB = { type: 'keydown', timeStamp: 200 };

    // Track eventA as the scheduler event
    mockGlobal.event = eventA;
    api.trackSchedulerEvent();

    // Same event as tracked -> should return defaults (null / -1.1)
    const type1 = api.resolveEventType();
    if (type1 !== null) {
        process.stderr.write('Expected null for tracked event, got: ' + JSON.stringify(type1) + '\\n');
        process.exit(1);
    }
    const ts1 = api.resolveEventTimeStamp();
    if (ts1 !== -1.1) {
        process.stderr.write('Expected -1.1 for tracked event timestamp, got: ' + ts1 + '\\n');
        process.exit(1);
    }

    // Different event -> should return its type and timestamp
    mockGlobal.event = eventB;
    const type2 = api.resolveEventType();
    if (type2 !== 'keydown') {
        process.stderr.write('Expected keydown for new event, got: ' + JSON.stringify(type2) + '\\n');
        process.exit(1);
    }
    const ts2 = api.resolveEventTimeStamp();
    if (ts2 !== 200) {
        process.stderr.write('Expected 200 for new event timestamp, got: ' + ts2 + '\\n');
        process.exit(1);
    }
    """)
    assert r.returncode == 0, f"Failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint check passes (pass_to_pass)."""
    _install_deps()
    r = subprocess.run(
        ["yarn", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flow_fabric():
    """Repo's Flow typecheck for fabric renderer passes (pass_to_pass)."""
    _install_deps()
    r = subprocess.run(
        ["node", "./scripts/tasks/flow-ci", "fabric"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Flow check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_react_fabric_tests():
    """Repo's ReactFabric tests pass (pass_to_pass)."""
    _install_deps()
    r = subprocess.run(
        ["yarn", "test", "--testPathPattern", "ReactFabric", "--ci"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ReactFabric tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_react_native_tests():
    """Repo's ReactNative tests pass (pass_to_pass)."""
    _install_deps()
    r = subprocess.run(
        ["yarn", "test", "--testPathPattern", "ReactNative", "--ci"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ReactNative tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_check_license():
    """Repo's license check passes (pass_to_pass)."""
    r = subprocess.run(
        ["./scripts/ci/check_license.sh"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"License check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_print_warnings():
    """Repo's print warnings check passes (pass_to_pass)."""
    _install_deps()
    r = subprocess.run(
        ["./scripts/ci/test_print_warnings.sh"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Print warnings check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — default behavior preserved
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_no_event_returns_defaults():
    """Without global.event, resolveEventType returns null and resolveEventTimeStamp returns -1.1."""
    r = _run_js("""
    mockGlobal.event = undefined;
    const type1 = api.resolveEventType();
    if (type1 !== null) {
        process.stderr.write('Expected null when no event, got: ' + JSON.stringify(type1) + '\\n');
        process.exit(1);
    }
    const ts1 = api.resolveEventTimeStamp();
    if (ts1 !== -1.1) {
        process.stderr.write('Expected -1.1 when no event, got: ' + ts1 + '\\n');
        process.exit(1);
    }

    // Also test with null
    mockGlobal.event = null;
    const type2 = api.resolveEventType();
    if (type2 !== null) {
        process.stderr.write('Expected null when event is null, got: ' + JSON.stringify(type2) + '\\n');
        process.exit(1);
    }
    const ts2 = api.resolveEventTimeStamp();
    if (ts2 !== -1.1) {
        process.stderr.write('Expected -1.1 when event is null, got: ' + ts2 + '\\n');
        process.exit(1);
    }
    """)
    assert r.returncode == 0, f"Failed:\n{r.stderr}"
