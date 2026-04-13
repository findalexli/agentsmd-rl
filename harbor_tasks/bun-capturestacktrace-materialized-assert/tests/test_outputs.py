"""
Task: bun-capturestacktrace-materialized-assert
Repo: oven-sh/bun @ 44f5b6a1dc8f0c03fe81c6f133f9565c9457a4e7
PR:   28617

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

C++ task (JSC/WebKit bindings). Cannot compile Bun in the test container,
so f2p checks use subprocess.run() to execute Python scripts that parse
the C++ source with brace-matching scope analysis.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/bun"
CPP_FILE = Path(REPO) / "src/bun.js/bindings/FormatStackTraceForJS.cpp"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_function_body(strip_comments: bool = True) -> str:
    """Extract errorConstructorFuncCaptureStackTrace body from C++ source."""
    text = CPP_FILE.read_text()
    m = re.search(
        r"errorConstructorFuncCaptureStackTrace\b(.*?)(?=\nJSC_DEFINE_HOST_FUNCTION|\Z)",
        text,
        re.DOTALL,
    )
    assert m, "errorConstructorFuncCaptureStackTrace not found in source file"
    body = m.group(1)
    if strip_comments:
        body = re.sub(r"//[^\n]*", "", body)
        body = re.sub(r"/\*.*?\*/", "", body, flags=re.DOTALL)
    return body


def _run_cpp_check(assertion_code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python verification script via subprocess that analyzes the C++ source.

    The subprocess receives `text` (file contents, comments stripped) and a
    pre-loaded `_extract_branches()` helper that returns (if_body, else_body)
    for the hasMaterializedErrorInfo conditional block. The assertion_code
    should use `assert` statements and `print("PASS")` on success.
    """
    preamble = (
        'import re, sys\n'
        'from pathlib import Path\n'
        '\n'
        f'text = Path("{CPP_FILE}").read_text()\n'
        '# Strip comments to prevent trivial gaming\n'
        r'text = re.sub(r"//[^\n]*", "", text)' + '\n'
        r'text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)' + '\n'
        '\n'
    )

    extractor = (
        r'def _extract_branches():' + '\n'
        r'    m = re.search(r"errorConstructorFuncCaptureStackTrace\b", text)' + '\n'
        r'    assert m, "errorConstructorFuncCaptureStackTrace not found"' + '\n'
        r'    region = text[m.start():]' + '\n'
        r'    # \w+ before -> rejects negated form (!instance->)' + '\n'
        r'    if_m = re.search(r"\bif\s*\(\s*\w+->hasMaterializedErrorInfo\s*\(\s*\)\s*\)", region)' + '\n'
        r'    assert if_m, "Positive hasMaterializedErrorInfo if-condition not found"' + '\n'
        r'    rest = region[if_m.end():]' + '\n'
        r'    bp = rest.find("{")' + '\n'
        r'    assert bp >= 0, "No opening brace after if-condition"' + '\n'
        r'    depth, end = 0, -1' + '\n'
        r'    for i in range(bp, len(rest)):' + '\n'
        r'        if rest[i] == "{": depth += 1' + '\n'
        r'        elif rest[i] == "}":' + '\n'
        r'            depth -= 1' + '\n'
        r'            if depth == 0: end = i; break' + '\n'
        r'    assert end >= 0, "Unbalanced braces in if-body"' + '\n'
        r'    if_body = rest[bp:end + 1]' + '\n'
        r'    erest = rest[end + 1:]' + '\n'
        r'    em = re.search(r"\belse\s*\{", erest)' + '\n'
        r'    else_body = ""' + '\n'
        r'    if em:' + '\n'
        r'        eb = em.end() - 1' + '\n'
        r'        depth = 0' + '\n'
        r'        for i in range(eb, len(erest)):' + '\n'
        r'            if erest[i] == "{": depth += 1' + '\n'
        r'            elif erest[i] == "}":' + '\n'
        r'                depth -= 1' + '\n'
        r'                if depth == 0: else_body = erest[eb:i + 1]; break' + '\n'
        r'    return if_body, else_body' + '\n'
        '\n'
        'if_body, else_body = _extract_branches()\n'
    )

    script = preamble + extractor + "\n" + assertion_code
    tmp = Path("/tmp/_cpp_check.py")
    tmp.write_text(script)
    try:
        return subprocess.run(
            ["python3", str(tmp)],
            capture_output=True, text=True, timeout=timeout,
        )
    finally:
        tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_source_file_exists():
    """FormatStackTraceForJS.cpp must exist and be non-empty."""
    assert CPP_FILE.exists(), f"{CPP_FILE} does not exist"
    assert CPP_FILE.stat().st_size > 0, f"{CPP_FILE} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — subprocess-based C++ scope analysis
# ---------------------------------------------------------------------------

def test_materialized_branch_with_else():
    """hasMaterializedErrorInfo must be a POSITIVE branching condition
    (if+else), not a negated guard. The buggy code has if (!...) with no
    dedicated else for the materialized path."""
    r = _run_cpp_check(
        'assert else_body, "No else branch after hasMaterializedErrorInfo check"\n'
        'print("PASS")\n'
    )
    assert r.returncode == 0, (
        f"Branch structure check failed:\n{r.stderr or r.stdout}"
    )


def test_setStackFrames_not_in_materialized_path():
    """setStackFrames must NOT appear in the materialized-info (if) branch.
    The buggy code calls setStackFrames unconditionally after materialization,
    violating JSC's invariant (m_errorInfoMaterialized=true + non-null m_stackTrace)."""
    r = _run_cpp_check(
        'assert not re.search(r"\\bsetStackFrames\\s*\\(", if_body), (\n'
        '    "setStackFrames found in materialized (if) branch — "\n'
        '    "this causes ASSERT(!m_errorInfoMaterialized) failure"\n'
        ')\n'
        'print("PASS")\n'
    )
    assert r.returncode == 0, (
        f"setStackFrames check failed:\n{r.stderr or r.stdout}"
    )


def test_materialized_path_eagerly_sets_stack():
    """When error info is already materialized, the fix must eagerly compute
    and set the .stack property via putDirect (not through lazy accessor)."""
    r = _run_cpp_check(
        'assert re.search(r"\\bputDirect\\s*\\(", if_body), (\n'
        '    "Materialized path missing putDirect call for .stack property"\n'
        ')\n'
        'assert re.search(r"\\bcomputeErrorInfoToJSValue\\s*\\(", if_body), (\n'
        '    "Materialized path missing computeErrorInfoToJSValue call"\n'
        ')\n'
        'print("PASS")\n'
    )
    assert r.returncode == 0, (
        f"Eager stack write check failed:\n{r.stderr or r.stdout}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + structural
# ---------------------------------------------------------------------------

def test_function_signature_preserved():
    """errorConstructorFuncCaptureStackTrace must still be declared with
    JSC_DEFINE_HOST_FUNCTION wrapper."""
    text = CPP_FILE.read_text()
    assert re.search(
        r"JSC_DEFINE_HOST_FUNCTION.*errorConstructorFuncCaptureStackTrace", text
    ), "errorConstructorFuncCaptureStackTrace function signature missing"


def test_lazy_accessor_in_non_materialized_path():
    """Non-materialized path must still install a lazy custom accessor via
    putDirectCustomAccessor — preserves lazy evaluation for the common case."""
    body = _get_function_body()
    assert re.search(
        r"\bputDirectCustomAccessor\s*\(", body
    ), "putDirectCustomAccessor missing — lazy accessor for non-materialized path removed"


def test_delete_property_preserved():
    """Non-materialized path must delete the existing .stack property before
    installing the custom accessor (DeletePropertySlot pattern)."""
    body = _get_function_body()
    assert re.search(
        r"\bdeleteProperty\s*\(", body
    ), "deleteProperty missing — needed to clear .stack before installing custom accessor"


def test_exception_safety():
    """Function must include RETURN_IF_EXCEPTION for proper JSC exception safety."""
    body = _get_function_body()
    assert re.search(
        r"\bRETURN_IF_EXCEPTION\s*\(", body
    ), "RETURN_IF_EXCEPTION missing — exception safety violated"


def test_not_stub():
    """Function must have substantial implementation — at least 35 non-blank
    non-comment lines. Prevents trivial stubs."""
    body = _get_function_body()
    lines = [line for line in body.strip().split("\n") if line.strip()]
    assert (
        len(lines) >= 35
    ), f"Function has only {len(lines)} non-blank lines — likely a stub"


def test_jsc_api_diversity():
    """Function must use at least 4 different JSC API calls — prevents
    keyword-stuffed or minimal implementations."""
    body = _get_function_body()
    api_patterns = [
        r"\bjsDynamicCast\s*<",
        r"\bRETURN_IF_EXCEPTION\s*\(",
        r"\bputDirect(CustomAccessor|WithoutTransition)?\s*\(",
        r"\bdeleteProperty\s*\(",
        r"\bsetStackFrames\s*\(",
        r"\bhasMaterializedErrorInfo\s*\(",
        r"\bmaterializeErrorInfoIfNeeded\s*\(",
        r"\bcomputeErrorInfo(ToJSValue)?\s*\(",
        r"\bgetFramesForCaller\s*\(",
        r"\bDeletePropertyModeScope\b",
    ]
    found = sum(1 for pat in api_patterns if re.search(pat, body))
    assert found >= 4, f"Only {found} distinct JSC APIs found — need at least 4"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md / SKILL.md
# ---------------------------------------------------------------------------

def test_no_tabs_in_function():
    """Bun C++ uses spaces for indentation. No tabs in the function body.
    Derived from AGENTS.md: 'Follow existing code style - check neighboring files for patterns'."""
    text = CPP_FILE.read_text()
    m = re.search(
        r"errorConstructorFuncCaptureStackTrace\b(.*?)(?=\nJSC_DEFINE_HOST_FUNCTION|\Z)",
        text,
        re.DOTALL,
    )
    assert m, "Function not found"
    assert "\t" not in m.group(1), "Tabs found in function body — use spaces"


def test_root_h_include():
    """C++ bindings files must include root.h at the top.
    Derived from implementing-jsc-classes-cpp SKILL.md: 'Include #include "root.h" at the top of C++ files'."""
    text = CPP_FILE.read_text()
    lines = text.split("\n")
    include_lines = [
        (i, line) for i, line in enumerate(lines)
        if re.match(r'\s*#\s*include\s+[<"]', line)
    ]
    assert include_lines, "No #include directives found in file"
    root_h = [line for _, line in include_lines if "root.h" in line]
    assert root_h, '#include "root.h" missing from FormatStackTraceForJS.cpp'


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — file content checks for repo coding standards
# These verify the repo's coding standards by checking file content directly.
# NOTE: These are origin: static because they read files directly, not run CI commands.
# ---------------------------------------------------------------------------

def test_cpp_file_trailing_newline():
    """C++ files must end with a newline (pass_to_pass static check)."""
    text = CPP_FILE.read_text()
    assert text.endswith("\n"), "File must end with a newline"


def test_cpp_no_trailing_whitespace():
    """C++ files must not have trailing whitespace (pass_to_pass static check)."""
    text = CPP_FILE.read_text()
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        if line != line.rstrip():
            assert False, f"Trailing whitespace on line {i}"


def test_cpp_no_banned_patterns():
    """C++ files must not contain banned Zig patterns (pass_to_pass static check)."""
    text = CPP_FILE.read_text()
    banned_patterns = [
        "std.debug.assert",
        "std.debug.print",
        "std.log",
    ]
    for pattern in banned_patterns:
        assert pattern not in text, f"Banned pattern '{pattern}' found in C++ file"


def test_cpp_include_order():
    """C++ files should have root.h first in local includes (pass_to_pass static check)."""
    text = CPP_FILE.read_text()
    lines = text.split("\n")
    local_includes = []
    for i, line in enumerate(lines):
        if m := re.match(r'\s*#\s*include\s+"([^"]+)"', line):
            local_includes.append((i, m.group(1)))
    if local_includes:
        first_local = local_includes[0]
        assert "root.h" in first_local[1], f'Expected "root.h" to be first include, found "{first_local[1]}"'


def test_repo_cpp_syntax_valid():
    """C++ file must have valid syntax indicators (pass_to_pass static check)."""
    text = CPP_FILE.read_text()
    required_patterns = [
        r"#include\s+",
        r"JSC_DEFINE_HOST_FUNCTION",
        r"return\s+",
        r"\{\s*\n",
    ]
    for pattern in required_patterns:
        assert re.search(pattern, text), f"Missing required C++ pattern: {pattern}"


def test_repo_error_function_present():
    """errorConstructorFuncCaptureStackTrace must be present (pass_to_pass static check)."""
    text = CPP_FILE.read_text()
    assert "errorConstructorFuncCaptureStackTrace" in text, "Required function not found"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates (p2p_enrichment) — subprocess.run() commands
# These run actual commands that the repo's CI runs. MUST use subprocess.run().
# ---------------------------------------------------------------------------

def test_repo_python_misctools_syntax():
    """Repo's Python helper scripts in misctools must have valid syntax (pass_to_pass repo_tests).
    CI validates these debugging helper scripts compile correctly."""
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
    """Repo's Python test scripts must have valid syntax (pass_to_pass repo_tests).
    CI validates test helper scripts compile correctly."""
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
    """Repo's shell scripts must have valid bash syntax (pass_to_pass repo_tests).
    CI validates shell script syntax as part of linting."""
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
    """Modified C++ file must exist in repo (pass_to_pass repo_tests).
    Verifies the target file for the PR fix is present at expected path."""
    r = subprocess.run(
        ["test", "-f", f"{REPO}/src/bun.js/bindings/FormatStackTraceForJS.cpp"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"C++ source file not found at expected path"


def test_repo_git_tracks_file():
    """Modified C++ file must be tracked by git (pass_to_pass repo_tests).
    Verifies the target file is part of the git repository."""
    r = subprocess.run(
        ["git", "ls-files", "src/bun.js/bindings/FormatStackTraceForJS.cpp"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0 and r.stdout.strip(), f"C++ source file not tracked by git"


def test_repo_cpp_basic_syntax():
    """Modified C++ file must have valid basic syntax (pass_to_pass repo_tests).
    CI validates that C++ source files have required structural elements."""
    script = '''
import re
import sys

with open("/workspace/bun/src/bun.js/bindings/FormatStackTraceForJS.cpp") as f:
    content = f.read()

required_patterns = [
    ("JSC_DEFINE_HOST_FUNCTION", "Function definition"),
    ("return", "Return statement"),
    ("#include", "Include directive"),
    ("errorConstructorFuncCaptureStackTrace", "Target function name"),
]

for pattern, desc in required_patterns:
    if pattern not in content:
        print(f"Missing required element: {desc}")
        sys.exit(1)

print("Basic C++ syntax validation passed")
'''
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"C++ syntax validation failed:\n{r.stderr}"


def test_repo_cpp_structure_validation():
    '''Modified C++ file must have complete structure with required components (pass_to_pass repo_tests).
    CI validates that C++ bindings have all necessary JSC API patterns.'''
    script = '''
import re
import sys

cpp_file = "/workspace/bun/src/bun.js/bindings/FormatStackTraceForJS.cpp"
with open(cpp_file) as f:
    content = f.read()

patterns = [
    ("JSC_DEFINE_HOST_FUNCTION", "Host function definition"),
    ("errorConstructorFuncCaptureStackTrace", "Target function name"),
    ("hasMaterializedErrorInfo", "Materialized error check"),
    ("setStackFrames", "Stack frames setter"),
    ("putDirect", "Direct property setter"),
    ("computeErrorInfoToJSValue", "Error info computation"),
    ("RETURN_IF_EXCEPTION", "Exception safety"),
]

failed = 0
for pattern, desc in patterns:
    if pattern not in content:
        print(f"Missing: {desc}")
        failed += 1

if failed > 0:
    sys.exit(1)

print("C++ structure validation passed")
'''
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"C++ structure validation failed:\n{r.stderr}"


def test_repo_additional_shell_scripts():
    '''Additional repo shell scripts must have valid bash syntax (pass_to_pass repo_tests).
    CI validates shell script syntax as part of linting.'''
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


