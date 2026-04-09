"""
Task: react-flight-encodeReply-jsx-root
Repo: facebook/react @ 2dd9b7cf76c31df5d7e26e5199e3c362c3e94f95
PR:   35730

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
REPLY_CLIENT = REPO + "/packages/react-client/src/ReactFlightReplyClient.js"
FLIGHT_CLIENT = REPO + "/packages/react-client/src/ReactFlightClient.js"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _inject_and_run_jest(test_file_rel: str, test_name: str, test_code: str,
                         test_path_pattern: str) -> None:
    """Inject a test case into an existing React test file and run it via Jest.

    The test file is restored to its original state after execution.
    """
    test_file = Path(REPO) / test_file_rel
    original = test_file.read_text()

    # Insert before the last }); (which closes the outermost describe block)
    lines = original.split('\n')
    insert_idx = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == '});':
            insert_idx = i
            break
    assert insert_idx is not None, f"Could not find describe block closing in {test_file_rel}"

    lines.insert(insert_idx, test_code)
    test_file.write_text('\n'.join(lines))

    try:
        r = subprocess.run(
            ["yarn", "test", "--no-watchman",
             "--testPathPattern", test_path_pattern,
             "--testNamePattern", test_name],
            cwd=REPO, capture_output=True, text=True, timeout=180,
        )
        assert r.returncode == 0, (
            f"Jest test '{test_name}' failed.\n"
            f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-500:]}"
        )
    finally:
        test_file.write_text(original)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file existence and basic structure
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_files_exist():
    """Both modified files must exist at expected paths."""
    assert Path(REPLY_CLIENT).exists(), f"Missing: {REPLY_CLIENT}"
    assert Path(FLIGHT_CLIENT).exists(), f"Missing: {FLIGHT_CLIENT}"


# [static] pass_to_pass
def test_js_syntax_reply_client():
    """ReactFlightReplyClient.js must be readable and non-empty."""
    src = Path(REPLY_CLIENT).read_text()
    assert len(src.splitlines()) > 100, "ReactFlightReplyClient.js is too short — likely stubbed"
    for marker in ("processReply", "REACT_ELEMENT_TYPE", "temporaryReferences",
                    "serializeTemporaryReferenceMarker"):
        assert marker in src, f"ReactFlightReplyClient.js missing expected symbol: {marker}"


# [static] pass_to_pass
def test_js_syntax_flight_client():
    """ReactFlightClient.js must be readable and non-empty."""
    src = Path(FLIGHT_CLIENT).read_text()
    assert len(src.splitlines()) > 100, "ReactFlightClient.js is too short — likely stubbed"
    for marker in ("moveDebugInfoFromChunkToInnerValue", "addAsyncInfo",
                    "_debugInfo", "Object.defineProperty"):
        assert marker in src, f"ReactFlightClient.js missing expected symbol: {marker}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via React's Jest runner
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_encodereply_jsx_root_behavior():
    """encodeReply with JSX element as root must not throw when temporaryReferences provided.

    Runs a focused Jest test via React's test runner (yarn test).
    On base commit: encodeReply throws 'React Element cannot be passed to Server Functions'.
    On fix: JSX root is correctly serialized as a temporary reference.
    """
    _inject_and_run_jest(
        test_file_rel="packages/react-server-dom-webpack/src/__tests__/ReactFlightDOMReply-test.js",
        test_name="__eval_jsx_root__",
        test_code="""
  it('__eval_jsx_root__', async () => {
    const React = require('react');
    const jsx = React.createElement('div');
    const temporaryReferences = ReactServerDOMClient.createTemporaryReferenceSet();
    const body = await ReactServerDOMClient.encodeReply(jsx, {temporaryReferences});
    expect(body).toBeDefined();
  });
""",
        test_path_pattern="ReactFlightDOMReply-test",
    )


# [pr_diff] fail_to_pass
def test_frozen_client_ref_behavior():
    """Frozen client reference element must not crash when debug info is attached.

    Runs a focused Jest test via React's test runner (yarn test).
    On base commit: Object.defineProperty on frozen element throws TypeError in dev mode.
    On fix: Object.isFrozen guard prevents the crash.
    """
    _inject_and_run_jest(
        test_file_rel="packages/react-client/src/__tests__/ReactFlight-test.js",
        test_name="__eval_frozen_ref__",
        test_code="""
  it('__eval_frozen_ref__', async () => {
    const ClientReference = clientReference(React.createElement('span'));

    function App() {
      return ReactServer.createElement('div', null, ClientReference);
    }

    const transport = ReactNoopFlightServer.render(ReactServer.createElement(App));
    await act(async () => {
      const result = await ReactNoopFlightClient.read(transport);
      ReactNoop.render(result);
    });

    expect(ReactNoop).toMatchRenderedOutput(<div><span /></div>);
  });
""",
        test_path_pattern="react-client/src/__tests__/ReactFlight-test",
    )


# [pr_diff] fail_to_pass
def test_frozen_guard_in_add_async_info():
    """addAsyncInfo must guard Object.defineProperty with Object.isFrozen.

    The same frozen-element crash occurs in addAsyncInfo when a chunk resolves
    to a frozen React element and async debug info needs to be attached.
    This supplements the behavioral test above which exercises moveDebugInfoFromChunkToInnerValue.
    """
    src = Path(FLIGHT_CLIENT).read_text()
    lines = src.splitlines()
    fn_start = next(
        (i for i, l in enumerate(lines) if "function addAsyncInfo" in l),
        None,
    )
    assert fn_start is not None, "addAsyncInfo function not found"
    region = "\n".join(lines[fn_start: fn_start + 40])
    assert "Object.isFrozen" in region, (
        "Object.isFrozen guard not found in addAsyncInfo — "
        "frozen elements will crash when receiving async debug info"
    )
    assert "Object.defineProperty" in region, (
        "Object.defineProperty not found in addAsyncInfo — unexpected structural change"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_error_preserved_for_non_temp_ref_jsx():
    """The original throw for JSX without a TemporaryReferenceSet must be preserved.

    The fix only handles the case where temporaryReferences is provided AND the
    value is the model root. JSX without temp refs should still throw.
    """
    src = Path(REPLY_CLIENT).read_text()
    assert "React Element cannot be passed to Server Functions" in src, (
        "Original error message for non-temp-ref JSX was removed"
    )
    assert "temporary reference set" in src, (
        "Error message mentioning 'temporary reference set' not found"
    )


# [static] pass_to_pass
def test_not_stub():
    """Neither modified file has been replaced with a stub."""
    for path, min_lines, key_fn in [
        (REPLY_CLIENT, 200, "processReply"),
        (FLIGHT_CLIENT, 500, "moveDebugInfoFromChunkToInnerValue"),
    ]:
        src = Path(path).read_text()
        lines = src.splitlines()
        assert len(lines) >= min_lines, (
            f"{path}: only {len(lines)} lines — expected >= {min_lines}"
        )
        assert key_fn in src, f"{path}: key function '{key_fn}' missing"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repository CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flow_dom_node():
    """Repo's Flow typecheck (dom-node renderer) passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "flow", "dom-node"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Flow check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_react_flight_tests():
    """ReactFlight module tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test", "--testPathPattern", "ReactFlight-test.js",
         "--no-watchman", "--ci"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ReactFlight tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_react_flight_dom_reply_tests():
    """ReactFlightDOMReply module tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test", "--testPathPattern", "ReactFlightDOMReply-test.js",
         "--no-watchman", "--ci"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ReactFlightDOMReply tests failed:\n{r.stderr[-500:]}"
