"""Behavioral tests for facebook/react#36055.

The PR adds a defense-in-depth check in `parseModelString` of
`ReactFlightReplyServer.js` so that a `$B` (Blob) reference whose backing
FormData entry is *not* a Blob is rejected.  Without the fix, an attacker
can stash a large string in a FormData slot and reference it via `$B`,
and `decodeReply` will silently return that string instead of a Blob.
After the fix, decoding such a payload throws.

These tests exercise the behavior end-to-end via Jest.  We drop a custom
Jest spec into the React repo, run it through `yarn test`, and tear it
down again so the working tree stays clean.
"""

import subprocess
from pathlib import Path

REPO = Path("/workspace/react")
TESTS_DIR = REPO / "packages/react-server-dom-webpack/src/__tests__"
FIXTURE_NAME = "ReactFlightReplyBlobValidation-task-test.js"
FIXTURE_PATH = TESTS_DIR / FIXTURE_NAME

# A standalone Jest spec that mirrors the setup boilerplate of the
# existing ReactFlightDOMReply-test.js but only contains the security
# behavior we care about. Assertions are deliberately loose so any
# reasonable type-check fix passes, not just the gold patch.
JEST_SPEC = r"""
'use strict';

import {patchMessageChannel} from '../../../../scripts/jest/patchMessageChannel';

global.ReadableStream =
  require('web-streams-polyfill/ponyfill/es6').ReadableStream;
global.TextEncoder = require('util').TextEncoder;
global.TextDecoder = require('util').TextDecoder;

let webpackServerMap;
let ReactServerDOMServer;
let ReactServerScheduler;

describe('ReactFlightReplyBlobValidation', () => {
  beforeEach(() => {
    jest.resetModules();

    ReactServerScheduler = require('scheduler');
    patchMessageChannel(ReactServerScheduler);

    jest.mock('react', () => require('react/react.react-server'));
    jest.mock('react-server-dom-webpack/server', () =>
      require('react-server-dom-webpack/server.browser'),
    );
    const WebpackMock = require('./utils/WebpackMock');
    webpackServerMap = WebpackMock.webpackServerMap;
    require('react');
    ReactServerDOMServer = require('react-server-dom-webpack/server.browser');
    jest.resetModules();
    __unmockReact();
  });

  it('throws when a $B reference is backed by a short string', async () => {
    const formData = new FormData();
    formData.set('1', 'attacker-payload');
    formData.set('0', JSON.stringify(['$B1']));
    let error;
    try {
      await ReactServerDOMServer.decodeReply(formData, webpackServerMap);
    } catch (x) {
      error = x;
    }
    expect(error).toBeDefined();
    expect(error).toBeInstanceOf(Error);
    expect(typeof error.message).toBe('string');
    expect(error.message.length).toBeGreaterThan(0);
  });

  it('throws when a $B reference is backed by a longer string', async () => {
    const formData = new FormData();
    formData.set('1', '-'.repeat(50000));
    formData.set('0', JSON.stringify(['$B1']));
    let error;
    try {
      await ReactServerDOMServer.decodeReply(formData, webpackServerMap);
    } catch (x) {
      error = x;
    }
    expect(error).toBeDefined();
    expect(error).toBeInstanceOf(Error);
  });

  it('still decodes a $B reference when its backing entry is a real Blob', async () => {
    const blob = new Blob(['hello task'], {type: 'text/plain'});
    const formData = new FormData();
    formData.set('1', blob);
    formData.set('0', JSON.stringify(['$B1']));
    const result = await ReactServerDOMServer.decodeReply(
      formData,
      webpackServerMap,
    );
    expect(Array.isArray(result)).toBe(true);
    expect(result[0]).toBeInstanceOf(Blob);
  });
});
"""


def _write_fixture():
    FIXTURE_PATH.write_text(JEST_SPEC)


def _remove_fixture():
    if FIXTURE_PATH.exists():
        FIXTURE_PATH.unlink()


def setup_module(module):
    _write_fixture()


def teardown_module(module):
    _remove_fixture()


def _run_jest(pattern: str, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["yarn", "test", "--silent", "--no-watchman", pattern],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_blob_string_reference_rejected():
    """f2p: decoding a `$B` ref whose backing entry is a string must throw.

    On the base commit, `decodeReply` silently returns the string. After a
    correct fix it throws. We do not pin the exact error message so any
    reasonable type guard passes.
    """
    r = _run_jest("ReactFlightReplyBlobValidation-task-test")
    assert r.returncode == 0, (
        "Jest failed for the Blob validation spec:\n"
        f"--- stdout (tail) ---\n{r.stdout[-2000:]}\n"
        f"--- stderr (tail) ---\n{r.stderr[-2000:]}"
    )


def test_existing_reply_suite_still_passes():
    """p2p: the existing ReactFlightDOMReply-test suite still passes.

    Catches regressions where an over-eager fix breaks valid Blob/Reply
    decoding paths.
    """
    r = _run_jest("ReactFlightDOMReply-test")
    assert r.returncode == 0, (
        "Existing ReactFlightDOMReply suite failed after the change:\n"
        f"--- stdout (tail) ---\n{r.stdout[-2000:]}\n"
        f"--- stderr (tail) ---\n{r.stderr[-2000:]}"
    )


def test_repo_lint_changed_files():
    """p2p: `yarn linc` (lint changed files) passes.

    React's CI gates on lint of changed files. Catches style issues such
    as missing semicolons, double quotes (single quotes are the rule),
    or stray `console.log` calls in the agent's edits.
    """
    r = subprocess.run(
        ["yarn", "linc"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        "yarn linc failed on changed files:\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n"
        f"--- stderr ---\n{r.stderr[-2000:]}"
    )
