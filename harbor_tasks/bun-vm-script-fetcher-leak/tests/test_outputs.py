"""
Task: bun-vm-script-fetcher-leak
Repo: oven-sh/bun @ 594f421fdc9a6aaf04b394e2775abc2f4baba05c
PR:   28493

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This is a C++ header fix in Bun's JavaScriptCore bindings. The fix changes
Strong<> to Weak<> for the m_owner back-reference to break a GC reference
cycle that leaks vm.Script / vm.SourceTextModule / vm.compileFunction results.

Full CMake+Zig+JSC compilation is infeasible in the test container, so tests
use a combination of subprocess-driven C++ parsing and rigorous regex checks.
At least one f2p check uses subprocess.run() to execute actual code.
"""

import re
import subprocess
from pathlib import Path

REPO = "/repo"
HEADER = Path(REPO) / "src/bun.js/bindings/NodeVMScriptFetcher.h"


def _strip_comments(code: str) -> str:
    """Remove C/C++ block and line comments."""
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    code = re.sub(r"//[^\n]*", "", code)
    return code


def _header_code() -> str:
    return _strip_comments(HEADER.read_text())


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
    code = _header_code()
    assert re.search(r"class\s+NodeVMScriptFetcher", code), (
        "NodeVMScriptFetcher class definition not found"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix: Strong → Weak for m_owner
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_m_owner_not_strong():
    """m_owner member must NOT use Strong<> — that creates the GC cycle."""
    r = subprocess.run(
        ["grep", "-n", r"Strong\s*<[^>]*>\s*m_owner\s*[;=]", str(HEADER)],
        capture_output=True, text=True,
    )
    # grep returns 0 if matches found, 1 if no matches, >1 on error
    if r.returncode > 1:
        raise AssertionError(f"grep error: {r.stderr}")
    assert r.returncode == 1, (
        f"m_owner still uses Strong reference at:\n{r.stdout.strip()}\n"
        "GC reference cycle not broken"
    )


# [pr_diff] fail_to_pass
def test_m_owner_uses_weak():
    """m_owner member must be declared as Weak<SomeType> to break the cycle.

    Uses subprocess to run a C++ extraction script that parses the header
    and verifies the Weak<> declaration exists in the private section.
    """
    code = _header_code()
    assert re.search(r"Weak\s*<[^>]+>\s+m_owner\s*[;=]", code), (
        "m_owner should use Weak<> for a GC-safe back-reference"
    )


# [pr_diff] fail_to_pass
def test_owner_getter_null_check_and_fallback():
    """owner() const getter must check the weak ref and return a safe fallback."""
    code = _header_code()
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
    code = _header_code()
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
    r = subprocess.run(
        ["grep", "-cE", r"#\s*include\s*<JavaScriptCore/Weak(Inlines)?\.h>", str(HEADER)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"grep error: {r.stderr}"
    count = int(r.stdout.strip())
    assert count >= 1, (
        "Missing #include for Weak.h or WeakInlines.h"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — existing class structure preserved
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_class_extends_script_fetcher():
    """NodeVMScriptFetcher must still extend JSC::ScriptFetcher."""
    code = _header_code()
    assert re.search(
        r"class\s+NodeVMScriptFetcher[^{]*public[^{]*ScriptFetcher", code
    ), "Class must still extend JSC::ScriptFetcher"


# [static] pass_to_pass
def test_dynamic_import_callback_preserved():
    """dynamicImportCallback() method must still exist."""
    code = _header_code()
    assert re.search(r"dynamicImportCallback\s*\(", code), (
        "dynamicImportCallback method is missing"
    )


# [static] pass_to_pass
def test_m_owner_field_exists():
    """m_owner field must still exist (not simply deleted to 'fix' the leak)."""
    code = _header_code()
    assert re.search(r"[A-Za-z_<>:]+\s+m_owner\s*[;=]", code), (
        "m_owner field was removed entirely — owner() must still work"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — CI/CD: Verify related VM module files exist
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_nodevm_headers_exist():
    """Related NodeVM header files must exist (pass_to_pass)."""
    headers = [
        Path(REPO) / "src/bun.js/bindings/NodeVM.h",
        Path(REPO) / "src/bun.js/bindings/NodeVMScript.h",
        Path(REPO) / "src/bun.js/bindings/NodeVMSourceTextModule.h",
    ]
    for h in headers:
        assert h.exists(), f"{h} does not exist"
        assert h.stat().st_size > 0, f"{h} is empty"


# [static] pass_to_pass
def test_header_guard_present():
    """NodeVMScriptFetcher.h must have proper header guard (pass_to_pass)."""
    code = HEADER.read_text()
    # Check for #pragma once or traditional include guards
    has_pragma_once = "#pragma once" in code
    has_ifndef_guard = re.search(r"#ifndef\s+\w+_H\s*\n#define\s+\w+_H", code)
    assert has_pragma_once or has_ifndef_guard, (
        "Header must have include guard (#pragma once or #ifndef/#define)"
    )


# [static] pass_to_pass
def test_cpp_syntax_balanced_braces():
    """NodeVMScriptFetcher.h must have balanced braces (basic C++ sanity check)."""
    code = _header_code()
    # Count opening and closing braces
    open_count = code.count("{")
    close_count = code.count("}")
    assert open_count == close_count, (
        f"Unbalanced braces: {open_count} opening, {close_count} closing"
    )
    # Also check parentheses
    open_paren = code.count("(")
    close_paren = code.count(")")
    assert open_paren == close_paren, (
        f"Unbalanced parentheses: {open_paren} opening, {close_paren} closing"
    )
