"""
Task: react-deferred-value-stuck-suspension
Repo: react @ ed69815cebae33b0326cc69faa90f813bb924f3b
PR:   36134

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import os
from pathlib import Path

REPO = "/workspace/react"

# Injected JS test that exercises the useDeferredValue-stuck bug.
# Uses React's internal test infrastructure (ReactNoop, Scheduler, act, assertLog).
_JS_TEST_CONTENT = r"""'use strict';

let React;
let ReactNoop;
let Scheduler;
let act;
let useState;
let useDeferredValue;
let Suspense;
let assertLog;
let textCache;

describe('HarborDeferredValueStuckRegression', () => {
  beforeEach(() => {
    jest.resetModules();
    React = require('react');
    ReactNoop = require('react-noop-renderer');
    Scheduler = require('scheduler');
    act = require('internal-test-utils').act;
    useState = React.useState;
    useDeferredValue = React.useDeferredValue;
    Suspense = React.Suspense;
    const InternalTestUtils = require('internal-test-utils');
    assertLog = InternalTestUtils.assertLog;
    textCache = new Map();
  });

  function resolveText(text) {
    const record = textCache.get(text);
    if (record === undefined) {
      textCache.set(text, {status: 'resolved', value: text});
    } else if (record.status === 'pending') {
      const thenable = record.value;
      record.status = 'resolved';
      record.value = text;
      thenable.pings.forEach(t => t());
    }
  }

  function readText(text) {
    const record = textCache.get(text);
    if (record !== undefined) {
      switch (record.status) {
        case 'resolved':
          return record.value;
        case 'pending':
          Scheduler.log(`Suspend! [${text}]`);
          throw record.value;
        case 'rejected':
          throw record.value;
      }
    }
    const thenable = {
      pings: [],
      then(resolve) {
        if (newRecord.status === 'pending') {
          thenable.pings.push(resolve);
        }
      },
    };
    Scheduler.log(`Suspend! [${text}]`);
    const newRecord = {status: 'pending', value: thenable};
    textCache.set(text, newRecord);
    throw thenable;
  }

  function Text({text}) {
    Scheduler.log(text);
    return text;
  }

  function AsyncText({text}) {
    const result = readText(text);
    Scheduler.log(result);
    return result;
  }

  it('deferred value catches up when suspension resolves during render', async () => {
    let setValue;
    function App() {
      const [value, _setValue] = useState('initial');
      setValue = _setValue;
      const deferred = useDeferredValue(value);
      return (
        <Suspense fallback={<Text text="Loading..." />}>
          <AsyncText text={'A:' + deferred} />
          <Sibling text={deferred} />
        </Suspense>
      );
    }

    function Sibling({text}) {
      if (text !== 'initial') {
        resolveText('A:' + text);
      }
      readText('B:' + text);
      Scheduler.log('B: ' + text);
      return text;
    }

    const root = ReactNoop.createRoot();
    resolveText('A:initial');
    resolveText('B:initial');
    await act(() => root.render(<App />));
    assertLog(['A:initial', 'B: initial']);

    resolveText('B:updated');
    await act(() => setValue('updated'));
    assertLog([
      'A:initial',
      'B: initial',
      'Suspend! [A:updated]',
      'B: updated',
      'Loading...',
      'A:updated',
      'B: updated',
    ]);
    expect(root).toMatchRenderedOutput('A:updatedupdated');
  });

  it('deferred value catches up with different values', async () => {
    let setValue;
    function App() {
      const [value, _setValue] = useState('v1');
      setValue = _setValue;
      const deferred = useDeferredValue(value);
      return (
        <Suspense fallback={<Text text="Loading..." />}>
          <AsyncText text={'X:' + deferred} />
          <Sibling text={deferred} />
        </Suspense>
      );
    }

    function Sibling({text}) {
      if (text !== 'v1') {
        resolveText('X:' + text);
      }
      readText('Y:' + text);
      Scheduler.log('Y: ' + text);
      return text;
    }

    const root = ReactNoop.createRoot();
    resolveText('X:v1');
    resolveText('Y:v1');
    await act(() => root.render(<App />));
    assertLog(['X:v1', 'Y: v1']);

    resolveText('Y:v2');
    await act(() => setValue('v2'));
    assertLog([
      'X:v1',
      'Y: v1',
      'Suspend! [X:v2]',
      'Y: v2',
      'Loading...',
      'X:v2',
      'Y: v2',
    ]);
    expect(root).toMatchRenderedOutput('X:v2v2');
  });
});
"""

_JS_TEST_PATH = os.path.join(
    REPO,
    "packages/react-reconciler/src/__tests__/HarborDeferredValueStuck-test.js",
)


def _ensure_js_test_file():
    """Write the JS test file to the repo (idempotent)."""
    if not os.path.exists(_JS_TEST_PATH):
        Path(_JS_TEST_PATH).write_text(_JS_TEST_CONTENT)


def _run_jest(test_name_pattern, file_pattern="HarborDeferredValueStuck", timeout=300):
    """Run a single Jest test by name pattern in the source channel."""
    _ensure_js_test_file()
    r = subprocess.run(
        [
            "yarn", "test",
            "--silent",
            "--no-watchman",
            "-t", test_name_pattern,
            file_pattern,
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return r


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_deferred_value_catches_up():
    """useDeferredValue catches up when suspension resolves during same render."""
    r = _run_jest("deferred value catches up when suspension resolves during render")
    assert r.returncode == 0, (
        f"Jest test failed (deferred value stuck):\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_deferred_value_catches_up_variant():
    """useDeferredValue catches up with different parameter values."""
    r = _run_jest("deferred value catches up with different values")
    assert r.returncode == 0, (
        f"Jest test failed (deferred value stuck with variant values):\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_deferred_value_tests():
    """Existing deferred value tests still pass."""
    r = subprocess.run(
        [
            "yarn", "test",
            "--silent",
            "--no-watchman",
            "-t", "does not defer during a transition",
            "ReactDeferredValue",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"Existing deferred value test failed:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [repo_tests] pass_to_pass — CI/CD lint check
def test_repo_lint():
    """Repo's ESLint passes on base commit (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "lint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"ESLint check failed:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [repo_tests] pass_to_pass — CI/CD flow typecheck
def test_repo_flow():
    """Repo's Flow typecheck passes on base commit (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "flow", "dom-browser"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Flow typecheck failed:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [repo_tests] pass_to_pass — CI/CD reconciler tests (subset that passes on base)
def test_repo_reconciler_hooks_basic():
    """Repo's react-reconciler hooks basic tests pass on base commit (pass_to_pass)."""
    r = subprocess.run(
        [
            "yarn", "test",
            "--silent",
            "--no-watchman",
            "--testPathPattern", "ReactHooks-test",
            "--testNamePattern", "basic",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"ReactHooks basic tests failed:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [repo_tests] pass_to_pass — CI/CD version check
def test_repo_version_check():
    """Repo's version check passes on base commit (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/version-check.js"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Version check failed:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [repo_tests] pass_to_pass — CI/CD license check
def test_repo_license_check():
    """Repo's license check passes on base commit (pass_to_pass)."""
    r = subprocess.run(
        ["./scripts/ci/check_license.sh"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"License check failed:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — .claude/skills/fix/SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .claude/skills/fix/SKILL.md:10 @ ed69815cebae33b0326cc69faa90f813bb924f3b
def test_prettier_formatting():
    """Changed file must pass prettier formatting (from fix skill)."""
    target = "packages/react-reconciler/src/ReactFiberWorkLoop.js"
    r = subprocess.run(
        ["npx", "prettier", "--check", target],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"Prettier check failed on {target}:\n{r.stdout}\n{r.stderr}"
    )
