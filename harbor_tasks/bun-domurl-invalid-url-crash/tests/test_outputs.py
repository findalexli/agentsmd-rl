"""
Task: bun-domurl-invalid-url-crash
Repo: oven-sh/bun @ 9e93bfa1b69a2f9b8c05acb15e02c5506dd4cbc8
PR:   28309

Fix: Add RETURN_IF_EXCEPTION(throwScope, {}); between toJSNewlyCreated and
jsCast in BunString__toJSDOMURL (src/bun.js/bindings/BunString.cpp).

Building Bun requires Zig + WebKit (~30min, ~32GB RAM), so all tests are
structural — they inspect the C++ source to verify the fix is applied.
# AST-only because: C++ code requires full Bun build chain (Zig + WebKit + CMake)

All checks must pass for reward = 1. Any failure = reward 0.
Each def test_*() maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/repo"
TARGET = f"{REPO}/src/bun.js/bindings/BunString.cpp"


def _load() -> str:
    """Read BunString.cpp with single-line comments stripped."""
    content = Path(TARGET).read_text()
    content = re.sub(r"//[^\n]*", "", content)
    return content


def _func_region() -> str:
    """Extract the BunString__toJSDOMURL function body (up to 2000 chars)."""
    content = _load()
    idx = content.find("BunString__toJSDOMURL")
    assert idx >= 0, "BunString__toJSDOMURL not found in BunString.cpp"

    rest = content[idx:]
    end = len(rest)
    for marker in ['extern "C"', "\nJSC__", "\nBunString__"]:
        pos = rest.find(marker, 100)
        if 0 < pos < end:
            end = pos
    return rest[: min(end, 2000)]


def _between_tojs_and_domurl_cast(region: str) -> str:
    """Return code between the semicolon ending toJSNewlyCreated and jsCast<...JSDOMURL*>."""
    jsn = region.find("toJSNewlyCreated")
    assert jsn >= 0, "toJSNewlyCreated not found in BunString__toJSDOMURL"

    # Find jsCast<WebCore::JSDOMURL*> or jsCast<JSDOMURL*> — the DOMURL-specific cast
    # that comes AFTER toJSNewlyCreated (not the earlier GlobalObject cast)
    jsc_match = re.search(r"jsCast<[^>]*JSDOMURL\*>", region[jsn:])
    assert jsc_match is not None, "jsCast<...JSDOMURL*> not found after toJSNewlyCreated"
    jsc = jsn + jsc_match.start()

    between = region[jsn:jsc]
    semi = between.find(";")
    assert semi >= 0, "No semicolon found after toJSNewlyCreated call"
    return between[semi + 1 :]


# ---------------------------------------------------------------------------
# fail_to_pass — pr_diff
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_exception_guard_between_tojs_and_jscast():
    """An exception guard must exist between toJSNewlyCreated and jsCast<JSDOMURL>.

    On the base commit, no guard is present: toJSNewlyCreated can propagate
    an exception (for an invalid URL) but the code proceeds to call
    jsCast<JSDOMURL*>() on the null result — crashing the process.

    The fix inserts a check that returns early when an exception is pending.
    """
    after = _between_tojs_and_domurl_cast(_func_region())

    guard_patterns = [
        "RETURN_IF_EXCEPTION",
        "throwScope",
        "hasPendingException",
        "scope.exception",
        ".isEmpty()",
        "!jsValue",
        "isNull()",
    ]
    found = next((p for p in guard_patterns if p in after), None)
    assert found is not None, (
        "No exception/null guard found between toJSNewlyCreated and jsCast<JSDOMURL>. "
        "Must check for exceptions before dereferencing the result."
    )


# [pr_diff] fail_to_pass
def test_guard_prevents_null_deref_on_error():
    """The guard must divert control flow so jsCast is skipped on error.

    Simply checking the exception is not enough — the code must also return
    (or branch) before reaching jsCast<JSDOMURL*>(jsValue.asCell()).
    RETURN_IF_EXCEPTION(throwScope, {}) both checks and returns.
    """
    after = _between_tojs_and_domurl_cast(_func_region())

    # RETURN_IF_EXCEPTION is a single-macro solution (check + return)
    if "RETURN_IF_EXCEPTION" in after:
        return

    # Otherwise there must be an explicit return or branch
    has_return = bool(re.search(r"\breturn\b", after))
    has_conditional = bool(
        re.search(
            r"if\s*\([^)]*(?:exception|null|empty|!|isEmpty|throwScope|scope)\b",
            after,
            re.IGNORECASE,
        )
    )
    assert has_return and has_conditional, (
        "Guard found but does not divert control flow. "
        "Use RETURN_IF_EXCEPTION(throwScope, {}) to both check and return."
    )


# ---------------------------------------------------------------------------
# pass_to_pass — pr_diff / static
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_success_path_preserved():
    """The success path must still reach jsCast, reportExtraMemoryAllocated,
    and RELEASE_AND_RETURN — in that order after toJSNewlyCreated.

    The fix adds a guard but must not remove or reorder the existing code.
    """
    region = _func_region()

    jsn = region.find("toJSNewlyCreated")
    # Search for the DOMURL-specific jsCast after toJSNewlyCreated
    jsc_match = re.search(r"jsCast<[^>]*JSDOMURL\*>", region[jsn:])
    assert jsn >= 0, "toJSNewlyCreated not found"
    assert jsc_match is not None, "jsCast<JSDOMURL*> not found after toJSNewlyCreated"
    jsc = jsn + jsc_match.start()

    rma = region.find("reportExtraMemoryAllocated", jsc)
    rar = region.find("RELEASE_AND_RETURN", jsc)

    assert rma >= 0, "reportExtraMemoryAllocated not found after jsCast"
    assert rar >= 0, "RELEASE_AND_RETURN not found after jsCast"
    assert jsc < rma, "reportExtraMemoryAllocated must come after jsCast"
    assert rma < rar, "RELEASE_AND_RETURN must come after reportExtraMemoryAllocated"


# [static] pass_to_pass
def test_file_not_gutted():
    """BunString.cpp must retain substantial content — guards against stubbing."""
    lines = len(Path(TARGET).read_text().splitlines())
    assert lines > 400, f"File appears stubbed ({lines} lines, expected > 400)"


# ---------------------------------------------------------------------------
# fail_to_pass — agent_config
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass
# Source: .claude/skills/implementing-jsc-classes-cpp/SKILL.md line 184 @ 9e93bfa
def test_includes_root_header():
    """BunString.cpp must include root.h as required for C++ bindings files.

    Per .claude/skills/implementing-jsc-classes-cpp/SKILL.md line 184,
    C++ files in the bindings directory must include root.h at the top.
    This verifies the convention is maintained after the fix is applied.
    """
    content = Path(TARGET).read_text()
    assert '#include "root.h"' in content, (
        'BunString.cpp must include "root.h". '
        "Per .claude/skills/implementing-jsc-classes-cpp/SKILL.md line 184, "
        'C++ bindings files must include "root.h" at the top.'
    )


# [agent_config] fail_to_pass
# Source: .claude/skills/implementing-jsc-classes-cpp/SKILL.md @ 9e93bfa
# The SKILL.md documents the established JSC exception-handling idiom:
# RETURN_IF_EXCEPTION(throwScope, {}). The nearby URL__fromJS function in
# the same file already uses this macro as a template.
def test_uses_return_if_exception_macro():
    """Fix must use RETURN_IF_EXCEPTION, not an ad-hoc null/empty check.

    The Bun C++ bindings skill file documents RETURN_IF_EXCEPTION(throwScope, {})
    as the idiomatic macro for handling pending JSC exceptions in binding
    functions that return an encoded JSValue. Using a manual if-check instead
    is non-idiomatic and inconsistent with patterns in the same file.
    """
    after = _between_tojs_and_domurl_cast(_func_region())
    assert "RETURN_IF_EXCEPTION" in after, (
        "Fix does not use RETURN_IF_EXCEPTION. "
        "Per .claude/skills/implementing-jsc-classes-cpp/SKILL.md, use "
        "RETURN_IF_EXCEPTION(throwScope, {}) — the established macro for "
        "checking pending exceptions in JSC binding functions."
    )
