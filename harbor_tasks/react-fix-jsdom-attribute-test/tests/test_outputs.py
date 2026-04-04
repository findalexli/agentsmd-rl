"""
Task: react-fix-jsdom-attribute-test
Repo: facebook/react @ 90b2dd442cc05048b2a6ade5020c463ab0499eca
PR:   35654

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Fix: Adds a JSDOM setAttribute override so that JSDOM throws on non-coercible
values (matching real browser behavior), then unifies the TemporalLike test
assertion to always expect a TypeError, and removes a stale TODO comment.

Files changed:
  packages/react-dom/src/__tests__/ReactDOMAttribute-test.js
  packages/shared/CheckStringCoercion.js
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
ATTR_TEST = f"{REPO}/packages/react-dom/src/__tests__/ReactDOMAttribute-test.js"
COERCION = f"{REPO}/packages/shared/CheckStringCoercion.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both modified files must parse without errors."""
    for path in [ATTR_TEST, COERCION]:
        r = subprocess.run(
            ["node", "--check", path],
            capture_output=True,
            timeout=30,
        )
        assert r.returncode == 0, (
            f"{path} has syntax errors:\n{r.stderr.decode()}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_jsdom_setattribute_override():
    """JSDOM setAttribute override must be added to the test file.

    The fix overrides Element.prototype.setAttribute to explicitly stringify
    values (e.g. '' + value or String(value)), making JSDOM throw on
    non-coercible inputs (matching real browser setAttribute semantics).
    """
    src = Path(ATTR_TEST).read_text()
    assert "Element.prototype.setAttribute" in src, (
        "Element.prototype.setAttribute override not found in ReactDOMAttribute-test.js"
    )
    # The override must coerce to string — accept common JS coercion patterns
    coercion_patterns = [
        r"['\"][\s]*\+\s*value",       # '' + value or "" + value
        r"value\s*\+\s*['\"]",          # value + '' or value + ""
        r"String\s*\(\s*value\s*\)",    # String(value)
        r"`\$\{value\}`",              # `${value}`
        r"value\.toString\(\)",         # value.toString()
    ]
    assert any(re.search(p, src) for p in coercion_patterns), (
        "setAttribute override must coerce value to string "
        "(e.g. '' + value, String(value), `${value}`)"
    )


# [pr_diff] fail_to_pass
def test_temporal_like_assertion_unified():
    """TemporalLike test must use a single unified assertion, not a conditional.

    On base, the test branched on gate('enableTrustedTypesIntegration') && !__DEV__
    to expect different errors in different configurations. The fix removes this
    divergence so there is one consistent assertion for all configurations.
    """
    src = Path(ATTR_TEST).read_text()
    # The old branching pattern must be gone
    assert "rejects.toThrowError('2020-01-01')" not in src, (
        "Old branch expecting '2020-01-01' error still present"
    )
    # No conditional gate divergence around the TemporalLike assertion
    assert "gate('enableTrustedTypesIntegration') && !__DEV__" not in src, (
        "Conditional gate divergence still present in TemporalLike assertion"
    )
    # The unified assertion expects a TypeError
    assert "rejects.toThrowError(new TypeError" in src, (
        "Unified TypeError assertion not found in TemporalLike test"
    )


# [pr_diff] fail_to_pass
def test_stale_todo_removed():
    """Stale TODO comment about enableTrustedTypesIntegration must be removed.

    The old code had a TODO suggesting the DEV warning for string coercion might
    be unnecessary when Trusted Types integration is enabled. This was incorrect
    reasoning; the check is needed regardless.
    """
    src = Path(COERCION).read_text()
    assert "for enableTrustedTypesIntegration we don't toString" not in src, (
        "Stale TODO comment still present in CheckStringCoercion.js"
    )


# [pr_diff] fail_to_pass
def test_temporal_like_test_passes():
    """The TemporalLike attribute test must pass after the fix.

    On base, JSDOM's setAttribute doesn't throw on non-coercible values, so the
    test fails with an unexpected outcome. After the JSDOM fix, the test passes.
    """
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "ReactDOMAttribute", "-t", "throws with Temporal-like objects",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    combined = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, (
        f"TemporalLike test failed:\n{combined[-3000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression guard
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_setattribute_override_at_top_level():
    """The JSDOM setAttribute override must be at the top of the file, before any describe block.

    Placing it at module scope ensures it applies to all tests in the file.
    The fix injects it before the first 'describe(' call.
    """
    src = Path(ATTR_TEST).read_text()
    lines = src.splitlines()
    override_line = next(
        (i for i, l in enumerate(lines) if "Element.prototype.setAttribute" in l), None
    )
    describe_line = next(
        (i for i, l in enumerate(lines) if l.strip().startswith("describe(")), None
    )
    assert override_line is not None, "Element.prototype.setAttribute override not found"
    assert describe_line is not None, "No describe() block found"
    assert override_line < describe_line, (
        f"Override (line {override_line+1}) must appear before first describe() (line {describe_line+1})"
    )


# [repo_tests] pass_to_pass
def test_other_attribute_tests_pass():
    """The full ReactDOMAttribute test suite must still pass (regression guard)."""
    r = subprocess.run(
        [
            "yarn", "test", "--silent", "--no-watchman",
            "ReactDOMAttribute",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    combined = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, (
        f"ReactDOMAttribute test suite failed:\n{combined[-3000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .claude/skills/
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/feature-flags/SKILL.md:79 @ 90b2dd44
def test_no_string_gate_syntax():
    """gate() calls must use arrow-function syntax, not string syntax.

    Config rule: "It's gate(flags => flags.name), not gate('name')"
    Base code violates this with gate('enableTrustedTypesIntegration').
    """
    src = Path(ATTR_TEST).read_text()
    string_gates = re.findall(r"""gate\(\s*['"]""", src)
    assert len(string_gates) == 0, (
        "gate() must use arrow function syntax: gate(flags => flags.name), "
        f"not gate('name'). Found {len(string_gates)} string-style gate() call(s)"
    )
