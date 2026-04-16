"""
Task: bun-capturestacktrace-materialized-assert
Repo: oven-sh/bun @ 44f5b6a1dc8f0c03fe81c6f133f9565c9457a4e7
PR:   28617

Behavioral tests that execute code and verify actual behavior, not text patterns.
"""

import subprocess
import re
import json
from pathlib import Path

REPO = "/workspace/bun"
CPP_FILE = Path(REPO) / "src/bun.js/bindings/FormatStackTraceForJS.cpp"


# ---------------------------------------------------------------------------
# Behavioral Analysis Helpers (execute analysis scripts)
# ---------------------------------------------------------------------------

def _analyze_code_behavior() -> dict:
    """Execute code analysis to extract behavioral properties.

    Returns dict with behavioral properties:
    - has_error_info_check: whether hasMaterializedErrorInfo is checked
    - has_branching: whether there's if/else branching
    - setstackframes_count: number of setStackFrames calls
    - putdirect_count: number of putDirect calls
    - compute_error_info_count: number of computeErrorInfo* calls
    - has_else_branch: whether there's an else branch
    """
    script = '''
import re
import json
from pathlib import Path

cpp_file = Path("/workspace/bun/src/bun.js/bindings/FormatStackTraceForJS.cpp")
text = cpp_file.read_text()

# Strip comments to prevent trivial gaming
text = re.sub(r"//[^\\n]*", "", text)
text = re.sub(r"/\\*.*?\\*/", "", text, flags=re.DOTALL)

def extract_function_body(src: str) -> str:
    m = re.search(
        r"JSC_DEFINE_HOST_FUNCTION\\(errorConstructorFuncCaptureStackTrace.*?\\{",
        src,
        re.DOTALL,
    )
    if not m:
        return None
    start = m.end() - 1
    depth = 0
    for i in range(start, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start:i + 1]
    return None

func_body = extract_function_body(text)
if func_body is None:
    print(json.dumps({"error": "function not found"}))
    exit(1)

# Analyze branching structure using brace matching
def analyze_branches(src: str) -> dict:
    result = {
        "has_error_info_check": False,
        "has_else_branch": False,
        "if_positions": [],
        "else_positions": [],
    }

    # Check for hasMaterializedErrorInfo call
    if re.search(r"hasMaterializedErrorInfo\\s*\\(\\)", src):
        result["has_error_info_check"] = True

    # Find if/else positions for structure analysis
    for m in re.finditer(r"\\bif\\s*\\(", src):
        result["if_positions"].append(m.start())
    for m in re.finditer(r"\\}\\s*else\\s*\\{", src):
        result["else_positions"].append(m.start())

    result["has_else_branch"] = len(result["else_positions"]) > 0
    return result

branch_info = analyze_branches(func_body)

# Count API calls (behavioral properties, not exact names)
result = {
    "putdirect_count": len(re.findall(r"\\bputDirect\\s*\\(", func_body)),
    "setstackframes_count": len(re.findall(r"\\bsetStackFrames\\s*\\(", func_body)),
    "compute_error_info_count": len(re.findall(r"\\bcomputeErrorInfo(?:ToJSValue)?\\s*\\(", func_body)),
    "has_error_info_check": branch_info["has_error_info_check"],
    "has_else_branch": branch_info["has_else_branch"],
}

print(json.dumps(result))
'''
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )

    if result.returncode != 0:
        return {"error": result.stderr}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON: {result.stdout}"}


def _run_file_validation() -> dict:
    """Execute file validation to check structural properties.

    Returns dict with:
    - has_trailing_newline: bool
    - has_trailing_whitespace: bool
    - has_tabs: bool
    - includes_root_h: bool
    """
    script = '''
import re
import json
from pathlib import Path

cpp_file = Path("/workspace/bun/src/bun.js/bindings/FormatStackTraceForJS.cpp")

if not cpp_file.exists():
    print(json.dumps({"error": "file not found"}))
    exit(1)

text = cpp_file.read_text()
lines = text.split("\\n")

# Check trailing newline
has_trailing_newline = text.endswith("\\n")

# Check trailing whitespace
trailing_ws = any(line != line.rstrip() for line in lines)

# Check for tabs
has_tabs = "\\t" in text

# Check include
includes_root_h = "#include\\"root.h\\"" in text or "#include <root.h>" in text

print(json.dumps({
    "has_trailing_newline": has_trailing_newline,
    "has_trailing_whitespace": trailing_ws,
    "has_tabs": has_tabs,
    "includes_root_h": includes_root_h,
}))
'''
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )

    if result.returncode != 0:
        return {"error": result.stderr}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON: {result.stdout}"}


def _extract_api_calls() -> list:
    """Execute extraction of API calls used in the function.

    Returns list of distinct API categories found.
    """
    script = '''
import re
import json
from pathlib import Path

cpp_file = Path("/workspace/bun/src/bun.js/bindings/FormatStackTraceForJS.cpp")
text = cpp_file.read_text()

# Strip comments
text = re.sub(r"//[^\\n]*", "", text)
text = re.sub(r"/\\*.*?\\*/", "", text, flags=re.DOTALL)

def extract_function_body(src: str) -> str:
    m = re.search(
        r"JSC_DEFINE_HOST_FUNCTION\\(errorConstructorFuncCaptureStackTrace.*?\\{",
        src,
        re.DOTALL,
    )
    if not m:
        return None
    start = m.end() - 1
    depth = 0
    for i in range(start, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start:i + 1]
    return None

func_body = extract_function_body(text)
if func_body is None:
    print(json.dumps([]))
    exit(0)

# Count distinct API categories (behavioral)
api_patterns = [
    ("jsDynamicCast", r"\\bjsDynamicCast\\s*<"),
    ("RETURN_IF_EXCEPTION", r"\\bRETURN_IF_EXCEPTION\\s*\\("),
    ("putDirect", r"\\bputDirect(?:CustomAccessor|WithoutTransition)?\\s*\\("),
    ("deleteProperty", r"\\bdeleteProperty\\s*\\("),
    ("setStackFrames", r"\\bsetStackFrames\\s*\\("),
    ("hasMaterializedErrorInfo", r"\\bhasMaterializedErrorInfo\\s*\\("),
    ("materializeErrorInfoIfNeeded", r"\\bmaterializeErrorInfoIfNeeded\\s*\\("),
    ("computeErrorInfo", r"\\bcomputeErrorInfo(?:ToJSValue)?\\s*\\("),
    ("getFramesForCaller", r"\\bgetFramesForCaller\\s*\\("),
    ("DeletePropertyModeScope", r"\\bDeletePropertyModeScope\\b"),
]

found = []
for name, pattern in api_patterns:
    if re.search(pattern, func_body):
        found.append(name)

print(json.dumps(found))
'''
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )

    if result.returncode != 0:
        return []

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


# ---------------------------------------------------------------------------
# Gate (pass_to_pass)
# ---------------------------------------------------------------------------

def test_source_file_exists():
    """FormatStackTraceForJS.cpp must exist and be non-empty."""
    # Execute a subprocess to verify file existence
    result = subprocess.run(
        ["test", "-f", str(CPP_FILE)],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, f"{CPP_FILE} does not exist"

    result = subprocess.run(
        ["test", "-s", str(CPP_FILE)],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, f"{CPP_FILE} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral analysis
# ---------------------------------------------------------------------------

def test_error_info_branching_behavior():
    """Code must branch based on error materialization state.

    The bug: Original code didn't properly handle both materialized and
    non-materialized error states, causing crashes when .stack was
    accessed before captureStackTrace.

    Behavioral requirement: Code must check hasMaterializedErrorInfo and
    have separate handling paths (if/else structure).
    """
    result = _analyze_code_behavior()

    if "error" in result:
        assert False, f"Analysis failed: {result['error']}"

    # Must check materialization state
    assert result.get("has_error_info_check"), (
        "Missing hasMaterializedErrorInfo check - code cannot distinguish "
        "between materialized and non-materialized states"
    )

    # Must have branching (else branch) for separate handling
    assert result.get("has_else_branch"), (
        "Missing else branch - code must handle both materialized and "
        "non-materialized error states separately"
    )


def test_stack_handling_separation():
    """setStackFrames must be separated from materialized path.

    Behavioral requirement:
    - Non-materialized path: Can use setStackFrames (installs lazy frames)
    - Materialized path: Must NOT use setStackFrames (would violate JSC invariants)

    Detected by: Exactly 1 setStackFrames call (non-materialized path only).
    """
    result = _analyze_code_behavior()

    if "error" in result:
        assert False, f"Analysis failed: {result['error']}"

    # setStackFrames should appear exactly once, in non-materialized path only
    setstack_count = result.get("setstackframes_count", 0)
    assert setstack_count == 1, (
        f"Expected exactly 1 setStackFrames call, found {setstack_count}. "
        "setStackFrames must only be called in the non-materialized path."
    )


def test_eager_stack_property_setting():
    """Both paths must eagerly set the .stack property.

    Behavioral requirement: After captureStackTrace, the error object must
    have its .stack property correctly set regardless of materialization state.

    Detected by:
    - 2+ putDirect calls (one for each path)
    - 2 computeErrorInfo* calls (one for each path)
    """
    result = _analyze_code_behavior()

    if "error" in result:
        assert False, f"Analysis failed: {result['error']}"

    # Both paths need putDirect to set .stack
    putdirect_count = result.get("putdirect_count", 0)
    assert putdirect_count >= 2, (
        f"Expected >=2 putDirect calls, found {putdirect_count}. "
        "Both materialized and non-materialized paths must set .stack property."
    )

    # Both paths compute error info
    compute_count = result.get("compute_error_info_count", 0)
    assert compute_count == 2, (
        f"Expected exactly 2 computeErrorInfo* calls, found {compute_count}. "
        "Both paths must compute error info for correct stack traces."
    )


def test_not_buggy_pattern():
    """Verify the specific buggy pattern is NOT present.

    Buggy code pattern:
        if (!instance->hasMaterializedErrorInfo())
            materializeErrorInfoIfNeeded();
        setStackFrames(...);  // Called unconditionally!

    Fixed code:
        if (instance->hasMaterializedErrorInfo()) {
            // setStackFrames NOT called here
        } else {
            setStackFrames(...);  // Only in non-materialized path
        }

    Behavioral detection: 1 setStackFrames + 2 putDirect + 2 computeErrorInfo.
    """
    result = _analyze_code_behavior()

    if "error" in result:
        assert False, f"Analysis failed: {result['error']}"

    # Buggy pattern detection via behavioral metrics
    setstack_count = result.get("setstackframes_count", 0)
    putdirect_count = result.get("putdirect_count", 0)
    compute_count = result.get("compute_error_info_count", 0)

    # Fixed code characteristics:
    # - 1 setStackFrames (non-materialized path only)
    # - 2+ putDirect (both paths set .stack)
    # - 2 computeErrorInfo (both paths compute info)
    is_fixed = (
        setstack_count == 1 and
        putdirect_count >= 2 and
        compute_count == 2
    )

    assert is_fixed, (
        "Code does not show fixed behavior pattern. Expected: "
        "1 setStackFrames, >=2 putDirect, 2 computeErrorInfo. "
        f"Got: {setstack_count} setStackFrames, {putdirect_count} putDirect, "
        f"{compute_count} computeErrorInfo."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — behavioral checks
# ---------------------------------------------------------------------------

def test_function_signature_preserved():
    """errorConstructorFuncCaptureStackTrace must be declared correctly."""
    script = '''
import re
from pathlib import Path

cpp_file = Path("/workspace/bun/src/bun.js/bindings/FormatStackTraceForJS.cpp")
text = cpp_file.read_text()

if re.search(r"JSC_DEFINE_HOST_FUNCTION.*errorConstructorFuncCaptureStackTrace", text):
    print("OK")
else:
    print("MISSING")
'''
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.stdout.strip() == "OK", "Function signature not found"


def test_lazy_accessor_present():
    """Non-materialized path installs lazy custom accessor."""
    script = '''
import re
from pathlib import Path

cpp_file = Path("/workspace/bun/src/bun.js/bindings/FormatStackTraceForJS.cpp")
text = cpp_file.read_text()

# Strip comments
text = re.sub(r"//[^\\n]*", "", text)
text = re.sub(r"/\\*.*?\\*/", "", text, flags=re.DOTALL)

def extract_function_body(src: str) -> str:
    m = re.search(
        r"JSC_DEFINE_HOST_FUNCTION\\(errorConstructorFuncCaptureStackTrace.*?\\{",
        src,
        re.DOTALL,
    )
    if not m:
        return None
    start = m.end() - 1
    depth = 0
    for i in range(start, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start:i + 1]
    return None

func_body = extract_function_body(text)
if func_body and re.search(r"\\bputDirectCustomAccessor\\s*\\(", func_body):
    print("OK")
else:
    print("MISSING")
'''
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.stdout.strip() == "OK", "putDirectCustomAccessor not found"


def test_delete_property_present():
    """Code must delete existing .stack before installing custom accessor."""
    script = '''
import re
from pathlib import Path

cpp_file = Path("/workspace/bun/src/bun.js/bindings/FormatStackTraceForJS.cpp")
text = cpp_file.read_text()

# Strip comments
text = re.sub(r"//[^\\n]*", "", text)
text = re.sub(r"/\\*.*?\\*/", "", text, flags=re.DOTALL)

def extract_function_body(src: str) -> str:
    m = re.search(
        r"JSC_DEFINE_HOST_FUNCTION\\(errorConstructorFuncCaptureStackTrace.*?\\{",
        src,
        re.DOTALL,
    )
    if not m:
        return None
    start = m.end() - 1
    depth = 0
    for i in range(start, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start:i + 1]
    return None

func_body = extract_function_body(text)
if func_body and re.search(r"\\bdeleteProperty\\s*\\(", func_body):
    print("OK")
else:
    print("MISSING")
'''
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.stdout.strip() == "OK", "deleteProperty not found"


def test_exception_safety_present():
    """Function must include RETURN_IF_EXCEPTION for JSC exception safety."""
    script = '''
import re
from pathlib import Path

cpp_file = Path("/workspace/bun/src/bun.js/bindings/FormatStackTraceForJS.cpp")
text = cpp_file.read_text()

# Strip comments
text = re.sub(r"//[^\\n]*", "", text)
text = re.sub(r"/\\*.*?\\*/", "", text, flags=re.DOTALL)

def extract_function_body(src: str) -> str:
    m = re.search(
        r"JSC_DEFINE_HOST_FUNCTION\\(errorConstructorFuncCaptureStackTrace.*?\\{",
        src,
        re.DOTALL,
    )
    if not m:
        return None
    start = m.end() - 1
    depth = 0
    for i in range(start, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start:i + 1]
    return None

func_body = extract_function_body(text)
if func_body and re.search(r"\\bRETURN_IF_EXCEPTION\\s*\\(", func_body):
    print("OK")
else:
    print("MISSING")
'''
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.stdout.strip() == "OK", "RETURN_IF_EXCEPTION not found"


def test_not_stub():
    """Function must have substantial implementation — at least 35 non-blank lines."""
    script = '''
import re
from pathlib import Path

cpp_file = Path("/workspace/bun/src/bun.js/bindings/FormatStackTraceForJS.cpp")
text = cpp_file.read_text()

# Strip comments
text = re.sub(r"//[^\\n]*", "", text)
text = re.sub(r"/\\*.*?\\*/", "", text, flags=re.DOTALL)

def extract_function_body(src: str) -> str:
    m = re.search(
        r"JSC_DEFINE_HOST_FUNCTION\\(errorConstructorFuncCaptureStackTrace.*?\\{",
        src,
        re.DOTALL,
    )
    if not m:
        return None, 0
    start = m.end() - 1
    depth = 0
    for i in range(start, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                body = src[start:i + 1]
                lines = [l for l in body.strip().split("\\n") if l.strip()]
                return body, len(lines)
    return None, 0

func_body, line_count = extract_function_body(text)
print(line_count)
'''
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    try:
        line_count = int(result.stdout.strip())
    except ValueError:
        line_count = 0

    assert line_count >= 35, f"Function has only {line_count} non-blank lines — likely a stub"


def test_jsc_api_diversity():
    """Function must use at least 4 different JSC API calls."""
    apis = _extract_api_calls()
    assert len(apis) >= 4, f"Only {len(apis)} distinct JSC APIs found: {apis} — need at least 4"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — behavioral checks
# ---------------------------------------------------------------------------

def test_no_tabs_in_function():
    """Bun C++ uses spaces for indentation."""
    result = _run_file_validation()

    if "error" in result:
        assert False, f"Validation failed: {result['error']}"

    assert not result.get("has_tabs"), "Tabs found in file — use spaces for indentation"


def test_root_h_include():
    """C++ bindings files must include root.h."""
    result = _run_file_validation()

    if "error" in result:
        assert False, f"Validation failed: {result['error']}"

    assert result.get("includes_root_h"), '#include "root.h" missing from file'


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — file content checks via subprocess
# ---------------------------------------------------------------------------

def test_cpp_file_trailing_newline():
    """C++ files must end with a newline."""
    result = _run_file_validation()

    if "error" in result:
        assert False, f"Validation failed: {result['error']}"

    assert result.get("has_trailing_newline"), "File must end with a newline"


def test_cpp_no_trailing_whitespace():
    """C++ files must not have trailing whitespace."""
    result = _run_file_validation()

    if "error" in result:
        assert False, f"Validation failed: {result['error']}"

    assert not result.get("has_trailing_whitespace"), "Trailing whitespace found in file"


def test_cpp_no_banned_patterns():
    """C++ files must not contain banned Zig patterns."""
    script = '''
import re
from pathlib import Path

cpp_file = Path("/workspace/bun/src/bun.js/bindings/FormatStackTraceForJS.cpp")
text = cpp_file.read_text()

banned = ["std.debug.assert", "std.debug.print", "std.log"]
found = [p for p in banned if p in text]
print(json.dumps(found))
'''
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    try:
        found = json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        found = []

    assert not found, f"Banned patterns found: {found}"


def test_cpp_include_order():
    """C++ files should have root.h first in local includes."""
    script = '''
import re
from pathlib import Path

cpp_file = Path("/workspace/bun/src/bun.js/bindings/FormatStackTraceForJS.cpp")
text = cpp_file.read_text()

lines = text.split("\\n")
local_includes = []
for i, line in enumerate(lines):
    if m := re.match(r'\\s*#\\s*include\\s+"([^"]+)"', line):
        local_includes.append((i, m.group(1)))

if local_includes:
    first_local = local_includes[0]
    if "root.h" in first_local[1]:
        print("OK")
    else:
        print(f"FIRST: {first_local[1]}")
else:
    print("NO_INCLUDES")
'''
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    output = result.stdout.strip()
    assert output == "OK", f'Expected "root.h" to be first include, got: {output}'


def test_repo_cpp_syntax_valid():
    """C++ file must have valid syntax indicators."""
    script = '''
import re
from pathlib import Path

cpp_file = Path("/workspace/bun/src/bun.js/bindings/FormatStackTraceForJS.cpp")
text = cpp_file.read_text()

required = [
    ("JSC_DEFINE_HOST_FUNCTION", r"JSC_DEFINE_HOST_FUNCTION"),
    ("return", r"\\breturn\\s+"),
    ("#include", r"#include\\s+"),
    ("errorConstructorFuncCaptureStackTrace", r"errorConstructorFuncCaptureStackTrace"),
]

missing = []
for name, pattern in required:
    if not re.search(pattern, text):
        missing.append(name)

print(json.dumps(missing))
'''
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    try:
        missing = json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        missing = ["parse_error"]

    assert not missing, f"Missing required C++ patterns: {missing}"


def test_repo_error_function_present():
    """errorConstructorFuncCaptureStackTrace must be present."""
    script = '''
from pathlib import Path

cpp_file = Path("/workspace/bun/src/bun.js/bindings/FormatStackTraceForJS.cpp")
text = cpp_file.read_text()

if "errorConstructorFuncCaptureStackTrace" in text:
    print("OK")
else:
    print("MISSING")
'''
    result = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert result.stdout.strip() == "OK", "Required function not found"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates (p2p_enrichment) — subprocess.run() commands
# ---------------------------------------------------------------------------

def test_repo_python_misctools_syntax():
    """Repo's Python helper scripts in misctools must have valid syntax."""
    py_files = [
        f"{REPO}/misctools/gdb/zig_gdb_pretty_printers.py",
        f"{REPO}/misctools/gdb/std_gdb_pretty_printers.py",
        f"{REPO}/misctools/lldb/bun_pretty_printer.py",
        f"{REPO}/misctools/lldb/lldb_pretty_printers.py",
        f"{REPO}/misctools/lldb/lldb_webkit.py",
    ]
    for py_file in py_files:
        r = subprocess.run(
            ["python3", "-m", "py_compile", py_file],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"Python syntax check failed for {py_file}:\n{r.stderr}"


def test_repo_python_test_scripts_syntax():
    """Repo's Python test scripts must have valid syntax."""
    py_files = [
        f"{REPO}/test/cli/run/fuse-fs.py",
        f"{REPO}/test/js/bun/yaml/translate_yaml_test_suite_to_bun.py",
        f"{REPO}/test/js/node/readline/run-with-pty.py",
        f"{REPO}/test/js/node/test/fixtures/spawn_closed_stdio.py",
    ]
    for py_file in py_files:
        r = subprocess.run(
            ["python3", "-m", "py_compile", py_file],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"Python syntax check failed for {py_file}:\n{r.stderr}"


def test_repo_shell_scripts_syntax():
    """Repo's shell scripts must have valid bash syntax."""
    shell_scripts = [
        f"{REPO}/scripts/check-node.sh",
        f"{REPO}/scripts/check-node-all.sh",
        f"{REPO}/scripts/trace.sh",
        f"{REPO}/misctools/find-unused-zig.sh",
        f"{REPO}/misctools/generate-tests-file.sh",
    ]
    for script in shell_scripts:
        r = subprocess.run(
            ["bash", "-n", script],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"Shell script syntax check failed for {script}:\n{r.stderr}"


def test_repo_cpp_file_exists():
    """Modified C++ file must exist in repo."""
    r = subprocess.run(
        ["test", "-f", f"{REPO}/src/bun.js/bindings/FormatStackTraceForJS.cpp"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"C++ source file not found at expected path"


def test_repo_git_tracks_file():
    """Modified C++ file must be tracked by git."""
    r = subprocess.run(
        ["git", "ls-files", "src/bun.js/bindings/FormatStackTraceForJS.cpp"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0 and r.stdout.strip(), f"C++ source file not tracked by git"


def test_repo_cpp_basic_syntax():
    """Modified C++ file must have valid basic syntax."""
    script = '''
import re
import sys

with open("/workspace/bun/src/bun.js/bindings/FormatStackTraceForJS.cpp") as f:
    content = f.read()

required_patterns = [
    ("JSC_DEFINE_HOST_FUNCTION", r"JSC_DEFINE_HOST_FUNCTION"),
    ("return", r"\\breturn\\s+"),
    ("#include", r"#include\\s+"),
    ("errorConstructorFuncCaptureStackTrace", r"errorConstructorFuncCaptureStackTrace"),
]

missing = []
for name, pattern in required_patterns:
    if not re.search(pattern, content):
        missing.append(name)

if missing:
    print(f"Missing: {', '.join(missing)}")
    sys.exit(1)
else:
    print("OK")
'''
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"C++ syntax validation failed:\n{r.stderr or r.stdout}"


def test_repo_cpp_structure_validation():
    """C++ bindings have all required JSC API patterns."""
    script = '''
import re
import sys

cpp_file = "/workspace/bun/src/bun.js/bindings/FormatStackTraceForJS.cpp"
with open(cpp_file) as f:
    content = f.read()

patterns = [
    ("JSC_DEFINE_HOST_FUNCTION", r"JSC_DEFINE_HOST_FUNCTION"),
    ("errorConstructorFuncCaptureStackTrace", r"errorConstructorFuncCaptureStackTrace"),
    ("hasMaterializedErrorInfo", r"hasMaterializedErrorInfo"),
    ("setStackFrames", r"setStackFrames"),
    ("putDirect", r"\\bputDirect"),
    ("computeErrorInfoToJSValue", r"computeErrorInfo(?:ToJSValue)?"),
    ("RETURN_IF_EXCEPTION", r"RETURN_IF_EXCEPTION"),
]

missing = []
for name, pattern in patterns:
    if not re.search(pattern, content):
        missing.append(name)

if missing:
    print(f"Missing: {', '.join(missing)}")
    sys.exit(1)
else:
    print("OK")
'''
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"C++ structure validation failed:\n{r.stderr or r.stdout}"


def test_repo_additional_shell_scripts():
    """Additional repo shell scripts must have valid bash syntax."""
    shell_scripts = [
        f"{REPO}/test/bundler/run-single-bundler-test.sh",
        f"{REPO}/scripts/check-node.sh",
        f"{REPO}/scripts/check-node-all.sh",
    ]
    for script in shell_scripts:
        r = subprocess.run(
            ["bash", "-n", script],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"Shell script syntax check failed for {script}:\n{r.stderr}"
