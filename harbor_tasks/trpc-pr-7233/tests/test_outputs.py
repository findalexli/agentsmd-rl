"""
Test suite for trpc#7233: buffered chunks discarded on stream close in httpBatchStreamLink

Verifies behavior:
1. Buffered chunks are preserved when a stream closes normally (not aborted)
2. A descriptive error is thrown when stream closes before head data is received

These tests use tsx to run TypeScript code that imports and calls the actual
jsonl module functions, then assert on the returned values.
"""

import subprocess
import sys
import json
import os
import tempfile

REPO = "/workspace/trpc"
STREAM_DIR = f"{REPO}/packages/server/src/unstable-core-do-not-import/stream"


def run_ts_test(ts_code, timeout=120):
    """Run TypeScript code using tsx and return parsed JSON output."""
    # Write code to a temp file to avoid shell quoting issues
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False, dir=STREAM_DIR) as f:
        f.write(ts_code)
        temp_file = f.name

    try:
        result = subprocess.run(
            ["pnpm", "exec", "tsx", temp_file],
            cwd=STREAM_DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout + result.stderr

        # Try to parse JSON from output
        for line in output.strip().split('\n'):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue

        return {"passed": False, "error": f"No JSON output. Exit: {result.returncode}. Output: {output[:500]}"}
    except subprocess.TimeoutExpired:
        return {"passed": False, "error": "Test timed out"}
    except Exception as e:
        return {"passed": False, "error": str(e)}
    finally:
        os.unlink(temp_file)


def test_buffered_chunks_preserved_on_close():
    """
    F2P: Verifies that buffered chunks are delivered on normal stream completion.

    Creates a stream that yields values 0-4 quickly (so they buffer) and closes
    normally. Without the fix, some values would be discarded. With the fix,
    all 5 values are delivered.
    """
    ts_code = '''
import { jsonlStreamProducer, jsonlStreamConsumer } from './jsonl.js';
import SuperJSON from 'superjson';

async function runTest() {
  const abortController = new AbortController();
  const data = {
    0: Promise.resolve({
      [Symbol.asyncIterator]: async function* () {
        for (let i = 0; i < 5; i++) {
          yield i;
        }
      },
    }),
  };

  const stream = jsonlStreamProducer({
    data,
    serialize: (v) => SuperJSON.serialize(v),
  });

  const [head] = await jsonlStreamConsumer({
    from: stream,
    deserialize: (v) => SuperJSON.deserialize(v),
    abortController,
  });

  const iterable = await head[0];
  const values: number[] = [];

  for await (const item of iterable) {
    values.push(item);
    await new Promise((r) => setTimeout(r, 10));
  }

  const expected = [0, 1, 2, 3, 4];
  const passed = values.length === expected.length &&
    values.every((v, i) => v === expected[i]);

  console.log(JSON.stringify({ passed, values, expected }));
}

runTest().catch((err) => {
  console.log(JSON.stringify({ passed: false, values: [], expected: [0,1,2,3,4], error: err.message }));
  process.exit(1);
});
'''

    result = run_ts_test(ts_code)

    assert result.get("passed"), (
        f"Buffered chunks not preserved. "
        f"Expected: {result.get('expected')}, Got: {result.get('values')}. "
        f"Error: {result.get('error', 'none')}"
    )


def test_stream_close_before_head_gives_descriptive_error():
    """
    F2P: Verifies that stream close before head rejects with descriptive Error.

    Creates a ReadableStream that closes immediately without emitting any data.
    Without the fix, the rejection is undefined. With the fix, it's an Error
    with message 'Stream closed before head was received'.
    """
    ts_code = '''
import { jsonlStreamConsumer } from './jsonl.js';

async function runTest() {
  const abortController = new AbortController();

  // Create a ReadableStream that closes immediately with no data
  const emptyStream = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.close();
    },
  });

  let rejection;
  try {
    await jsonlStreamConsumer({
      from: emptyStream,
      abortController,
    });
    rejection = { message: 'NOT_REJECTED' };
  } catch (e) {
    rejection = e;
  }

  const isError = rejection instanceof Error;
  const hasCorrectMessage = isError && rejection.message === 'Stream closed before head was received';
  const passed = isError && hasCorrectMessage;

  console.log(JSON.stringify({
    passed,
    isError,
    rejectionMessage: isError ? rejection.message : String(rejection),
    expectedMessage: 'Stream closed before head was received'
  }));
}

runTest().catch((err) => {
  console.log(JSON.stringify({
    passed: false,
    isError: false,
    rejectionMessage: err.message,
    expectedMessage: 'Stream closed before head was received',
    error: err.message
  }));
  process.exit(1);
});
'''

    result = run_ts_test(ts_code)

    assert result.get("passed"), (
        f"Stream close before head did not produce descriptive error. "
        f"Is Error: {result.get('isError')}, "
        f"Message: {result.get('rejectionMessage')}, "
        f"Expected: '{result.get('expectedMessage')}'. "
        f"Error: {result.get('error', 'none')}"
    )


def test_repo_builds():
    """P2P: Repo builds successfully."""
    r = subprocess.run(
        ["pnpm", "build", "--filter=@trpc/server"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    output = r.stdout + r.stderr
    assert r.returncode == 0, f"Build failed:\n{output[-1000:]}"


def test_repo_typecheck():
    """P2P: All packages typecheck successfully."""
    r = subprocess.run(
        ["pnpm", "typecheck-packages"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    output = r.stdout + r.stderr
    assert r.returncode == 0, f"Typecheck failed:\n{output[-1000:]}"


def test_repo_lint():
    """P2P: Repo lints successfully."""
    r = subprocess.run(
        ["pnpm", "lint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    output = r.stdout + r.stderr
    assert r.returncode == 0, f"Lint failed:\n{output[-1000:]}"


if __name__ == "__main__":
    sys.exit(subprocess.run(["python3", "-m", "pytest", __file__, "-v"]).returncode)