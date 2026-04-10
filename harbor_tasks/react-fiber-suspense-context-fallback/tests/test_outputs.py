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

  await act(async () => {
    setCtxValue('B');
  });
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
    assert "primaryChildFragment" in src, \
        "Should use primaryChildFragment to navigate to fallback sibling"


def test_file_exists():
    """Target file ReactFiberNewContext.js exists."""
    assert Path(TARGET).exists()


def test_repo_lint():
    """Repo ESLint passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/eslint.js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    combined = r.stdout + r.stderr
    assert r.returncode == 0, f"ESLint failed:\n{combined[-500:]}"


def test_repo_flow():
    """Repo Flow typecheck passes for dom-browser (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/flow.js", "dom-browser"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    combined = r.stdout + r.stderr
    assert r.returncode == 0, f"Flow check failed:\n{combined[-500:]}"


def test_repo_unit_newcontext():
    """Repo ReactNewContext unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/jest/jest-cli.js", "--testPathPattern", "ReactNewContext", "--silent"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    combined = r.stdout + r.stderr
    assert r.returncode == 0, f"ReactNewContext tests failed:\n{combined[-500:]}"


def test_repo_version_check():
    """Repo version check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/version-check.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    combined = r.stdout + r.stderr
    assert r.returncode == 0, f"Version check failed:\n{combined[-500:]}"


def test_repo_suspense_tests():
    """Repo ReactSuspense tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/jest/jest-cli.js", "--testPathPattern", "ReactSuspense", "--silent"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    combined = r.stdout + r.stderr
    assert r.returncode == 0, f"ReactSuspense tests failed:\n{combined[-500:]}"


def test_repo_fiber_tests():
    """Repo ReactFiber tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/jest/jest-cli.js", "--testPathPattern", "ReactFiber", "--silent"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    combined = r.stdout + r.stderr
    assert r.returncode == 0, f"ReactFiber tests failed:\n{combined[-500:]}"


def test_repo_suspense_fallback():
    """Repo ReactSuspenseFallback tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/jest/jest-cli.js", "--testPathPattern", "ReactSuspenseFallback", "--silent"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    combined = r.stdout + r.stderr
    assert r.returncode == 0, f"ReactSuspenseFallback tests failed:\n{combined[-500:]}"


def test_repo_context_propagation():
    """Repo ReactContextPropagation tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/jest/jest-cli.js", "--testPathPattern", "ReactContextPropagation", "--silent"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    combined = r.stdout + r.stderr
    assert r.returncode == 0, f"ReactContextPropagation tests failed:\n{combined[-500:]}"
