"""
Task: bun-domurl-invalid-url-crash
Repo: oven-sh/bun @ 9e93bfa1b69a2f9b8c05acb15e02c5506dd4cbc8
PR:   28309

Fix: Add RETURN_IF_EXCEPTION(throwScope, {}); between toJSNewlyCreated and
jsCast in BunString__toJSDOMURL (src/bun.js/bindings/BunString.cpp).

Bun requires Zig + WebKit (~30min, ~32GB RAM) to build from source,
so behavioral tests use git diff + Python subprocess analysis to verify
the fix is applied correctly.

All checks must pass for reward = 1. Any failure = reward 0.
Each def test_*() maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/repo"
TARGET = f"{REPO}/src/bun.js/bindings/BunString.cpp"


def _extract_func_region() -> str:
    """Extract the BunString__toJSDOMURL function body with comments stripped."""
    content = Path(TARGET).read_text()
    content = re.sub(r"//[^\n]*", "", content)

    idx = content.find("BunString__toJSDOMURL")
    assert idx >= 0, "BunString__toJSDOMURL not found in BunString.cpp"

    rest = content[idx:]
    end = len(rest)
    for marker in ['extern "C"', "\nJSC__", "\nBunString__"]:
        pos = rest.find(marker, 100)
        if 0 < pos < end:
            end = pos
    return rest[: min(end, 2000)]


def _between_tojs_and_jscast(region: str) -> str:
    """Return code between toJSNewlyCreated semicolon and jsCast<JSDOMURL*>."""
    jsn = region.find("toJSNewlyCreated")
    assert jsn >= 0, "toJSNewlyCreated not found"

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
def test_fix_adds_return_if_exception():
    """RETURN_IF_EXCEPTION must be added between toJSNewlyCreated and jsCast.

    Uses subprocess to run a Python analysis script that locates the
    BunString__toJSDOMURL function and verifies RETURN_IF_EXCEPTION(throwScope, {})
    appears between the toJSNewlyCreated call and the jsCast<JSDOMURL*> dereference.
    """
    r = subprocess.run(
        [
            "python3",
            "-c",
            """
import re, sys
content = open('/repo/src/bun.js/bindings/BunString.cpp').read()
# Strip single-line comments to avoid false matches
content = re.sub(r'//[^\\n]*', '', content)

idx = content.find('BunString__toJSDOMURL')
if idx < 0:
    print('FAIL: BunString__toJSDOMURL not found', file=sys.stderr)
    sys.exit(1)

region = content[idx:idx + 800]
jsn = region.find('toJSNewlyCreated')
jsc = region.find('jsCast', jsn + 10)
if jsn < 0 or jsc < 0:
    print('FAIL: toJSNewlyCreated or jsCast not found', file=sys.stderr)
    sys.exit(1)

between = region[jsn:jsc]
if 'RETURN_IF_EXCEPTION' not in between:
    print('FAIL: RETURN_IF_EXCEPTION not between toJSNewlyCreated and jsCast', file=sys.stderr)
    sys.exit(1)

# Verify the macro call is complete with correct args: RETURN_IF_EXCEPTION(throwScope, {})
if not re.search(r'RETURN_IF_EXCEPTION\\s*\\(\\s*throwScope\\s*,\\s*\\{\\s*\\}\\s*\\)', between):
    print('FAIL: RETURN_IF_EXCEPTION call incomplete or wrong arguments', file=sys.stderr)
    sys.exit(1)

print('PASS')
""",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"RETURN_IF_EXCEPTION check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_fix_is_minimal():
    """The fix should be a pure insertion — no deletions of existing code.

    Uses subprocess to run git diff and verify the change only adds the
    RETURN_IF_EXCEPTION line without modifying or removing existing lines.
    """
    r = subprocess.run(
        ["git", "diff", "--", "src/bun.js/bindings/BunString.cpp"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    diff = r.stdout
    assert diff.strip(), "No diff found for BunString.cpp — fix may not have been applied"

    added = [l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    removed = [l for l in diff.splitlines() if l.startswith("-") and not l.startswith("---")]

    # The fix is a single-line insertion
    assert len(added) >= 1, f"Expected additions in diff, got none"
    # Should not remove any existing lines
    assert len(removed) == 0, (
        f"Fix should be pure insertion (no deletions), but found {len(removed)} removed lines: {removed}"
    )
    # At least one added line must contain RETURN_IF_EXCEPTION
    assert any(
        "RETURN_IF_EXCEPTION" in l for l in added
    ), f"Added lines do not contain RETURN_IF_EXCEPTION: {added}"


# [pr_diff] fail_to_pass
def test_guard_prevents_null_deref_on_error():
    """The guard must divert control flow so jsCast is skipped on error.

    Simply checking the exception is not enough — the code must also return
    (or branch) before reaching jsCast<JSDOMURL*>(jsValue.asCell()).
    RETURN_IF_EXCEPTION(throwScope, {}) both checks and returns.
    """
    after = _between_tojs_and_jscast(_extract_func_region())

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
    region = _extract_func_region()

    jsn = region.find("toJSNewlyCreated")
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
# agent_config
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass
# Source: .claude/skills/implementing-jsc-classes-cpp/SKILL.md @ 9e93bfa
def test_uses_return_if_exception_macro():
    """Fix must use RETURN_IF_EXCEPTION, not an ad-hoc null/empty check.

    Per .claude/skills/implementing-jsc-classes-cpp/SKILL.md, the established
    JSC exception-handling idiom is RETURN_IF_EXCEPTION(throwScope, {}).
    The nearby URL__fromJS function in the same file already uses this macro.
    """
    after = _between_tojs_and_jscast(_extract_func_region())
    assert "RETURN_IF_EXCEPTION" in after, (
        "Fix does not use RETURN_IF_EXCEPTION. "
        "Per .claude/skills/implementing-jsc-classes-cpp/SKILL.md, use "
        "RETURN_IF_EXCEPTION(throwScope, {}) — the established macro for "
        "checking pending exceptions in JSC binding functions."
    )


# [agent_config] pass_to_pass
# Source: .claude/skills/implementing-jsc-classes-cpp/SKILL.md line 184 @ 9e93bfa
def test_includes_root_header():
    """BunString.cpp must include root.h as required for C++ bindings files.

    Per .claude/skills/implementing-jsc-classes-cpp/SKILL.md line 184,
    C++ files in the bindings directory must include root.h at the top.
    """
    content = Path(TARGET).read_text()
    assert '#include "root.h"' in content, (
        'BunString.cpp must include "root.h". '
        "Per .claude/skills/implementing-jsc-classes-cpp/SKILL.md line 184, "
        'C++ bindings files must include "root.h" at the top.'
    )
