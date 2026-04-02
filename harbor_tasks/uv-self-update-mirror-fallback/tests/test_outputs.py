"""
Task: uv-self-update-mirror-fallback
Repo: astral-sh/uv @ 7228ad62b9de7f9b5d887ef4b2be9bb033a04191
PR:   14936

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Rust code — no cargo/compiler in the Docker image, so all tests do
source-level analysis on crates/uv-bin-install/src/lib.rs.
"""

import re
from pathlib import Path

REPO = "/workspace/uv"
FILE = Path(REPO) / "crates/uv-bin-install/src/lib.rs"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stripped_source() -> str:
    """Return file source with comments removed (prevents keyword-stuffing)."""
    src = FILE.read_text(encoding="utf-8")
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", "", src)
    return src


def _extract_fn(src: str, name: str) -> str | None:
    """Extract a function body (from 'fn <name>' to its closing brace).

    String-aware: skips braces inside Rust string literals.
    """
    pat = re.compile(r"fn\s+" + re.escape(name) + r"\s*[\(<]")
    m = pat.search(src)
    if not m:
        return None
    try:
        start = src.index("{", m.start())
    except ValueError:
        return None
    depth = 0
    in_string = False
    escape_next = False
    for i in range(start, len(src)):
        c = src[i]
        if escape_next:
            escape_next = False
            continue
        if c == "\\" and in_string:
            escape_next = True
            continue
        if c == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        if depth == 0:
            return src[m.start() : i + 1]
    return None


def _extract_match_arm(fn_body: str | None, arm_name: str) -> str | None:
    """Extract a single match arm, string-aware.

    Handles both brace-enclosed arms (=> { ... }) and expression arms
    (=> vec![...],) by tracking all bracket types and skipping string content.
    """
    if fn_body is None:
        return None
    idx = fn_body.find(arm_name)
    if idx < 0:
        return None
    rest = fn_body[idx:]

    arrow = rest.find("=>")
    if arrow < 0:
        return None

    brace_depth = 0
    bracket_depth = 0
    paren_depth = 0
    in_string = False
    escape_next = False

    for i in range(arrow + 2, len(rest)):
        c = rest[i]
        if escape_next:
            escape_next = False
            continue
        if c == "\\" and in_string:
            escape_next = True
            continue
        if c == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == "{":
            brace_depth += 1
        elif c == "}":
            brace_depth -= 1
            if brace_depth < 0:
                return rest[:i]
        elif c == "[":
            bracket_depth += 1
        elif c == "]":
            bracket_depth -= 1
        elif c == "(":
            paren_depth += 1
        elif c == ")":
            paren_depth -= 1
        elif (
            c == ","
            and brace_depth == 0
            and bracket_depth == 0
            and paren_depth == 0
        ):
            return rest[: i + 1]
    return rest


def _variant_maps_to_true(fn_body: str, variant: str) -> bool:
    """Check if a Self::<variant> pattern leads to => true in a match expr.

    Handles both single-variant arms (Self::Foo => true) and chained arms
    (Self::Foo | Self::Bar => true) by scanning a window around the variant.
    """
    lines = fn_body.split("\n")
    for i, line in enumerate(lines):
        if variant in line:
            window = "\n".join(lines[max(0, i - 6) : i + 10])
            if re.search(r"=>\s*true", window):
                return True
    return False


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: Rust code, no cargo/compiler in Docker image
def test_uv_mirror_url():
    """Binary::Uv manifest_urls arm constructs URL from VERSIONS_MANIFEST_MIRROR."""
    src = _stripped_source()
    manifest_fn = _extract_fn(src, "manifest_urls")
    assert manifest_fn is not None, "manifest_urls function not found"

    uv_arm = _extract_match_arm(manifest_fn, "Self::Uv")
    assert uv_arm is not None, "Self::Uv arm not found in manifest_urls"

    # Must use the mirror constant in a format! + parse call
    has_mirror = bool(
        re.search(r"format!\s*\([^)]*VERSIONS_MANIFEST_MIRROR", uv_arm)
    )
    assert has_mirror, (
        "Uv arm does not construct URL with format!(VERSIONS_MANIFEST_MIRROR)"
    )


# [pr_diff] fail_to_pass
# AST-only because: Rust code, no cargo/compiler in Docker image
def test_uv_mirror_order():
    """Binary::Uv lists mirror URL before canonical GitHub URL."""
    src = _stripped_source()
    manifest_fn = _extract_fn(src, "manifest_urls")
    assert manifest_fn is not None, "manifest_urls function not found"

    uv_arm = _extract_match_arm(manifest_fn, "Self::Uv")
    assert uv_arm is not None, "Self::Uv arm not found"

    m_mirror = re.search(r"format!\s*\([^)]*VERSIONS_MANIFEST_MIRROR", uv_arm)
    m_canon = re.search(r"format!\s*\([^)]*VERSIONS_MANIFEST_URL\b", uv_arm)
    assert m_mirror and m_canon, "Uv arm missing mirror or canonical URL"
    assert m_mirror.start() < m_canon.start(), (
        "Mirror URL must appear before canonical URL in the vec"
    )


# [pr_diff] fail_to_pass
# AST-only because: Rust code, no cargo/compiler in Docker image
def test_manifest_parse_fallback():
    """ManifestParse errors trigger URL fallback in should_try_next_url."""
    src = _stripped_source()
    fallback_fn = _extract_fn(src, "should_try_next_url")
    assert fallback_fn is not None, "should_try_next_url function not found"

    assert re.search(r"ManifestParse", fallback_fn), (
        "ManifestParse not referenced in should_try_next_url"
    )
    assert _variant_maps_to_true(fallback_fn, "ManifestParse"), (
        "ManifestParse does not map to true in should_try_next_url"
    )


# [pr_diff] fail_to_pass
# AST-only because: Rust code, no cargo/compiler in Docker image
def test_manifest_utf8_fallback():
    """ManifestUtf8 errors trigger URL fallback in should_try_next_url."""
    src = _stripped_source()
    fallback_fn = _extract_fn(src, "should_try_next_url")
    assert fallback_fn is not None, "should_try_next_url function not found"

    assert re.search(r"ManifestUtf8", fallback_fn), (
        "ManifestUtf8 not referenced in should_try_next_url"
    )
    assert _variant_maps_to_true(fallback_fn, "ManifestUtf8"), (
        "ManifestUtf8 does not map to true in should_try_next_url"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
# AST-only because: Rust code, no cargo/compiler in Docker image
def test_ruff_urls_intact():
    """Binary::Ruff still has both mirror and canonical URLs in manifest_urls."""
    src = _stripped_source()
    manifest_fn = _extract_fn(src, "manifest_urls")
    assert manifest_fn is not None, "manifest_urls function not found"

    ruff_arm = _extract_match_arm(manifest_fn, "Self::Ruff")
    assert ruff_arm is not None, "Self::Ruff arm not found"
    assert re.search(r"VERSIONS_MANIFEST_MIRROR", ruff_arm), (
        "Ruff arm missing mirror URL"
    )
    assert re.search(r"VERSIONS_MANIFEST_URL\b", ruff_arm), (
        "Ruff arm missing canonical URL"
    )


# [pr_diff] pass_to_pass
# AST-only because: Rust code, no cargo/compiler in Docker image
def test_existing_fallback_intact():
    """Download and ManifestFetch still trigger fallback in should_try_next_url."""
    src = _stripped_source()
    fallback_fn = _extract_fn(src, "should_try_next_url")
    assert fallback_fn is not None, "should_try_next_url function not found"

    for variant in ["Download", "ManifestFetch"]:
        assert re.search(rf"\b{variant}\b", fallback_fn), (
            f"{variant} not in should_try_next_url"
        )
        assert _variant_maps_to_true(fallback_fn, variant), (
            f"{variant} does not map to true in should_try_next_url"
        )


# [pr_diff] pass_to_pass
# AST-only because: Rust code, no cargo/compiler in Docker image
def test_stream_fallback_intact():
    """Stream errors still trigger fallback in should_try_next_url."""
    src = _stripped_source()
    fallback_fn = _extract_fn(src, "should_try_next_url")
    assert fallback_fn is not None, "should_try_next_url function not found"

    assert re.search(r"\bStream\b", fallback_fn), (
        "Stream not in should_try_next_url"
    )
    assert _variant_maps_to_true(fallback_fn, "Stream"), (
        "Stream does not map to true in should_try_next_url"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ 7228ad62b9de7f9b5d887ef4b2be9bb033a04191
# AST-only because: Rust code, no cargo/compiler in Docker image
def test_no_panic_unreachable():
    """No panic! or unreachable! in manifest_urls or should_try_next_url (CLAUDE.md line 7)."""
    src = _stripped_source()
    for fn_name in ["manifest_urls", "should_try_next_url"]:
        fn_body = _extract_fn(src, fn_name)
        assert fn_body is not None, f"{fn_name} function not found"
        assert not re.search(r"\bpanic!\b", fn_body), (
            f"{fn_name} contains panic!"
        )
        assert not re.search(r"\bunreachable!\b", fn_body), (
            f"{fn_name} contains unreachable!"
        )


# [agent_config] pass_to_pass — CLAUDE.md:7 @ 7228ad62b9de7f9b5d887ef4b2be9bb033a04191
# AST-only because: Rust code, no cargo/compiler in Docker image
def test_no_unsafe_blocks():
    """No unsafe code in manifest_urls or should_try_next_url (CLAUDE.md line 7)."""
    src = _stripped_source()
    for fn_name in ["manifest_urls", "should_try_next_url"]:
        fn_body = _extract_fn(src, fn_name)
        assert fn_body is not None, f"{fn_name} function not found"
        assert not re.search(r"\bunsafe\s*\{", fn_body), (
            f"{fn_name} contains unsafe block"
        )


# [agent_config] pass_to_pass — CLAUDE.md:10 @ 7228ad62b9de7f9b5d887ef4b2be9bb033a04191
# AST-only because: Rust code, no cargo/compiler in Docker image
def test_no_allow_attribute():
    """No #[allow()] in modified functions — prefer #[expect()] (CLAUDE.md line 10)."""
    src = _stripped_source()
    for fn_name in ["manifest_urls", "should_try_next_url"]:
        fn_body = _extract_fn(src, fn_name)
        assert fn_body is not None, f"{fn_name} function not found"
        assert not re.search(r"#\[allow\(", fn_body), (
            f"{fn_name} uses #[allow()] — prefer #[expect()] per CLAUDE.md"
        )


# ---------------------------------------------------------------------------
# Anti-stub (static) — structural validity
# ---------------------------------------------------------------------------

# [static] fail_to_pass
# AST-only because: Rust code, no cargo/compiler in Docker image
def test_uv_arm_not_stub():
    """Binary::Uv arm has >= 2 URL entries (not a stub)."""
    src = _stripped_source()
    manifest_fn = _extract_fn(src, "manifest_urls")
    assert manifest_fn is not None, "manifest_urls function not found"

    uv_arm = _extract_match_arm(manifest_fn, "Self::Uv")
    assert uv_arm is not None, "Self::Uv arm not found"

    # Must have at least 2 parse(format!()) calls — one mirror, one canonical
    parse_calls = re.findall(r"parse\s*\(\s*&?\s*format!\s*\(", uv_arm)
    assert len(parse_calls) >= 2, (
        f"Uv arm has {len(parse_calls)} parse(format!()) calls, need >= 2"
    )
    # Must have enough substance (not just a single-line stub)
    non_blank = [l for l in uv_arm.split("\n") if l.strip()]
    assert len(non_blank) >= 4, (
        f"Uv arm has {len(non_blank)} non-blank lines, need >= 4"
    )
