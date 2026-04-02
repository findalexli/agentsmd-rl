"""
Task: uv-python-source-explicit-method
Repo: astral-sh/uv @ d7da792648a6e8bc2e56162f5890f44333df9ab8
PR:   #18569

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: This is a Rust project with no cargo/rustc in the Docker image.
All tests are structural (regex on source) — this is the only viable approach.
"""

import re
from pathlib import Path

FILE = Path("/repo/crates/uv-python/src/discovery.rs")

EXPLICIT_VARIANTS = [
    "ProvidedPath", "ParentInterpreter", "ActiveEnvironment", "CondaPrefix"
]
NON_EXPLICIT_VARIANTS = [
    "Managed", "DiscoveredEnvironment", "SearchPath", "SearchPathFirst",
    "Registry", "MicrosoftStore", "BaseCondaPrefix",
]
ALL_VARIANTS = EXPLICIT_VARIANTS + NON_EXPLICIT_VARIANTS


def _extract_method_body(src: str, method_pattern: str) -> str:
    """Extract the brace-matched body of a Rust method."""
    m = re.search(method_pattern, src)
    assert m, f"Method matching {method_pattern!r} not found"
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
        i += 1
    return src[start : i - 1]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_is_explicit_method_exists():
    """PythonSource has an is_explicit method returning bool."""
    src = FILE.read_text()
    assert re.search(
        r"fn\s+is_explicit\s*\(\s*&?\s*self\s*\)\s*->\s*bool\s*\{", src
    ), "is_explicit(&?self) -> bool method not found on PythonSource"


# [pr_diff] fail_to_pass
def test_is_explicit_variant_mapping():
    """is_explicit returns true for explicit variants, false for non-explicit."""
    src = FILE.read_text()
    body = _extract_method_body(
        src, r"fn\s+is_explicit\s*\(\s*&?\s*self\s*\)\s*->\s*bool\s*\{"
    )

    # Check correct true/false mapping via match arms or matches! macro
    true_arm = re.search(
        r"((?:(?:Self|PythonSource)::\w+\s*\|?\s*)+)\s*=>\s*true", body, re.DOTALL
    )
    false_arm = re.search(
        r"((?:(?:Self|PythonSource)::\w+\s*\|?\s*)+)\s*=>\s*false", body, re.DOTALL
    )
    matches_call = re.search(r"matches!\s*\(\s*self\s*,\s*(.*?)\)", body, re.DOTALL)

    if true_arm and false_arm:
        true_text, false_text = true_arm.group(1), false_arm.group(1)
        for v in EXPLICIT_VARIANTS:
            assert v in true_text, f"{v} should map to true but missing from true arm"
        for v in NON_EXPLICIT_VARIANTS:
            # Allow wildcard _ => false
            if v not in false_text:
                assert re.search(r"_\s*=>\s*false", body), (
                    f"{v} should map to false but missing from false arm (no wildcard)"
                )
    elif matches_call:
        matched_text = matches_call.group(1)
        for v in EXPLICIT_VARIANTS:
            assert v in matched_text, f"{v} should be in matches! (explicit)"
        for v in NON_EXPLICIT_VARIANTS:
            assert v not in matched_text, f"{v} should NOT be in matches! (non-explicit)"
    else:
        neg = re.search(r"!\s*matches!\s*\(\s*self\s*,\s*(.*?)\)", body, re.DOTALL)
        assert neg, "Could not parse is_explicit return logic"
        matched_text = neg.group(1)
        for v in NON_EXPLICIT_VARIANTS:
            assert v in matched_text, f"{v} should be in !matches! (non-explicit)"
        for v in EXPLICIT_VARIANTS:
            assert v not in matched_text, f"{v} should NOT be in !matches!"


# [pr_diff] fail_to_pass
def test_allows_installation_delegates():
    """allows_installation calls source.is_explicit() instead of inline match."""
    src = FILE.read_text()
    body = _extract_method_body(
        src, r"fn\s+allows_installation\s*\(self.*?\{"
    )
    assert ".is_explicit()" in body, (
        "allows_installation does not call .is_explicit()"
    )
    assert not re.search(r"let\s+is_explicit\s*=\s*match\s+", body), (
        "allows_installation still has inline 'let is_explicit = match'"
    )


# [pr_diff] fail_to_pass
def test_allows_installation_no_inline_variant_match():
    """allows_installation must not contain PythonSource variant arms for explicit check."""
    src = FILE.read_text()
    body = _extract_method_body(
        src, r"fn\s+allows_installation\s*\(self.*?\{"
    )
    # The old code had PythonSource::ProvidedPath etc. inline — the refactored version
    # should not mention these variants in the context of is_explicit logic
    explicit_refs = [v for v in EXPLICIT_VARIANTS if f"PythonSource::{v}" in body]
    assert not explicit_refs, (
        f"allows_installation still references explicit variants inline: {explicit_refs}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_is_maybe_system_preserved():
    """is_maybe_system method must still exist (regression guard)."""
    src = FILE.read_text()
    assert re.search(
        r"fn\s+is_maybe_system\s*\(\s*&?\s*self\s*\)\s*->\s*bool", src
    ), "is_maybe_system method missing — regression"


# [repo_tests] pass_to_pass
def test_allows_installation_preserved():
    """allows_installation method must still exist and compile structurally."""
    src = FILE.read_text()
    assert re.search(
        r"fn\s+allows_installation\s*\(self.*?\{", src
    ), "allows_installation method missing — regression"


# [repo_tests] pass_to_pass
def test_python_source_enum_preserved():
    """PythonSource enum must still have all expected variants."""
    src = FILE.read_text()
    for variant in ALL_VARIANTS:
        assert re.search(rf"\b{variant}\b", src), (
            f"PythonSource variant {variant} missing from source"
        )


# ---------------------------------------------------------------------------
# Anti-stub (static)
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_is_explicit_not_stub():
    """is_explicit must have match/matches! with >=4 variant refs, not a trivial stub."""
    src = FILE.read_text()
    body = _extract_method_body(
        src, r"fn\s+is_explicit\s*\(\s*&?\s*self\s*\)\s*->\s*bool\s*\{"
    )
    assert "match" in body or "matches!" in body, (
        "is_explicit has no match/matches! expression"
    )
    variant_refs = set(re.findall(r"(?:Self|PythonSource)::(\w+)", body))
    assert len(variant_refs) >= 4, (
        f"is_explicit references only {len(variant_refs)} variants (need >=4)"
    )
    lines = [l.strip() for l in body.strip().splitlines() if l.strip()]
    assert len(lines) >= 3, f"is_explicit body too short ({len(lines)} lines)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:7 @ d7da792648a6e8bc2e56162f5890f44333df9ab8
def test_no_panic_unwrap_in_is_explicit():
    """AVOID using panic!, unreachable!, .unwrap(), unsafe code (CLAUDE.md:7)."""
    src = FILE.read_text()
    body = _extract_method_body(
        src, r"fn\s+is_explicit\s*\(\s*&?\s*self\s*\)\s*->\s*bool\s*\{"
    )
    for bad in [".unwrap()", "panic!", "unreachable!", "unsafe"]:
        assert bad not in body, f"is_explicit contains forbidden pattern: {bad}"


# [agent_config] fail_to_pass — CLAUDE.md:7,10 @ d7da792648a6e8bc2e56162f5890f44333df9ab8
def test_no_clippy_allow_in_is_explicit():
    """No #[allow(clippy::...)] — prefer #[expect()] if needed (CLAUDE.md:7,10)."""
    src = FILE.read_text()
    # Find the is_explicit method and a few lines before it (for attributes)
    m = re.search(
        r"((?:#\[.*?\]\s*)*fn\s+is_explicit\s*\(\s*&?\s*self\s*\)\s*->\s*bool\s*\{)",
        src, re.DOTALL,
    )
    assert m, "is_explicit method not found"
    preamble = m.group(1)
    body = _extract_method_body(
        src, r"fn\s+is_explicit\s*\(\s*&?\s*self\s*\)\s*->\s*bool\s*\{"
    )
    combined = preamble + body
    assert "#[allow(" not in combined, (
        "is_explicit uses #[allow(...)]; prefer #[expect()] per CLAUDE.md:10"
    )
