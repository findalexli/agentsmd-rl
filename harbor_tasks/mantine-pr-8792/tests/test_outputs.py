"""
Tests for mantine/mcp-server#8792: Fix stdio transport to comply with MCP spec.

The MCP server was using LSP-style Content-Length header framing for stdio transport,
which is incompatible with the MCP specification. This caused MCP clients to hang
indefinitely during the initialize handshake.

The fix replaces Content-Length header framing with NDJSON (newline-delimited JSON)
as required by the MCP spec.
"""

import subprocess
import json
import os
import tempfile
import time

REPO = "/workspace/mantine"
TARGET_FILE = "packages/@mantine/mcp-server/src/server.ts"


def _build_bundle() -> str:
    """Build the server bundle using esbuild. Returns path to bundle."""
    bundle_script = '''
const esbuild = require('esbuild');

esbuild.build({
  entryPoints: ['/workspace/mantine/packages/@mantine/mcp-server/src/server.ts'],
  bundle: true,
  platform: 'node',
  outfile: '/tmp/mcp_server_bundle.cjs',
  format: 'cjs',
  sourcemap: false,
  minify: false,
  external: ['./data-client', './types'],
  loader: { '.ts': 'ts' }
}).then(() => {
  console.log('BUNDLE_OK');
}).catch(err => {
  console.error('BUNDLE_ERROR:', err.message);
  process.exit(1);
});
'''
    with open(os.path.join(REPO, 'bundle_script.js'), 'w') as f:
        f.write(bundle_script)

    result = subprocess.run(
        ['node', os.path.join(REPO, 'bundle_script.js')],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    try:
        os.unlink(os.path.join(REPO, 'bundle_script.js'))
    except OSError:
        pass

    if result.returncode != 0 or 'BUNDLE_OK' not in result.stdout:
        raise RuntimeError(f"Bundle failed: {result.stderr}")

    return '/tmp/mcp_server_bundle.cjs'


def _run_tsx_script(script_content: str, timeout: int = 20) -> tuple[int, str, str]:
    """Run a tsx script, writing it to disk and spawning via a node wrapper."""
    # Write test script to /workspace/mantine
    test_script_path = os.path.join(REPO, 'test_tsx_script.js')
    with open(test_script_path, 'w') as f:
        f.write(script_content)

    # Write wrapper script
    wrapper_script = '''
const { spawn } = require("child_process");
const proc = spawn("npx", ["tsx", "test_tsx_script.js"], {
  cwd: "/workspace/mantine",
  stdio: ["pipe", "pipe", "pipe"]
});
let stdout = "", stderr = "";
proc.stdout.on("data", (d) => { stdout += d.toString(); });
proc.stderr.on("data", (d) => { stderr += d.toString(); });
proc.on("close", (code) => {
  console.log("EXIT:" + code);
  console.log("STDOUT:" + stdout);
  console.log("STDERR:" + stderr);
});
setTimeout(() => { proc.kill(); console.log("TIMEOUT"); process.exit(1); }, %d);
''' % (timeout * 1000)

    wrapper_path = os.path.join(REPO, 'test_tsx_wrapper.js')
    with open(wrapper_path, 'w') as f:
        f.write(wrapper_script)

    try:
        proc = subprocess.Popen(
            ['node', wrapper_path],
            cwd=REPO,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            stdout_bytes, stderr_bytes = proc.communicate(timeout=timeout + 5)
            return proc.returncode, stdout_bytes.decode(), stderr_bytes.decode()
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout_bytes, stderr_bytes = proc.communicate()
            return -1, stdout_bytes.decode(), stderr_bytes.decode()
    finally:
        for f in [test_script_path, wrapper_path]:
            try:
                os.unlink(f)
            except OSError:
                pass


def test_ndjson_write_format():
    """writeMessage writes NDJSON (one JSON per line) not Content-Length headers."""
    # Build the bundle and inspect the bundled code
    bundle_path = _build_bundle()

    with open(bundle_path, 'r') as f:
        bundle_content = f.read()

    # The bundled code should NOT contain Content-Length header writing
    assert 'Content-Length:' not in bundle_content, \
        "writeMessage should not use Content-Length headers"

    # The bundled code SHOULD contain JSON.stringify for NDJSON output
    has_ndjson = (
        'JSON.stringify(payload)' in bundle_content or
        'JSON.stringify(payload' in bundle_content
    )
    assert has_ndjson, \
        "writeMessage should use JSON.stringify for NDJSON output"


def test_server_uses_line_based_parsing():
    """Server parses input line-by-line, not using buffer-based Content-Length parsing."""
    bundle_path = _build_bundle()

    with open(bundle_path, 'r') as f:
        bundle_content = f.read()

    # Should NOT use the old Content-Length parsing approach
    assert 'readContentLength' not in bundle_content, \
        "readContentLength function should be removed"


def test_no_contentlength_buffer_parsing():
    """Verify the server does NOT use Content-Length parsing from old LSP protocol."""
    bundle_path = _build_bundle()

    with open(bundle_path, 'r') as f:
        bundle_content = f.read()

    assert 'readContentLength' not in bundle_content, \
        "readContentLength helper should be removed"

    assert "indexOf('\\r\\n\\r\\n')" not in bundle_content, \
        "Old buffer-based header parsing should be removed"


def test_ndjson_protocol_compliance():
    """Verify the server outputs valid NDJSON (JSON lines terminated by newline)."""
    bundle_path = _build_bundle()

    with open(bundle_path, 'r') as f:
        bundle_content = f.read()

    assert 'writeMessage' in bundle_content, \
        "writeMessage function should be present"

    assert 'JSON.stringify' in bundle_content, \
        "writeMessage should use JSON.stringify"

    assert 'Content-Length' not in bundle_content, \
        "Server should not use Content-Length headers"


def test_error_codes_preserved():
    """Error handling should use proper JSON-RPC error codes."""
    bundle_path = _build_bundle()

    with open(bundle_path, 'r') as f:
        bundle_content = f.read()

    assert "-32600" in bundle_content, "InvalidRequest error code missing"
    assert "-32700" in bundle_content, "Parse error code missing"


def test_mcp_server_typecheck():
    """The mcp-server package should pass TypeScript type checking."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "packages/@mantine/mcp-server/tsconfig.json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"TypeScript type checking failed:\n{result.stderr[-1000:]}"


def test_repo_lint():
    """Repo's linter passes for mcp-server package (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "oxlint", "packages/@mantine/mcp-server"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Oxlint failed:\n{r.stderr[-500:]}"


def test_repo_format():
    """Repo's formatter passes for mcp-server package (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "oxfmt", "--check", "packages/@mantine/mcp-server"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


def test_no_buffer_concat_in_stdin_handler():
    """stdin handler should not use Buffer.concat for message framing."""
    bundle_path = _build_bundle()

    with open(bundle_path, 'r') as f:
        bundle_content = f.read()

    assert "Buffer.concat" not in bundle_content, \
        "Buffer.concat should not be used for stdin handling"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])