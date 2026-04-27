"""Tests for Tracing.group returning a Disposable."""
import pathlib
import re
import subprocess

REPO = pathlib.Path("/workspace/playwright")
TYPES_D_TS_CORE = REPO / "packages/playwright-core/types/types.d.ts"
TYPES_D_TS_CLIENT = REPO / "packages/playwright-client/types/types.d.ts"
TRACING_LIB_JS = REPO / "packages/playwright-core/lib/client/tracing.js"


def _run_node(script: str, timeout: int = 60) -> str:
    """Execute a Node.js snippet from /workspace/playwright. Fail loudly on nonzero exit."""
    result = subprocess.run(
        ["node", "-e", script],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    assert result.returncode == 0, (
        f"Node script exit={result.returncode}\n"
        f"--- stdout ---\n{result.stdout}\n"
        f"--- stderr ---\n{result.stderr}"
    )
    return result.stdout


_FAKE_INSTANCE_SETUP = """
const { Tracing } = require('./packages/playwright-core/lib/client/tracing.js');
const fake = Object.create(Tracing.prototype);
fake._additionalSources = new Set();
const channelLog = [];
fake._channel = {
    tracingGroup: async (opts) => { channelLog.push(['tracingGroup', opts]); },
    tracingGroupEnd: async () => { channelLog.push(['tracingGroupEnd']); },
};
fake.groupEnd = async function() { await this._channel.tracingGroupEnd(); };
"""


def test_group_returns_disposable():
    """Tracing.group resolves to an object with a callable dispose() method."""
    out = _run_node(_FAKE_INSTANCE_SETUP + """
(async () => {
    for (const name of ['outer', 'inner with spaces', '']) {
        const result = await fake.group(name);
        if (result === undefined || result === null) {
            console.error('FAIL: group returned ' + result + ' for name=' + JSON.stringify(name));
            process.exit(2);
        }
        if (typeof result.dispose !== 'function') {
            console.error('FAIL: returned value has no dispose() method (typeof=' + typeof result.dispose + ')');
            process.exit(3);
        }
    }
    console.log('OK');
})().catch(e => { console.error('UNEXPECTED:', e); process.exit(4); });
""")
    assert "OK" in out, f"unexpected node output: {out!r}"


def test_dispose_calls_group_end_exactly_once():
    """Calling dispose() on the returned object triggers tracingGroupEnd exactly once."""
    out = _run_node(_FAKE_INSTANCE_SETUP + """
(async () => {
    const result = await fake.group('grp');
    // Before disposing: only the group call should have happened
    let endCount = channelLog.filter(e => e[0] === 'tracingGroupEnd').length;
    if (endCount !== 0) {
        console.error('FAIL: tracingGroupEnd was called before dispose(): ' + endCount);
        process.exit(2);
    }
    await result.dispose();
    endCount = channelLog.filter(e => e[0] === 'tracingGroupEnd').length;
    if (endCount !== 1) {
        console.error('FAIL: tracingGroupEnd not called after dispose, count=' + endCount);
        process.exit(3);
    }
    // Calling dispose() again should not trigger another groupEnd
    await result.dispose();
    endCount = channelLog.filter(e => e[0] === 'tracingGroupEnd').length;
    if (endCount !== 1) {
        console.error('FAIL: dispose() invoked groupEnd more than once, count=' + endCount);
        process.exit(4);
    }
    console.log('OK');
})().catch(e => { console.error('UNEXPECTED:', e); process.exit(5); });
""")
    assert "OK" in out, f"unexpected node output: {out!r}"


def test_returned_value_supports_async_dispose_protocol():
    """Returned object implements Symbol.asyncDispose (the `await using` protocol)."""
    out = _run_node(_FAKE_INSTANCE_SETUP + """
(async () => {
    const d = await fake.group('outer');
    if (d == null || typeof d[Symbol.asyncDispose] !== 'function') {
        console.error('FAIL: returned value lacks Symbol.asyncDispose');
        process.exit(2);
    }
    // Invoking the protocol method must trigger groupEnd, just like
    // `await using` would on scope exit.
    await d[Symbol.asyncDispose]();
    const endCount = channelLog.filter(e => e[0] === 'tracingGroupEnd').length;
    if (endCount !== 1) {
        console.error('FAIL: Symbol.asyncDispose did not call groupEnd; endCount=' + endCount);
        process.exit(3);
    }
    console.log('OK');
})().catch(e => { console.error('UNEXPECTED:', e); process.exit(4); });
""")
    assert "OK" in out, f"unexpected node output: {out!r}"


def _tracing_group_return_type(types_path: pathlib.Path) -> str:
    """Extract the return type of Tracing.group() from a generated types.d.ts."""
    content = types_path.read_text()
    iface = content.find("export interface Tracing {")
    assert iface >= 0, f"`export interface Tracing {{` not found in {types_path}"
    # The group method's signature ends with the location object then `}): Promise<...>;`
    sub = content[iface : iface + 12000]
    pattern = (
        r"location\?:\s*\{\s*"
        r"file:\s*string;\s*"
        r"line\?:\s*number;\s*"
        r"column\?:\s*number;\s*"
        r"\};\s*"
        r"\}\)\s*:\s*Promise<([^>]+)>;"
    )
    m = re.search(pattern, sub)
    assert m, f"Could not locate Tracing.group return type in {types_path}"
    return m.group(1).strip()


def test_public_types_d_ts_returns_disposable():
    """Generated types.d.ts shows Tracing.group returning Promise<Disposable>."""
    for path in (TYPES_D_TS_CORE, TYPES_D_TS_CLIENT):
        rt = _tracing_group_return_type(path)
        assert rt == "Disposable", (
            f"In {path}: expected `Promise<Disposable>` for Tracing.group, "
            f"got `Promise<{rt}>`"
        )


def test_repo_check_deps():
    """Repository DEPS.list constraints still hold (pass-to-pass)."""
    r = subprocess.run(
        ["node", "utils/check_deps.js"],
        cwd=str(REPO), capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"check_deps failed (exit={r.returncode}):\n"
        f"--- stdout ---\n{r.stdout}\n"
        f"--- stderr ---\n{r.stderr}"
    )


def test_repo_lint_packages():
    """Workspace package consistency holds (pass-to-pass)."""
    r = subprocess.run(
        ["node", "utils/workspace.js", "--ensure-consistent"],
        cwd=str(REPO), capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"lint-packages failed (exit={r.returncode}):\n"
        f"--- stdout ---\n{r.stdout}\n"
        f"--- stderr ---\n{r.stderr}"
    )


def test_repo_eslint_modified_file():
    """ESLint passes on the primary modified source file (pass-to-pass)."""
    r = subprocess.run(
        ["npx", "eslint", "packages/playwright-core/src/client/tracing.ts"],
        cwd=str(REPO), capture_output=True, text=True, timeout=180,
    )
    assert r.returncode == 0, (
        f"eslint failed (exit={r.returncode}):\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n"
        f"--- stderr ---\n{r.stderr[-2000:]}"
    )
