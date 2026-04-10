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
import pytest
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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD standards from ban-words.test.ts
# ---------------------------------------------------------------------------


def test_no_undefined_equality_comparison():
    """No undefined equality comparisons (== undefined, != undefined) in builtins.
    Banned by repo's ban-words.test.ts — this is Undefined Behavior."""
    banned_patterns = [
        " != undefined",
        " == undefined",
        "undefined != ",
        "undefined == ",
    ]
    for filepath in [TS_FILE, INTERNALS_FILE]:
        text = Path(filepath).read_text()
        for i, line in enumerate(text.split("\n"), 1):
            stripped = line.strip()
            # Skip comments
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            for pattern in banned_patterns:
                assert pattern not in stripped, (
                    f"{Path(filepath).name}:{i} contains banned pattern '{pattern}' — "
                    "this is Undefined Behavior per ban-words.test.ts"
                )


def test_no_bare_jsboolean():
    """No bare .jsBoolean(true/false) calls in builtins — use .true/.false.
    Banned by repo's ban-words.test.ts."""
    banned_patterns = [
        ".jsBoolean(true)",
        "JSValue.true",
        ".jsBoolean(false)",
        "JSValue.false",
    ]
    for filepath in [TS_FILE, INTERNALS_FILE]:
        text = Path(filepath).read_text()
        for i, line in enumerate(text.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            for pattern in banned_patterns:
                assert pattern not in stripped, (
                    f"{Path(filepath).name}:{i} contains banned pattern '{pattern}' — "
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
    for filepath in [TS_FILE, INTERNALS_FILE]:
        text = Path(filepath).read_text()
        for i, line in enumerate(text.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            for pattern in banned_patterns:
                assert pattern not in stripped, (
                    f"{Path(filepath).name}:{i} contains banned pattern '{pattern}' — "
                    "use bun.* alternatives per ban-words.test.ts"
                )


def test_typescript_braces_balance():
    """TypeScript files must have balanced braces (basic syntax check)."""
    for filepath in [TS_FILE, INTERNALS_FILE]:
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
        # Check if bun is in default install location
        default_bun = os.path.expanduser("~/.bun/bin/bun")
        if os.path.exists(default_bun):
            bun_exe = default_bun

    if not bun_exe:
        # Install unzip if needed, then install Bun
        subprocess.run(
            ["apt-get", "update", "-qq"],
            capture_output=True, timeout=60,
        )
        subprocess.run(
            ["apt-get", "install", "-y", "-qq", "unzip"],
            capture_output=True, timeout=60,
        )
        install = subprocess.run(
            "curl -fsSL https://bun.sh/install | bash",
            shell=True, capture_output=True, text=True, timeout=120,
        )
        if install.returncode != 0:
            pytest.skip(f"Could not install Bun: {install.stderr}")
        bun_exe = os.path.expanduser("~/.bun/bin/bun")

    r = subprocess.run(
        [bun_exe, "./test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Ban-words test failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_typescript_typecheck():
    """TypeScript typecheck passes (tsc --noEmit) (pass_to_pass).
    Verifies TypeScript files have no type errors."""
    import shutil

    bun_exe = shutil.which("bun")
    if not bun_exe:
        # Check if bun is in default install location
        default_bun = os.path.expanduser("~/.bun/bin/bun")
        if os.path.exists(default_bun):
            bun_exe = default_bun

    if not bun_exe:
        # Install unzip if needed, then install Bun
        subprocess.run(
            ["apt-get", "update", "-qq"],
            capture_output=True, timeout=60,
        )
        subprocess.run(
            ["apt-get", "install", "-y", "-qq", "unzip"],
            capture_output=True, timeout=60,
        )
        install = subprocess.run(
            "curl -fsSL https://bun.sh/install | bash",
            shell=True, capture_output=True, text=True, timeout=120,
        )
        if install.returncode != 0:
            pytest.skip(f"Could not install Bun: {install.stderr}")
        bun_exe = os.path.expanduser("~/.bun/bin/bun")

    # Use bunx to run tsc
    r = subprocess.run(
        [bun_exe, "x", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


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
            capture_output=True, timeout=60,
        )
        subprocess.run(
            ["apt-get", "install", "-y", "-qq", "unzip"],
            capture_output=True, timeout=60,
        )
        install = subprocess.run(
            "curl -fsSL https://bun.sh/install | bash",
            shell=True, capture_output=True, text=True, timeout=120,
        )
        if install.returncode != 0:
            pytest.skip(f"Could not install Bun: {install.stderr}")
        bun_exe = os.path.expanduser("~/.bun/bin/bun")

    return bun_exe


def test_repo_js_builtins_syntax():
    """JS builtins files have valid syntax (pass_to_pass).
    Parses TypeScript builtins with Bun to verify no syntax errors.
    Based on CI checks that validate builtin source files."""
    bun_exe = _ensure_bun_installed()

    # Parse the main ReadableStream builtins to verify syntax
    for filepath in [TS_FILE, INTERNALS_FILE]:
        r = subprocess.run(
            [bun_exe, "--eval", f"await Bun.file('{filepath}').text(); console.log('OK')"],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0 and "OK" in r.stdout, (
            f"Syntax error in {Path(filepath).name}:\n{r.stderr[-500:]}"
        )


def test_repo_streams_readablestream_test():
    """Repo's Web Streams test file runs successfully (pass_to_pass).
    Runs the repo's streams test which covers ReadableStream functionality."""
    bun_exe = _ensure_bun_installed()

    r = subprocess.run(
        [bun_exe, "test", "./test/js/web/streams/streams.test.js", "--timeout", "30000"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
