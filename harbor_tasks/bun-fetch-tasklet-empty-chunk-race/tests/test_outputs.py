"""
Task: bun-fetch-tasklet-empty-chunk-race
Repo: bun @ 770893d28ff94013abed5520482848609a6872f9
PR: 28982

Verify that the empty non-terminal chunk race condition fix is present in FetchTasklet.zig.
The bug caused pipeline(Readable.fromWeb(res.body), ...) to stall when an empty
chunk raced with the streaming callback.
"""

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

def test_empty_chunk_guard_present():
    """The fix adds a guard to skip empty non-terminal chunks in onBodyReceived.

    The race condition occurred when:
    1. HTTP thread writes to scheduled_response_buffer and enqueues onProgressUpdate
    2. JS thread touches res.body -> onStartStreaming drains the buffer
    3. onProgressUpdate task runs and finds empty buffer

    Without the guard, ByteStream.onData was called with len=0, which caused
    native-readable.ts handleNumberResult(0) to not push(), leaving node:stream
    state.reading=true forever, stalling the pipeline.
    """
    src = Path(TARGET_FILE).read_text()

    # The fix adds this specific guard before onBodyReceived():
    # if (this.scheduled_response_buffer.list.items.len == 0 and
    #     this.result.has_more and
    #     this.result.isSuccess())
    # {
    #     return;
    # }

    # Check for the key components of the guard
    guard_components = [
        "scheduled_response_buffer.list.items.len == 0",
        "this.result.has_more",
        "this.result.isSuccess()",
        "stale-task race",  # The comment explaining the race
        "onStartStreamingHTTPResponseBodyCallback",  # Referenced in comment
    ]

    for component in guard_components:
        assert component in src, f"Missing guard component: {component}"


def test_guard_placement_correct():
    """The guard must be placed before onBodyReceived() call inside is_waiting_body block."""
    src = Path(TARGET_FILE).read_text()

    # Find the is_waiting_body section
    assert "if (this.is_waiting_body)" in src, "Missing is_waiting_body check"

    # The guard should be INSIDE the is_waiting_body block, BEFORE onBodyReceived()
    # We verify by checking the comment comes before the onBodyReceived call
    waiting_body_pos = src.find("if (this.is_waiting_body)")
    guard_comment_pos = src.find("stale-task race")
    onbody_call_pos = src.find("try this.onBodyReceived()", waiting_body_pos)

    assert guard_comment_pos > waiting_body_pos, "Guard comment not inside is_waiting_body block"
    assert guard_comment_pos < onbody_call_pos, "Guard not placed before onBodyReceived() call"


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
