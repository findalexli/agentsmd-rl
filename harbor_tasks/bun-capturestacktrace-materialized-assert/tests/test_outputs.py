"""
Task: bun-capturestacktrace-materialized-assert
Repo: oven-sh/bun @ 44f5b6a1dc8f0c03fe81c6f133f9565c9457a4e7
PR:   28617

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: This is a C++ task (JSC/WebKit). The test container cannot compile
or execute Bun, so all checks are structural — they parse the source file
and verify the correct code patterns exist. We strip comments to prevent
trivial gaming.
"""

import re
from pathlib import Path

REPO = "/workspace/bun"
CPP_FILE = Path(REPO) / "src/bun.js/bindings/FormatStackTraceForJS.cpp"


def _get_function_body(strip_comments: bool = True) -> str:
    """Extract errorConstructorFuncCaptureStackTrace body, optionally stripped of comments."""
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


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_source_file_exists():
    """FormatStackTraceForJS.cpp must exist and be non-empty."""
    assert CPP_FILE.exists(), f"{CPP_FILE} does not exist"
    assert CPP_FILE.stat().st_size > 0, f"{CPP_FILE} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core bug fix checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_materialized_branch_with_else():
    """hasMaterializedErrorInfo must be used as a POSITIVE branching condition
    (if+else), not a negated guard. The buggy code has if (!has...) with no
    dedicated else for the materialized path."""
    body = _get_function_body()
    # Must be a positive check: if (x->hasMaterializedErrorInfo()), NOT if (!x->hasMaterializedErrorInfo())
    # \w+ before -> rejects the negated form since ! is not \w
    has_positive_if = re.search(r"\bif\s*\(\s*\w+->hasMaterializedErrorInfo\s*\(", body)
    assert has_positive_if, (
        "hasMaterializedErrorInfo not used as a positive if-condition — "
        "the buggy pattern uses if (!...) which inverts the logic"
    )
    after_if = body[has_positive_if.start() :]
    assert re.search(
        r"\}\s*else\s*\{", after_if
    ), "No else branch after hasMaterializedErrorInfo check"


# [pr_diff] fail_to_pass
def test_setStackFrames_not_in_materialized_path():
    """setStackFrames must NOT appear in the materialized-info branch.
    The buggy code calls setStackFrames unconditionally after materialization,
    violating JSC's invariant (m_errorInfoMaterialized=true + non-null m_stackTrace)."""
    body = _get_function_body()
    has_if = re.search(r"\bif\s*\(.*hasMaterializedErrorInfo\s*\(", body)
    assert has_if, "hasMaterializedErrorInfo if-block not found"
    after_if = body[has_if.start() :]
    else_match = re.search(r"\}\s*else\s*\{", after_if)
    assert else_match, "No else branch found"
    materialized_block = after_if[: else_match.start()]
    assert not re.search(
        r"\bsetStackFrames\s*\(", materialized_block
    ), "setStackFrames called in materialized path — this causes the assertion failure"


# [pr_diff] fail_to_pass
def test_materialized_path_eagerly_sets_stack():
    """When error info is already materialized, the fix must eagerly compute
    and set the .stack property via a direct-write API (putDirect, etc.),
    NOT through setStackFrames + lazy accessor."""
    body = _get_function_body()
    has_if = re.search(r"\bif\s*\(.*hasMaterializedErrorInfo\s*\(", body)
    assert has_if, "hasMaterializedErrorInfo if-block not found"
    after_if = body[has_if.start() :]
    else_match = re.search(r"\}\s*else\s*\{", after_if)
    assert else_match, "No else branch found"
    materialized_block = after_if[: else_match.start()]
    assert re.search(
        r"\b(putDirect|putDirectWithoutTransition|defineOwnProperty)\s*\(",
        materialized_block,
    ), "Materialized path missing direct property write for .stack"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + structural
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_function_signature_preserved():
    """errorConstructorFuncCaptureStackTrace must still be declared with
    JSC_DEFINE_HOST_FUNCTION wrapper."""
    text = CPP_FILE.read_text()
    assert re.search(
        r"JSC_DEFINE_HOST_FUNCTION.*errorConstructorFuncCaptureStackTrace", text
    ), "errorConstructorFuncCaptureStackTrace function signature missing"


# [pr_diff] pass_to_pass
def test_lazy_accessor_in_non_materialized_path():
    """Non-materialized path must still install a lazy custom accessor via
    putDirectCustomAccessor — this preserves lazy evaluation for the common case."""
    body = _get_function_body()
    assert re.search(
        r"\bputDirectCustomAccessor\s*\(", body
    ), "putDirectCustomAccessor missing — lazy accessor for non-materialized path removed"


# [pr_diff] pass_to_pass
def test_delete_property_preserved():
    """Non-materialized path must delete the existing .stack property before
    installing the custom accessor (DeletePropertySlot pattern)."""
    body = _get_function_body()
    assert re.search(
        r"\bdeleteProperty\s*\(", body
    ), "deleteProperty missing — needed to clear .stack before installing custom accessor"


# [pr_diff] pass_to_pass
def test_exception_safety():
    """Function must include RETURN_IF_EXCEPTION for proper JSC exception safety."""
    body = _get_function_body()
    assert re.search(
        r"\bRETURN_IF_EXCEPTION\s*\(", body
    ), "RETURN_IF_EXCEPTION missing — exception safety violated"


# [static] pass_to_pass
def test_not_stub():
    """Function must have substantial implementation — at least 35 non-blank
    non-comment lines. Prevents trivial stubs."""
    body = _get_function_body()
    lines = [line for line in body.strip().split("\n") if line.strip()]
    assert (
        len(lines) >= 35
    ), f"Function has only {len(lines)} non-blank lines — likely a stub"


# [static] pass_to_pass
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

# [agent_config] pass_to_pass — AGENTS.md:228 (follow existing code style)
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


# [agent_config] pass_to_pass — .claude/skills/implementing-jsc-classes-cpp/SKILL.md:184
def test_root_h_include():
    """C++ bindings files must include root.h at the top.
    Derived from implementing-jsc-classes-cpp SKILL.md: 'Include #include "root.h" at the top of C++ files'."""
    # AST-only because: C++ cannot be compiled/executed in this container
    text = CPP_FILE.read_text()
    # root.h must appear before any other includes or code
    lines = text.split("\n")
    include_lines = [
        (i, line) for i, line in enumerate(lines)
        if re.match(r'\s*#\s*include\s+[<"]', line)
    ]
    assert include_lines, "No #include directives found in file"
    root_h = [line for _, line in include_lines if "root.h" in line]
    assert root_h, '#include "root.h" missing from FormatStackTraceForJS.cpp'
