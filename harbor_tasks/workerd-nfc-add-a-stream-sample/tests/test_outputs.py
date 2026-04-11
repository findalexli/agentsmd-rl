"""
Task: workerd-nfc-add-a-stream-sample
Repo: cloudflare/workerd @ 87abde7e73188dd0543944255fa6c0632d857fe8
PR:   5874

Add a web-streams sample demonstrating ReadableStream, TransformStream,
and byte streams with sync/async variants plus a README documenting endpoints.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/workerd"
SAMPLE_DIR = Path(REPO) / "samples" / "web-streams"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

def test_syntax_check():
    """streams-util.js can be imported as a valid ES module in Node.js."""
    js_file = SAMPLE_DIR / "streams-util.js"
    assert js_file.exists(), "samples/web-streams/streams-util.js must exist"
    # Dynamic import validates syntax and module structure
    result = subprocess.run(
        ["node", "--input-type=module", "-e",
         f"await import('file://{js_file}')"],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, f"streams-util.js failed to import: {result.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_sync_stream_produces_chunks():
    """createSyncLoremStream(N) yields exactly N chunks of non-empty text."""
    script = """
import { createSyncLoremStream } from 'file:///workspace/workerd/samples/web-streams/streams-util.js';
const stream = createSyncLoremStream(5);
const reader = stream.getReader();
let chunks = 0;
let totalBytes = 0;
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  chunks++;
  totalBytes += value.byteLength;
}
console.log(JSON.stringify({ chunks, totalBytes }));
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["chunks"] == 5, f"Expected 5 chunks, got {data['chunks']}"
    assert data["totalBytes"] > 100, f"Expected substantial text, got {data['totalBytes']} bytes"


def test_uppercase_transform():
    """createSyncUppercaseTransform converts text to uppercase via pipeThrough."""
    script = """
import { createSyncLoremStream, createSyncUppercaseTransform }
  from 'file:///workspace/workerd/samples/web-streams/streams-util.js';
const stream = createSyncLoremStream(2);
const transform = createSyncUppercaseTransform();
const transformed = stream.pipeThrough(transform);
const reader = transformed.getReader();
const decoder = new TextDecoder();
let text = '';
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  text += decoder.decode(value, { stream: true });
}
text += decoder.decode();
// All alphabetic chars should be uppercase
const hasLower = /[a-z]/.test(text);
const hasUpper = /[A-Z]/.test(text);
console.log(JSON.stringify({ hasLower, hasUpper, length: text.length }));
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert not data["hasLower"], "Uppercase transform should not leave lowercase letters"
    assert data["hasUpper"], "Output should contain uppercase letters"
    assert data["length"] > 50, f"Expected substantial output, got {data['length']} chars"


def test_byte_stream_supports_byob():
    """createSyncLoremByteStream creates a byte-type stream supporting BYOB reads."""
    script = """
import { createSyncLoremByteStream }
  from 'file:///workspace/workerd/samples/web-streams/streams-util.js';
const stream = createSyncLoremByteStream(3);
const reader = stream.getReader({ mode: 'byob' });
let totalBytes = 0;
let chunks = 0;
while (true) {
  const { done, value } = await reader.read(new Uint8Array(8192));
  if (done) break;
  totalBytes += value.byteLength;
  chunks++;
}
console.log(JSON.stringify({ chunks, totalBytes }));
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, f"Byte stream BYOB read failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["chunks"] >= 1, "Byte stream should produce at least 1 chunk"
    assert data["totalBytes"] > 50, f"Expected substantial output, got {data['totalBytes']} bytes"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documents the sample endpoints
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# Pass-to-pass (static) — config references modules
# ---------------------------------------------------------------------------

def test_config_references_modules():
    """config.capnp must declare both worker.js and streams-util.js modules."""
    config = SAMPLE_DIR / "config.capnp"
    assert config.exists(), "samples/web-streams/config.capnp must exist"
    content = config.read_text()
    assert "worker.js" in content or "worker" in content, \
        "config.capnp should reference the worker module"
    assert "streams-util" in content, \
        "config.capnp should reference the streams-util module"
    assert "Workerd" in content or "workerd" in content, \
        "config.capnp should use the Workerd schema"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — sample structure follows repo conventions
# ---------------------------------------------------------------------------

def test_sample_structure():
    """Sample directory follows the same structure as other samples."""
    # Check that all required files exist
    assert (SAMPLE_DIR / "README.md").exists(), \
        "samples/web-streams/README.md must exist"
    assert (SAMPLE_DIR / "config.capnp").exists(), \
        "samples/web-streams/config.capnp must exist"
    assert (SAMPLE_DIR / "worker.js").exists(), \
        "samples/web-streams/worker.js must exist"
    assert (SAMPLE_DIR / "streams-util.js").exists(), \
        "samples/web-streams/streams-util.js must exist"

    # README should follow the pattern of other samples (has running instructions)
    readme = (SAMPLE_DIR / "README.md").read_text()
    assert "#" in readme, "README.md should have a title header"
    assert "config.capnp" in readme, \
        "README.md should reference config.capnp in running instructions"


def test_streams_util_exports():
    """streams-util.js exports all required functions for the sample."""
    js_file = SAMPLE_DIR / "streams-util.js"
    assert js_file.exists(), "streams-util.js must exist"
    content = js_file.read_text()

    # Check for all required exports mentioned in the PR
    required_exports = [
        "createSyncLoremStream",
        "createAsyncLoremStream",
        "createSyncLoremByteStream",
        "createAsyncLoremByteStream",
        "createSyncUppercaseTransform",
        "createAsyncUppercaseTransform",
    ]
    for export in required_exports:
        assert f"export function {export}" in content, \
            f"streams-util.js must export {export}"


def test_worker_syntax_and_imports():
    """worker.js is valid ES module with correct imports from streams-util."""
    worker_file = SAMPLE_DIR / "worker.js"
    assert worker_file.exists(), "worker.js must exist"
    content = worker_file.read_text()

    # Check it imports from streams-util
    assert 'from "streams-util"' in content, \
        "worker.js should import from streams-util module"

    # Check it exports a default fetch handler
    assert "export default" in content, \
        "worker.js should export a default object"
    assert "async fetch(request)" in content, \
        "worker.js should have a fetch handler"

    # Validate syntax by trying to import as module (like we do for streams-util.js)
    # Note: worker.js imports from "streams-util" which won't resolve in Node.js,
    # so we just check the file parses as valid JS by reading it
    result = subprocess.run(
        ["node", "--check", str(worker_file)],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, f"worker.js has syntax errors: {result.stderr}"
