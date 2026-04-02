"""
Task: bun-vm-script-fetcher-leak
Repo: oven-sh/bun @ 594f421fdc9a6aaf04b394e2775abc2f4baba05c
PR:   28493

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: This is a C++ header fix. Bun requires a full CMake+Zig+JSC build
that is infeasible in the test container, so every check is structural
(regex on the source file). Each regex is context-aware — it matches
declarations/definitions, not stray occurrences in comments or strings.
"""

import re
from pathlib import Path

REPO = "/repo"
HEADER = Path(REPO) / "src/bun.js/bindings/NodeVMScriptFetcher.h"


def _strip_comments(code: str) -> str:
    """Remove C/C++ block and line comments."""
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    code = re.sub(r"//[^\n]*", "", code)
    return code


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file and class must exist
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_header_file_exists():
    """NodeVMScriptFetcher.h must exist and be non-empty."""
    assert HEADER.exists(), f"{HEADER} does not exist"
    assert HEADER.stat().st_size > 0, f"{HEADER} is empty"


# [static] pass_to_pass
def test_class_definition_present():
    """NodeVMScriptFetcher class definition must be present."""
    code = _strip_comments(HEADER.read_text())
    assert re.search(r"class\s+NodeVMScriptFetcher", code), (
        "NodeVMScriptFetcher class definition not found"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix: Strong → Weak for m_owner
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_m_owner_not_strong():
    """m_owner member must NOT use Strong<> — that creates the GC cycle."""
    code = _strip_comments(HEADER.read_text())
    match = re.search(r"Strong\s*<[^>]*>\s+m_owner\s*[;=]", code)
    assert match is None, (
        "m_owner still uses Strong reference — GC reference cycle not broken"
    )


# [pr_diff] fail_to_pass
def test_m_owner_uses_weak():
    """m_owner member must be declared as Weak<SomeType> to break the cycle."""
    code = _strip_comments(HEADER.read_text())
    assert re.search(r"Weak\s*<[^>]+>\s+m_owner\s*[;=]", code), (
        "m_owner should use Weak<> for a GC-safe back-reference"
    )


# [pr_diff] fail_to_pass
def test_owner_getter_null_check_and_fallback():
    """owner() const getter must check the weak ref and return a safe fallback."""
    code = _strip_comments(HEADER.read_text())
    m = re.search(r"owner\s*\(\s*\)\s*const\s*\{([^}]*)\}", code, re.DOTALL)
    assert m, "owner() const getter not found"
    body = m.group(1)
    # Require an explicit conditional (if or ternary) — plain .get() doesn't count
    has_check = bool(re.search(r"(if\s*\(|\?)", body))
    has_fallback = bool(re.search(r"jsUndefined|jsNull|JSValue\s*[\(\{]\s*[\)\}]", body))
    assert has_check, "owner() getter must check whether the weak ref is still alive"
    assert has_fallback, "owner() getter must return a safe fallback (e.g. jsUndefined())"


# [pr_diff] fail_to_pass
def test_owner_setter_or_ctor_guards_iscell():
    """Owner setter and/or constructor must guard Weak assignment with isCell/isObject."""
    code = _strip_comments(HEADER.read_text())
    found = 0

    # Check setter: void owner(VM&, JSValue...) { ... }
    setter = re.search(r"void\s+owner\s*\([^)]*\)\s*\{([^}]*)\}", code, re.DOTALL)
    if setter:
        body = setter.group(1)
        if re.search(r"isCell|isObject", body) and re.search(r"Weak\s*<", body):
            found += 1

    # Check constructor: NodeVMScriptFetcher(...) [: init-list] { ... }
    ctor = re.search(
        r"NodeVMScriptFetcher\s*\([^)]*\)\s*(?::[^{]*)?\{([^}]*)\}", code, re.DOTALL
    )
    if ctor:
        body = ctor.group(1)
        if re.search(r"isCell|isObject", body) and re.search(r"Weak\s*<", body):
            found += 1

    assert found >= 1, (
        "At least one of owner setter or constructor must guard with isCell/isObject "
        "before assigning to Weak<>"
    )


# [pr_diff] fail_to_pass
def test_weak_header_included():
    """Must #include a Weak-related JSC header (Weak.h or WeakInlines.h)."""
    code = _strip_comments(HEADER.read_text())
    assert re.search(r"#\s*include\s*<JavaScriptCore/Weak(Inlines)?\.h>", code), (
        "Missing #include for Weak.h or WeakInlines.h"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — existing class structure preserved
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_class_extends_script_fetcher():
    """NodeVMScriptFetcher must still extend JSC::ScriptFetcher."""
    code = _strip_comments(HEADER.read_text())
    assert re.search(
        r"class\s+NodeVMScriptFetcher[^{]*public[^{]*ScriptFetcher", code
    ), "Class must still extend JSC::ScriptFetcher"


# [repo_tests] pass_to_pass
def test_dynamic_import_callback_preserved():
    """dynamicImportCallback() method must still exist."""
    code = _strip_comments(HEADER.read_text())
    assert re.search(r"dynamicImportCallback\s*\(", code), (
        "dynamicImportCallback method is missing"
    )


# [repo_tests] pass_to_pass
def test_m_owner_field_exists():
    """m_owner field must still exist (not simply deleted to 'fix' the leak)."""
    code = _strip_comments(HEADER.read_text())
    assert re.search(r"[A-Za-z_<>:]+\s+m_owner\s*[;=]", code), (
        "m_owner field was removed entirely — owner() must still work"
    )
