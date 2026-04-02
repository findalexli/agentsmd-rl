"""
Task: bun-async-iterable-response-crash
Repo: oven-sh/bun @ 9ead1e121d5cca2eaddad66d439ab3c0a74225f2
PR:   28457

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

WHY STRUCTURAL: Bun's JS builtins use JSC-specific intrinsics
($getByIdDirectPrivate, $isReadableStream, etc.) that cannot be parsed or
executed by any standard JS engine. C++ requires full Zig/CMake/JSC build.
All checks accept multiple valid fix strategies.
"""

import re
from pathlib import Path

REPO = "/workspace/bun"
TS_FILE = Path(REPO) / "src/js/builtins/ReadableStream.ts"
INTERNALS_FILE = Path(REPO) / "src/js/builtins/ReadableStreamInternals.ts"
CPP_FILE = Path(REPO) / "src/bun.js/bindings/webcore/ReadableStream.cpp"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — files must exist
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_source_files_exist():
    """Core source files must exist and be non-empty."""
    for f in [TS_FILE, INTERNALS_FILE, CPP_FILE]:
        assert f.exists() and f.stat().st_size > 0, f"{f} missing or empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_null_excluded_from_direct_stream_path():
    """readableStreamTo* functions must not let null underlyingSource into the
    direct-stream path. The bug: initializeArrayBufferStream sets
    underlyingSource to null, but !== undefined lets null through.

    Accepts: != null, == null (inverted), !underlyingSource, !== null added,
    != undefined (loose), typeof check, optional chaining, or removal of
    the !== undefined pattern.
    """
    text = TS_FILE.read_text()
    funcs = [
        "readableStreamToArray",
        "readableStreamToText",
        "readableStreamToArrayBuffer",
        "readableStreamToBytes",
    ]
    for func in funcs:
        m = re.search(
            r"function\s+" + func + r"\b(.*?)(?=\nfunction\s|\Z)", text, re.DOTALL
        )
        assert m, f"{func} not found in ReadableStream.ts"
        body = m.group(1)

        has_bug = bool(re.search(r"underlyingSource\s*!==\s*undefined", body))

        fix_patterns = [
            r"underlyingSource\s*!=\s*null",
            r"underlyingSource\s*===?\s*null",
            r"[(!]\s*underlyingSource\s*[)&|]",
            r"underlyingSource\s*!=\s*undefined",
            r"underlyingSource\s*!==\s*null",
            r"typeof\s+underlyingSource\s*[!=]",
            r"underlyingSource\?\.\w",
        ]
        any_fix = any(re.search(p, body) for p in fix_patterns)

        assert not has_bug or any_fix, (
            f"{func}: underlyingSource check still uses !== undefined without null guard"
        )


# [pr_diff] fail_to_pass
def test_close_direct_stream_sink_guard():
    """onCloseDirectStream must guard against null/undefined sink before
    accessing sink.end(). Accepts: local var + if-guard, optional chaining,
    try/catch, direct truthiness check, or null comparison."""
    text = INTERNALS_FILE.read_text()
    m = re.search(
        r"function\s+onCloseDirectStream\b(.*?)(?=\nfunction\s|\nexport\s|\Z)",
        text,
        re.DOTALL,
    )
    assert m, "onCloseDirectStream not found"
    body = m.group(1)

    guards = [
        re.search(
            r"(?:var|let|const)\s+\w+\s*=\s*this\.\$sink.*?if\s*\(\s*!\w+\s*\)",
            body,
            re.DOTALL,
        ),
        re.search(r"if\s*\(\s*!this\.\$sink\s*\)", body),
        re.search(
            r"if\s*\(\s*this\.\$sink\s*(?:===?\s*(?:null|undefined)|==\s*null)", body
        ),
        re.search(r"if\s*\(\s*this\.\$sink\s*\)", body),
        re.search(r"\.\$sink\?\.\w", body),
        re.search(r"try\s*\{[^}]*\.\$?sink.*?end", body, re.DOTALL),
        re.search(
            r"(?:var|let|const)\s+(\w+)\s*=\s*this\.\$sink.*?\1\.end",
            body,
            re.DOTALL,
        ),
    ]
    assert any(guards), "onCloseDirectStream has no null guard for sink"


# [pr_diff] fail_to_pass
def test_flush_direct_stream_sink_guard():
    """onFlushDirectStream must guard against null/undefined sink before
    accessing sink.flush(). Same acceptance patterns as close guard."""
    text = INTERNALS_FILE.read_text()
    m = re.search(
        r"function\s+onFlushDirectStream\b(.*?)(?=\nfunction\s|\nexport\s|\Z)",
        text,
        re.DOTALL,
    )
    assert m, "onFlushDirectStream not found"
    body = m.group(1)

    guards = [
        re.search(
            r"(?:var|let|const)\s+\w+\s*=\s*this\.\$sink.*?if\s*\(\s*!\w+\s*\)",
            body,
            re.DOTALL,
        ),
        re.search(r"if\s*\(\s*!this\.\$sink\s*\)", body),
        re.search(
            r"if\s*\(\s*this\.\$sink\s*(?:===?\s*(?:null|undefined)|==\s*null)", body
        ),
        re.search(r"if\s*\(\s*this\.\$sink\s*\)", body),
        re.search(r"\.\$sink\?\.\w", body),
        re.search(r"try\s*\{[^}]*\.\$?sink.*?flush", body, re.DOTALL),
        re.search(
            r"(?:var|let|const)\s+(\w+)\s*=\s*this\.\$sink.*?\1\.flush",
            body,
            re.DOTALL,
        ),
    ]
    assert any(guards), "onFlushDirectStream has no null guard for sink"


# [pr_diff] fail_to_pass
def test_stream_locked_on_direct_consumption():
    """readableStreamToArrayBufferDirect must lock the stream to prevent
    double-consumption. Accepts: putByIdDirectPrivate with reader/disturbed,
    acquireReader, addReadRequest, or any lock mechanism."""
    text = INTERNALS_FILE.read_text()
    m = re.search(
        r"function\s+readableStreamToArrayBufferDirect\b(.*?)(?=\nfunction\s|\nexport\s|\Z)",
        text,
        re.DOTALL,
    )
    assert m, "readableStreamToArrayBufferDirect not found"
    body = m.group(1)

    lock_patterns = [
        re.search(r"putByIdDirectPrivate.*?(?:reader|Reader)", body, re.IGNORECASE),
        re.search(r"(?:disturbed|Disturbed)", body),
        re.search(r"acquireReadableStream", body),
        re.search(r"addReadRequest", body),
        re.search(r"(?:setReadableStreamState|readableStreamState)", body),
        re.search(r"(?:lock|Lock)", body),
    ]
    assert any(lock_patterns), (
        "readableStreamToArrayBufferDirect does not lock the stream"
    )


# [pr_diff] fail_to_pass
def test_cpp_exception_handling_after_call():
    """C++ wrappers for readableStreamTo* must handle exceptions after calling
    JS builtins via call(). Accepts: RETURN_IF_EXCEPTION, scope.exception(),
    EXCEPTION_GUARD, throwScope, DECLARE_THROW_SCOPE, RELEASE_AND_RETURN."""
    text = CPP_FILE.read_text()

    exception_patterns = [
        r"RETURN_IF_EXCEPTION",
        r"scope\.exception\(\)",
        r"EXCEPTION_GUARD",
        r"throwScope",
        r"DECLARE_THROW_SCOPE",
        r"RELEASE_AND_RETURN.*scope",
    ]

    sections = re.split(r'(?=(?:extern\s+"C"|JSC_DEFINE_HOST_FUNCTION))', text)
    funcs_with_exception = 0
    for section in sections:
        if "readableStreamTo" not in section:
            continue
        if any(re.search(p, section) for p in exception_patterns):
            funcs_with_exception += 1

    assert funcs_with_exception >= 7, (
        f"Only {funcs_with_exception}/7+ C++ readableStreamTo* wrappers have exception handling"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_core_functions_preserved():
    """Key ReadableStream functions still exist with substantial content."""
    ts_text = TS_FILE.read_text()
    for func in [
        "readableStreamToArray",
        "readableStreamToText",
        "readableStreamToArrayBuffer",
        "readableStreamToBytes",
    ]:
        assert f"function {func}" in ts_text, f"{func} missing from ReadableStream.ts"

    internals_text = INTERNALS_FILE.read_text()
    for func in ["onCloseDirectStream", "onFlushDirectStream"]:
        assert f"function {func}" in internals_text, (
            f"{func} missing from ReadableStreamInternals.ts"
        )

    assert internals_text.count("\n") > 1000, "ReadableStreamInternals.ts appears gutted"
    assert ts_text.count("\n") > 100, "ReadableStream.ts appears gutted"


# [agent_config] pass_to_pass — src/js/CLAUDE.md:56 @ 9ead1e121d5cca2eaddad66d439ab3c0a74225f2
def test_no_bare_call_apply():
    """No bare .call/.apply in JS builtins — must use .$call/.$apply.
    Rule from src/js/CLAUDE.md line 56."""
    for filepath in [TS_FILE, INTERNALS_FILE]:
        text = filepath.read_text()
        for i, line in enumerate(text.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            assert not re.search(r"(?<!\$)\.call\s*\(", stripped), (
                f"{filepath.name}:{i} uses bare .call() — must use .$call()"
            )
            assert not re.search(r"(?<!\$)\.apply\s*\(", stripped), (
                f"{filepath.name}:{i} uses bare .apply() — must use .$apply()"
            )


# [agent_config] pass_to_pass — src/js/CLAUDE.md:103 @ 9ead1e121d5cca2eaddad66d439ab3c0a74225f2
def test_no_dynamic_require():
    """require() calls in JS builtins must use string literals only.
    Rule from src/js/CLAUDE.md line 103."""
    for filepath in [TS_FILE, INTERNALS_FILE]:
        text = filepath.read_text()
        for i, line in enumerate(text.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            # Match require(variable) but not require("string") or require('string')
            m = re.search(r'\brequire\s*\((?!\s*["\'])', stripped)
            assert not m, (
                f"{filepath.name}:{i} uses dynamic require() — must use string literals"
            )
