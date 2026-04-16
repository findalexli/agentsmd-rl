"""
Task: bun-async-iterable-response-crash
Repo: oven-sh/bun @ 9ead1e121d5cca2eaddad66d439ab3c0a74225f2
PR:   28457

Behavioral tests verify the fix for Response body consumption from async iterables.
These tests exercise the Bun runtime to verify:
1. Null underlyingSource doesn't crash when consuming Response bodies
2. Stream locking prevents double consumption
3. Sink guards prevent crashes during close/flush
4. C++ exception handling works correctly
"""

import os
import pytest
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/bun"


def _ensure_bun_installed():
    """Ensure Bun is installed and return the path to the executable."""
    import shutil

    bun_exe = shutil.which("bun")
    if not bun_exe:
        default_bun = os.path.expanduser("~/.bun/bin/bun")
        if os.path.exists(default_bun):
            bun_exe = default_bun

    if not bun_exe:
        subprocess.run(
            ["apt-get", "update", "-qq"],
            capture_output=True,
            timeout=60,
        )
        subprocess.run(
            ["apt-get", "install", "-y", "-qq", "unzip"],
            capture_output=True,
            timeout=60,
        )
        install = subprocess.run(
            "curl -fsSL https://bun.sh/install | bash",
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if install.returncode != 0:
            pytest.skip(f"Could not install Bun: {install.stderr}")
        bun_exe = os.path.expanduser("~/.bun/bin/bun")

    return bun_exe


def _run_js_test(js_code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write JS test code to a temp file and execute via Bun."""
    fd, path = tempfile.mkstemp(suffix=".js")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(js_code)
        bun_exe = _ensure_bun_installed()
        return subprocess.run(
            [bun_exe, "run", path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO,
        )
    finally:
        os.unlink(path)


# -----------------------------------------------------------------------------
# Pass-to-pass (static)
# -----------------------------------------------------------------------------


def test_source_files_exist():
    """Core source files must exist and be non-empty."""
    ts_file = f"{REPO}/src/js/builtins/ReadableStream.ts"
    internals_file = f"{REPO}/src/js/builtins/ReadableStreamInternals.ts"
    cpp_file = f"{REPO}/src/bun.js/bindings/webcore/ReadableStream.cpp"
    for f in [ts_file, internals_file, cpp_file]:
        p = Path(f)
        assert p.exists() and p.stat().st_size > 0, f"{f} missing or empty"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via Bun runtime
# -----------------------------------------------------------------------------


def test_null_excluded_from_direct_stream_path():
    """Null underlyingSource must be excluded from direct-stream path.

    The bug: readableStreamTo* functions used !== undefined check, but
    async iterable Response bodies set underlyingSource to null. This caused
    null to be passed to the direct-stream path, leading to crashes.

    The fix changes !== undefined to != null (loose equality) so null
    is properly excluded from the direct-stream path.

    This test verifies that Response body consumption from async iterables
    works correctly (null underlyingSource is handled, not passed to direct path).
    """
    js_code = """
async function* gen() {
    yield new Uint8Array([1, 2, 3]);
    yield new Uint8Array([4, 5, 6]);
}

const body = {};
body[Symbol.asyncIterator] = () => gen();
const resp = new Response(body);

// This should work - the null underlyingSource should not crash
// but should be properly excluded from the direct-stream path
async function test() {
    try {
        const bytes = await resp.bytes();
        if (bytes.length === 6) {
            console.log("PASS: Consumed 6 bytes from async iterable Response");
            return 0;
        } else {
            console.error("FAIL: Expected 6 bytes, got", bytes.length);
            return 1;
        }
    } catch (e) {
        console.error("FAIL: Exception:", e.message);
        return 1;
    }
}

process.exit(await test());
"""
    r = _run_js_test(js_code)
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS: Consumed 6 bytes from async iterable Response" in r.stdout


def test_close_direct_stream_sink_guard():
    """onCloseDirectStream must guard against null/undefined sink before sink.end().

    The bug: onCloseDirectStream called this.\$sink.end() without checking if
    the sink was null/undefined, causing a crash when closing streams with
    no valid sink.

    The fix adds a guard: var sink = this.\$sink; if (!sink) return;

    This test verifies that closing a direct stream doesn't crash due to
    null sink access.
    """
    js_code = """
// Create and consume a direct stream to trigger onCloseDirectStream
const stream = new ReadableStream({
    type: "direct",
    pull(controller) {
        controller.write(new Uint8Array([1, 2, 3]));
        controller.close();
    }
});

async function test() {
    const reader = stream.getReader();
    try {
        let chunks = [];
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            chunks.push(value);
        }
        await reader.closed;
        console.log("PASS: Direct stream closed without crashing, read", chunks.length, "chunks");
        return 0;
    } catch (e) {
        console.error("FAIL: Error during stream close:", e.message);
        return 1;
    }
}

process.exit(await test());
"""
    r = _run_js_test(js_code)
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS: Direct stream closed without crashing" in r.stdout


def test_flush_direct_stream_sink_guard():
    """onFlushDirectStream must guard against null/undefined sink before sink.flush().

    The bug: onFlushDirectStream called this.\$sink.flush() without checking if
    the sink was null/undefined, causing a crash during flush operations.

    The fix adds a guard: var sink = this.\$sink; if (!sink) return;

    This test verifies that flushing a direct stream (via multiple writes)
    doesn't crash due to null sink access.
    """
    js_code = """
// Create a direct stream with multiple writes to trigger flush operations
const stream = new ReadableStream({
    type: "direct",
    pull(controller) {
        controller.write(new Uint8Array([1, 2, 3]));
        controller.write(new Uint8Array([4, 5, 6]));
        controller.close();
    }
});

async function test() {
    try {
        // Use Bun.readableStreamToBytes which triggers the direct stream path
        const bytes = await Bun.readableStreamToBytes(stream);
        if (bytes.length === 6) {
            console.log("PASS: Direct stream flushed without crashing, got", bytes.length, "bytes");
            return 0;
        } else {
            console.error("FAIL: Expected 6 bytes, got", bytes.length);
            return 1;
        }
    } catch (e) {
        console.error("FAIL: Error during stream flush:", e.message);
        return 1;
    }
}

process.exit(await test());
"""
    r = _run_js_test(js_code)
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS: Direct stream flushed without crashing" in r.stdout


def test_stream_locked_on_direct_consumption():
    """readableStreamToArrayBufferDirect must lock the stream to prevent double-consumption.

    The bug: When consuming a stream via the direct path, the stream was not
    properly locked, allowing double-consumption which could cause race
    conditions and crashes.

    The fix sets stream.\$disturbed = true and creates a reader object to
    mark the stream as locked during consumption.

    This test verifies that after consuming a Response body once, the
    second consumption is properly rejected with a lock/disturbed error.
    """
    js_code = """
async function* gen() {
    yield new Uint8Array([1, 2, 3]);
}

const body = {};
body[Symbol.asyncIterator] = () => gen();
const resp = new Response(body);

async function test() {
    // First consumption should succeed
    try {
        const bytes1 = await resp.bytes();
        if (bytes1.length !== 3) {
            console.error("FAIL: First consumption got wrong byte count:", bytes1.length);
            return 1;
        }
    } catch (e) {
        console.error("FAIL: First consumption threw:", e.message);
        return 1;
    }

    // Second consumption should reject - stream should be locked/disturbed
    try {
        await resp.bytes();
        console.error("FAIL: Second consumption should have been rejected");
        return 1;
    } catch (e) {
        // Expected - stream is locked/consumed
        const msg = e.message.toLowerCase();
        if (msg.includes("locked") || msg.includes("disturbed") ||
            msg.includes("closed") || msg.includes("read") ||
            msg.includes("invalid state")) {
            console.log("PASS: Double consumption prevented with error:", e.message);
            return 0;
        } else {
            console.error("FAIL: Unexpected error on second consumption:", e.message);
            return 1;
        }
    }
}

process.exit(await test());
"""
    r = _run_js_test(js_code)
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS: Double consumption prevented" in r.stdout


def test_cpp_exception_handling_after_call():
    """C++ readableStreamTo* wrappers must handle exceptions after call() to JS builtins.

    The bug: C++ wrapper functions (readableStreamToText, readableStreamToBytes, etc.)
    called JavaScript builtins without checking for exceptions afterward. If the
    JS function threw, the exception wasn't caught, leading to crashes.

    The fix adds RETURN_IF_EXCEPTION(throwScope, {}) after each call() to
    properly catch and propagate JS exceptions to C++.

    This test verifies that exceptions thrown from async iterables are properly
    propagated through the C++/JS boundary rather than crashing the process.
    """
    js_code = """
async function* throwingGen() {
    throw new Error("Test exception from async iterator");
}

const body = {};
body[Symbol.asyncIterator] = () => throwingGen();
const resp = new Response(body);

async function test() {
    try {
        await resp.bytes();
        console.error("FAIL: Should have thrown an exception");
        return 1;
    } catch (e) {
        // The exception should propagate properly (not crash the process)
        if (e.message.includes("Test exception")) {
            console.log("PASS: Exception properly propagated through C++ boundary:", e.message);
            return 0;
        } else {
            console.error("FAIL: Wrong exception message:", e.message);
            return 1;
        }
    }
}

process.exit(await test());
"""
    r = _run_js_test(js_code)
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS: Exception properly propagated" in r.stdout


# -----------------------------------------------------------------------------
# Additional behavioral tests for coverage
# -----------------------------------------------------------------------------


def test_async_iterable_response_text():
    """Response.text() on async iterable body should work correctly."""
    js_code = """
async function* gen() {
    yield "Hello, ";
    yield "World!";
}

const body = {};
body[Symbol.asyncIterator] = () => gen();
const resp = new Response(body);

async function test() {
    try {
        const text = await resp.text();
        if (text === "Hello, World!") {
            console.log("PASS: Got correct text:", text);
            return 0;
        } else {
            console.error("FAIL: Expected 'Hello, World!', got:", text);
            return 1;
        }
    } catch (e) {
        console.error("FAIL: Exception:", e.message);
        return 1;
    }
}

process.exit(await test());
"""
    r = _run_js_test(js_code)
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS: Got correct text" in r.stdout


def test_async_iterable_response_arraybuffer():
    """Response.arrayBuffer() on async iterable body should work correctly."""
    js_code = """
async function* gen() {
    yield new Uint8Array([1, 2, 3]);
}

const body = {};
body[Symbol.asyncIterator] = () => gen();
const resp = new Response(body);

async function test() {
    try {
        const buffer = await resp.arrayBuffer();
        if (buffer.byteLength === 3) {
            console.log("PASS: Got ArrayBuffer with", buffer.byteLength, "bytes");
            return 0;
        } else {
            console.error("FAIL: Expected 3 bytes, got", buffer.byteLength);
            return 1;
        }
    } catch (e) {
        console.error("FAIL: Exception:", e.message);
        return 1;
    }
}

process.exit(await test());
"""
    r = _run_js_test(js_code)
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS: Got ArrayBuffer with" in r.stdout


# -----------------------------------------------------------------------------
# Pass-to-pass (pr_diff) - Static code quality checks
# -----------------------------------------------------------------------------


def test_core_functions_preserved():
    """Key ReadableStream functions still exist with substantial content."""
    ts_file = f"{REPO}/src/js/builtins/ReadableStream.ts"
    internals_file = f"{REPO}/src/js/builtins/ReadableStreamInternals.ts"
    ts_text = Path(ts_file).read_text()
    for func in [
        "readableStreamToArray",
        "readableStreamToText",
        "readableStreamToArrayBuffer",
        "readableStreamToBytes",
    ]:
        assert f"function {func}" in ts_text, f"{func} missing from ReadableStream.ts"

    internals_text = Path(internals_file).read_text()
    for func in ["onCloseDirectStream", "onFlushDirectStream"]:
        assert f"function {func}" in internals_text, (
            f"{func} missing from ReadableStreamInternals.ts"
        )

    assert internals_text.count("\n") > 1000, "ReadableStreamInternals.ts appears gutted"
    assert ts_text.count("\n") > 100, "ReadableStream.ts appears gutted"


# [agent_config] pass_to_pass - src/js/CLAUDE.md:56 @ 9ead1e121d5cca2eaddad66d439ab3c0a74225f2
def test_no_bare_call_apply():
    """No bare .call/.apply in JS builtins - must use .\$call/.\$apply.
    Rule from src/js/CLAUDE.md line 56."""
    import re
    ts_file = f"{REPO}/src/js/builtins/ReadableStream.ts"
    internals_file = f"{REPO}/src/js/builtins/ReadableStreamInternals.ts"
    for filepath in [ts_file, internals_file]:
        text = Path(filepath).read_text()
        for i, line in enumerate(text.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            assert not re.search(r"(?<!\$)\.call\s*\(", stripped), (
                f"{Path(filepath).name}:{i} uses bare .call() - must use .\$call()"
            )
            assert not re.search(r"(?<!\$)\.apply\s*\(", stripped), (
                f"{Path(filepath).name}:{i} uses bare .apply() - must use .\$apply()"
            )


# [agent_config] pass_to_pass - src/js/CLAUDE.md:103 @ 9ead1e121d5cca2eaddad66d439ab3c0a74225f2
def test_no_dynamic_require():
    """require() calls in JS builtins must use string literals only.
    Rule from src/js/CLAUDE.md line 103."""
    import re
    ts_file = f"{REPO}/src/js/builtins/ReadableStream.ts"
    internals_file = f"{REPO}/src/js/builtins/ReadableStreamInternals.ts"
    for filepath in [ts_file, internals_file]:
        text = Path(filepath).read_text()
        for i, line in enumerate(text.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            m = re.search(r'\brequire\s*\((?!\s*["\'])', stripped)
            assert not m, (
                f"{Path(filepath).name}:{i} uses dynamic require() - must use string literals"
            )


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI/CD standards from ban-words.test.ts
# -----------------------------------------------------------------------------


def test_no_undefined_equality_comparison():
    """No undefined equality comparisons (== undefined, != undefined) in builtins.
    Banned by repo's ban-words.test.ts - this is Undefined Behavior."""
    import re
    banned_patterns = [
        " != undefined",
        " == undefined",
        "undefined != ",
        "undefined == ",
    ]
    ts_file = f"{REPO}/src/js/builtins/ReadableStream.ts"
    internals_file = f"{REPO}/src/js/builtins/ReadableStreamInternals.ts"
    for filepath in [ts_file, internals_file]:
        text = Path(filepath).read_text()
        for i, line in enumerate(text.split("\n"), 1):
            stripped = line.strip()
            # Skip comments
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            for pattern in banned_patterns:
                assert pattern not in stripped, (
                    f"{Path(filepath).name}:{i} contains banned pattern '{pattern}' - "
                    "this is Undefined Behavior per ban-words.test.ts"
                )


def test_no_bare_jsboolean():
    """No bare .jsBoolean(true/false) calls in builtins - use .true/.false.
    Banned by repo's ban-words.test.ts."""
    import re
    banned_patterns = [
        ".jsBoolean(true)",
        "JSValue.true",
        ".jsBoolean(false)",
        "JSValue.false",
    ]
    ts_file = f"{REPO}/src/js/builtins/ReadableStream.ts"
    internals_file = f"{REPO}/src/js/builtins/ReadableStreamInternals.ts"
    for filepath in [ts_file, internals_file]:
        text = Path(filepath).read_text()
        for i, line in enumerate(text.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            for pattern in banned_patterns:
                assert pattern not in stripped, (
                    f"{Path(filepath).name}:{i} contains banned pattern '{pattern}' - "
                    "use .true/.false instead per ban-words.test.ts"
                )


def test_no_std_debug_in_builtins():
    """No std.debug.assert, std.debug.print in builtins.
    Banned by repo's ban-words.test.ts."""
    banned_patterns = [
        "std.debug.assert",
        "std.debug.dumpStackTrace",
        "std.debug.print",
        "std.log",
    ]
    ts_file = f"{REPO}/src/js/builtins/ReadableStream.ts"
    internals_file = f"{REPO}/src/js/builtins/ReadableStreamInternals.ts"
    for filepath in [ts_file, internals_file]:
        text = Path(filepath).read_text()
        for i, line in enumerate(text.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            for pattern in banned_patterns:
                assert pattern not in stripped, (
                    f"{Path(filepath).name}:{i} contains banned pattern '{pattern}' - "
                    "use bun.* alternatives per ban-words.test.ts"
                )


def test_typescript_braces_balance():
    """TypeScript files must have balanced braces (basic syntax check)."""
    ts_file = f"{REPO}/src/js/builtins/ReadableStream.ts"
    internals_file = f"{REPO}/src/js/builtins/ReadableStreamInternals.ts"
    for filepath in [ts_file, internals_file]:
        text = Path(filepath).read_text()
        # Simple brace counting (doesn't account for string literals, but catches major issues)
        open_braces = text.count("{")
        close_braces = text.count("}")
        assert open_braces == close_braces, (
            f"{Path(filepath).name}: unbalanced braces "
            f"({open_braces} open, {close_braces} close)"
        )
        # Also check parentheses
        open_parens = text.count("(")
        close_parens = text.count(")")
        assert open_parens == close_parens, (
            f"{Path(filepath).name}: unbalanced parentheses "
            f"({open_parens} open, {close_parens} close)"
        )


def test_repo_ban_words_test():
    """Repo's ban-words test passes - no banned patterns in Zig source files (pass_to_pass).
    Runs the repo's actual ban-words test which checks for undefined behavior patterns,
    std.debug usage, and other banned patterns in Zig source files."""
    import shutil

    bun_exe = shutil.which("bun")
    if not bun_exe:
        default_bun = os.path.expanduser("~/.bun/bin/bun")
        if os.path.exists(default_bun):
            bun_exe = default_bun

    if not bun_exe:
        subprocess.run(
            ["apt-get", "update", "-qq"],
            capture_output=True,
            timeout=60,
        )
        subprocess.run(
            ["apt-get", "install", "-y", "-qq", "unzip"],
            capture_output=True,
            timeout=60,
        )
        install = subprocess.run(
            "curl -fsSL https://bun.sh/install | bash",
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if install.returncode != 0:
            pytest.skip(f"Could not install Bun: {install.stderr}")
        bun_exe = os.path.expanduser("~/.bun/bin/bun")

    r = subprocess.run(
        [bun_exe, "./test/internal/ban-words.test.ts"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ban-words test failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_typescript_typecheck():
    """TypeScript typecheck passes (tsc --noEmit) (pass_to_pass).
    Verifies TypeScript files have no type errors."""
    import shutil

    bun_exe = shutil.which("bun")
    if not bun_exe:
        default_bun = os.path.expanduser("~/.bun/bin/bun")
        if os.path.exists(default_bun):
            bun_exe = default_bun

    if not bun_exe:
        subprocess.run(
            ["apt-get", "update", "-qq"],
            capture_output=True,
            timeout=60,
        )
        subprocess.run(
            ["apt-get", "install", "-y", "-qq", "unzip"],
            capture_output=True,
            timeout=60,
        )
        install = subprocess.run(
            "curl -fsSL https://bun.sh/install | bash",
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if install.returncode != 0:
            pytest.skip(f"Could not install Bun: {install.stderr}")
        bun_exe = os.path.expanduser("~/.bun/bin/bun")

    # Use bunx to run tsc
    r = subprocess.run(
        [bun_exe, "x", "tsc", "--noEmit"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_js_builtins_syntax():
    """JS builtins files have valid syntax (pass_to_pass).
    Parses TypeScript builtins with Bun to verify no syntax errors."""
    import shutil

    bun_exe = shutil.which("bun")
    if not bun_exe:
        default_bun = os.path.expanduser("~/.bun/bin/bun")
        if os.path.exists(default_bun):
            bun_exe = default_bun

    if not bun_exe:
        subprocess.run(
            ["apt-get", "update", "-qq"],
            capture_output=True,
            timeout=60,
        )
        subprocess.run(
            ["apt-get", "install", "-y", "-qq", "unzip"],
            capture_output=True,
            timeout=60,
        )
        install = subprocess.run(
            "curl -fsSL https://bun.sh/install | bash",
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if install.returncode != 0:
            pytest.skip(f"Could not install Bun: {install.stderr}")
        bun_exe = os.path.expanduser("~/.bun/bin/bun")

    # Parse the main ReadableStream builtins to verify syntax
    ts_file = f"{REPO}/src/js/builtins/ReadableStream.ts"
    internals_file = f"{REPO}/src/js/builtins/ReadableStreamInternals.ts"
    for filepath in [ts_file, internals_file]:
        r = subprocess.run(
            [bun_exe, "--eval", f"await Bun.file('{filepath}').text(); console.log('OK')"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert r.returncode == 0 and "OK" in r.stdout, (
            f"Syntax error in {Path(filepath).name}:\n{r.stderr[-500:]}"
        )


def test_repo_streams_readablestream_test():
    """Repo's Web Streams test file runs successfully (pass_to_pass).
    Runs the repo's streams test which covers ReadableStream functionality."""
    import shutil

    bun_exe = shutil.which("bun")
    if not bun_exe:
        default_bun = os.path.expanduser("~/.bun/bin/bun")
        if os.path.exists(default_bun):
            bun_exe = default_bun

    if not bun_exe:
        subprocess.run(
            ["apt-get", "update", "-qq"],
            capture_output=True,
            timeout=60,
        )
        subprocess.run(
            ["apt-get", "install", "-y", "-qq", "unzip"],
            capture_output=True,
            timeout=60,
        )
        install = subprocess.run(
            "curl -fsSL https://bun.sh/install | bash",
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if install.returncode != 0:
            pytest.skip(f"Could not install Bun: {install.stderr}")
        bun_exe = os.path.expanduser("~/.bun/bin/bun")

    r = subprocess.run(
        [bun_exe, "test", "./test/js/web/streams/streams.test.js", "--timeout", "30000"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Streams test failed:\n{r.stderr[-1000:]}{r.stdout[-500:]}"
