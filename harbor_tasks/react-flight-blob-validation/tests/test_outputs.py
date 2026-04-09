"""
Task: react-flight-blob-validation
Repo: react @ c80a07509582daadf275f36ffe7a88c3b12e9db4
PR:   36055

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/react"
SOURCE_FILE = "packages/react-server/src/ReactFlightReplyServer.js"
CODES_FILE = "scripts/error-codes/codes.json"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_blob_validation_behavior():
    """$B reference backed by a string must be rejected by decodeReply."""
    test_js = textwrap.dedent("""\
        'use strict';

        import {patchMessageChannel} from '../../../../scripts/jest/patchMessageChannel';

        global.ReadableStream =
          require('web-streams-polyfill/ponyfill/es6').ReadableStream;
        global.TextEncoder = require('util').TextEncoder;
        global.TextDecoder = require('util').TextDecoder;

        let webpackServerMap;
        let ReactServerDOMServer;
        let ReactServerScheduler;

        describe('BlobGuardTest', () => {
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
            ReactServerDOMServer = require('react-server-dom-webpack/server.browser');
          });

          it('rejects long string backing entry for $B reference', async () => {
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
            expect(error.message).toContain('Blob');
          });

          it('rejects short string backing entry for $B reference', async () => {
            const formData = new FormData();
            formData.set('1', 'not-a-blob');
            formData.set('0', JSON.stringify(['$B1']));
            let error;
            try {
              await ReactServerDOMServer.decodeReply(formData, webpackServerMap);
            } catch (x) {
              error = x;
            }
            expect(error).toBeDefined();
          });
        });
    """)
    test_dir = Path(REPO) / "packages/react-server-dom-webpack/src/__tests__"
    test_file = test_dir / "BlobGuardTest-test.js"
    test_file.write_text(test_js)
    try:
        r = subprocess.run(
            ["yarn", "test", "--silent", "--no-watchman", "BlobGuardTest"],
            cwd=REPO,
            capture_output=True,
            timeout=90,
        )
        stdout = r.stdout.decode(errors="replace")
        stderr = r.stderr.decode(errors="replace")
        assert r.returncode == 0, (
            f"Jest blob guard test failed (rc={r.returncode}):\n"
            f"{stdout[-2000:]}\n{stderr[-2000:]}"
        )
    finally:
        test_file.unlink(missing_ok=True)


# [pr_diff] fail_to_pass
def test_blob_guard_in_source():
    """The $B case in parseModelString must validate instanceof Blob."""
    src = Path(f"{REPO}/{SOURCE_FILE}").read_text()
    # Find the case 'B' block and check for instanceof Blob
    # The pattern: within the Blob handling block, there must be an instanceof check
    blob_case = re.search(
        r"case\s+['\"]B['\"]:\s*\{(.*?)\n\s*\}",
        src,
        re.DOTALL,
    )
    assert blob_case is not None, "Could not find case 'B' block in parseModelString"
    block = blob_case.group(1)
    assert "instanceof Blob" in block, (
        "The $B case must check 'instanceof Blob' before returning the backing entry"
    )
    # Verify it throws on non-Blob (not just a silent return)
    assert "throw" in block or "Error" in block, (
        "The $B case must throw an error when backing entry is not a Blob"
    )


# [agent_config] fail_to_pass — .claude/skills/extract-errors/SKILL.md:3,8-12
def test_error_code_registered():
    """Error codes file must contain an entry for the Blob validation error."""
    codes = json.loads(Path(f"{REPO}/{CODES_FILE}").read_text())
    # Find any error code whose message mentions Blob validation
    blob_messages = [
        (code, msg)
        for code, msg in codes.items()
        if "Blob" in msg and "not" in msg.lower()
    ]
    assert len(blob_messages) >= 1, (
        "codes.json must contain an error code for Blob type validation "
        f"(e.g., 'Referenced Blob is not a Blob.'). Found codes: {list(codes.keys())[-5:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_reply_tests():
    """Upstream ReactFlightDOMReply tests still pass."""
    r = subprocess.run(
        ["yarn", "test", "--silent", "--no-watchman", "ReactFlightDOMReply"],
        cwd=REPO,
        capture_output=True,
        timeout=90,
    )
    stdout = r.stdout.decode(errors="replace")
    stderr = r.stderr.decode(errors="replace")
    assert r.returncode == 0, (
        f"Upstream ReactFlightDOMReply tests failed (rc={r.returncode}):\n"
        f"{stdout[-2000:]}\n{stderr[-2000:]}"
    )
