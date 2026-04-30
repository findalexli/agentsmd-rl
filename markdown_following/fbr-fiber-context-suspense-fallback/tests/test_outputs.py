"""
Task: fbr-fiber-context-suspense-fallback
Repo: facebook/react @ f944b4c5352be02623d2d7415c0806350f875114
PR:   36160

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This is a JavaScript/React repo. All behavioral tests write a temporary Jest
test file into the react-reconciler __tests__ directory, run it via yarn test,
and clean up. The jest infrastructure handles JSX transforms, React module
resolution, and async act() — no browser needed (ReactNoop renderer).
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
TARGET = f"{REPO}/packages/react-reconciler/src/ReactFiberNewContext.js"
TESTS_DIR = Path(REPO) / "packages/react-reconciler/src/__tests__"


def _run_jest(tmp_name: str, content: str) -> subprocess.CompletedProcess:
    """Write a temporary jest file, run it via yarn test, always delete it."""
    tmp = TESTS_DIR / f"{tmp_name}.js"
    tmp.write_text(content)
    try:
        return subprocess.run(
            ["yarn", "test", "--silent", "--no-watchman", tmp_name],
            cwd=REPO, capture_output=True, timeout=180,
        )
    finally:
        tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """ReactFiberNewContext.js must parse without syntax errors."""
    r = subprocess.run(
        ["node", "--check", TARGET],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in ReactFiberNewContext.js:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_context_propagates_to_fallback_simple():
    """Context change above a suspended Suspense boundary reaches fallback consumers via fiber propagation."""
    # Without React.memo, the parent re-renders and the fallback updates through
    # normal rendering, not fiber propagation. A memo barrier ensures the ONLY
    # path for context to reach FallbackConsumer is fiber-level propagation —
    # which is exactly what the fix corrects.
    jest_code = """\'use strict\';

let React;
let ReactNoop;
let act;

describe(\'_tmp_ctx_fallback_simple\', () => {
    beforeEach(() => {
        jest.resetModules();
        React = require(\'react\');
        ReactNoop = require(\'react-noop-renderer\');
        act = require(\'internal-test-utils\').act;
    });

    it(\'context change updates fallback consumer while suspended (memo barrier)\', async () => {
        const {useState, useContext, Suspense, memo} = React;
        const Context = React.createContext(\'A\');
        let setContext;
        let renderedValue = null;
        const pendingPromise = new Promise(() => {}); // never resolves

        // memo prevents re-render of SuspenseWrapper when context changes,
        // so fiber-level propagation is the only mechanism that can reach
        // FallbackConsumer inside the Suspense fallback.
        const SuspenseWrapper = memo(function SuspenseWrapper() {
            return React.createElement(
                Suspense, {fallback: React.createElement(FallbackConsumer)},
                React.createElement(AsyncChild)
            );
        });

        function App() {
            const [value, setValue] = useState(\'A\');
            setContext = setValue;
            return React.createElement(
                Context.Provider, {value},
                React.createElement(SuspenseWrapper)
            );
        }

        function FallbackConsumer() {
            renderedValue = useContext(Context);
            return null;
        }

        function AsyncChild() {
            throw pendingPromise;
        }

        const root = ReactNoop.createRoot();
        await act(() => { root.render(React.createElement(App)); });

        // Fallback is showing — initial context value
        expect(renderedValue).toBe(\'A\');

        // Update context while still suspended
        await act(() => { setContext(\'B\'); });

        // Without fix: renderedValue stays \'A\' (fallback skipped during propagation)
        // With fix:    renderedValue updates to \'B\'
        expect(renderedValue).toBe(\'B\');
    });

    it(\'multiple context updates all reach fallback via fiber propagation\', async () => {
        const {useState, useContext, Suspense, memo} = React;
        const Context = React.createContext(\'v0\');
        let setContext;
        const renderLog = [];
        const pendingPromise = new Promise(() => {});

        const SuspenseWrapper = memo(function SuspenseWrapper() {
            return React.createElement(
                Suspense, {fallback: React.createElement(FallbackConsumer)},
                React.createElement(AsyncChild)
            );
        });

        function App() {
            const [value, setValue] = useState(\'v0\');
            setContext = setValue;
            return React.createElement(
                Context.Provider, {value},
                React.createElement(SuspenseWrapper)
            );
        }

        function FallbackConsumer() {
            renderLog.push(useContext(Context));
            return null;
        }

        function AsyncChild() {
            throw pendingPromise;
        }

        const root = ReactNoop.createRoot();
        await act(() => { root.render(React.createElement(App)); });
        await act(() => { setContext(\'v1\'); });
        await act(() => { setContext(\'v2\'); });

        // Each context update must trigger a re-render of the fallback consumer
        const lastValue = renderLog[renderLog.length - 1];
        expect(lastValue).toBe(\'v2\');
        // At minimum initial + 2 updates = 3 renders
        expect(renderLog.length).toBeGreaterThanOrEqual(3);
    });
});
"""
    r = _run_jest("_tmp_ctx_fallback_simple", jest_code)
    assert r.returncode == 0, (
        f"test_context_propagates_to_fallback_simple failed:\n"
        f"{r.stdout.decode()[-3000:]}\n{r.stderr.decode()[-500:]}"
    )


# [pr_diff] fail_to_pass
def test_context_propagates_to_fallback_memo_boundary():
    """Context reaches fallback consumer even when React.memo prevents Suspense wrapper re-render."""
    jest_code = """\'use strict\';

let React;
let ReactNoop;
let act;

describe(\'_tmp_ctx_fallback_memo\', () => {
    beforeEach(() => {
        jest.resetModules();
        React = require(\'react\');
        ReactNoop = require(\'react-noop-renderer\');
        act = require(\'internal-test-utils\').act;
    });

    it(\'context change reaches fallback through memo boundary\', async () => {
        const {useState, useContext, Suspense, memo} = React;
        const Context = React.createContext(\'X\');
        let setContext;
        let renderedValue = null;
        const pendingPromise = new Promise(() => {});

        const MemoSuspense = memo(function MemoSuspense() {
            return React.createElement(
                Suspense, {fallback: React.createElement(FallbackConsumer)},
                React.createElement(AsyncChild)
            );
        });

        function App() {
            const [value, setValue] = useState(\'X\');
            setContext = setValue;
            return React.createElement(
                Context.Provider, {value},
                React.createElement(MemoSuspense)
            );
        }

        function FallbackConsumer() {
            renderedValue = useContext(Context);
            return null;
        }

        function AsyncChild() {
            throw pendingPromise;
        }

        const root = ReactNoop.createRoot();
        await act(() => { root.render(React.createElement(App)); });
        expect(renderedValue).toBe(\'X\');

        await act(() => { setContext(\'Y\'); });
        expect(renderedValue).toBe(\'Y\');
    });

    it(\'context change with multiple memo layers still reaches fallback\', async () => {
        const {useState, useContext, Suspense, memo} = React;
        const Context = React.createContext(\'p\');
        let setContext;
        let renderedValue = null;
        const pendingPromise = new Promise(() => {});

        const Inner = memo(function Inner() {
            return React.createElement(
                Suspense, {fallback: React.createElement(FallbackConsumer)},
                React.createElement(AsyncChild)
            );
        });

        const Outer = memo(function Outer() {
            return React.createElement(Inner);
        });

        function App() {
            const [value, setValue] = useState(\'p\');
            setContext = setValue;
            return React.createElement(
                Context.Provider, {value},
                React.createElement(Outer)
            );
        }

        function FallbackConsumer() {
            renderedValue = useContext(Context);
            return null;
        }

        function AsyncChild() {
            throw pendingPromise;
        }

        const root = ReactNoop.createRoot();
        await act(() => { root.render(React.createElement(App)); });
        expect(renderedValue).toBe(\'p\');

        await act(() => { setContext(\'q\'); });
        expect(renderedValue).toBe(\'q\');
    });
});
"""
    r = _run_jest("_tmp_ctx_fallback_memo", jest_code)
    assert r.returncode == 0, (
        f"test_context_propagates_to_fallback_memo_boundary failed:\n"
        f"{r.stdout.decode()[-3000:]}\n{r.stderr.decode()[-500:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression guard
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_context_propagation_tests():
    """Existing ReactContextPropagation test suite must still pass after the fix."""
    r = subprocess.run(
        ["yarn", "test", "--silent", "--no-watchman",
         "ReactContextPropagation-test"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"Regression in ReactContextPropagation suite:\n"
        f"{r.stdout.decode()[-3000:]}\n{r.stderr.decode()[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_lint():
    """ESLint must pass on ReactFiberNewContext.js (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "lint", TARGET],
        cwd=REPO, capture_output=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"ESLint failed on ReactFiberNewContext.js:\n"
        f"{r.stdout.decode()[-1000:]}\n{r.stderr.decode()[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_reconciler_tests():
    """React reconciler test suite must pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test", "--silent", "--no-watchman", "--testPathPattern", "react-reconciler"],
        cwd=REPO, capture_output=True, timeout=180,
    )
    assert r.returncode == 0, (
        f"React reconciler tests failed:\n"
        f"{r.stdout.decode()[-3000:]}\n{r.stderr.decode()[-500:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_jest_babel_plugin_react_compil_yarn():
    """pass_to_pass | CI job 'Jest babel-plugin-react-compiler' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn install --frozen-lockfile'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_jest_babel_plugin_react_compil_yarn_2():
    """pass_to_pass | CI job 'Jest babel-plugin-react-compiler' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn workspace babel-plugin-react-compiler jest'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_babel_plugin_react_compil_yarn():
    """pass_to_pass | CI job 'Lint babel-plugin-react-compiler' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn workspace babel-plugin-react-compiler lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_flags_ensure_clean_build_directory():
    """pass_to_pass | CI job 'Check flags' → step 'Ensure clean build directory'"""
    r = subprocess.run(
        ["bash", "-lc", 'rm -rf build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Ensure clean build directory' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_flags_yarn():
    """pass_to_pass | CI job 'Check flags' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn flags'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")