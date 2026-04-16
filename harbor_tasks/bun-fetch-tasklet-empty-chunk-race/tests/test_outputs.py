"""
Task: bun-fetch-tasklet-empty-chunk-race
Repo: bun @ 770893d28ff94013abed5520482848609a6872f9
PR: 28982

Verify that the empty non-terminal chunk race condition fix is present in FetchTasklet.zig.
The bug caused pipeline(Readable.fromWeb(res.body), ...) to stall when an empty
chunk raced with the streaming callback.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
TARGET_FILE = f"{REPO}/src/bun.js/webcore/fetch/FetchTasklet.zig"


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax / compilation checks
# -----------------------------------------------------------------------------

def test_zig_syntax_check():
    """FetchTasklet.zig must have valid Zig syntax."""
    src = Path(TARGET_FILE).read_text()
    # Basic structural checks for valid Zig
    assert "pub const FetchTasklet" in src, "Missing FetchTasklet struct"
    assert "is_waiting_body" in src, "Missing is_waiting_body field check"
    assert "onBodyReceived" in src, "Missing onBodyReceived call"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral verification
# -----------------------------------------------------------------------------

def _find_guard_condition(src):
    """Find and parse the guard condition in onBodyReceived.

    Returns the guard block text if found, None otherwise.
    The guard skips processing when buffer is empty and more data is coming.
    """
    # Pattern to find the guard block inside is_waiting_body
    # It should be before try this.onBodyReceived()
    # Look for a return statement preceded by buffer empty check
    pattern = r'if\s*\([^)]*\.list\.items\.len\s*==\s*0[^}]*return\s*;'
    match = re.search(pattern, src, re.DOTALL)
    return match.group(0) if match else None


def _parse_guard_semantics(guard_text):
    """Parse the guard to extract its semantic components.

    Returns a dict with:
    - buffer_empty: bool (checks buffer length == 0)
    - has_more_check: bool (checks has_more is true)
    - success_check: bool (checks result is successful)
    - returns_early: bool (causes early return)
    """
    semantics = {
        'buffer_empty': False,
        'has_more_check': False,
        'success_check': False,
        'returns_early': False,
    }

    if not guard_text:
        return semantics

    # Check for buffer empty condition: list.items.len == 0 or similar
    if re.search(r'\.list\.items\.len\s*==\s*0', guard_text):
        semantics['buffer_empty'] = True

    # Check for has_more check (result.has_more or similar)
    if re.search(r'result\.has_more|has_more', guard_text):
        semantics['has_more_check'] = True

    # Check for success check (result.isSuccess() or !result.isError() or similar)
    if re.search(r'result\.isSuccess\(\)|result\.isError\(\)|result\.status', guard_text):
        semantics['success_check'] = True

    # Check for early return
    if re.search(r'return\s*;', guard_text):
        semantics['returns_early'] = True

    return semantics


def test_empty_chunk_guard_present():
    """The fix adds a guard to skip empty non-terminal chunks in onBodyReceived.

    The guard checks:
    1. The scheduled_response_buffer is empty (length == 0)
    2. The response indicates more data is coming (has_more is true)
    3. The result is successful

    If all conditions are met, we return early to avoid calling onBodyReceived
    with empty data (which would cause the race condition stall).
    """
    src = Path(TARGET_FILE).read_text()

    # Find the guard block
    guard_text = _find_guard_condition(src)

    # Parse its semantics
    semantics = _parse_guard_semantics(guard_text)

    # Verify all required semantic components are present
    assert semantics['buffer_empty'], \
        "Guard must check that buffer is empty (list.items.len == 0)"
    assert semantics['has_more_check'], \
        "Guard must check that more data is coming (has_more)"
    assert semantics['success_check'], \
        "Guard must check that result is successful (isSuccess/isError/status)"
    assert semantics['returns_early'], \
        "Guard must return early when conditions are met"


def _find_guard_position(src):
    """Find the position of the guard relative to key landmarks.

    Returns (guard_start, guard_end, onbody_start) or None if not found.
    """
    # Find is_waiting_body block
    waiting_body_match = re.search(r'if\s*\(\s*this\.is_waiting_body\s*\)', src)
    if not waiting_body_match:
        return None
    waiting_body_start = waiting_body_match.start()

    # Find the guard (buffer empty check followed by return)
    guard_match = re.search(
        r'if\s*\([^)]*\.list\.items\.len\s*==\s*0[^}]*return\s*;',
        src,
        re.DOTALL
    )
    if not guard_match:
        return None
    guard_start = guard_match.start()
    guard_end = guard_match.end()

    # Find onBodyReceived call after the guard
    onbody_match = re.search(r'try\s+this\.onBodyReceived\(\)', src[guard_end:])
    if not onbody_match:
        return None
    onbody_start = guard_end + onbody_match.start()

    return (guard_start, guard_end, onbody_start, waiting_body_start)


def test_guard_placement_correct():
    """The guard must be placed inside is_waiting_body block, before onBodyReceived().

    The guard should be:
    1. Inside the is_waiting_body conditional block
    2. Before the onBodyReceived() call

    This ensures the race condition is handled before we try to process
    an empty chunk that was already drained by the streaming callback.
    """
    src = Path(TARGET_FILE).read_text()

    positions = _find_guard_position(src)
    assert positions is not None, \
        "Guard not found: expected 'if (buffer_len == 0) { return; }' pattern before onBodyReceived()"

    guard_start, guard_end, onbody_start, waiting_body_start = positions

    # Guard must be inside is_waiting_body block
    assert guard_start > waiting_body_start, \
        "Guard must be inside is_waiting_body block"

    # Guard must be before onBodyReceived call
    assert guard_end < onbody_start, \
        "Guard must be placed before onBodyReceived() call"


def test_terminal_zero_length_chunk_not_affected():
    """Terminal zero-length chunks (has_more=false) must still be processed.

    The guard should ONLY skip empty chunks when has_more is true (more data coming).
    When has_more is false, the buffer might be empty at the end of the response,
    and this is NOT the race condition - it's normal end-of-stream behavior.
    """
    src = Path(TARGET_FILE).read_text()

    # Find the guard condition
    guard_match = re.search(
        r'if\s*\([^)]*\.list\.items\.len\s*==\s*0[^}]*return\s*;',
        src,
        re.DOTALL
    )
    assert guard_match is not None, "Guard not found"

    guard_text = guard_match.group(0)

    # The guard must include a has_more check
    # This ensures that when has_more is false, we don't skip processing
    assert re.search(r'has_more', guard_text), \
        "Guard must check has_more to avoid skipping terminal zero-length chunks"

    # Verify the guard is an AND condition (all must be true)
    # This means has_more is part of the guard, so terminal chunks won't trigger it
    assert 'and' in guard_text.lower() or '&&' in guard_text, \
        "Guard must use AND logic so has_more check actually prevents skipping terminal chunks"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) - regression + anti-stub
# -----------------------------------------------------------------------------

def test_not_stub():
    """FetchTasklet implementation must have substantial logic, not just stubs."""
    src = Path(TARGET_FILE).read_text()

    # Count function definitions and substantial code blocks
    functions = src.count("pub fn ") + src.count("fn ")
    comments = src.count("//")

    # Should have multiple functions and comments
    assert functions >= 5, f"Too few functions ({functions}), likely a stub"
    assert comments >= 10, f"Too few comments ({comments}), likely a stub"

    # Check for key struct fields that indicate real implementation
    assert "scheduled_response_buffer" in src, "Missing scheduled_response_buffer field"
    assert "result:" in src or "result :" in src, "Missing result field"


def test_zig_compiles():
    """Zig code must compile without errors (basic syntax validation)."""
    # Use zig fmt to validate syntax (doesn't require full build)
    r = subprocess.run(
        ["zig", "fmt", "--check", TARGET_FILE],
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Zig fmt check failed:\n{r.stderr.decode()}"


def test_stream_api_not_broken():
    """Basic streaming must still work after the fix (no regression).

    This ensures the guard doesn't break normal streaming behavior.
    """
    # Create a simple test script that uses streaming
    test_script = '''
import { serve } from "bun";

const server = serve({
    port: 0,
    fetch(req) {
        const body = new ReadableStream({
            start(controller) {
                controller.enqueue(new TextEncoder().encode("hello"));
                controller.close();
            }
        });
        return new Response(body);
    }
});

const res = await fetch(`http://localhost:${server.port}`);
const text = await res.text();
if (text !== "hello") {
    console.error("Expected 'hello', got:", text);
    process.exit(1);
}
console.log("Stream test passed");
server.stop();
'''

    # Write and run the test
    test_file = "/tmp/stream_test.ts"
    Path(test_file).write_text(test_script)

    r = subprocess.run(
        ["bun", "run", test_file],
        capture_output=True,
        timeout=30,
    )

    # This is a P2P test - it should work both before and after the fix
    # We mainly care that it doesn't crash or hang
    assert r.returncode == 0, f"Stream test failed:\n{r.stderr.decode()}"
    assert b"Stream test passed" in r.stdout, "Stream test didn't complete correctly"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI/CD checks from the repo
# -----------------------------------------------------------------------------

def test_repo_lint():
    """Repo's JavaScript lint passes (pass_to_pass).

    Runs oxlint on src/js to verify no lint errors.
    This is part of the repo's CI (bun run lint).
    Uses 'bun x' instead of bunx to avoid PATH issues.
    """
    r = subprocess.run(
        ["bun", "x", "oxlint", "--config=oxlint.json", "--format=github", "src/js"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_banned_words():
    """Repo's banned words check passes (pass_to_pass).

    Runs internal test to verify no banned words are used.
    This is part of the repo's CI format check.
    """
    r = subprocess.run(
        ["bun", "test", "test/internal/ban-words.test.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Banned words check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_zig_fmt():
    """Repo's Zig code passes zig fmt check (pass_to_pass).

    Runs zig fmt --check on the target file to verify formatting.
    This is part of the repo's CI format check.
    """
    r = subprocess.run(
        ["zig", "fmt", "--check", TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Zig fmt check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_prettier():
    """Repo's TypeScript files pass prettier check (pass_to_pass).

    Runs prettier --check on scripts directory to verify formatting.
    This is part of the repo's CI format check.
    """
    r = subprocess.run(
        ["bun", "x", "prettier", "--check", "--plugin=prettier-plugin-organize-imports",
         "--config=.prettierrc", "scripts/*.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_fetch_body_stream():
    """Repo's fetch body stream tests pass (pass_to_pass).

    Runs bun test on test/js/web/fetch/body-stream.test.ts.
    This validates body streaming functionality in FetchTasklet.zig.
    """
    r = subprocess.run(
        ["bun", "test", "test/js/web/fetch/body-stream.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Fetch body stream test failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_fetch_response():
    """Repo's fetch response tests pass (pass_to_pass).

    Runs bun test on test/js/web/fetch/response.test.ts.
    This validates Response body handling that uses FetchTasklet.
    """
    r = subprocess.run(
        ["bun", "test", "test/js/web/fetch/response.test.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Fetch response test failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_fetch_body():
    """Repo's fetch body tests pass (pass_to_pass).

    Runs bun test on test/js/web/fetch/body.test.ts.
    This validates Request/Response body mixin functionality.
    """
    r = subprocess.run(
        ["bun", "test", "test/js/web/fetch/body.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Fetch body test failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_fetch_body_clone():
    """Repo's fetch body clone tests pass (pass_to_pass).

    Runs bun test on test/js/web/fetch/body-clone.test.ts.
    This validates body cloning functionality which is related to
    streaming and the FetchTasklet response handling.
    """
    r = subprocess.run(
        ["bun", "test", "test/js/web/fetch/body-clone.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Fetch body clone test failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_fetch_stream_fast_path():
    """Repo's fetch stream fast path tests pass (pass_to_pass).

    Runs bun test on test/js/web/fetch/stream-fast-path.test.ts.
    This validates byte blob loading and streaming fast paths
    related to body handling in FetchTasklet.
    """
    r = subprocess.run(
        ["bun", "test", "test/js/web/fetch/stream-fast-path.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Fetch stream fast path test failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"