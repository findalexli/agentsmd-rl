"""
Task: react-flight-chunk-stale-reason
Repo: react @ 1e3152365df2f7a23a5ad947e83f40914413be16
PR:   36024

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import os
import re
from pathlib import Path

REPO = "/workspace/react"

# The full test case from the PR — injected into the existing test file if absent.
INJECTED_TEST = r"""
  it('should not retain stale error reason after reentrant module chunk initialization', async () => {
    function MyComponent() {
      return <div>hello from client component</div>;
    }
    const ClientComponent = clientExports(MyComponent);

    let resolveAsyncComponent;
    async function AsyncComponent() {
      await new Promise(r => {
        resolveAsyncComponent = r;
      });
      return null;
    }

    function ServerComponent() {
      return (
        <>
          <ClientComponent />
          <Suspense>
            <AsyncComponent />
          </Suspense>
        </>
      );
    }

    const {writable: flightWritable, readable: flightReadable} =
      getTestStream();
    const {writable: fizzWritable, readable: fizzReadable} = getTestStream();

    const {pipe} = await serverAct(() =>
      ReactServerDOMServer.renderToPipeableStream(
        <ServerComponent />,
        webpackMap,
      ),
    );
    pipe(flightWritable);

    let response = null;
    function getResponse() {
      if (response === null) {
        response =
          ReactServerDOMClient.createFromReadableStream(flightReadable);
      }
      return response;
    }

    let evaluatingModuleId = null;
    const origRequire = global.__webpack_require__;
    global.__webpack_require__ = function (id) {
      if (id === evaluatingModuleId) {
        throw new ReferenceError(
          "Cannot access 'MyComponent' before initialization",
        );
      }
      const result = origRequire(id);
      if (result === MyComponent) {
        evaluatingModuleId = id;
        if (__DEV__) {
          React.captureOwnerStack();
        }
        evaluatingModuleId = null;
      }
      return result;
    };

    function App() {
      return use(getResponse());
    }

    await serverAct(async () => {
      ReactDOMFizzServer.renderToPipeableStream(<App />).pipe(fizzWritable);
    });

    global.__webpack_require__ = origRequire;

    await serverAct(async () => {
      resolveAsyncComponent();
    });

    const container = document.createElement('div');
    await readInto(container, fizzReadable);
    expect(container.innerHTML).toContain('hello from client component');
  });

"""

ANCHOR = "it('should be able to recover from a direct reference erroring server-side'"


def _ensure_test_injected():
    """Inject the regression test into ReactFlightDOM-test.js if it is not already present."""
    test_file = os.path.join(
        REPO,
        "packages/react-server-dom-webpack/src/__tests__/ReactFlightDOM-test.js",
    )
    content = Path(test_file).read_text()

    marker = "should not retain stale error reason after reentrant module chunk initialization"
    if marker in content:
        return  # Already present (gold patch or agent added it)

    assert ANCHOR in content, (
        f"Could not find injection anchor in {test_file}. "
        "The test file structure may have changed."
    )
    content = content.replace(ANCHOR, INJECTED_TEST + "  " + ANCHOR)
    Path(test_file).write_text(content)


# ---------------------------------------------------------------------------
# Fail-to-pass — core behavioral test (subprocess)
# ---------------------------------------------------------------------------

def test_reentrant_chunk_no_stale_reason():
    """Flight stream must not crash from stale chunk.reason after reentrant module init."""
    _ensure_test_injected()

    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "packages/react-server-dom-webpack/src/__tests__/ReactFlightDOM-test.js",
            "-t", "should not retain stale error reason",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    out = r.stdout.decode(errors="replace")
    err = r.stderr.decode(errors="replace")
    assert r.returncode == 0, (
        f"Reentrant chunk initialization test failed (exit {r.returncode}):\n"
        f"{err[-3000:]}\n{out[-3000:]}"
    )
    # Verify the test actually ran (not just skipped)
    assert "1 passed" in err or "1 passed" in out or "Tests:" in err, (
        f"Test may not have run. Output:\n{err[-2000:]}\n{out[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass — all init sites clear stale reason (source verification)
# ---------------------------------------------------------------------------

def test_all_init_sites_clear_reason():
    """All chunk initialization sites must reset reason after successful init."""
    # --- ReactFlightClient.js: two init functions must clear reason ---
    client_path = os.path.join(
        REPO, "packages/react-client/src/ReactFlightClient.js"
    )
    client_lines = Path(client_path).read_text().splitlines()

    # Find every line that sets status = INITIALIZED (excluding ERRORED lines)
    init_indices = [
        i for i, line in enumerate(client_lines)
        if ".status = INITIALIZED;" in line
    ]
    assert len(init_indices) >= 2, (
        f"Expected at least 2 INITIALIZED sites in ReactFlightClient.js, "
        f"found {len(init_indices)}"
    )

    for idx in init_indices:
        # Within the next 5 lines, reason must be set to null/undefined
        window = "\n".join(client_lines[idx : idx + 5])
        assert ".reason = null" in window or ".reason = undefined" in window, (
            f"Initialization site at line {idx + 1} in ReactFlightClient.js "
            f"does not clear chunk.reason after setting INITIALIZED:\n{window}"
        )

    # --- ReactFlightReplyServer.js: loadServerReference must clear reason ---
    reply_path = os.path.join(
        REPO, "packages/react-server/src/ReactFlightReplyServer.js"
    )
    reply_lines = Path(reply_path).read_text().splitlines()

    reply_init_indices = [
        i for i, line in enumerate(reply_lines)
        if ".status = INITIALIZED;" in line
    ]
    assert len(reply_init_indices) >= 1, (
        "Expected at least 1 INITIALIZED site in ReactFlightReplyServer.js"
    )

    for idx in reply_init_indices:
        window = "\n".join(reply_lines[idx : idx + 5])
        assert ".reason = null" in window or ".reason = undefined" in window, (
            f"Initialization site at line {idx + 1} in ReactFlightReplyServer.js "
            f"does not clear promise.reason after setting INITIALIZED:\n{window}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass — existing upstream test still passes (subprocess)
# ---------------------------------------------------------------------------

def test_existing_flight_error_recovery():
    """Existing 'recover from direct reference erroring' test must still pass."""
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "packages/react-server-dom-webpack/src/__tests__/ReactFlightDOM-test.js",
            "-t", "should be able to recover from a direct reference erroring server-side",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    out = r.stdout.decode(errors="replace")
    err = r.stderr.decode(errors="replace")
    assert r.returncode == 0, (
        f"Existing error-recovery test failed (exit {r.returncode}):\n"
        f"{err[-3000:]}\n{out[-3000:]}"
    )
