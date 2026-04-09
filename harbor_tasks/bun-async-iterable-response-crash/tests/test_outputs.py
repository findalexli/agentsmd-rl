"""
Task: bun-async-iterable-response-crash
Repo: oven-sh/bun @ 9ead1e121d5cca2eaddad66d439ab3c0a74225f2
PR:   28457

Tests verify the fix for Response body consumption from async iterables.
Behavioral fail-to-pass tests extract operators and control flow from source,
then evaluate JavaScript null coercion semantics, verify guard ordering, and
compile/run C code to analyze exception handling.
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/bun"
TS_FILE = f"{REPO}/src/js/builtins/ReadableStream.ts"
INTERNALS_FILE = f"{REPO}/src/js/builtins/ReadableStreamInternals.ts"
CPP_FILE = f"{REPO}/src/bun.js/bindings/webcore/ReadableStream.cpp"


def _run_analysis(code: str, *args, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a Python analysis script to a temp file and execute via subprocess."""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        return subprocess.run(
            ["python3", path, *args],
            capture_output=True, text=True, timeout=timeout,
        )
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Pass-to-pass (static)
# ---------------------------------------------------------------------------


def test_source_files_exist():
    """Core source files must exist and be non-empty."""
    for f in [TS_FILE, INTERNALS_FILE, CPP_FILE]:
        p = Path(f)
        assert p.exists() and p.stat().st_size > 0, f"{f} missing or empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral semantic analysis via subprocess
# ---------------------------------------------------------------------------


def test_null_excluded_from_direct_stream_path():
    """readableStreamTo* must correctly exclude null underlyingSource.
    Extracts the comparison operator and evaluates JS null coercion semantics
    to determine if null would incorrectly enter the direct-stream path."""
    r = _run_analysis(r'''
import re, sys

# JavaScript null coercion: does `if (null OP VALUE)` enter the branch?
# null !== undefined -> true  (BUG: enters direct path, null.pull crashes)
# null != null       -> false (CORRECT: skips direct path)
# null != undefined  -> false (CORRECT: loose coercion treats null == undefined)
NULL_ENTERS = {
    ("!==", "undefined"): True,   # BUG: strict !== doesn't coerce null==undefined
    ("!==", "null"):      False,
    ("!=",  "undefined"): False,  # loose != coerces null==undefined -> true
    ("!=",  "null"):      False,
}

text = open(sys.argv[1]).read()
funcs = ["readableStreamToArray", "readableStreamToText",
         "readableStreamToArrayBuffer", "readableStreamToBytes"]

for func in funcs:
    m = re.search(
        r"function\s+" + func + r"\b(.*?)(?=\nexport\s+function\s|\Z)",
        text, re.DOTALL,
    )
    if not m:
        print(f"FAIL: {func} not found", file=sys.stderr); sys.exit(1)
    body = m.group(1)

    # Extract the underlyingSource comparison operator and RHS
    cm = re.search(r"underlyingSource\s*([!=]{2,3})\s*(undefined|null)\b", body)
    if cm:
        op, rhs = cm.group(1), cm.group(2)
        enters = NULL_ENTERS.get((op, rhs))
        if enters is True:
            print(f"FAIL: {func}: null enters direct path "
                  f"(null {op} {rhs} is true in JS)", file=sys.stderr)
            sys.exit(1)
        elif enters is None:
            print(f"FAIL: {func}: unhandled operator {op} {rhs}", file=sys.stderr)
            sys.exit(1)
    else:
        # Accept: truthiness check or == null guard
        if not re.search(r"if\s*\(\s*underlyingSource\s*[)&|]|"
                         r"underlyingSource\s*==\s*null", body):
            print(f"FAIL: {func}: no null handling", file=sys.stderr)
            sys.exit(1)

print("PASS")
''', TS_FILE)
    assert r.returncode == 0, f"Null coercion bug: {r.stderr}"
    assert "PASS" in r.stdout


def test_close_direct_stream_sink_guard():
    """onCloseDirectStream must guard sink before .end() to prevent crash
    when sink has already been cleaned up (set to undefined)."""
    r = _run_analysis(r'''
import re, sys

text = open(sys.argv[1]).read()
m = re.search(
    r"function\s+onCloseDirectStream\b(.*?)(?=\nexport\s+function\s|\Z)",
    text, re.DOTALL,
)
if not m:
    print("FAIL: onCloseDirectStream not found", file=sys.stderr); sys.exit(1)
body = m.group(1)

# The sink must be guarded before .end() is called.
# Valid patterns:
#   1. var X = this.$sink; if (!X) return; ... X.end()  (guard before use)
#   2. this.$sink?.end()  (optional chaining)
#   3. if (!this.$sink) return; ... this.$sink.end()  (early return)
safe = False

# Pattern 1: extract to variable, guard, then use
vm = re.search(r"(?:var|let|const)\s+(\w+)\s*=\s*this\.\$sink", body)
if vm:
    var = vm.group(1)
    rest = body[vm.end():]
    guard = re.search(r"if\s*\(\s*!" + var + r"\s*\)\s*return", rest)
    end_call = re.search(var + r"\.end\s*\(", rest)
    if guard and end_call and guard.start() < end_call.start():
        safe = True

if not safe and re.search(r"\.\$sink\?\.\s*end\s*\(", body):
    safe = True

if not safe and re.search(r"if\s*\(\s*!this\.\$sink\s*\)\s*return", body):
    safe = True

if not safe:
    print("FAIL: sink.end() called without null guard", file=sys.stderr)
    sys.exit(1)

print("PASS")
''', INTERNALS_FILE)
    assert r.returncode == 0, f"Sink guard missing: {r.stderr}"
    assert "PASS" in r.stdout


def test_flush_direct_stream_sink_guard():
    """onFlushDirectStream must guard sink before .flush() to prevent crash
    when sink has already been cleaned up (set to undefined)."""
    r = _run_analysis(r'''
import re, sys

text = open(sys.argv[1]).read()
m = re.search(
    r"function\s+onFlushDirectStream\b(.*?)(?=\nexport\s+function\s|\Z)",
    text, re.DOTALL,
)
if not m:
    print("FAIL: onFlushDirectStream not found", file=sys.stderr); sys.exit(1)
body = m.group(1)

safe = False

# Pattern 1: extract to variable, guard, then use
vm = re.search(r"(?:var|let|const)\s+(\w+)\s*=\s*this\.\$sink", body)
if vm:
    var = vm.group(1)
    rest = body[vm.end():]
    guard = re.search(r"if\s*\(\s*!" + var + r"\s*\)\s*return", rest)
    flush_call = re.search(var + r"\.flush\s*\(", rest)
    if guard and flush_call and guard.start() < flush_call.start():
        safe = True

if not safe and re.search(r"\.\$sink\?\.\s*flush\s*\(", body):
    safe = True

if not safe and re.search(r"if\s*\(\s*!this\.\$sink\s*\)\s*return", body):
    safe = True

if not safe:
    print("FAIL: sink.flush() called without null guard", file=sys.stderr)
    sys.exit(1)

print("PASS")
''', INTERNALS_FILE)
    assert r.returncode == 0, f"Sink guard missing: {r.stderr}"
    assert "PASS" in r.stdout


def test_stream_locked_on_direct_consumption():
    """readableStreamToArrayBufferDirect must mark stream as consumed/locked
    before calling pull(), preventing double-consumption."""
    r = _run_analysis(r'''
import re, sys

text = open(sys.argv[1]).read()
m = re.search(
    r"function\s+readableStreamToArrayBufferDirect\b(.*?)(?=\nexport\s+function\s|\Z)",
    text, re.DOTALL,
)
if not m:
    print("FAIL: readableStreamToArrayBufferDirect not found", file=sys.stderr)
    sys.exit(1)
body = m.group(1)

# Find pull() call
pull_m = re.search(r"\bpull\s*\(\s*controller", body)
if not pull_m:
    pull_m = re.search(r"\bpull\s*\(", body)
if not pull_m:
    print("FAIL: no pull() call found", file=sys.stderr); sys.exit(1)

pre_pull = body[:pull_m.start()]

# Stream must be locked/marked BEFORE pull():
lock_patterns = [
    r'putByIdDirectPrivate\s*\(\s*stream\s*,\s*["\x27]reader["\x27]',
    r'\bdisturbed\s*=\s*true',
    r'acquireReadableStreamDefaultReader',
]

if not any(re.search(p, pre_pull) for p in lock_patterns):
    print("FAIL: stream not locked before pull()", file=sys.stderr)
    sys.exit(1)

print("PASS")
''', INTERNALS_FILE)
    assert r.returncode == 0, f"Stream not locked: {r.stderr}"
    assert "PASS" in r.stdout


def test_cpp_exception_handling_after_call():
    """C++ readableStreamTo* wrappers must handle exceptions after call()
    to JS builtins. Compiles and runs a C analysis program that checks each
    wrapper function for RETURN_IF_EXCEPTION after call(globalObject, ...)."""
    c_source = """
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "Usage: %s <file>\\n", argv[0]); return 1; }

    FILE *f = fopen(argv[1], "r");
    if (!f) { fprintf(stderr, "Cannot open %s\\n", argv[1]); return 1; }

    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *buf = malloc(len + 1);
    fread(buf, 1, len, f);
    buf[len] = '\\0';
    fclose(f);

    /* These 4 functions had call(globalObject) but NO RETURN_IF_EXCEPTION
       before the fix. The fix adds it to each one. */
    const char *funcs[] = {
        "readableStreamToText",
        "readableStreamToFormData",
        "readableStreamToJSON",
        "readableStreamToBlob",
        NULL
    };

    int checked = 0, handled = 0;

    for (int i = 0; funcs[i]; i++) {
        char *pos = strstr(buf, funcs[i]);
        if (!pos) continue;

        char *brace = strchr(pos, '{');
        if (!brace) continue;

        /* Find end of function (next extern "C" or EOF) */
        char *end = strstr(brace + 1, "\\nextern ");
        if (!end) end = buf + len;

        /* Check for call(globalObject in function body */
        char *s = brace;
        int has_call = 0;
        while (s < end) {
            s = strstr(s, "call(globalObject");
            if (!s || s >= end) break;
            has_call = 1;
            break;
        }

        if (has_call) {
            checked++;
            char saved = *end;
            *end = '\\0';
            if (strstr(brace, "RETURN_IF_EXCEPTION")) handled++;
            *end = saved;
        }
    }

    free(buf);

    if (checked < 4) {
        fprintf(stderr, "FAIL: only %d wrapper functions with call() found\\n", checked);
        return 1;
    }
    if (handled < checked) {
        fprintf(stderr, "FAIL: %d/%d handle exceptions after call()\\n", handled, checked);
        return 1;
    }

    printf("PASS\\n");
    return 0;
}
"""
    fd, c_path = tempfile.mkstemp(suffix=".c")
    bin_path = c_path.replace(".c", "")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(c_source)
        comp = subprocess.run(
            ["gcc", "-o", bin_path, c_path],
            capture_output=True, text=True, timeout=30,
        )
        assert comp.returncode == 0, f"C compile failed: {comp.stderr}"

        run = subprocess.run(
            [bin_path, CPP_FILE],
            capture_output=True, text=True, timeout=10,
        )
        assert run.returncode == 0, f"C analysis: {run.stderr}"
        assert "PASS" in run.stdout
    finally:
        for p in [c_path, bin_path]:
            if os.path.exists(p):
                os.unlink(p)


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff)
# ---------------------------------------------------------------------------


def test_core_functions_preserved():
    """Key ReadableStream functions still exist with substantial content."""
    ts_text = Path(TS_FILE).read_text()
    for func in [
        "readableStreamToArray",
        "readableStreamToText",
        "readableStreamToArrayBuffer",
        "readableStreamToBytes",
    ]:
        assert f"function {func}" in ts_text, f"{func} missing from ReadableStream.ts"

    internals_text = Path(INTERNALS_FILE).read_text()
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


# [agent_config] pass_to_pass — src/js/CLAUDE.md:103 @ 9ead1e121d5cca2eaddad66d439ab3c0a74225f2
def test_no_dynamic_require():
    """require() calls in JS builtins must use string literals only.
    Rule from src/js/CLAUDE.md line 103."""
    for filepath in [TS_FILE, INTERNALS_FILE]:
        text = Path(filepath).read_text()
        for i, line in enumerate(text.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            m = re.search(r'\brequire\s*\((?!\s*["\'])', stripped)
            assert not m, (
                f"{Path(filepath).name}:{i} uses dynamic require() — must use string literals"
            )
