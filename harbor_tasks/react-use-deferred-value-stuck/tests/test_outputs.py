"""
Task: react-use-deferred-value-stuck
Repo: facebook/react @ ed69815cebae33b0326cc69faa90f813bb924f3b
PR:   36134

useDeferredValue gets stuck when a suspension is resolved during the same
render.  The fix records pinged lanes in pingSuspendedRoot's render-phase
branch so markRootSuspended won't mark them as suspended.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
TARGET = f"{REPO}/packages/react-reconciler/src/ReactFiberWorkLoop.js"
TEST_DIR = f"{REPO}/packages/react-reconciler/src/__tests__"


def _run_jest(test_path: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a single Jest test file via React's jest-cli."""
    return subprocess.run(
        ["node", "scripts/jest/jest-cli.js", "--forceExit", test_path],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_deferred_value_catches_up():
    """useDeferredValue catches up when a suspension is resolved mid-render."""
    test_file = Path(TEST_DIR) / "_eval_deferred_stuck-test.js"
    test_file.write_text("""\
'use strict';

let React;
let ReactNoop;
let Scheduler;
let act;
let useDeferredValue;
let useState;
let Suspense;
let assertLog;
let textCache;

describe('useDeferredValue stuck regression', () => {
  beforeEach(() => {
    jest.resetModules();
    React = require('react');
    ReactNoop = require('react-noop-renderer');
    Scheduler = require('scheduler');
    const InternalTestUtils = require('internal-test-utils');
    act = InternalTestUtils.act;
    assertLog = InternalTestUtils.assertLog;
    useDeferredValue = React.useDeferredValue;
    useState = React.useState;
    Suspense = React.Suspense;
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
        case 'pending':
          Scheduler.log('Suspend! [' + text + ']');
          throw record.value;
        case 'rejected':
          throw record.value;
        case 'resolved':
          return record.value;
      }
    } else {
      Scheduler.log('Suspend! [' + text + ']');
      const thenable = {
        pings: [],
        then(resolve) {
          if (newRecord.status === 'pending') {
            thenable.pings.push(resolve);
          } else {
            Promise.resolve().then(() => resolve(newRecord.value));
          }
        },
      };
      const newRecord = {status: 'pending', value: thenable};
      textCache.set(text, newRecord);
      throw thenable;
    }
  }

  function Text({text}) {
    Scheduler.log(text);
    return text;
  }

  function AsyncText({text}) {
    readText(text);
    Scheduler.log(text);
    return text;
  }

  it('deferred value catches up when suspension resolved during same render', async () => {
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
        // Resolve A during this render, simulating data arriving mid-render.
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

    // Pre-resolve B so the sibling won't suspend on retry.
    resolveText('B:updated');

    await act(() => setValue('updated'));
    assertLog([
      // Sync render defers the value.
      'A:initial',
      'B: initial',
      // Deferred render: A suspends, then Sibling resolves A mid-render.
      'Suspend! [A:updated]',
      'B: updated',
      'Loading...',
      // React retries and the deferred value catches up.
      'A:updated',
      'B: updated',
    ]);
    expect(root).toMatchRenderedOutput('A:updatedupdated');
  });
});
""")
    try:
        r = _run_jest(
            "packages/react-reconciler/src/__tests__/_eval_deferred_stuck-test.js"
        )
        combined = r.stdout + r.stderr
        assert r.returncode == 0, (
            f"useDeferredValue regression test failed:\n{combined[-3000:]}"
        )
    finally:
        test_file.unlink(missing_ok=True)


# [pr_diff] fail_to_pass
def test_pinged_lanes_in_render_branch():
    """pingSuspendedRoot records pinged lanes when in render phase.

    On the base commit, when a ping fires during the render phase and we
    can't call prepareFreshStack, the pinged lanes are NOT recorded. The fix
    adds a workInProgressRootPingedLanes merge in this exact code path so
    markRootSuspended knows to exclude them.
    """
    src = Path(TARGET).read_text()

    # Locate pingSuspendedRoot function
    func_keyword = "function pingSuspendedRoot"
    func_start = src.index(func_keyword)
    func_body = src[func_start : func_start + 3000]

    # The render-phase else branch sits between prepareFreshStack and the
    # outer "Even though we can't restart" comment that begins the other
    # else branch.
    prep_idx = func_body.index("prepareFreshStack")
    else_idx = func_body.index("Even though we can")
    render_phase_section = func_body[prep_idx:else_idx]

    # The fix must record pinged lanes in this section
    assert "workInProgressRootPingedLanes" in render_phase_section, (
        "pingSuspendedRoot must record workInProgressRootPingedLanes in the "
        "render-phase branch (between prepareFreshStack and the outer else)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_deferred_value_tests():
    """Existing ReactDeferredValue test suite still passes."""
    r = _run_jest(
        "packages/react-reconciler/src/__tests__/ReactDeferredValue-test.js",
        timeout=120,
    )
    combined = r.stdout + r.stderr
    assert r.returncode == 0, (
        f"Existing ReactDeferredValue tests failed:\n{combined[-3000:]}"
    )
