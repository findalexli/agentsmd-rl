"""
Task: react-context-suspense-fallback
Repo: react @ f944b4c5352be02623d2d7415c0806350f875114
PR:   36160

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import os
from pathlib import Path

REPO = "/workspace/react"

_JS_TEST_CONTENT = r"""'use strict';

let React;
let ReactNoop;
let Scheduler;
let act;
let useState;
let useContext;
let Suspense;
let getCacheForType;
let caches;
let seededCache;
let assertLog;

describe('SuspenseFallbackContextPropagation', () => {
  beforeEach(() => {
    jest.resetModules();
    React = require('react');
    ReactNoop = require('react-noop-renderer');
    Scheduler = require('scheduler');
    const InternalTestUtils = require('internal-test-utils');
    act = InternalTestUtils.act;
    assertLog = InternalTestUtils.assertLog;
    useState = React.useState;
    useContext = React.useContext;
    Suspense = React.Suspense;
    getCacheForType = React.unstable_getCacheForType;
    caches = [];
    seededCache = null;
  });

  function createTextCache() {
    if (seededCache !== null) {
      const cache = seededCache;
      seededCache = null;
      return cache;
    }
    const data = new Map();
    const version = caches.length + 1;
    const cache = {
      version,
      data,
      resolve(text) {
        const record = data.get(text);
        if (record === undefined) {
          data.set(text, {status: 'resolved', value: text});
        } else if (record.status === 'pending') {
          const thenable = record.value;
          record.status = 'resolved';
          record.value = text;
          thenable.pings.forEach(t => t());
        }
      },
    };
    caches.push(cache);
    return cache;
  }

  function readText(text) {
    const textCache = getCacheForType(createTextCache);
    const record = textCache.data.get(text);
    if (record !== undefined) {
      switch (record.status) {
        case 'pending':
          Scheduler.log('Suspend! [' + text + ']');
          throw record.value;
        case 'rejected':
          throw record.value;
        case 'resolved':
          return textCache.version;
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
      textCache.data.set(text, newRecord);
      throw thenable;
    }
  }

  function Text({text}) {
    Scheduler.log(text);
    return text;
  }

  // @gate enableLegacyCache
  it('context change propagates to Suspense fallback consumer', async () => {
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
      readText('data');
      return <Text text="Loaded" />;
    }

    await act(() => {
      root.render(<App />);
    });
    assertLog([
      'Suspend! [data]',
      'Fallback: A',
      'A',
      'Suspend! [data]',
    ]);
    expect(root).toMatchRenderedOutput('Fallback: AA');

    await act(() => {
      setContext('B');
    });
    assertLog([
      'Suspend! [data]',
      'Fallback: B',
      'B',
      'Suspend! [data]',
    ]);
    expect(root).toMatchRenderedOutput('Fallback: BB');
  });

  // @gate enableLegacyCache
  it('sequential context updates propagate to Suspense fallback', async () => {
    const root = ReactNoop.createRoot();
    const Context = React.createContext('x');

    let setContext;
    function App() {
      const [value, _setValue] = useState('x');
      setContext = _setValue;
      return (
        <Context.Provider value={value}>
          <MemoizedOuter />
          <Text text={value} />
        </Context.Provider>
      );
    }

    const MemoizedOuter = React.memo(function MemoizedOuter() {
      return (
        <Suspense fallback={<FallbackReader />}>
          <SuspendingChild />
        </Suspense>
      );
    });

    function FallbackReader() {
      const value = useContext(Context);
      return <Text text={'Loading: ' + value} />;
    }

    function SuspendingChild() {
      readText('content');
      return <Text text="Done" />;
    }

    await act(() => {
      root.render(<App />);
    });
    assertLog([
      'Suspend! [content]',
      'Loading: x',
      'x',
      'Suspend! [content]',
    ]);
    expect(root).toMatchRenderedOutput('Loading: xx');

    await act(() => {
      setContext('y');
    });
    assertLog([
      'Suspend! [content]',
      'Loading: y',
      'y',
      'Suspend! [content]',
    ]);
    expect(root).toMatchRenderedOutput('Loading: yy');

    await act(() => {
      setContext('z');
    });
    assertLog([
      'Suspend! [content]',
      'Loading: z',
      'z',
      'Suspend! [content]',
    ]);
    expect(root).toMatchRenderedOutput('Loading: zz');
  });
});
"""

_JS_TEST_PATH = os.path.join(
    REPO,
    "packages/react-reconciler/src/__tests__/SuspenseFallbackContext-test.js",
)


def _ensure_js_test_file():
    if not os.path.exists(_JS_TEST_PATH):
        Path(_JS_TEST_PATH).write_text(_JS_TEST_CONTENT)


def _run_jest(test_name_pattern, file_pattern="SuspenseFallbackContext", timeout=180):
    _ensure_js_test_file()
    r = subprocess.run(
        [
            "yarn", "test",
            "-r=experimental",
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


# [pr_diff] fail_to_pass
def test_context_propagation_to_suspense_fallback():
    r = _run_jest("context change propagates to Suspense fallback consumer")
    assert r.returncode == 0, (
        f"Jest test failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_sequential_context_updates_in_fallback():
    r = _run_jest("sequential context updates propagate to Suspense fallback")
    assert r.returncode == 0, (
        f"Jest test failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_existing_context_propagation():
    r = subprocess.run(
        [
            "yarn", "test",
            "-r=experimental",
            "--silent",
            "--no-watchman",
            "ReactContextPropagation",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"Existing context propagation tests failed:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [repo_tests] pass_to_pass - CI: yarn flow dom-node
def test_repo_flow_typecheck():
    r = subprocess.run(
        ["yarn", "flow", "dom-node"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Flow type checking failed:\n"
        f"{r.stdout[-1000:]}\n{r.stderr[-1000:]}"
    )


# [repo_tests] pass_to_pass - CI: yarn linc
def test_repo_lint_changed():
    r = subprocess.run(
        ["yarn", "linc"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"ESLint (linc) failed:\n"
        f"{r.stdout[-1000:]}\n{r.stderr[-1000:]}"
    )


# [repo_tests] pass_to_pass - CI: yarn lint (full lint check)
def test_repo_lint_full():
    r = subprocess.run(
        ["yarn", "lint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"ESLint (full) failed:\n"
        f"{r.stdout[-1000:]}\n{r.stderr[-1000:]}"
    )


# [repo_tests] pass_to_pass - CI: yarn flags (feature flags check)
def test_repo_flags():
    r = subprocess.run(
        ["yarn", "flags"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"Feature flags check failed:\n"
        f"{r.stdout[-1000:]}\n{r.stderr[-1000:]}"
    )


# [repo_tests] pass_to_pass - CI: yarn version-check
def test_repo_version_check():
    r = subprocess.run(
        ["yarn", "version-check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Version check failed:\n"
        f"{r.stdout[-1000:]}\n{r.stderr[-1000:]}"
    )


# [repo_tests] pass_to_pass - unit tests for ReactNewContext
def test_repo_react_new_context():
    r = subprocess.run(
        [
            "yarn", "test",
            "-r=experimental",
            "--silent",
            "--no-watchman",
            "ReactNewContext",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"ReactNewContext tests failed:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [repo_tests] pass_to_pass - DOM server integration tests for NewContext
def test_repo_dom_server_new_context():
    r = subprocess.run(
        [
            "yarn", "test",
            "-r=experimental",
            "--silent",
            "--no-watchman",
            "ReactDOMServerIntegrationNewContext",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"ReactDOMServerIntegrationNewContext tests failed:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [agent_config] pass_to_pass
def test_prettier_formatting():
    target = "packages/react-reconciler/src/ReactFiberNewContext.js"
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
