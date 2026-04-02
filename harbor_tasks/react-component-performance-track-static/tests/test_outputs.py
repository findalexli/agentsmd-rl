"""
Task: react-component-performance-track-static
Repo: facebook/react @ 3e319a943cff862b8fbb8e96868f9f153a9e199d
PR:   35629

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/react"
FORKS = Path(f"{REPO}/packages/shared/forks")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — files must exist
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_files_exist():
    """All four feature flag fork files must be present."""
    for name in [
        "ReactFeatureFlags.native-fb-dynamic.js",
        "ReactFeatureFlags.native-fb.js",
        "ReactFeatureFlags.www-dynamic.js",
        "ReactFeatureFlags.www.js",
    ]:
        assert (FORKS / name).exists(), f"Missing required fork file: {name}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_native_fb_dynamic_flag_removed():
    """enableComponentPerformanceTrack must not be exported as __VARIANT__ in native-fb-dynamic.js."""
    content = (FORKS / "ReactFeatureFlags.native-fb-dynamic.js").read_text()
    bad_lines = [
        line for line in content.splitlines()
        if "enableComponentPerformanceTrack" in line and "__VARIANT__" in line
    ]
    assert not bad_lines, (
        "Flag still exported as __VARIANT__ in native-fb-dynamic.js:\n"
        + "\n".join(bad_lines)
    )


# [pr_diff] fail_to_pass
def test_www_dynamic_flag_removed():
    """enableComponentPerformanceTrack must not be exported as __VARIANT__ in www-dynamic.js."""
    content = (FORKS / "ReactFeatureFlags.www-dynamic.js").read_text()
    bad_lines = [
        line for line in content.splitlines()
        if "enableComponentPerformanceTrack" in line and "__VARIANT__" in line
    ]
    assert not bad_lines, (
        "Flag still exported as __VARIANT__ in www-dynamic.js:\n"
        + "\n".join(bad_lines)
    )


# [pr_diff] fail_to_pass
def test_native_fb_static_true():
    """enableComponentPerformanceTrack must be statically true in native-fb.js, not __PROFILE__ gated."""
    content = (FORKS / "ReactFeatureFlags.native-fb.js").read_text()

    # Must have a static true declaration
    static_lines = [
        line for line in content.splitlines()
        if "enableComponentPerformanceTrack" in line and "= true" in line
    ]
    assert static_lines, (
        "enableComponentPerformanceTrack is not statically set to true in native-fb.js"
    )

    # Must NOT use __PROFILE__ gating for this flag
    profile_lines = [
        line for line in content.splitlines()
        if "enableComponentPerformanceTrack" in line and "__PROFILE__" in line
    ]
    assert not profile_lines, (
        "enableComponentPerformanceTrack is still gated behind __PROFILE__ in native-fb.js:\n"
        + "\n".join(profile_lines)
    )


# [pr_diff] fail_to_pass
def test_www_static_true():
    """enableComponentPerformanceTrack must be statically set to true in www.js."""
    content = (FORKS / "ReactFeatureFlags.www.js").read_text()
    static_lines = [
        line for line in content.splitlines()
        if "enableComponentPerformanceTrack" in line and "= true" in line
    ]
    assert static_lines, (
        "enableComponentPerformanceTrack is not statically set to true in www.js"
    )


# [pr_diff] fail_to_pass
def test_www_not_destructured_from_dynamic():
    """enableComponentPerformanceTrack must not be destructured from the dynamic flags object in www.js."""
    content = (FORKS / "ReactFeatureFlags.www.js").read_text()
    for line in content.splitlines():
        stripped = line.strip()
        # Destructured form is a bare identifier with trailing comma, no assignment operator
        if stripped == "enableComponentPerformanceTrack," and "=" not in line:
            assert False, (
                f"Flag still destructured from dynamic flags in www.js: {line!r}"
            )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression check
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_performance_issue_reporting_intact():
    """enablePerformanceIssueReporting must still be defined in terms of enableComponentPerformanceTrack in native-fb.js."""
    content = (FORKS / "ReactFeatureFlags.native-fb.js").read_text()
    assert "enablePerformanceIssueReporting" in content, (
        "enablePerformanceIssueReporting is missing from native-fb.js"
    )
    dependent_lines = [
        line for line in content.splitlines()
        if "enablePerformanceIssueReporting" in line and "enableComponentPerformanceTrack" in line
    ]
    assert dependent_lines, (
        "enablePerformanceIssueReporting no longer references enableComponentPerformanceTrack in native-fb.js"
    )
