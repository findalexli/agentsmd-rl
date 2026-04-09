"""
Task: react-suspense-fallback-context-propagation
Repo: react @ f944b4c5352be02623d2d7415c0806350f875114
PR:   36160

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/react"
TEST_FILE = (
    "packages/react-reconciler/src/__tests__/ReactContextPropagation-test.js"
)


def _run_jest(test_name_pattern=None, timeout=240):
    """Run React jest tests on ReactContextPropagation with experimental channel."""
    cmd = [
        "node", "scripts/jest/jest-cli.js",
        "--release-channel=experimental",
        "--no-watchman",
        "ReactContextPropagation",
    ]
    if test_name_pattern:
        cmd.extend(["-t", test_name_pattern])
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, timeout=timeout)
    stdout = r.stdout.decode(errors="replace")
    stderr = r.stderr.decode(errors="replace")
    return r.returncode, stdout, stderr


def _inject_test_and_run(test_code, test_name_pattern):
    """Inject a test into ReactContextPropagation-test.js and run it via jest."""
    test_file = Path(f"{REPO}/{TEST_FILE}")
    original = test_file.read_text()

    # Insert the test before the final closing of the describe block: "});\n"
    # Find the last occurrence of "});" which closes the describe block
    last_close = original.rfind("});")
    assert last_close != -1, "Could not find closing of describe block"
    modified = original[:last_close] + "\n" + test_code + "\n" + original[last_close:]
    test_file.write_text(modified)

    try:
        rc, stdout, stderr = _run_jest(test_name_pattern)
        assert rc == 0, (
            f"Test '{test_name_pattern}' failed (exit {rc}):\n"
            f"STDOUT:\n{stdout[-2000:]}\nSTDERR:\n{stderr[-2000:]}"
        )
    finally:
        # Always restore the original file
        test_file.write_text(original)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified JS file must parse without syntax errors."""
    # React uses Flow, so we check with node --check on a simplified parse.
    # Use the repo's own babel/flow tooling via a quick require() test.
    target = "packages/react-reconciler/src/ReactFiberNewContext.js"
    r = subprocess.run(
        ["node", "-e", f"""
            const fs = require('fs');
            const code = fs.readFileSync('{target}', 'utf8');
            // Basic check: file exists, is non-empty, and has the function
            if (code.length < 100) throw new Error('File too short');
            if (!code.includes('propagateContextChanges')) {{
                throw new Error('Missing propagateContextChanges function');
            }}
            // Check for obvious syntax issues by looking for balanced braces
            const opens = (code.match(/\\{{/g) || []).length;
            const closes = (code.match(/\\}}/g) || []).length;
            if (Math.abs(opens - closes) > 2) {{
                throw new Error('Mismatched braces: ' + opens + ' open vs ' + closes + ' close');
            }}
            console.log('Syntax check passed');
        """],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Syntax check failed:\n{r.stderr.decode(errors='replace')}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_context_propagation_to_suspense_fallback():
    """Context changes above a suspended Suspense boundary must propagate to
    fallback consumers through a memo boundary."""
    test_code = textwrap.dedent("""\
      // @gate enableLegacyCache
      it('injected: context change propagates to Suspense fallback (memo boundary)', async () => {
        const root = ReactNoop.createRoot();
        const Context = React.createContext('A');

        let setContext;
        function App() {
          const [value, _setValue] = useState('A');
          setContext = _setValue;
          return (
            <Context.Provider value={value}>
              <MemoizedWrapper />
              <Text text={value} />
            </Context.Provider>
          );
        }

        const MemoizedWrapper = React.memo(function MemoizedWrapper() {
          return (
            <Suspense fallback={<FallbackConsumer />}>
              <AsyncChild />
            </Suspense>
          );
        });

        function FallbackConsumer() {
          const value = useContext(Context);
          return <Text text={'Fallback: ' + value} />;
        }

        function AsyncChild() {
          readText('async');
          return <Text text="Content" />;
        }

        // Initial render - primary content suspends, fallback is shown
        await act(() => {
          root.render(<App />);
        });
        assertLog([
          'Suspend! [async]',
          'Fallback: A',
          'A',
          // pre-warming
          'Suspend! [async]',
        ]);
        expect(root).toMatchRenderedOutput('Fallback: AA');

        // Update context while still suspended. The fallback consumer should
        // re-render with the new value.
        await act(() => {
          setContext('B');
        });
        assertLog([
          'Suspend! [async]',
          'Fallback: B',
          'B',
          // pre-warming
          'Suspend! [async]',
        ]);
        expect(root).toMatchRenderedOutput('Fallback: BB');

        // Unsuspend. The primary content should render with the latest context.
        await act(async () => {
          await resolveText('async');
        });
        assertLog(['Content']);
        expect(root).toMatchRenderedOutput('ContentB');
      });
    """)
    _inject_test_and_run(
        test_code,
        "injected: context change propagates to Suspense fallback",
    )


# [pr_diff] fail_to_pass
def test_multiple_context_updates_propagate_to_fallback():
    """Multiple sequential context updates must all reach fallback consumers
    with correct values (numeric context, no sibling consumer)."""
    test_code = textwrap.dedent("""\
      // @gate enableLegacyCache
      it('injected: multiple context updates propagate to Suspense fallback', async () => {
        const root = ReactNoop.createRoot();
        const Context = React.createContext(0);

        let setContext;
        function App() {
          const [value, _setValue] = useState(0);
          setContext = _setValue;
          return (
            <Context.Provider value={value}>
              <MemoizedWrapper />
            </Context.Provider>
          );
        }

        const MemoizedWrapper = React.memo(function MemoizedWrapper() {
          return (
            <Suspense fallback={<FallbackConsumer />}>
              <AsyncChild />
            </Suspense>
          );
        });

        function FallbackConsumer() {
          const value = useContext(Context);
          return <Text text={'Count: ' + value} />;
        }

        function AsyncChild() {
          readText('pending');
          return <Text text="Done" />;
        }

        await act(() => {
          root.render(<App />);
        });
        assertLog([
          'Suspend! [pending]',
          'Count: 0',
          // pre-warming
          'Suspend! [pending]',
        ]);
        expect(root).toMatchRenderedOutput('Count: 0');

        // First update
        await act(() => {
          setContext(1);
        });
        assertLog([
          'Suspend! [pending]',
          'Count: 1',
          // pre-warming
          'Suspend! [pending]',
        ]);
        expect(root).toMatchRenderedOutput('Count: 1');

        // Second update with a different value
        await act(() => {
          setContext(42);
        });
        assertLog([
          'Suspend! [pending]',
          'Count: 42',
          // pre-warming
          'Suspend! [pending]',
        ]);
        expect(root).toMatchRenderedOutput('Count: 42');
      });
    """)
    _inject_test_and_run(
        test_code,
        "injected: multiple context updates propagate to Suspense fallback",
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_context_propagation_tests_pass():
    """Existing ReactContextPropagation tests still pass."""
    rc, stdout, stderr = _run_jest()
    assert rc == 0, (
        f"Existing tests failed (exit {rc}):\n"
        f"STDOUT:\n{stdout[-2000:]}\nSTDERR:\n{stderr[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_react_new_context_tests_pass():
    """ReactNewContext tests pass (pass_to_pass) — tests for modified module."""
    cmd = [
        "node", "scripts/jest/jest-cli.js",
        "--release-channel=experimental",
        "--no-watchman",
        "ReactNewContext",
    ]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, timeout=300)
    stdout = r.stdout.decode(errors="replace")
    stderr = r.stderr.decode(errors="replace")
    assert r.returncode == 0, (
        f"ReactNewContext tests failed (exit {r.returncode}):\n"
        f"STDOUT:\n{stdout[-2000:]}\nSTDERR:\n{stderr[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_lint_passes():
    """Repo's ESLint checks pass (pass_to_pass)."""
    r = subprocess.run(
        ["node", "scripts/tasks/eslint.js"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-1000:]}{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_flow_passes():
    """Repo's Flow typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "scripts/tasks/flow.js", "dom-node"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Flow check failed:\n{r.stderr[-1000:]}{r.stdout[-1000:]}"
