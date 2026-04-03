"""
Task: selenium-build-pin-browsers-in-bazel
Repo: SeleniumHQ/selenium @ 130c11dd86c9bc4367b75eb6ac75a42c56a65887
PR:   16743

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/selenium"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """BUILD.bazel must be valid Starlark (balanced braces/parens)."""
    build = Path(REPO) / "common" / "BUILD.bazel"
    content = build.read_text()
    assert content.count("(") == content.count(")"), "Unbalanced parentheses in BUILD.bazel"
    assert content.count("[") == content.count("]"), "Unbalanced brackets in BUILD.bazel"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_pin_browsers_default_true():
    """The pin_browsers bool_flag must default to True."""
    build = Path(REPO) / "common" / "BUILD.bazel"
    content = build.read_text()
    # Find the pin_browsers bool_flag block and check its default
    match = re.search(
        r'bool_flag\s*\(\s*name\s*=\s*"pin_browsers".*?\)',
        content,
        re.DOTALL,
    )
    assert match, "pin_browsers bool_flag not found in common/BUILD.bazel"
    block = match.group(0)
    assert "True" in block, \
        "pin_browsers build_setting_default must be True, not False"
    assert "False" not in block, \
        "pin_browsers build_setting_default must not be False"


# [pr_diff] fail_to_pass
def test_ci_dotnet_no_explicit_pin():
    """ci-dotnet.yml must not contain --pin_browsers=true (redundant with new default)."""
    ci = Path(REPO) / ".github" / "workflows" / "ci-dotnet.yml"
    content = ci.read_text()
    assert "--pin_browsers=true" not in content, \
        "ci-dotnet.yml should not have explicit --pin_browsers=true"


# [pr_diff] fail_to_pass
def test_ci_java_no_explicit_pin():
    """ci-java.yml must not contain --pin_browsers=true."""
    ci = Path(REPO) / ".github" / "workflows" / "ci-java.yml"
    content = ci.read_text()
    assert "--pin_browsers=true" not in content, \
        "ci-java.yml should not have explicit --pin_browsers=true"


# [pr_diff] fail_to_pass
def test_ci_python_no_explicit_pin():
    """ci-python.yml must not contain --pin_browsers=true."""
    ci = Path(REPO) / ".github" / "workflows" / "ci-python.yml"
    content = ci.read_text()
    assert "--pin_browsers=true" not in content, \
        "ci-python.yml should not have explicit --pin_browsers=true"


# [pr_diff] fail_to_pass
def test_ci_ruby_no_explicit_pin():
    """ci-ruby.yml must not contain --pin_browsers as a standalone flag."""
    ci = Path(REPO) / ".github" / "workflows" / "ci-ruby.yml"
    content = ci.read_text()
    # Ruby CI used --pin_browsers (without =true), check it's removed
    lines = content.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped == "--pin_browsers" or stripped == "--pin_browsers \\":
            raise AssertionError(
                "ci-ruby.yml should not have standalone --pin_browsers flag"
            )


# [pr_diff] fail_to_pass
def test_bazelrc_remote_no_pin_browsers():
    """.bazelrc.remote must not set --//common:pin_browsers (redundant)."""
    bazelrc = Path(REPO) / ".bazelrc.remote"
    content = bazelrc.read_text()
    assert "--//common:pin_browsers" not in content, \
        ".bazelrc.remote should not have explicit --//common:pin_browsers"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_pin_browsers_flag_exists():
    """The pin_browsers bool_flag must still exist in BUILD.bazel."""
    build = Path(REPO) / "common" / "BUILD.bazel"
    content = build.read_text()
    assert "pin_browsers" in content, \
        "common/BUILD.bazel must still define the pin_browsers flag"
    assert "bool_flag" in content, \
        "common/BUILD.bazel must still use bool_flag for pin_browsers"
