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


# [pr_diff] fail_to_pass
def test_unhandled_rejection_handler():
    """Process must register an unhandledRejection handler that exits with reloadFailed code.

    Behavioral test: Verifies the handler is present and syntactically valid by:
    1. Checking the handler is registered on process
    2. Verifying the handler body contains calls to process.exit with reloadFailed
    3. Executing a test that confirms the handler exits with code 34
    """
    src = Path(CLIENT).read_text()

    # Check that handler exists - basic structural check
    has_handler = 'process.on("unhandledRejection"' in src or "process.on('unhandledRejection'" in src
    assert has_handler, "No unhandledRejection handler registered in client-fixture.mjs"

    # Extract the handler using brace-depth matching (more robust than regex)
    handler_start = src.find('process.on("unhandledRejection"')
    if handler_start == -1:
        handler_start = src.find("process.on('unhandledRejection'")
    assert handler_start != -1, "Could not locate unhandledRejection handler"

    # Find the opening brace of the handler function
    brace_start = src.find('{', handler_start)
    assert brace_start != -1, "Could not find handler body start"

    # Match braces to find handler body
    depth = 1
    brace_end = brace_start + 1
    for i in range(brace_start + 1, min(brace_start + 1000, len(src))):
        if src[i] == '{':
            depth += 1
        elif src[i] == '}':
            depth -= 1
            if depth == 0:
                brace_end = i
                break

    handler_body = src[brace_start + 1:brace_end]

    # Verify handler body has actual logic (not empty/stub)
    assert len(handler_body.strip()) >= 10, "unhandledRejection handler body is too short/empty"

    # Behavioral verification: the handler should call process.exit with reloadFailed
    has_exit = "process.exit" in handler_body
    has_reload_failed = "reloadFailed" in handler_body or "exitCodeMap" in handler_body
    assert has_exit and has_reload_failed, (
        "unhandledRejection handler must call process.exit with reloadFailed code"
    )

    # Execute behavioral test: construct and run the handler
    # This verifies the handler code is syntactically valid and does what it claims
    test_script = textwrap.dedent(f"""\
    import {{ exitCodeMap }} from '/workspace/bun/test/bake/exit-code-map.mjs';

    // Register the handler extracted from client-fixture.mjs
    process.on('unhandledRejection', reason => {{{handler_body}}});

    // Trigger an unhandled rejection
    Promise.reject(new Error('test rejection'));

    // Give it time to process
    setTimeout(() => {{
      console.log('NO_EXIT');
      process.exit(0);
    }}, 500);
    """)

    script_path = Path("/tmp/test_unhandled_rejection.mjs")
    script_path.write_text(test_script)

    r = subprocess.run(
        ["node", str(script_path)],
        capture_output=True, timeout=5,
    )

    # The handler should cause exit with code 34 (reloadFailed)
    assert r.returncode == 34, (
        f"unhandledRejection handler did not exit with reloadFailed code (34), got {r.returncode}"
    )


# [pr_diff] fail_to_pass
def test_exit_code_propagation():
    """Client exit code must be forwarded to output stream in bake-harness.ts.

    Behavioral verification: The harness must capture the subprocess exit code
    and make it available on the output stream. This test verifies:
    1. The harness accesses proc.exited (subprocess lifecycle)
    2. The output stream receives the exit code assignment

    Multiple implementation patterns are acceptable:
    - Direct: proc.exited.then(code => this.output.exitCode = code)
    - Async/await: this.output.exitCode = await proc.exited
    - Via variable: const code = await proc.exited; this.output.exitCode = code
    """
    src = Path(HARNESS).read_text()

    # Step 1: Verify subprocess exit is being monitored
    # The harness must wait for proc.exited (a Promise<number>) to resolve
    has_proc_exited_access = "proc.exited" in src or "subprocess.exited" in src
    assert has_proc_exited_access, (
        "Must access subprocess exit state via proc.exited; "
        "client exit code not being captured from subprocess lifecycle"
    )

    # Step 2: Verify exit code flows to output stream
    # Look for any pattern where output's exitCode property is assigned from subprocess exit
    has_exit_code_wiring = (
        # Async/await pattern: this.output.exitCode = await proc.exited
        bool(re.search(r'output\.exitCode\s*=\s*(?:await\s*)?(?:proc|subprocess)\.exited', src)) or
        # Promise .then() pattern: proc.exited.then(code => ... output.exitCode = code)
        bool(re.search(r'(?:proc|subprocess)\.exited.*\.then.*output\.exitCode\s*=', src, re.DOTALL)) or
        # Via intermediate variable: const code = await proc.exited; output.exitCode = code
        bool(re.search(r'(?:proc|subprocess)\.exited.*[\s\S]{0,100}output\.exitCode\s*=', src, re.DOTALL))
    )

    assert has_exit_code_wiring, (
        "Client exit code must be forwarded to output stream; "
        "need wiring from proc.exited to output.exitCode property"
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
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_prettier_format():
    """Repo's JavaScript/TypeScript files must pass prettier format check.

    Origin: .github/workflows/format.yml — autofix.ci runs prettier on all PRs.
    Ensures code style consistency in bake test files.
    """
    r = subprocess.run(
        ["npx", "--yes", "prettier@3.6.2", "--check", CLIENT, HARNESS],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_oxlint():
    """Repo's JavaScript/TypeScript files must pass oxlint correctness checks.

    Origin: .github/workflows/lint.yml — runs oxlint with correctness rules.
    Ensures no critical lint errors (undefined vars, duplicate keys, etc).
    """
    r = subprocess.run(
        ["npx", "--yes", "oxlint@0.16.1", "--format=github", CLIENT, HARNESS],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # oxlint returns 0 on success (no errors), 1 on errors
    # Warnings don't cause non-zero exit by default
    assert r.returncode == 0, f"oxlint found errors:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_bake_harness_syntax():
    """bake-harness.ts must parse as valid TypeScript (syntax only).

    Origin: CI typecheck — verifies TypeScript files are syntactically valid
    before the build process. Uses tsc --noEmit for type-only checking.
    """
    r = subprocess.run(
        ["npx", "--yes", "typescript@5.9.2", "--noEmit", "--skipLibCheck", HARNESS],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Skip if tsc fails due to missing types/config - we just check it parses
    # The key is that it doesn't crash with syntax errors
    if "error TS" in r.stderr and "Cannot find" not in r.stderr:
        assert False, f"TypeScript syntax errors found:\n{r.stderr[-500:]}"
    # If it fails due to missing modules/types, that's OK for syntax check
    assert True


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
