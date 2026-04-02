"""
Task: react-perf-track-function-name
Repo: facebook/react @ 230772f99dac80be6dda9c59441fb4928612f18e
PR:   35659

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
TARGET = f"{REPO}/packages/shared"


def _node(script: str) -> tuple[str, int]:
    """Run a Node.js ESM script, returning (stdout+stderr, returncode)."""
    r = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=TARGET,
        capture_output=True,
        timeout=15,
    )
    return (r.stdout + r.stderr).decode(), r.returncode


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_import_ok():
    """Target file must import without syntax errors."""
    script = 'import { addValueToProperties } from "./ReactPerformanceTrackProperties.js";'
    out, rc = _node(script)
    assert rc == 0, f"Import failed:\n{out}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_class_nonstring_name():
    """Class with static non-string name property must be treated as anonymous, not produce wrong output."""
    # On base: value.name + '() {}' produces '[object Object]() {}', '42() {}', 'null() {}'
    # On fix:  typeof check routes all three to '() => {}'
    script = r"""
import { addValueToProperties } from "./ReactPerformanceTrackProperties.js";

const cases = [
  [class A { static name = {}; },  "object"],
  [class B { static name = 42; },  "number"],
  [class C { static name = null; }, "null"],
];

let failed = false;
for (const [cls, label] of cases) {
  const props = [];
  addValueToProperties("test", cls, props, 0, "");
  const desc = props[0][1];
  if (desc !== "() => {}") {
    process.stderr.write(`FAIL [${label}]: expected "() => {}", got ${JSON.stringify(desc)}\n`);
    failed = true;
  }
}
process.exit(failed ? 1 : 0);
"""
    out, rc = _node(script)
    assert rc == 0, f"Class nonstring name test failed:\n{out}"


# [pr_diff] fail_to_pass
def test_proxy_nonstring_name():
    """Proxy returning a non-string .name must be treated as anonymous without crashing."""
    # On base: desc = value.name + '() {}' produces wrong output (e.g. '42() {}')
    # On fix:  typeof check routes to '() => {}'
    script = r"""
import { addValueToProperties } from "./ReactPerformanceTrackProperties.js";

const cases = [
  [new Proxy(() => {}, { get(t, p) { return p === "name" ? 42 : t[p]; } }),       "number"],
  [new Proxy(() => {}, { get(t, p) { return p === "name" ? {x:1} : t[p]; } }),    "object"],
  [new Proxy(() => {}, { get(t, p) { return p === "name" ? false : t[p]; } }),    "boolean"],
];

let failed = false;
for (const [fn, label] of cases) {
  const props = [];
  try {
    addValueToProperties("test", fn, props, 0, "");
    const desc = props[0][1];
    if (desc !== "() => {}") {
      process.stderr.write(`FAIL [${label}]: expected "() => {}", got ${JSON.stringify(desc)}\n`);
      failed = true;
    }
  } catch (e) {
    process.stderr.write(`FAIL [${label}]: threw ${e.message}\n`);
    failed = true;
  }
}
process.exit(failed ? 1 : 0);
"""
    out, rc = _node(script)
    assert rc == 0, f"Proxy nonstring name test failed:\n{out}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_named_function_unchanged():
    """Normal named functions still produce 'fnName() {}' (regression guard)."""
    script = r"""
import { addValueToProperties } from "./ReactPerformanceTrackProperties.js";

const cases = [
  [function myFunc() {}, "myFunc() {}"],
  [function calculate() {}, "calculate() {}"],
  [function renderTree() {}, "renderTree() {}"],
];

let failed = false;
for (const [fn, expected] of cases) {
  const props = [];
  addValueToProperties("test", fn, props, 0, "");
  const desc = props[0][1];
  if (desc !== expected) {
    process.stderr.write(`FAIL: expected ${JSON.stringify(expected)}, got ${JSON.stringify(desc)}\n`);
    failed = true;
  }
}
process.exit(failed ? 1 : 0);
"""
    out, rc = _node(script)
    assert rc == 0, f"Named function regression test failed:\n{out}"


# [repo_tests] pass_to_pass
def test_anonymous_and_empty_name():
    """Anonymous functions and functions with empty names produce '() => {}'."""
    script = r"""
import { addValueToProperties } from "./ReactPerformanceTrackProperties.js";

// Arrow function — name is "" (inferred from variable is not the case here, anon context)
const anonFn = (() => function() {})();  // name = ""
const arrowFn = (() => (() => 42))();     // name = ""

const cases = [
  [anonFn, "anonymous"],
  [arrowFn, "arrow"],
];

let failed = false;
for (const [fn, label] of cases) {
  const props = [];
  addValueToProperties("test", fn, props, 0, "");
  const desc = props[0][1];
  if (desc !== "() => {}") {
    process.stderr.write(`FAIL [${label}]: expected "() => {}", got ${JSON.stringify(desc)}\n`);
    failed = true;
  }
}
process.exit(failed ? 1 : 0);
"""
    out, rc = _node(script)
    assert rc == 0, f"Anonymous/empty name test failed:\n{out}"
