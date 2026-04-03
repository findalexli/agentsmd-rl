"""
Task: selenium-bazeljs-avoid-shadowing-directory-with
Repo: SeleniumHQ/selenium @ fb478af81bafa330a1bb71a2eb8ace6b207bfe46
PR:   16784

The closure_test_suite targets named "test" collide with test/ directories
in the Bazel runfiles tree. All three JS packages must rename their target
and the atoms README must update its example commands accordingly.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/selenium"

BUILD_FILES = [
    f"{REPO}/javascript/atoms/BUILD.bazel",
    f"{REPO}/javascript/chrome-driver/BUILD.bazel",
    f"{REPO}/javascript/webdriver/BUILD.bazel",
]


def _extract_closure_test_suite_name(build_file: str) -> str:
    """Extract the name parameter from closure_test_suite in a BUILD.bazel file."""
    content = Path(build_file).read_text()
    match = re.search(r'closure_test_suite\(\s*name\s*=\s*"([^"]+)"', content)
    assert match, f"No closure_test_suite found in {build_file}"
    return match.group(1)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All three BUILD.bazel files still declare a closure_test_suite."""
    for path in BUILD_FILES:
        content = Path(path).read_text()
        assert "closure_test_suite(" in content, (
            f"Missing closure_test_suite declaration in {path}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — BUILD.bazel target renames
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_atoms_target_no_collision():
    """javascript/atoms closure_test_suite must not use name='test' (shadows test/ dir)."""
    name = _extract_closure_test_suite_name(f"{REPO}/javascript/atoms/BUILD.bazel")
    assert name != "test", (
        "closure_test_suite name='test' collides with the test/ directory in runfiles"
    )
    assert len(name) >= 2, "Target name should be a meaningful identifier"


# [pr_diff] fail_to_pass
def test_chrome_driver_target_no_collision():
    """javascript/chrome-driver closure_test_suite must not use name='test'."""
    name = _extract_closure_test_suite_name(
        f"{REPO}/javascript/chrome-driver/BUILD.bazel"
    )
    assert name != "test", (
        "closure_test_suite name='test' collides with the test/ directory in runfiles"
    )


# [pr_diff] fail_to_pass
def test_webdriver_target_no_collision():
    """javascript/webdriver closure_test_suite must not use name='test'."""
    name = _extract_closure_test_suite_name(
        f"{REPO}/javascript/webdriver/BUILD.bazel"
    )
    assert name != "test", (
        "closure_test_suite name='test' collides with the test/ directory in runfiles"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README.md must update example commands
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — consistency between BUILD and README
# ---------------------------------------------------------------------------

# [static] pass_to_pass
