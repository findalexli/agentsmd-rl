"""
Task: selenium-py-consolidate-ci-tests
Repo: SeleniumHQ/selenium @ 175b59bd383fa5ae7b966e85b18cfdf41919a75d
PR:   16766

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/selenium"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_build_files_valid():
    """BUILD.bazel and browsers.bzl exist and are non-empty."""
    build = Path(REPO) / "py" / "BUILD.bazel"
    bzl = Path(REPO) / "py" / "private" / "browsers.bzl"
    assert build.exists(), "py/BUILD.bazel must exist"
    assert bzl.exists(), "py/private/browsers.bzl must exist"
    content_build = build.read_text()
    content_bzl = bzl.read_text()
    assert len(content_build) > 1000, "BUILD.bazel seems too short"
    assert len(content_bzl) > 50, "browsers.bzl seems too short"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — BUILD.bazel consolidation
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_browser_config_dict_exists():
    """BUILD.bazel must define a dict mapping browsers to their test configuration."""
    build = Path(REPO) / "py" / "BUILD.bazel"
    content = build.read_text()
    # The dict should map browser names to configs with source globs
    # Accept any dict name but verify it maps browsers to browser_srcs
    assert "browser_srcs" in content.lower() or "BROWSER_TESTS" in content, \
        "BUILD.bazel should have a browser config dict with source mappings"
    # Must include at least chrome, firefox, edge, safari
    for browser in ["chrome", "firefox", "edge", "safari"]:
        assert f'"{browser}"' in content, \
            f"Browser config dict must include {browser}"


# [pr_diff] fail_to_pass
def test_generated_targets_combine_sources():
    """Generated test-<browser> targets must include both common and browser-specific sources."""
    build = Path(REPO) / "py" / "BUILD.bazel"
    content = build.read_text()
    # The generated targets should combine common + browser-specific globs
    # Check that common test paths AND browser_srcs are in the same glob() call
    # by looking for the list concatenation pattern
    assert re.search(
        r'glob\(\s*\[\s*"test/selenium/webdriver/common/\*\*/\*\.py".*?\]'
        r'.*?browser_srcs',
        content,
        re.DOTALL | re.IGNORECASE,
    ), "Generated targets should combine common tests with browser-specific sources"


# [pr_diff] fail_to_pass
def test_no_standalone_browser_test_suites():
    """Individual hardcoded py_test_suite blocks for browsers should be consolidated."""
    build = Path(REPO) / "py" / "BUILD.bazel"
    content = build.read_text()
    # Check that there are no standalone py_test_suite blocks for individual browsers
    # (they should all be generated from the dict now)
    standalone_pattern = re.compile(
        r'py_test_suite\(\s*\n\s*name\s*=\s*"test-(chrome|edge|firefox|ie|safari)"',
    )
    matches = standalone_pattern.findall(content)
    # There should be NO standalone blocks — they're all generated via list comprehension
    # The generated ones use "test-%s" % browser, not literal "test-chrome"
    assert len(matches) == 0, (
        f"Found standalone py_test_suite blocks for: {matches}. "
        "These should be consolidated into generated targets."
    )


# [pr_diff] fail_to_pass
def test_no_common_browser_targets():
    """The old common-<browser> target naming should be replaced with test-<browser>."""
    build = Path(REPO) / "py" / "BUILD.bazel"
    content = build.read_text()
    # Old pattern: name = "common-%s" % browser
    assert '"common-%s"' not in content, \
        "BUILD.bazel should use test-<browser> targets, not common-<browser>"


# [pr_diff] fail_to_pass
def test_bidi_targets_conditional():
    """BiDi test targets should only be generated for browsers that support BiDi."""
    build = Path(REPO) / "py" / "BUILD.bazel"
    content = build.read_text()
    # The bidi target list comprehension must have a conditional filter
    # Look for the bidi target generation with an if condition
    bidi_section = re.search(
        r'name\s*=\s*"test-%s-bidi".*?for\s+browser\s+in\s+\S+.*?if\s+',
        content,
        re.DOTALL,
    )
    assert bidi_section, (
        "BiDi targets should be conditionally generated "
        "(e.g., only for browsers with bidi=True)"
    )


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README.md documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
