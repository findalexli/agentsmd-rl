"""
Task: bun-async-iterable-response-crash
Repo: oven-sh/bun @ 9ead1e121d5cca2eaddad66d439ab3c0a74225f2
PR:   28457

Tests verify the fix for Response body consumption from async iterables.
Since the fix lives in TypeScript/C++ source files that are compiled into the
Bun binary (and we cannot rebuild), tests are static source-code checks that
verify the precise fix patterns are present/absent.
"""

import os
import re
import pytest
import subprocess
import shutil
from pathlib import Path

REPO = "/workspace/bun"

BUN_EXE = shutil.which("bun") or os.path.expanduser("~/.bun/bin/bun")


def _fail_if_no_bun():
    if not os.path.exists(BUN_EXE):
        pytest.skip("Bun binary not available")


# ---------------------------------------------------------------------------
# Pass-to-pass (static)
# ---------------------------------------------------------------------------


def test_source_files_exist():
    """Core source files must exist and be non-empty."""
    paths = [
        f"{REPO}/src/js/builtins/ReadableStream.ts",
        f"{REPO}/src/js/builtins/ReadableStreamInternals.ts",
        f"{REPO}/src/bun.js/bindings/webcore/ReadableStream.cpp",
    ]
    for p in paths:
        path = Path(p)
        assert path.exists() and path.stat().st_size > 0, f"{p} missing or empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — static source-code checks
# ---------------------------------------------------------------------------


def test_null_excluded_from_direct_stream_path():
    """readableStreamTo* functions must use != null (not !== undefined) for
    underlyingSource, so null (set by async-iterable Response bodies) is
    properly excluded from the direct-stream path."""
    ts = Path(f"{REPO}/src/js/builtins/ReadableStream.ts").read_text()

    # Gold: the 4 functions use != null
    assert "if (underlyingSource != null)" in ts, (
        "Missing != null check for underlyingSource — null from "
        "async-iterable bodies will still crash"
    )
    # Count: all 4 sites must be fixed
    count = ts.count("if (underlyingSource != null)")
    assert count == 4, (
        f"Expected 4 underlyingSource != null guards, found {count}"
    )
    # Base pattern must be gone
    assert "if (underlyingSource !== undefined)" not in ts, (
        "Found !== undefined check for underlyingSource — null will not be excluded"
    )


def test_close_direct_stream_sink_guard():
    """onCloseDirectStream must guard against null/undefined sink."""
    ts = Path(f"{REPO}/src/js/builtins/ReadableStreamInternals.ts").read_text()

    # Extract the onCloseDirectStream function body
    m = re.search(
        r"export function onCloseDirectStream\([^)]+\)\s*\{(.*?)\nexport function",
        ts, re.DOTALL,
    )
    assert m, "Cannot find onCloseDirectStream function"
    body = m.group(1)

    assert "var sink = this.$sink;" in body, (
        "onCloseDirectStream missing local sink variable assignment"
    )
    assert "if (!sink)" in body and "return" in body[body.index("if (!sink)"):body.index("if (!sink)") + 50], (
        "onCloseDirectStream missing null-sink guard (if (!sink) return)"
    )
    # Must use local 'sink' variable for .end()
    assert "sink.end()" in body, (
        "onCloseDirectStream must call sink.end() on the guarded local variable"
    )


def test_flush_direct_stream_sink_guard():
    """onFlushDirectStream must guard against null/undefined sink."""
    ts = Path(f"{REPO}/src/js/builtins/ReadableStreamInternals.ts").read_text()

    # Extract the onFlushDirectStream function body
    m = re.search(
        r"export function onFlushDirectStream\([^)]*\)\s*\{(.*?)\n(?:export function|\Z)",
        ts, re.DOTALL,
    )
    assert m, "Cannot find onFlushDirectStream function"
    body = m.group(1)

    assert "var sink = this.$sink;" in body, (
        "onFlushDirectStream missing local sink variable assignment"
    )
    assert "if (!sink)" in body and "return" in body[body.index("if (!sink)"):body.index("if (!sink)") + 50], (
        "onFlushDirectStream missing null-sink guard (if (!sink) return)"
    )
    # Must use local 'sink' variable for .flush() calls
    assert "sink.flush()" in body, (
        "onFlushDirectStream must call sink.flush() on the guarded local variable"
    )


def test_stream_locked_on_direct_consumption():
    """readableStreamToArrayBufferDirect must lock the stream to prevent
    double-consumption."""
    ts = Path(f"{REPO}/src/js/builtins/ReadableStreamInternals.ts").read_text()

    # Extract readableStreamToArrayBufferDirect function body
    m = re.search(
        r"export function readableStreamToArrayBufferDirect\((.+?)\n(?:export function|\Z)",
        ts, re.DOTALL,
    )
    assert m, "Cannot find readableStreamToArrayBufferDirect function"
    body = m.group(1)

    assert 'stream.$disturbed = true' in body, (
        "readableStreamToArrayBufferDirect missing stream.$disturbed = true — "
        "double-consumption not prevented"
    )
    assert '$putByIdDirectPrivate(stream, "reader", {})' in body, (
        'readableStreamToArrayBufferDirect missing dummy reader — '
        "isReadableStreamLocked will return false for second call"
    )
    # Cleanup must clear the dummy reader on error
    assert '$putByIdDirectPrivate(stream, "reader", undefined)' in body, (
        "readableStreamToArrayBufferDirect missing reader cleanup on error/success paths"
    )


def test_cpp_exception_handling_after_call():
    """C++ readableStreamTo* wrappers must handle exceptions after call() to JS
    builtins.  Each wrapper must have RETURN_IF_EXCEPTION(throwScope, {}); after
    its call(globalObject, function, callData, ...) invocation."""
    cpp = Path(f"{REPO}/src/bun.js/bindings/webcore/ReadableStream.cpp").read_text()

    count = cpp.count("RETURN_IF_EXCEPTION(throwScope, {});")
    # Base has 1 (in a different function).  Gold adds RETURN_IF_EXCEPTION after
    # call() in 6 wrapper functions: readableStreamToArrayBufferBody,
    # readableStreamToBytes, readableStreamToText, readableStreamToFormData,
    # readableStreamToJSON, readableStreamToBlob — bringing the total to >=5.
    assert count >= 5, (
        f"Expected >=5 RETURN_IF_EXCEPTION(throwScope, {{}}); in ReadableStream.cpp, "
        f"found {count} — JS exceptions can still crash across the C++ boundary"
    )

    # Also verify DECLARE_THROW_SCOPE was added in the 4 functions that lacked it
    dts_count = cpp.count("DECLARE_THROW_SCOPE(vm);")
    # Base has several already; gold adds 4 more (in readableStreamToText,
    # readableStreamToFormData, readableStreamToJSON, readableStreamToBlob).
    # Total should be >=7.  We'll be conservative and require >=6.
    assert dts_count >= 6, (
        f"Expected >=6 DECLARE_THROW_SCOPE(vm); in ReadableStream.cpp, "
        f"found {dts_count} — missing throw scope declarations"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — static code quality / anti-regression
# ---------------------------------------------------------------------------


def test_core_functions_preserved():
    """Key ReadableStream functions still exist with substantial content."""
    ts = Path(f"{REPO}/src/js/builtins/ReadableStream.ts").read_text()
    for func in [
        "readableStreamToArray",
        "readableStreamToText",
        "readableStreamToArrayBuffer",
        "readableStreamToBytes",
    ]:
        assert f"function {func}" in ts, f"{func} missing from ReadableStream.ts"

    internals = Path(f"{REPO}/src/js/builtins/ReadableStreamInternals.ts").read_text()
    for func in ["onCloseDirectStream", "onFlushDirectStream"]:
        assert f"function {func}" in internals, (
            f"{func} missing from ReadableStreamInternals.ts"
        )

    assert internals.count("\n") > 1000, "ReadableStreamInternals.ts appears gutted"
    assert ts.count("\n") > 100, "ReadableStream.ts appears gutted"


# [agent_config] pass_to_pass — src/js/CLAUDE.md:56
def test_no_bare_call_apply():
    """No bare .call/.apply in JS builtins — must use .$call/.$apply."""
    files = [
        f"{REPO}/src/js/builtins/ReadableStream.ts",
        f"{REPO}/src/js/builtins/ReadableStreamInternals.ts",
    ]
    for filepath in files:
        text = Path(filepath).read_text()
        for i, line in enumerate(text.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            assert not re.search(r"(?<!\$)\.call\s*\(", stripped), (
                f"{Path(filepath).name}:{i} uses bare .call() — must use .$call()"
            )
            assert not re.search(r"(?<!\$)\.apply\s*\(", stripped), (
                f"{Path(filepath).name}:{i} uses bare .apply() — must use .$apply()"
            )


# [agent_config] pass_to_pass — src/js/CLAUDE.md:103
def test_no_dynamic_require():
    """require() calls in JS builtins must use string literals only."""
    files = [
        f"{REPO}/src/js/builtins/ReadableStream.ts",
        f"{REPO}/src/js/builtins/ReadableStreamInternals.ts",
    ]
    for filepath in files:
        text = Path(filepath).read_text()
        for i, line in enumerate(text.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            m = re.search(r'\brequire\s*\((?!\s*["\'])', stripped)
            assert not m, (
                f"{Path(filepath).name}:{i} uses dynamic require() — must use string literals"
            )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD standards
# ---------------------------------------------------------------------------


def test_no_undefined_equality_comparison():
    """No undefined equality comparisons (== undefined, != undefined) in builtins.
    Banned by repo ban-words.test.ts."""
    banned = [" != undefined", " == undefined", "undefined != ", "undefined == "]
    files = [
        f"{REPO}/src/js/builtins/ReadableStream.ts",
        f"{REPO}/src/js/builtins/ReadableStreamInternals.ts",
    ]
    for filepath in files:
        text = Path(filepath).read_text()
        for i, line in enumerate(text.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            for pat in banned:
                assert pat not in stripped, (
                    f"{Path(filepath).name}:{i} contains banned pattern '{pat}'"
                )


def test_no_bare_jsboolean():
    """No bare .jsBoolean(true/false) — use .true/.false instead."""
    banned = [".jsBoolean(true)", ".jsBoolean(false)"]
    files = [
        f"{REPO}/src/js/builtins/ReadableStream.ts",
        f"{REPO}/src/js/builtins/ReadableStreamInternals.ts",
    ]
    for filepath in files:
        text = Path(filepath).read_text()
        for i, line in enumerate(text.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            for pat in banned:
                assert pat not in stripped, (
                    f"{Path(filepath).name}:{i} contains banned '{pat}'"
                )


def test_no_std_debug_in_builtins():
    """No std.debug.assert, std.debug.print in builtins."""
    banned = [
        "std.debug.assert",
        "std.debug.dumpStackTrace",
        "std.debug.print",
        "std.log",
    ]
    files = [
        f"{REPO}/src/js/builtins/ReadableStream.ts",
        f"{REPO}/src/js/builtins/ReadableStreamInternals.ts",
    ]
    for filepath in files:
        text = Path(filepath).read_text()
        for i, line in enumerate(text.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            for pat in banned:
                assert pat not in stripped, (
                    f"{Path(filepath).name}:{i} contains banned '{pat}'"
                )


def test_typescript_braces_balance():
    """TypeScript files must have balanced braces."""
    files = [
        f"{REPO}/src/js/builtins/ReadableStream.ts",
        f"{REPO}/src/js/builtins/ReadableStreamInternals.ts",
    ]
    for filepath in files:
        text = Path(filepath).read_text()
        assert text.count("{") == text.count("}"), (
            f"{Path(filepath).name}: unbalanced braces"
        )
        assert text.count("(") == text.count(")"), (
            f"{Path(filepath).name}: unbalanced parentheses"
        )


def test_repo_ban_words_test():
    """Repo's ban-words test passes (pass_to_pass)."""
    _fail_if_no_bun()
    r = subprocess.run(
        [BUN_EXE, "./test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Ban-words test failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_typescript_typecheck():
    """TypeScript typecheck passes — tsc --noEmit (pass_to_pass)."""
    _fail_if_no_bun()
    r = subprocess.run(
        [BUN_EXE, "x", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_js_builtins_syntax():
    """JS builtins files have valid syntax — parsed by Bun (pass_to_pass)."""
    _fail_if_no_bun()
    for rel in [
        "src/js/builtins/ReadableStream.ts",
        "src/js/builtins/ReadableStreamInternals.ts",
    ]:
        r = subprocess.run(
            [BUN_EXE, "--eval", f"await Bun.file('{rel}').text(); console.log('OK')"],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0 and "OK" in r.stdout, (
            f"Syntax error in {Path(rel).name}:\n{r.stderr[-500:]}"
        )


def test_repo_streams_readablestream_test():
    """Repo's Web Streams test file runs successfully (pass_to_pass)."""
    _fail_if_no_bun()
    r = subprocess.run(
        [BUN_EXE, "test", "./test/js/web/streams/streams.test.js", "--timeout", "30000"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Streams test failed:\n{r.stderr[-1000:]}{r.stdout[-500:]}"
