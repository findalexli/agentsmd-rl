"""Behavioral tests for asyncHandler fix.

These tests execute actual code to verify the behavior changes.
"""
import subprocess
import json
from pathlib import Path

REPO = "/workspace/express-async-handler"


def _run_node_test(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.js"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def test_sync_error_caught():
    """Sync errors thrown by handler are caught and passed to next() (fail_to_pass)."""
    r = _run_node_test("""
const asyncHandler = require('./index.js');

let capturedError = null;
const mockNext = (err) => { capturedError = err; };
const mockReq = {};
const mockRes = {};

// Create a sync handler that throws
const syncThrower = (req, res) => {
  throw new Error('sync error');
};

// Wrap it with asyncHandler
const wrapped = asyncHandler(syncThrower);

try {
  wrapped(mockReq, mockRes, mockNext);
} catch (e) {
  console.log(JSON.stringify({error: e.message, caughtByWrapper: false}));
  process.exit(0);
}

// Check if error was captured by next()
if (capturedError && capturedError.message === 'sync error') {
  console.log(JSON.stringify({caughtByNext: true, message: capturedError.message}));
} else if (capturedError) {
  console.log(JSON.stringify({caughtByNext: true, wrongMessage: capturedError.message}));
} else {
  console.log(JSON.stringify({caughtByNext: false, error: null}));
}
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    # After the fix, the error should be caught and passed to next()
    assert result.get("caughtByNext") is True, f"Sync error not caught by next(): {result}"
    assert result.get("message") == "sync error", f"Wrong error message: {result}"


def test_async_error_still_works():
    """Async errors (Promise rejections) continue to work (pass_to_pass)."""
    r = _run_node_test("""
const asyncHandler = require('./index.js');

let capturedError = null;
const mockNext = (err) => { capturedError = err; };
const mockReq = {};
const mockRes = {};

// Create an async handler that rejects
const asyncRejecter = async (req, res) => {
  throw new Error('async error');
};

// Wrap it with asyncHandler
const wrapped = asyncHandler(asyncRejecter);

// Call it and wait for promise chain
const ret = wrapped(mockReq, mockRes, mockNext);

if (ret && ret.then) {
  ret.then(() => {
    // After promise settles, check if error was caught
    setTimeout(() => {
      if (capturedError && capturedError.message === 'async error') {
        console.log(JSON.stringify({caughtByNext: true, message: capturedError.message}));
      } else {
        console.log(JSON.stringify({caughtByNext: false, error: capturedError}));
      }
    }, 10);
  });
} else {
  console.log(JSON.stringify({hasPromise: false}));
}
""")
    # Async test needs a bit more time, so run it differently
    r = subprocess.run(
        ["node", "-e", """
const asyncHandler = require('./index.js');

let capturedError = null;
const mockNext = (err) => { capturedError = err; };

const asyncRejecter = async (req, res) => {
  throw new Error('async error');
};

const wrapped = asyncHandler(asyncRejecter);
const ret = wrapped({}, {}, mockNext);

// Wait for promise chain to process
setTimeout(() => {
  if (capturedError && capturedError.message === 'async error') {
    console.log('PASS: async error caught');
  } else {
    console.log('FAIL: async error not caught, got: ' + JSON.stringify(capturedError));
    process.exit(1);
  }
}, 50);
"""],
        capture_output=True, text=True, timeout=5, cwd=REPO,
    )
    assert r.returncode == 0, f"Async error test failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Async error not properly caught: {r.stdout}"


def test_return_value_available():
    """The return value from the handler is still available (pass_to_pass)."""
    r = _run_node_test("""
const asyncHandler = require('./index.js');

const mockReq = {};
const mockRes = {};
const mockNext = () => {};

// Create a handler that returns a value
const returnHandler = (req, res) => {
  return { some: 'value', id: 123 };
};

// Wrap it
const wrapped = asyncHandler(returnHandler);
const ret = wrapped(mockReq, mockRes, mockNext);

// Check return value is preserved
if (ret && ret.some === 'value' && ret.id === 123) {
  console.log(JSON.stringify({returnValuePreserved: true, value: ret}));
} else {
  console.log(JSON.stringify({returnValuePreserved: false, got: ret}));
}
""")
    assert r.returncode == 0, f"Return value test failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result.get("returnValuePreserved") is True, f"Return value not preserved: {result}"


def test_no_thrown_error_escapes():
    """No sync error escapes the wrapper uncaught (fail_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const asyncHandler = require('./index.js');

let syncErrorCaught = false;

const throwingHandler = (req, res) => {
  throw new Error('should be caught');
};

const wrapped = asyncHandler(throwingHandler);

try {
  wrapped({}, {}, (err) => {
    if (err && err.message === 'should be caught') {
      console.log('PASS: error passed to next');
    } else {
      console.log('FAIL: wrong error: ' + err);
      process.exit(1);
    }
  });
} catch (e) {
  console.log('FAIL: error escaped wrapper: ' + e.message);
  process.exit(1);
}
"""],
        capture_output=True, text=True, timeout=5, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed with error: {r.stderr}"
    assert "PASS" in r.stdout, f"Error escaped wrapper: {r.stdout}"


def test_file_exists():
    """The main index.js file exists (static check)."""
    assert Path(f"{REPO}/index.js").exists(), "index.js not found"
