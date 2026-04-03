"""
Task: cypress-misc-update-playwrightwebkit-from-1242
Repo: cypress-io/cypress @ b92dcdb405dc8b2b417988b947b30a976c64f6fb
PR:   32852

WebKit cookie domain matching: add strict domain matching with apex fallback,
and update Cursor rules for Debian Trixie migration.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/cypress"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files have balanced braces."""
    for relpath in [
        "packages/server/lib/automation/util.ts",
        "packages/server/lib/browsers/webkit-automation.ts",
    ]:
        src = Path(f"{REPO}/{relpath}").read_text()
        opens = src.count("{") + src.count("(") + src.count("[")
        closes = src.count("}") + src.count(")") + src.count("]")
        assert abs(opens - closes) <= 2, (
            f"Bracket imbalance in {relpath}: opens={opens}, closes={closes}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cookie_matches_strict_domain_option():
    """cookieMatches must accept an options parameter with strictDomain."""
    src = Path(f"{REPO}/packages/server/lib/automation/util.ts").read_text()
    # The function signature must include a third parameter for strictDomain
    assert "strictDomain" in src, (
        "cookieMatches must support a strictDomain option"
    )
    # Verify it's in the function signature (not just a random comment)
    sig_match = re.search(
        r"cookieMatches\s*=\s*\([^)]*strictDomain[^)]*\)\s*=>",
        src,
    )
    assert sig_match is not None, (
        "strictDomain must appear in the cookieMatches function signature"
    )


# [pr_diff] fail_to_pass
def test_strict_domain_uses_exact_comparison():
    """With strictDomain, cookieMatches must use exact domain equality, not domainMatch."""
    src = Path(f"{REPO}/packages/server/lib/automation/util.ts").read_text()
    # When strictDomain is true, exact comparison (filter.domain !== cookie.domain)
    # should be used instead of domainMatch
    assert "strictDomain" in src, "strictDomain option not found"
    # Must have both: exact comparison for strict AND domainMatch for non-strict
    has_exact = "!== cookie.domain" in src or "!==cookie.domain" in src
    has_domain_match = "domainMatch" in src
    assert has_exact, (
        "strictDomain mode must use exact domain comparison (filter.domain !== cookie.domain)"
    )
    assert has_domain_match, (
        "Non-strict mode must still use domainMatch for apex domain matching"
    )


# [pr_diff] fail_to_pass
def test_webkit_getcookie_strict_then_fallback():
    """WebKit getCookie must try strict domain match first, then fall back to apex."""
    src = Path(f"{REPO}/packages/server/lib/browsers/webkit-automation.ts").read_text()
    # Extract the getCookie method body
    match = re.search(
        r"private\s+async\s+getCookie\s*\([^)]*\)\s*\{(.*?)\n  \}",
        src,
        re.DOTALL,
    )
    assert match is not None, "getCookie method not found in webkit-automation.ts"
    body = match.group(1)

    # Must call cookieMatches with strictDomain: true first
    assert "strictDomain: true" in body or "strictDomain:true" in body, (
        "getCookie must first attempt strict domain matching"
    )

    # Must have a fallback call to cookieMatches without strictDomain
    # (two separate find/cookieMatches calls)
    cookie_matches_calls = re.findall(r"cookieMatches\(", body)
    assert len(cookie_matches_calls) >= 2, (
        f"getCookie must call cookieMatches at least twice (strict then fallback), "
        f"found {len(cookie_matches_calls)} call(s)"
    )

    # The strict call must come before the fallback call
    strict_pos = body.find("strictDomain")
    # Find a cookieMatches call AFTER the strict one that does NOT have strictDomain
    after_strict = body[strict_pos:]
    # There should be another cookieMatches call after the strict domain block
    remaining_after_first_block = re.split(r"cookieMatches\(", after_strict, maxsplit=1)
    assert len(remaining_after_first_block) >= 2, (
        "Must have a fallback cookieMatches call after the strict domain attempt"
    )


# [pr_diff] fail_to_pass
def test_webkit_getcookie_uses_let_not_const():
    """getCookie cookie variable must be 'let' (reassigned in fallback), not 'const'."""
    src = Path(f"{REPO}/packages/server/lib/browsers/webkit-automation.ts").read_text()
    match = re.search(
        r"private\s+async\s+getCookie\s*\([^)]*\)\s*\{(.*?)\n  \}",
        src,
        re.DOTALL,
    )
    assert match is not None, "getCookie method not found"
    body = match.group(1)
    # The cookie variable in getCookie should be 'let' since it gets reassigned
    assert re.search(r"\blet\s+cookie\b", body), (
        "getCookie must use 'let cookie' (not 'const') since it's reassigned in the fallback path"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — Cursor rules update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — backward compatibility
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cookie_matches_backward_compat():
    """cookieMatches must still work without the options parameter (domainMatch path)."""
    src = Path(f"{REPO}/packages/server/lib/automation/util.ts").read_text()
    # The options parameter must be optional (has ?)
    assert re.search(r"options\?\s*:", src), (
        "options parameter must be optional in cookieMatches"
    )
    # domainMatch must still be used in the non-strict path
    assert "domainMatch" in src, (
        "domainMatch must still be used for non-strict domain matching"
    )
    # pathMatch must still be present (not accidentally removed)
    assert "pathMatch" in src, (
        "pathMatch logic must not be removed from cookieMatches"
    )
    # name matching must still be present
    assert "filter?.name" in src or "filter.name" in src, (
        "Name matching must not be removed from cookieMatches"
    )


# [static] pass_to_pass
def test_getcookies_unchanged():
    """getCookies (plural) must still use non-strict matching."""
    src = Path(f"{REPO}/packages/server/lib/browsers/webkit-automation.ts").read_text()
    match = re.search(
        r"private\s+async\s+getCookies\s*\([^)]*\)\s*\{(.*?)\n  \}",
        src,
        re.DOTALL,
    )
    assert match is not None, "getCookies method not found"
    body = match.group(1)
    # getCookies should NOT use strictDomain — only getCookie (singular) does
    assert "strictDomain" not in body, (
        "getCookies (plural) must not use strictDomain — only getCookie (singular) should"
    )
