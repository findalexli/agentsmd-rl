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
