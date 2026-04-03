"""
Task: bun-urlpattern-regexp-match-direct
Repo: oven-sh/bun @ 2920fac5f712c2714e3a0a97c2d6e8e8ad47cc1e
PR:   #28447

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/bun"

COMP_CPP = Path(REPO) / "src/bun.js/bindings/webcore/URLPatternComponent.cpp"
COMP_H = Path(REPO) / "src/bun.js/bindings/webcore/URLPatternComponent.h"
PAT_CPP = Path(REPO) / "src/bun.js/bindings/webcore/URLPattern.cpp"
CONSTR_CPP = Path(REPO) / "src/bun.js/bindings/webcore/URLPatternConstructorStringParser.cpp"


def _strip_comments(text: str) -> str:
    """Strip C/C++ comments for robust checking."""
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return text


def _read_stripped(path: Path) -> str:
    return _strip_comments(path.read_text())


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — files must exist and be structurally intact
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_source_files_intact():
    """Key source files exist, are not truncated, and have balanced braces."""
    for f in [COMP_CPP, COMP_H, PAT_CPP, CONSTR_CPP]:
        content = f.read_text()
        assert len(content) >= 500, f"File too short: {f.name}"
        assert abs(content.count("{") - content.count("}")) <= 3, (
            f"Unbalanced braces in {f.name}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_regexp_object_removed_direct_match():
    """Old componentExec+createComponentMatchResult replaced with single
    method using direct RegExp::match + ovector buffer, all co-located."""
    src = _read_stripped(COMP_CPP)
    header = _read_stripped(COMP_H)

    # (a) RegExpObject::create completely gone
    assert "RegExpObject::create" not in src, "RegExpObject::create still in .cpp"

    # (b) Old two-method pattern fully removed from .cpp
    assert not re.search(r"URLPatternComponent::componentExec\s*\(", src), (
        "componentExec definition still exists"
    )
    assert not re.search(r"URLPatternComponent::createComponentMatchResult\s*\(", src), (
        "createComponentMatchResult definition still exists"
    )

    # (c) Old declarations gone from header
    assert not re.search(r"componentExec\s*\(", header), "componentExec in header"
    assert not re.search(r"createComponentMatchResult\s*\(", header), (
        "createComponentMatchResult in header"
    )

    # (d) Replacement method returning optional<URLPatternComponentResult>
    fn_match = re.search(
        r"(?:std::optional|Optional)\s*<\s*URLPatternComponentResult\s*>\s+"
        r"(\w+::(\w+))\s*\([^)]*\)\s*(?:const\s*)?\{(.*?)^\}",
        src,
        re.DOTALL | re.MULTILINE,
    )
    assert fn_match, "No method returning optional<URLPatternComponentResult>"
    fn_body = fn_match.group(3)

    # (e) Direct RegExp::match call inside the replacement method
    has_match = (
        re.search(r"(?:regExp|m_regularExpression|regularExpression)\s*(?:\(\))?\s*->\s*match\w*\s*\(", fn_body)
        or re.search(r"RegExp\s*::\s*match\w*\s*\(", fn_body)
    )
    assert has_match, "No direct RegExp match call in replacement method"

    # (f) Ovector access in this function
    assert re.search(r"(?:ovector|ovectorSpan)\w*\s*\[", fn_body), (
        "No ovector index access in replacement method"
    )

    # (g) Capture group iteration loop
    assert re.search(r"for\s*\(", fn_body), "No capture group iteration loop"

    # (h) Group name mapping
    assert re.search(r"(?:groupName|m_groupNameList|NameMatchPair)", fn_body), (
        "No group name handling in replacement method"
    )

    # (i) Substring extraction from input
    assert re.search(r"substring|subpattern|input\s*\.", fn_body), (
        "No substring/input extraction in replacement method"
    )

    # (j) Sufficient substance (>= 12 non-empty lines)
    lines = [l for l in fn_body.strip().split("\n") if l.strip()]
    assert len(lines) >= 12, f"Replacement function too short ({len(lines)} lines)"

    # (k) Header declares this method
    assert re.search(
        r"(?:std::optional|Optional)\s*<\s*URLPatternComponentResult\s*>", header
    ), "Header missing optional<URLPatternComponentResult>"


# [pr_diff] fail_to_pass
def test_special_scheme_direct_matching():
    """matchSpecialSchemeProtocol uses direct RegExp::match instead of
    RegExpObject, and takes JSGlobalObject* (not ScriptExecutionContext&)."""
    src = _read_stripped(COMP_CPP)

    fn = re.search(
        r"matchSpecialSchemeProtocol\s*\([^)]*\)\s*(?:const\s*)?\{(.*?)^\}",
        src,
        re.DOTALL | re.MULTILINE,
    )
    assert fn, "matchSpecialSchemeProtocol function not found"
    body = fn.group(1)

    # Must NOT use old pattern
    assert "RegExpObject::create" not in body, "Still uses RegExpObject::create"
    assert "->exec(" not in body, "Still uses ->exec()"

    # Must have direct matching
    assert re.search(r"->\s*(?:match|test|matchInline)\w*\s*\(", body), (
        "No direct matching call"
    )

    # Must iterate special schemes
    assert re.search(r"for\s*\(|while\s*\(|find_if|any_of|ranges::", body), (
        "No iteration over special schemes"
    )

    # Signature: JSGlobalObject*, not ScriptExecutionContext&
    sig = re.search(r"matchSpecialSchemeProtocol\s*\(([^)]*)\)", src)
    assert sig, "matchSpecialSchemeProtocol signature not found"
    assert "ScriptExecutionContext" not in sig.group(1), "Still takes ScriptExecutionContext"


# [pr_diff] fail_to_pass
def test_match_consolidated():
    """URLPattern::match calls the new component matching method, removes
    componentExec/createComponentMatchResult, and consolidates locking."""
    src = _read_stripped(PAT_CPP)

    fn = re.search(
        r"URLPattern::match\s*\(.*?\)\s*\{(.*?)(?=\n\w.*?::\w|\Z)",
        src,
        re.DOTALL,
    )
    assert fn, "URLPattern::match not found"
    body = fn.group(1)

    # Old methods gone
    assert len(re.findall(r"componentExec\s*\(", body)) == 0, (
        "componentExec calls remain"
    )
    assert len(re.findall(r"createComponentMatchResult\s*\(", body)) == 0, (
        "createComponentMatchResult calls remain"
    )

    # New component matching method called
    has_new = (
        re.search(r"m_\w+Component\s*\.\s*\w*[Mm]atch\w*\s*\(", body)
        or re.search(r"component\s*\.\s*\w*[Mm]atch\w*\s*\(", body)
    )
    assert has_new, "No new component matching method called"

    # All 8 components referenced
    components = ["protocol", "username", "password", "hostname", "pathname", "port", "search", "hash"]
    found = sum(1 for c in components if re.search(r"m_" + c + r"Component", body))
    assert found >= 7, f"Only {found}/8 components referenced"

    # Lock consolidation (<=2, not 8)
    lock_count = len(re.findall(r"JSLockHolder|JSLock\b", body))
    assert lock_count <= 2, f"{lock_count} lock acquisitions (should be <=2)"


# [pr_diff] fail_to_pass
def test_constructor_parser_updated():
    """matchSpecialSchemeProtocol call site in URLPatternConstructorStringParser
    passes globalObject() instead of bare context."""
    src = _read_stripped(CONSTR_CPP)

    call = re.search(r"matchSpecialSchemeProtocol\s*\(([^)]*)\)", src)
    assert call, "matchSpecialSchemeProtocol call not found in constructor parser"

    arg = call.group(1).strip()
    # Must not pass bare context (old signature)
    assert arg not in ("context", "m_context"), "Still passing context directly"
    # Should reference globalObject
    assert re.search(r"globalObject", arg), f"Expected globalObject in arg, got: {arg}"


# [pr_diff] fail_to_pass
def test_header_source_coherence():
    """New component matching method declared in header AND defined in source,
    with matching return type. JSGlobalObject referenced in header."""
    header = _read_stripped(COMP_H)
    src = _read_stripped(COMP_CPP)

    # New method declared in header
    decl = re.search(
        r"(?:std::optional|Optional)\s*<\s*URLPatternComponentResult\s*>\s+(\w+)\s*\(",
        header,
    )
    assert decl, "No optional<URLPatternComponentResult> method in header"
    method_name = decl.group(1)

    # Defined in .cpp
    assert re.search(
        r"URLPatternComponent::" + re.escape(method_name) + r"\s*\(", src
    ), f"{method_name} declared in header but not defined in .cpp"

    # JSGlobalObject referenced in header
    assert re.search(r"class\s+JSGlobalObject", header) or re.search(
        r"JSGlobalObject\s*\*", header
    ), "JSGlobalObject not referenced in header"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression / anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_api_surface_preserved():
    """Core URLPattern types, methods, and symbols remain in headers and source."""
    h = COMP_H.read_text()
    cpp = COMP_CPP.read_text()
    pat = PAT_CPP.read_text()

    checks = [
        ("class URLPatternComponent", h, "header"),
        ("compile(", h, "header"),
        ("patternString()", h, "header"),
        ("matchSpecialSchemeProtocol(", h, "header"),
        ("m_regularExpression", h, "header"),
        ("m_groupNameList", h, "header"),
        ("URLPattern::match", pat, "URLPattern.cpp"),
        ("specialSchemeList", cpp, "URLPatternComponent.cpp"),
        ("namespace WebCore", cpp, "URLPatternComponent.cpp"),
    ]
    for needle, haystack, location in checks:
        assert needle in haystack, f"MISSING in {location}: {needle}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from agent config files
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_regexp_object_include():
    """RegExpObject.h is removed from URLPatternComponent.cpp as part of
    eliminating the RegExpObject wrapper — direct RegExp::match needs only
    <JavaScriptCore/RegExp.h>, not the higher-level RegExpObject."""
    src = _read_stripped(COMP_CPP)
    assert not re.search(r"#include.*RegExpObject\.h", src), (
        "Still includes RegExpObject.h"
    )


# [agent_config] pass_to_pass — .claude/skills/implementing-jsc-classes-cpp/SKILL.md:184 @ 2920fac
def test_root_h_included():
    """C++ files must include root.h — required by JSC classes skill."""
    # root.h is already present in all modified .cpp files at the base commit;
    # an agent must not remove it.
    for f in [COMP_CPP, PAT_CPP, CONSTR_CPP]:
        raw = f.read_text()
        assert re.search(r'#include\s+"root\.h"', raw), (
            f"Missing #include \"root.h\" in {f.name}"
        )
