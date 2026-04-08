"""
Task: bun-async-iterable-response-crash
Repo: oven-sh/bun @ 9ead1e121d5cca2eaddad66d439ab3c0a74225f2
PR:   28457

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Bun's JS builtins use JSC-specific intrinsics ($getByIdDirectPrivate,
$isReadableStream, etc.) that cannot be executed by any standard JS engine.
C++ requires full Zig/CMake/JSC build. All f2p checks use subprocess to run
code analysis against the actual source files, accepting multiple valid fix
strategies.
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


def _run_py(script: str, timeout: int = 30, **env_extra) -> subprocess.CompletedProcess:
    """Write analysis script to temp file and execute in subprocess."""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(script)
        env = {**os.environ, **{k: str(v) for k, v in env_extra.items()}}
        return subprocess.run(
            ["python3", path],
            capture_output=True, text=True, timeout=timeout, env=env,
        )
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — files must exist
# ---------------------------------------------------------------------------


def test_source_files_exist():
    """Core source files (ReadableStream.ts, ReadableStreamInternals.ts,
    ReadableStream.cpp) must exist and be non-empty."""
    for f in [TS_FILE, INTERNALS_FILE, CPP_FILE]:
        p = Path(f)
        assert p.exists() and p.stat().st_size > 0, f"{f} missing or empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix checks via subprocess
# ---------------------------------------------------------------------------


def test_null_excluded_from_direct_stream_path():
    """readableStreamTo* functions must exclude null underlyingSource from the
    direct-stream path. Uses subprocess code analysis."""
    result = _run_py(
        r"""
import re, sys, os

text = open(os.environ["TS_FILE"]).read()
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
    if not m:
        print(f"{func} not found", file=sys.stderr)
        sys.exit(1)
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

    if has_bug and not any_fix:
        print(f"{func}: still uses !== undefined without null guard", file=sys.stderr)
        sys.exit(1)

print("PASS")
""",
        TS_FILE=TS_FILE,
    )
    assert result.returncode == 0, f"Fix not detected: {result.stderr}"
    assert "PASS" in result.stdout


def test_close_direct_stream_sink_guard():
    """onCloseDirectStream must guard against null/undefined sink before
    sink.end(). Uses subprocess code analysis."""
    result = _run_py(
        r"""
import re, sys, os

text = open(os.environ["INTERNALS_FILE"]).read()
m = re.search(
    r"function\s+onCloseDirectStream\b(.*?)(?=\nfunction\s|\nexport\s|\Z)",
    text, re.DOTALL,
)
if not m:
    print("onCloseDirectStream not found", file=sys.stderr)
    sys.exit(1)
body = m.group(1)

guards = [
    re.search(
        r"(?:var|let|const)\s+\w+\s*=\s*this\.\$sink.*?if\s*\(\s*!\w+\s*\)",
        body, re.DOTALL,
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
        body, re.DOTALL,
    ),
]
if not any(guards):
    print("onCloseDirectStream has no null guard for sink", file=sys.stderr)
    sys.exit(1)

print("PASS")
""",
        INTERNALS_FILE=INTERNALS_FILE,
    )
    assert result.returncode == 0, f"No sink guard found: {result.stderr}"
    assert "PASS" in result.stdout


def test_flush_direct_stream_sink_guard():
    """onFlushDirectStream must guard against null/undefined sink before
    sink.flush(). Uses subprocess code analysis."""
    result = _run_py(
        r"""
import re, sys, os

text = open(os.environ["INTERNALS_FILE"]).read()
m = re.search(
    r"function\s+onFlushDirectStream\b(.*?)(?=\nfunction\s|\nexport\s|\Z)",
    text, re.DOTALL,
)
if not m:
    print("onFlushDirectStream not found", file=sys.stderr)
    sys.exit(1)
body = m.group(1)

guards = [
    re.search(
        r"(?:var|let|const)\s+\w+\s*=\s*this\.\$sink.*?if\s*\(\s*!\w+\s*\)",
        body, re.DOTALL,
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
        body, re.DOTALL,
    ),
]
if not any(guards):
    print("onFlushDirectStream has no null guard for sink", file=sys.stderr)
    sys.exit(1)

print("PASS")
""",
        INTERNALS_FILE=INTERNALS_FILE,
    )
    assert result.returncode == 0, f"No sink guard found: {result.stderr}"
    assert "PASS" in result.stdout


def test_stream_locked_on_direct_consumption():
    """readableStreamToArrayBufferDirect must lock the stream to prevent
    double-consumption. Uses subprocess code analysis."""
    result = _run_py(
        r"""
import re, sys, os

text = open(os.environ["INTERNALS_FILE"]).read()
m = re.search(
    r"function\s+readableStreamToArrayBufferDirect\b(.*?)(?=\nfunction\s|\nexport\s|\Z)",
    text, re.DOTALL,
)
if not m:
    print("readableStreamToArrayBufferDirect not found", file=sys.stderr)
    sys.exit(1)
body = m.group(1)

lock_patterns = [
    re.search(r"putByIdDirectPrivate.*?(?:reader|Reader)", body, re.IGNORECASE),
    re.search(r"(?:disturbed|Disturbed)", body),
    re.search(r"acquireReadableStream", body),
    re.search(r"addReadRequest", body),
    re.search(r"(?:setReadableStreamState|readableStreamState)", body),
    re.search(r"(?:lock|Lock)", body),
]
if not any(lock_patterns):
    print("readableStreamToArrayBufferDirect does not lock the stream", file=sys.stderr)
    sys.exit(1)

print("PASS")
""",
        INTERNALS_FILE=INTERNALS_FILE,
    )
    assert result.returncode == 0, f"No stream locking found: {result.stderr}"
    assert "PASS" in result.stdout


def test_cpp_exception_handling_after_call():
    """C++ wrappers for readableStreamTo* must handle exceptions after calling
    JS builtins via call(). Compiles and runs a C analyzer program."""
    c_source = f"""
#include <stdio.h>
#include <string.h>

int main() {{
    FILE *f = fopen("{CPP_FILE}", "r");
    if (!f) {{
        fprintf(stderr, "Cannot open ReadableStream.cpp\\n");
        return 1;
    }}

    char line[4096];
    int rie_count = 0;
    int scope_count = 0;

    while (fgets(line, sizeof(line), f)) {{
        if (strstr(line, "RETURN_IF_EXCEPTION")) rie_count++;
        if (strstr(line, "DECLARE_THROW_SCOPE")) scope_count++;
    }}
    fclose(f);

    /* The fix adds RETURN_IF_EXCEPTION after every readableStreamTo* call().
       Before fix: ~0-1 RETURN_IF_EXCEPTION in the file.
       After fix: 7+ RETURN_IF_EXCEPTION across the wrappers. */
    if (rie_count >= 7 && scope_count >= 6) {{
        printf("PASS\\n");
        return 0;
    }}
    fprintf(stderr, "Only %d RETURN_IF_EXCEPTION, %d DECLARE_THROW_SCOPE\\n", rie_count, scope_count);
    return 1;
}}
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
            [bin_path], capture_output=True, text=True, timeout=10,
        )
        assert run.returncode == 0, f"C analysis failed: {run.stderr}"
        assert "PASS" in run.stdout
    finally:
        if os.path.exists(c_path):
            os.unlink(c_path)
        if os.path.exists(bin_path):
            os.unlink(bin_path)


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
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
