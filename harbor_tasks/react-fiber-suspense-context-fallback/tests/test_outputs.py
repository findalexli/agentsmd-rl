"""
Task: react-fiber-suspense-context-fallback
Repo: facebook/react @ f944b4c5352be02623d2d7415c0806350f875114

Fix: propagateContextChanges skips primary (hidden) subtree and
propagates into the fallback so context consumers there re-render.

All checks must pass for reward = 1. Any failure = reward 0.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
TARGET = f"{REPO}/packages/react-reconciler/src/ReactFiberNewContext.js"
TEST_DIR = f"{REPO}/packages/react-reconciler/src/__tests__"


def test_context_propagation_in_suspense_fallback():
    """Context updates reach consumers inside Suspense fallback through memo boundary."""
    test_file = Path(TEST_DIR) / "_eval_context_fallback-test.js"
    # Write a Jest test that exercises the exact bug:
    # - A memo boundary prevents the Suspense boundary from re-rendering via parent
    # - Context propagation is the ONLY way the fallback consumer can see the update
    # - Without the fix, propagateContextChanges sets nextFiber=null and skips fallback
    # - With the fix, it navigates to primaryChildFragment.sibling (the fallback)
    test_file.write_text("""\
'use strict';

let React;
let ReactNoop;
let act;
let useState;
let useContext;

beforeEach(() => {
  jest.resetModules();
  React = require('react');
  ReactNoop = require('react-noop-renderer');
  const utils = require('internal-test-utils');
  act = utils.act;
  useState = React.useState;
  useContext = React.useContext;
});

test('context change propagates into suspense fallback through memo', async () => {
  const Ctx = React.createContext('A');
  const suspensePromise = new Promise(() => {});
  let setCtxValue;
  let lastFallbackValue = null;

  function App() {
    const [value, setValue] = useState('A');
    setCtxValue = setValue;
    return (
      <Ctx.Provider value={value}>
        <MemoWrapper />
      </Ctx.Provider>
    );
  }

  // Memo boundary is critical: it prevents the Suspense boundary from
  // re-rendering via parent, so only context propagation can reach the
  // fallback consumer.
  const MemoWrapper = React.memo(function MemoWrapper() {
    return (
      <React.Suspense fallback={<FallbackConsumer />}>
        <SuspendingChild />
      </React.Suspense>
    );
  });

  function SuspendingChild() {
    throw suspensePromise;
  }

  function FallbackConsumer() {
    const val = useContext(Ctx);
    lastFallbackValue = val;
    return val;
  }

  const root = ReactNoop.createRoot();

  await act(async () => {
    root.render(<App />);
  });
  expect(lastFallbackValue).toBe('A');

  // Update context value while primary children are still suspended
  await act(async () => {
    setCtxValue('B');
  });
  // With the fix: propagation follows fallback sibling path -> consumer re-renders
  // Without the fix: nextFiber=null skips the Suspense subtree -> consumer stale
  expect(lastFallbackValue).toBe('B');
});
""")
    try:
        r = subprocess.run(
            ["node", "scripts/jest/jest-cli.js", "--forceExit",
             "packages/react-reconciler/src/__tests__/_eval_context_fallback-test.js"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        combined = r.stdout + r.stderr
        assert r.returncode == 0, \
            f"Context propagation test failed:\n{combined[-3000:]}"
    finally:
        test_file.unlink(missing_ok=True)


def test_suspense_fallback_sibling_navigation():
    """Fix introduces primaryChildFragment for fallback sibling navigation."""
    src = Path(TARGET).read_text()
    # The fix replaces the broken nextFiber=null / nextFiber=fiber.child
    # with navigation through primaryChildFragment.sibling to reach fallback
    assert "primaryChildFragment" in src, \
        "Should use primaryChildFragment to navigate to fallback sibling"


def test_file_exists():
    """Target file ReactFiberNewContext.js exists."""
    assert Path(TARGET).exists()
