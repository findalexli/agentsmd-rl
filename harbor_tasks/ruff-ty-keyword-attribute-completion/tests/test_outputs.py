"""
Task: ruff-ty-keyword-attribute-completion
Repo: astral-sh/ruff @ 4aabc71fa2594b5c90105cc963cb04c1c4d52f51
PR:   #24232

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/ruff"
COMP_RS = f"{REPO}/crates/ty_ide/src/completion.rs"

# Rust test code injected into the completion module's test submodule.
# Each test exercises a different Python keyword as an attribute prefix.
HARBOR_KW_TESTS = r"""
#[test]
fn harbor_keyword_prefix_is_completes() {
    // "is" is Python keyword TokenKind::Is
    let test = completion_test_builder(
        "\
{1}.is<CURSOR>
",
    )
    .skip_builtins()
    .skip_keywords()
    .build();

    test.contains("isdisjoint");
}

#[test]
fn harbor_keyword_prefix_in_completes() {
    // "in" is Python keyword TokenKind::In
    let test = completion_test_builder(
        "\
[1, 2, 3].in<CURSOR>
",
    )
    .skip_builtins()
    .skip_keywords()
    .build();

    test.contains("index");
}

#[test]
fn harbor_keyword_prefix_for_completes() {
    // "for" is Python keyword TokenKind::For
    let test = completion_test_builder(
        "\
"abc".for<CURSOR>
",
    )
    .skip_builtins()
    .skip_keywords()
    .build();

    test.contains("format");
}

#[test]
fn harbor_keyword_prefix_not_completes() {
    // "not" is Python keyword TokenKind::Not
    let test = completion_test_builder(
        "\
class Foo:
    not_ready = True
Foo().not<CURSOR>
",
    )
    .skip_builtins()
    .skip_keywords()
    .build();

    test.contains("not_ready");
}
"""


def _cargo_env():
    """Return env dict with CARGO_PROFILE_DEV_OPT_LEVEL=1 for faster builds."""
    env = os.environ.copy()
    env["CARGO_PROFILE_DEV_OPT_LEVEL"] = "1"
    return env


# ---------------------------------------------------------------------------
# Shared fixture: inject harbor keyword tests, run once, parse per-test results
# ---------------------------------------------------------------------------

_kw_results: dict[str, bool] | None = None


def _run_keyword_tests() -> dict[str, bool]:
    """Inject Rust test code, run cargo nextest, return {test_name: passed}."""
    global _kw_results
    if _kw_results is not None:
        return _kw_results

    comp_rs = Path(COMP_RS)
    backup = comp_rs.read_text()
    test_file = Path(REPO) / "crates/ty_ide/src/harbor_kw_test.rs"

    try:
        # Write test file
        test_file.write_text(HARBOR_KW_TESTS)

        # Inject include!() before the final closing brace of the test module
        content = comp_rs.read_text()
        last_brace = content.rfind("}")
        assert last_brace != -1, "Could not find closing brace in completion.rs"
        new_content = (
            content[:last_brace]
            + '\n    include!("harbor_kw_test.rs");\n'
            + content[last_brace:]
        )
        comp_rs.write_text(new_content)

        # Run tests
        r = subprocess.run(
            [
                "cargo", "nextest", "run", "-p", "ty_ide",
                "--", "harbor_keyword_prefix",
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env=_cargo_env(),
        )
        output = r.stdout + "\n" + r.stderr
    finally:
        # Always restore original files
        comp_rs.write_text(backup)
        if test_file.exists():
            test_file.unlink()

    results = {}
    for name in [
        "harbor_keyword_prefix_is_completes",
        "harbor_keyword_prefix_in_completes",
        "harbor_keyword_prefix_for_completes",
        "harbor_keyword_prefix_not_completes",
    ]:
        results[name] = bool(re.search(rf"PASS.*{name}", output))

    _kw_results = results
    return results


# ---------------------------------------------------------------------------
# Shared fixture: run upstream completion tests once, reuse results
# ---------------------------------------------------------------------------

_completion_results: dict | None = None


def _run_upstream_completion_tests() -> dict:
    """Run upstream completion test suite once and cache results."""
    global _completion_results
    if _completion_results is not None:
        return _completion_results

    r = subprocess.run(
        [
            "cargo", "nextest", "run", "-p", "ty_ide",
            "--", "completion",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=_cargo_env(),
    )
    output = r.stdout + "\n" + r.stderr
    passed_match = re.search(r"(\d+) passed", output)
    passed = int(passed_match.group(1)) if passed_match else 0

    # Check specific attribute_access tests
    attr_tests = ["attribute_access_set", "attribute_access_empty"]
    attr_passed = sum(1 for t in attr_tests if re.search(rf"PASS.*{t}", output))

    _completion_results = {
        "returncode": r.returncode,
        "total_passed": passed,
        "attr_passed": attr_passed,
        "output": output,
    }
    return _completion_results


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """Modified code must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_ide", "--quiet"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=_cargo_env(),
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_keyword_prefix_is_completion():
    """{1}.is<CURSOR> must produce completions like isdisjoint.

    The lexer tokenizes 'is' as TokenKind::Is (keyword) instead of
    TokenKind::Name. The fix must handle keyword tokens after a dot.
    """
    results = _run_keyword_tests()
    assert results["harbor_keyword_prefix_is_completes"], (
        "Completion for {1}.is<CURSOR> did not return isdisjoint"
    )


# [pr_diff] fail_to_pass
def test_keyword_prefix_in_completion():
    """[1,2,3].in<CURSOR> must produce completions like index.

    The lexer tokenizes 'in' as TokenKind::In (keyword).
    """
    results = _run_keyword_tests()
    assert results["harbor_keyword_prefix_in_completes"], (
        "Completion for [1,2,3].in<CURSOR> did not return index"
    )


# [pr_diff] fail_to_pass
def test_keyword_prefix_for_completion():
    '''"abc".for<CURSOR> must produce completions like format.

    The lexer tokenizes 'for' as TokenKind::For (keyword).
    '''
    results = _run_keyword_tests()
    assert results["harbor_keyword_prefix_for_completes"], (
        'Completion for "abc".for<CURSOR> did not return format'
    )


# [pr_diff] fail_to_pass
def test_keyword_prefix_not_completion():
    """Foo().not<CURSOR> must produce completions like not_ready.

    The lexer tokenizes 'not' as TokenKind::Not (keyword).
    Tests custom class attribute, not just built-in type methods.
    """
    results = _run_keyword_tests()
    assert results["harbor_keyword_prefix_not_completes"], (
        "Completion for Foo().not<CURSOR> did not return not_ready"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_completion_tests_pass():
    """Upstream completion test suite must not regress."""
    results = _run_upstream_completion_tests()
    assert results["returncode"] == 0 and results["total_passed"] >= 10, (
        f"Existing completion tests failed or too few passed ({results['total_passed']}):\n"
        f"{results['output'][-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_existing_attribute_access_tests_pass():
    """Existing attribute_access completion tests must still pass."""
    results = _run_upstream_completion_tests()
    assert results["attr_passed"] >= 2, (
        f"Existing attribute_access tests failed ({results['attr_passed']} passed):\n"
        f"{results['output'][-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

def _get_diff():
    """Get git diff for completion.rs, assert file was modified."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", "crates/ty_ide/src/completion.rs"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    diff = r.stdout
    assert diff, "No changes to completion.rs — fix must modify this file"
    return diff


def _added_lines(diff: str) -> list[str]:
    """Extract added lines from a diff (lines starting with + but not +++)."""
    return [l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]


# [agent_config] fail_to_pass — AGENTS.md:79 @ 4aabc71f
def test_no_unwrap_panic_unreachable_in_diff():
    """No .unwrap(), panic!(), or unreachable!() in changed code (AGENTS.md:79).

    Rule: 'Try hard to avoid patterns that require panic!, unreachable!, or .unwrap().
    Instead, try to encode those constraints in the type system.'
    """
    diff = _get_diff()
    added = _added_lines(diff)
    unsafe_patterns = {
        ".unwrap()": [],
        "panic!(": [],
        "unreachable!(": [],
    }
    for line in added:
        for pattern in unsafe_patterns:
            if pattern in line:
                unsafe_patterns[pattern].append(line)
    violations = {p: lines for p, lines in unsafe_patterns.items() if lines}
    assert not violations, (
        f"Unsafe patterns in changed code (violates AGENTS.md:79):\n"
        + "\n".join(f"  {p}: {l}" for p, lines in violations.items() for l in lines)
    )
