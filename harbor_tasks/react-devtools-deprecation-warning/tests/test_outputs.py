"""
Task: react-devtools-deprecation-warning
Repo: facebook/react @ 014138df87869b174956f90a33fd6cf66e160114
PR:   facebook/react#35994

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/react"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks on pre-existing files
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Pre-existing modified files must parse without JS syntax errors."""
    files = [
        "packages/react-devtools-extensions/src/contentScripts/installHook.js",
        "packages/react-devtools-shared/src/backend/types.js",
        "packages/react-devtools-shared/src/hook.js",
    ]
    for f in files:
        path = Path(f"{REPO}/{f}")
        assert path.exists(), f"Missing file: {f}"
        r = subprocess.run(
            ["node", "--check", str(path)],
            capture_output=True, timeout=30,
        )
        assert r.returncode == 0, f"Syntax error in {f}:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_new_reactbuildtype_file_exists():
    """reactBuildType.js must be created with both required exports."""
    p = Path(f"{REPO}/packages/react-devtools-extensions/src/contentScripts/reactBuildType.js")
    assert p.exists(), "reactBuildType.js must be created"
    src = p.read_text()
    assert "reduceReactBuild" in src, "Must define reduceReactBuild"
    assert "createReactRendererListener" in src, "Must define createReactRendererListener"


def _strip_flow(src: str) -> str:
    """Strip Flow type annotations so the JS can run in plain node."""
    # Remove import type {...} lines
    src = re.sub(r"import type \{[^}]*\}[^\n]*\n", "", src)
    # Remove : null | ReactBuildType, : ReactBuildType parameter/return annotations
    src = re.sub(r":\s*(null\s*\|\s*)?ReactBuildType", "", src)
    # Remove ): ReactBuildType { return type on closing paren
    src = re.sub(r"\)\s*:\s*ReactBuildType\s*\{", ") {", src)
    # Remove ): void {
    src = re.sub(r"\)\s*:\s*void\s*\{", ") {", src)
    # Remove export from function declarations (keep functions in scope)
    src = re.sub(r"export function", "function", src)
    # Remove block comments (Flow pragma, license headers)
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)
    return src


# [pr_diff] fail_to_pass
def test_reduce_react_build_worst_build_wins():
    """reduceReactBuild must implement 'worst build' logic: non-production beats production."""
    p = Path(f"{REPO}/packages/react-devtools-extensions/src/contentScripts/reactBuildType.js")
    assert p.exists(), "reactBuildType.js must exist"
    src = _strip_flow(p.read_text())

    test_code = (
        src
        + """
function assertEq(actual, expected, label) {
  if (actual !== expected)
    throw new Error(label + ': expected ' + JSON.stringify(expected) + ' got ' + JSON.stringify(actual));
}
// null always accepts the first value
assertEq(reduceReactBuild(null, 'production'),   'production',   'null+production');
assertEq(reduceReactBuild(null, 'development'),  'development',  'null+development');
assertEq(reduceReactBuild(null, 'outdated'),     'outdated',     'null+outdated');
// production is overridden by any non-production value
assertEq(reduceReactBuild('production', 'development'), 'development', 'prod+dev');
assertEq(reduceReactBuild('production', 'outdated'),    'outdated',    'prod+outdated');
assertEq(reduceReactBuild('production', 'deadcode'),    'deadcode',    'prod+deadcode');
// non-production is NOT overridden by production
assertEq(reduceReactBuild('development', 'production'), 'development', 'dev+prod');
assertEq(reduceReactBuild('outdated',    'production'), 'outdated',    'outdated+prod');
// non-production can still be updated by another non-production value
assertEq(reduceReactBuild('development', 'outdated'),   'outdated',    'dev+outdated');
console.log('OK');
"""
    )
    r = subprocess.run(["node", "-e", test_code], capture_output=True, timeout=30)
    assert r.returncode == 0, (
        f"reduceReactBuild logic incorrect:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )
    assert "OK" in r.stdout.decode()


# [pr_diff] fail_to_pass
def test_listener_maintains_state_across_renderers():
    """createReactRendererListener must preserve worst build across multiple renderer attachments."""
    p = Path(f"{REPO}/packages/react-devtools-extensions/src/contentScripts/reactBuildType.js")
    assert p.exists(), "reactBuildType.js must exist"
    src = _strip_flow(p.read_text())

    test_code = (
        src
        + """
function makeWindow() {
  const msgs = [];
  return { msgs, postMessage(m) { msgs.push(m.payload.reactBuildType); } };
}

// Scenario 1: dev first, then two production renderers — must keep 'development'
const w1 = makeWindow();
const l1 = createReactRendererListener(w1);
l1({ reactBuildType: 'development' });
l1({ reactBuildType: 'production' });
l1({ reactBuildType: 'production' });
if (w1.msgs[1] !== 'development') throw new Error('Scenario 1 msg[1]: expected development got ' + w1.msgs[1]);
if (w1.msgs[2] !== 'development') throw new Error('Scenario 1 msg[2]: expected development got ' + w1.msgs[2]);

// Scenario 2: production first, then dev — must switch to 'development'
const w2 = makeWindow();
const l2 = createReactRendererListener(w2);
l2({ reactBuildType: 'production' });
l2({ reactBuildType: 'development' });
if (w2.msgs[0] !== 'production')   throw new Error('Scenario 2 msg[0]: expected production got '   + w2.msgs[0]);
if (w2.msgs[1] !== 'development')  throw new Error('Scenario 2 msg[1]: expected development got '  + w2.msgs[1]);

// Scenario 3: listeners are independent (closure state not shared)
const w3a = makeWindow();
const w3b = makeWindow();
const la = createReactRendererListener(w3a);
const lb = createReactRendererListener(w3b);
la({ reactBuildType: 'development' });
lb({ reactBuildType: 'production' });
if (w3a.msgs[0] !== 'development') throw new Error('Scenario 3a: expected development got ' + w3a.msgs[0]);
if (w3b.msgs[0] !== 'production')  throw new Error('Scenario 3b: expected production got '  + w3b.msgs[0]);

console.log('OK');
"""
    )
    r = subprocess.run(["node", "-e", test_code], capture_output=True, timeout=30)
    assert r.returncode == 0, (
        f"Listener state management incorrect:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )
    assert "OK" in r.stdout.decode()


# [pr_diff] fail_to_pass
def test_installhook_uses_factory_not_inline():
    """installHook.js must use createReactRendererListener factory; inline listener must be gone."""
    src = Path(
        f"{REPO}/packages/react-devtools-extensions/src/contentScripts/installHook.js"
    ).read_text()
    assert "createReactRendererListener" in src, (
        "installHook.js must import and use createReactRendererListener"
    )
    # Old inline pattern sent 'react-renderer-attached' directly inside the listener
    assert "react-renderer-attached" not in src, (
        "Old inline 'react-renderer-attached' listener must be removed from installHook.js"
    )


# [pr_diff] fail_to_pass
def test_react_build_type_union_exported():
    """ReactBuildType must be exported from types.js with all five required literal values."""
    src = Path(
        f"{REPO}/packages/react-devtools-shared/src/backend/types.js"
    ).read_text()
    assert "export type ReactBuildType" in src, "types.js must export ReactBuildType"
    for value in ("deadcode", "development", "outdated", "production", "unminified"):
        assert f"'{value}'" in src, f"ReactBuildType must include literal '{value}'"


# ---------------------------------------------------------------------------
# Anti-stub (static, fail_to_pass) — verifies real logic in new file
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_not_stub():
    """New reactBuildType.js must contain real implementation logic, not stubs."""
    p = Path(
        f"{REPO}/packages/react-devtools-extensions/src/contentScripts/reactBuildType.js"
    )
    assert p.exists(), "reactBuildType.js must exist"
    src = p.read_text()
    # File must have meaningful length and contain a return statement with conditional logic
    assert len(src) > 200, "File seems too short to contain real logic"
    assert "return" in src, "reduceReactBuild must have return statements"
    assert (
        "currentReactBuildType" in src or "displayedReactBuild" in src
    ), "Must reference internal state variable"
