"""Behavioral tests for facebook/react#36055.

The PR adds a defense-in-depth check in `parseModelString` of
`ReactFlightReplyServer.js` so that a `$B` (Blob) reference whose backing
FormData entry is *not* a Blob is rejected.  Without the fix, an attacker
can stash a large string in a FormData slot and reference it via `$B`,
and `decodeReply` will silently return that string instead of a Blob.
After the fix, decoding such a payload throws.

These tests exercise the behavior end-to-end via Jest.  We drop custom
Jest specs into the React repo, run them through `yarn test`, and tear
them down again so the working tree stays clean.
"""

import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/react")
TESTS_DIR = REPO / "packages/react-server-dom-webpack/src/__tests__"

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

FIXTURE_NAME_1 = "ReactFlightReplyBlobValidation-task-test.js"
FIXTURE_PATH_1 = TESTS_DIR / FIXTURE_NAME_1

# A standalone Jest spec that mirrors the setup boilerplate of the
# existing ReactFlightDOMReply-test.js but only contains the security
# behaviour we care about.
JEST_SPEC_1 = r"""
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
    expect(typeof error.message).toBe('string');
    expect(error.message.length).toBeGreaterThan(0);
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

# Second fixture: the PR author's own test case, extracted to a standalone
# spec so it can serve as an independent fail-to-pass signal.
FIXTURE_NAME_2 = "ReactFlightReplyPrAddedBlobTest-task-test.js"
FIXTURE_PATH_2 = TESTS_DIR / FIXTURE_NAME_2

JEST_SPEC_2 = r"""
'use strict';

import {patchMessageChannel} from '../../../../scripts/jest/patchMessageChannel';

global.ReadableStream =
  require('web-streams-polyfill/ponyfill/es6').ReadableStream;
global.TextEncoder = require('util').TextEncoder;
global.TextDecoder = require('util').TextDecoder;

let webpackServerMap;
let ReactServerDOMServer;
let ReactServerScheduler;

describe('ReactFlightReplyPrAddedBlobTest', () => {
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

  it('cannot deserialize a Blob reference backed by a string', async () => {
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
    expect(typeof error.message).toBe('string');
    expect(error.message.length).toBeGreaterThan(0);
  });
});
"""


def _write_fixtures():
    FIXTURE_PATH_1.write_text(JEST_SPEC_1)
    FIXTURE_PATH_2.write_text(JEST_SPEC_2)


def _remove_fixtures():
    for p in (FIXTURE_PATH_1, FIXTURE_PATH_2):
        if p.exists():
            p.unlink()


def setup_module(module):
    _write_fixtures()


def teardown_module(module):
    _remove_fixtures()


def _run_jest(pattern, timeout=600):
    return subprocess.run(
        ["yarn", "test", "--silent", "--no-watchman", pattern],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# =========================================================================
# f2p tests
# =========================================================================

def test_blob_string_reference_rejected():
    """f2p: decoding a $B ref whose backing entry is a string must throw.

    On the base commit decodeReply silently returns the string, so the
    two "throws" test cases in the spec fail and Jest exits non-zero.
    After a correct fix all three cases pass.
    """
    r = _run_jest("ReactFlightReplyBlobValidation-task-test")
    assert r.returncode == 0, (
        "Jest spec for Blob validation failed:\n"
        f"--- stdout (tail) ---\n{r.stdout[-2000:]}\n"
        f"--- stderr (tail) ---\n{r.stderr[-2000:]}"
    )


def test_pr_added_blob_reference_rejected():
    """f2p: PR author's test case — long string in a $B slot must throw.

    The PR author added a test named 'cannot deserialize a Blob reference
    backed by a string'.  We run it as a standalone spec so it exercises
    the same decodeReply path with a 50 000-character string.  On base
    no error is thrown → Jest fails.  On gold the validation rejects the
    payload → Jest passes.
    """
    r = _run_jest("ReactFlightReplyPrAddedBlobTest-task-test")
    assert r.returncode == 0, (
        "Jest spec for PR-added Blob test failed:\n"
        f"--- stdout (tail) ---\n{r.stdout[-2000:]}\n"
        f"--- stderr (tail) ---\n{r.stderr[-2000:]}"
    )


# =========================================================================
# p2p tests (regression guards)
# =========================================================================

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

    React's CI gates on lint of changed files.  Catches style issues such
    as missing semicolons, double quotes, or stray console.log calls.
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
