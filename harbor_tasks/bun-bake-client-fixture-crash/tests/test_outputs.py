"""
Task: bun-bake-client-fixture-crash
Repo: oven-sh/bun @ 923690e923b2f13e0815e8cf342748082058bede
PR:   28300

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/bun"
CLIENT = f"{REPO}/test/bake/client-fixture.mjs"
HARNESS = f"{REPO}/test/bake/bake-harness.ts"

# ---------------------------------------------------------------------------
# Shared helper: extract loadPage() and run it against a controlled HTTP server
# ---------------------------------------------------------------------------

EXTRACTOR_SCRIPT = textwrap.dedent("""\
import http from 'node:http';
import fs from 'node:fs';

const CLIENT_PATH = process.argv[2];
const TEST_MODE = process.argv[3];

const src = fs.readFileSync(CLIENT_PATH, 'utf8');

// Extract loadPage function using brace-depth matching
const startMatch = src.match(/async function loadPage\\s*\\([^)]*\\)\\s*\\{/);
if (!startMatch) {
  console.log('NO_FUNC:requests=0:writes=0');
  process.exit(0);
}
const startIdx = startMatch.index;
let depth = 0, endIdx = startIdx;
for (let i = startIdx; i < src.length; i++) {
  if (src[i] === '{') depth++;
  if (src[i] === '}') { depth--; if (depth === 0) { endIdx = i + 1; break; } }
}
const funcSrc = src.substring(startIdx, endIdx);

let requestCount = 0;
let writeCount = 0;

const server = http.createServer((req, res) => {
  requestCount++;
  if (TEST_MODE === 'null-ct') {
    // No content-type header at all
    res.writeHead(200);
    res.end('<html><head></head><body><script>1</script></body></html>');
  } else if (TEST_MODE === 'valid-charset') {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    res.end('<html><head></head><body><script>1</script></body></html>');
  } else if (TEST_MODE === 'retry') {
    if (requestCount <= 2) { req.socket.destroy(); return; }
    res.writeHead(200, { 'content-type': 'text/html' });
    res.end('<html><head></head><body><script>1</script></body></html>');
  } else if (TEST_MODE === 'valid') {
    res.writeHead(200, { 'content-type': 'text/html' });
    res.end('<html><head></head><body><script>1</script></body></html>');
  }
});

server.listen(0, '127.0.0.1', async () => {
  const port = server.address().port;
  globalThis.url = `http://127.0.0.1:${port}`;
  globalThis.window = {
    document: { write: (content) => { writeCount++; } }
  };
  globalThis.exitCodeMap = { reloadFailed: 34 };

  let exitCode = null;
  const origExit = process.exit;
  process.exit = (code) => { exitCode = code; throw new Error('__EXIT__'); };

  const timer = setTimeout(() => {
    process.exit = origExit;
    server.close();
    console.log(`TIMEOUT:requests=${requestCount}:writes=${writeCount}`);
    origExit(0);
  }, 15000);

  try {
    const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
    const testFn = new AsyncFunction(funcSrc + '\\nawait loadPage();');
    await testFn();
    clearTimeout(timer);
    console.log(`OK:requests=${requestCount}:writes=${writeCount}`);
  } catch (e) {
    clearTimeout(timer);
    if (e.message === '__EXIT__') {
      console.log(`EXIT:${exitCode}:requests=${requestCount}:writes=${writeCount}`);
    } else if (e instanceof TypeError) {
      console.log(`TYPEERROR:${e.message}:requests=${requestCount}:writes=${writeCount}`);
    } else if (e.cause && (e.cause.code === 'ECONNRESET' || e.cause.code === 'ECONNREFUSED')) {
      console.log(`CONN_ERROR:requests=${requestCount}:writes=${writeCount}`);
    } else {
      console.log(`ERROR:${e.constructor.name}:${e.message}:requests=${requestCount}:writes=${writeCount}`);
    }
  } finally {
    process.exit = origExit;
    server.close();
  }
});
""")


def _run_extractor(mode: str, timeout: int = 20) -> tuple:
    """Run extractor in given mode, return (status, request_count, write_count)."""
    script = Path("/tmp/extract_and_test.mjs")
    script.write_text(EXTRACTOR_SCRIPT)
    r = subprocess.run(
        ["node", str(script), CLIENT, mode],
        capture_output=True, text=True, timeout=timeout,
    )
    output = r.stdout.strip()
    if not output:
        return ("EMPTY", 0, 0)

    parts = output.split(":")
    status = parts[0]
    req = 0
    writes = 0
    for part in parts:
        if part.startswith("requests="):
            req = int(part.split("=")[1])
        if part.startswith("writes="):
            writes = int(part.split("=")[1])
    return (status, req, writes)


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """client-fixture.mjs must parse as valid JavaScript."""
    r = subprocess.run(
        ["node", "--check", CLIENT],
        capture_output=True, timeout=10,
    )
    assert r.returncode == 0, f"Syntax error:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_null_content_type_handled():
    """Null content-type header must not cause TypeError crash.

    The bug: loadPage() calls .match() on response.headers.get("content-type")
    without null check — TypeError when header is absent.
    Anti-stub: verifies the function actually fetched from the server.
    """
    status, req, _ = _run_extractor("null-ct")
    assert req >= 1, f"loadPage() never fetched from server (requests={req})"
    assert status in ("OK", "EXIT"), (
        f"Null content-type caused crash: status={status}"
    )


# [pr_diff] fail_to_pass
def test_retry_on_transient_failures():
    """loadPage() must retry fetch when server connection is refused/reset.

    Test server destroys the first 2 connections, then serves valid HTML.
    Anti-stub: verifies >=3 requests were made (2 failures + 1 success).
    """
    status, req, _ = _run_extractor("retry")
    assert req >= 3, (
        f"Expected >=3 requests (2 failures + 1 success), got {req} — no retry logic"
    )
    assert status == "OK", (
        f"Retry logic didn't recover after transient failures: status={status}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_valid_response_loads():
    """A normal response with valid content-type must load correctly."""
    status, req, writes = _run_extractor("valid")
    assert req >= 1, f"loadPage() never fetched (requests={req})"
    assert writes >= 1, f"document.write() never called (writes={writes})"
    assert status == "OK", f"Valid response failed: status={status}"


# [repo_tests] pass_to_pass
def test_valid_response_with_charset():
    """Response with 'text/html; charset=utf-8' content-type must load correctly."""
    status, req, writes = _run_extractor("valid-charset")
    assert req >= 1, f"loadPage() never fetched (requests={req})"
    assert writes >= 1, f"document.write() never called (writes={writes})"
    assert status == "OK", f"Content-type with charset failed: status={status}"


# ---------------------------------------------------------------------------
# Structural (pr_diff) — justified: require full bun runtime or process lifecycle
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_unhandled_rejection_handler():
    """Process must register an unhandledRejection handler.

    Structural justification: triggering an unhandled rejection requires the full
    client fixture lifecycle with happy-dom + IPC, which can't run without bun.
    """
    src = Path(CLIENT).read_text()
    assert "unhandledRejection" in src, "No unhandledRejection handler found"
    assert any(k in src for k in ("process.on", "process.once", "process.addListener")), \
        "unhandledRejection not registered on process"
    # Anti-stub: handler callback must have a meaningful body
    m = re.search(
        r'process\.(?:on|once|addListener)\s*\(\s*["\']unhandledRejection["\']\s*,'
        r'\s*(?:\([^)]*\)|[^,=]+)\s*=>\s*\{([\s\S]*?)\}',
        src,
    )
    assert m and len(m.group(1).strip()) >= 10, \
        "unhandledRejection handler is empty or a stub"


# [pr_diff] fail_to_pass
def test_exit_code_propagation():
    """Client exit code must be forwarded to OutputLineStream in bake-harness.ts.

    Structural justification: OutputLineStream is a Bun-internal class requiring
    building Bun from source (C++/Zig) — infeasible in test container.
    # AST-only because: bake-harness.ts requires full Bun runtime (C++/Zig build)
    """
    src = Path(HARNESS).read_text()
    # The fix must propagate the subprocess exit code to this.output.exitCode.
    # On the base commit, "output.exitCode" never appears (exitCode exists
    # elsewhere but is never assigned to the output stream).
    assert re.search(r'output\.exitCode\s*=', src), \
        "Client exit code not forwarded to OutputLineStream (need output.exitCode = ...)"


# ---------------------------------------------------------------------------
# Agent-config (agent_config) — coding conventions from test/CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass
def test_no_dynamic_import_in_client_fixture():
    """client-fixture.mjs must not use unnecessary dynamic import() calls.

    test/CLAUDE.md lines 218-220: only use dynamic import when specifically
    testing dynamic import behaviour. All imports must be static top-level.
    Structural justification: client-fixture.mjs is consumed as a subprocess
    fixture; dynamic imports would silently alter its module graph and loading
    behaviour without any observable runtime difference in the harness tests.
    """
    src = Path(CLIENT).read_text()
    # Dynamic import() looks like `import(` in expression position.
    # Static imports (`import foo from ...`) never have `(` directly after `import`.
    dynamic = re.findall(r'\bimport\s*\(', src)
    assert len(dynamic) == 0, (
        f"client-fixture.mjs uses dynamic import() ({len(dynamic)} occurrence(s)); "
        "use static top-level import statements instead (test/CLAUDE.md lines 218-220)"
    )
