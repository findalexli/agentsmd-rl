"""
Task: react-infinite-loop-warn-instead-of-throw
Repo: facebook/react @ 3f0b9e61c467cd6e09cac6fb69f6e8f68cd3c5d7

Fix: Distinguish between nested update kinds (sync lane vs phase spawn)
and warn via console.error instead of throwing for instrumentation-gated
infinite loop detection scenarios.

All checks must pass for reward = 1. Any failure = reward 0.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
TARGET = f"{REPO}/packages/react-reconciler/src/ReactFiberWorkLoop.js"

# Jest test that exercises the warn-instead-of-throw behavioral change.
# On base code: throwIfInfiniteUpdateLoopDetected() always throws → Jest test fails.
# On fixed code: it warns via console.error for phase-spawn/render-context paths → Jest test passes.
_JEST_TEST = """\
'use strict';

let React;
let ReactDOMClient;
let Scheduler;
let waitFor;

beforeEach(() => {
  jest.resetModules();
  React = require('react');
  ReactDOMClient = require('react-dom/client');
  Scheduler = require('scheduler');
  ({waitFor} = require('internal-test-utils'));
});

it('warns instead of throwing for render phase update on another component', async () => {
  let setState;
  function App() {
    const [, _setState] = React.useState(0);
    setState = _setState;
    return React.createElement(Child, null);
  }
  function Child() {
    // Calling another component's setState during render triggers
    // infinite loop detection via didIncludeRenderPhaseUpdate.
    setState(c => c + 1);
    return null;
  }

  const originalConsoleError = console.error;
  console.error = e => {
    if (
      typeof e === 'string' &&
      e.startsWith(
        'Maximum update depth exceeded. This could be an infinite loop.',
      )
    ) {
      Scheduler.log('stop');
    }
  };
  try {
    const container = document.createElement('div');
    const root = ReactDOMClient.createRoot(container);
    root.render(React.createElement(App, null));
    await waitFor(['stop']);
  } finally {
    console.error = originalConsoleError;
  }
});
"""


def test_warn_instead_of_throw_for_phase_spawn():
    """Phase-spawn infinite loop should warn via console.error instead of throwing."""
    test_dir = Path(REPO) / "packages" / "react-dom" / "src" / "__tests__"
    test_file = test_dir / "_eval_warn_behavior_test.js"
    test_file.write_text(_JEST_TEST)
    try:
        r = subprocess.run(
            ["yarn", "test", "--no-cache", "_eval_warn_behavior_test"],
            capture_output=True, text=True, timeout=90, cwd=REPO,
        )
        assert r.returncode == 0, (
            f"Jest test failed (expected warn-instead-of-throw behavior):\n"
            f"{r.stdout[-1500:]}\n{r.stderr[-500:]}"
        )
    finally:
        test_file.unlink(missing_ok=True)


def test_nested_update_kind_constants():
    """Should define constants to differentiate nested update types."""
    src = Path(TARGET).read_text()
    assert "NO_NESTED_UPDATE" in src, "Missing NO_NESTED_UPDATE constant"
    assert "NESTED_UPDATE_SYNC_LANE" in src, "Missing NESTED_UPDATE_SYNC_LANE constant"
    assert "NESTED_UPDATE_PHASE_SPAWN" in src, "Missing NESTED_UPDATE_PHASE_SPAWN constant"


def test_nested_update_kind_tracking():
    """nestedUpdateKind should be assigned for each detection path and reset."""
    src = Path(TARGET).read_text()
    assert "nestedUpdateKind = NESTED_UPDATE_SYNC_LANE" in src, \
        "Should set nestedUpdateKind for sync lane updates"
    assert "nestedUpdateKind = NESTED_UPDATE_PHASE_SPAWN" in src, \
        "Should set nestedUpdateKind for phase-spawned updates"
    assert "nestedUpdateKind = NO_NESTED_UPDATE" in src, \
        "Should reset nestedUpdateKind when no nested update"


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()
