"""
Task: react-enable-trusted-types
Repo: facebook/react @ e33071c6142ae5212483a63b87d5d962860e535a
PR:   N/A

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / parse checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All feature flag files must be syntactically valid JavaScript."""
    files = [
        "packages/shared/ReactFeatureFlags.js",
        "packages/shared/forks/ReactFeatureFlags.native-fb.js",
        "packages/shared/forks/ReactFeatureFlags.native-oss.js",
        "packages/shared/forks/ReactFeatureFlags.test-renderer.js",
        "packages/shared/forks/ReactFeatureFlags.test-renderer.native-fb.js",
        "packages/shared/forks/ReactFeatureFlags.test-renderer.www.js",
        "packages/shared/forks/ReactFeatureFlags.www-dynamic.js",
        "packages/shared/forks/ReactFeatureFlags.www.js",
    ]
    for f in files:
        r = subprocess.run(
            ["node", "--check", f],
            cwd=REPO, capture_output=True, timeout=30,
        )
        assert r.returncode == 0, f"Syntax error in {f}:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — flag must be set to true in each config file
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_main_flags_trusted_types_enabled():
    """packages/shared/ReactFeatureFlags.js must have enableTrustedTypesIntegration = true."""
    content = Path(f"{REPO}/packages/shared/ReactFeatureFlags.js").read_text()
    assert "enableTrustedTypesIntegration: boolean = true" in content, (
        "ReactFeatureFlags.js: enableTrustedTypesIntegration should be true"
    )


# [pr_diff] fail_to_pass
def test_native_fb_flag_enabled():
    """ReactFeatureFlags.native-fb.js must have enableTrustedTypesIntegration = true."""
    content = Path(f"{REPO}/packages/shared/forks/ReactFeatureFlags.native-fb.js").read_text()
    assert "enableTrustedTypesIntegration: boolean = true" in content, (
        "ReactFeatureFlags.native-fb.js: enableTrustedTypesIntegration should be true"
    )


# [pr_diff] fail_to_pass
def test_native_oss_flag_enabled():
    """ReactFeatureFlags.native-oss.js must have enableTrustedTypesIntegration = true."""
    content = Path(f"{REPO}/packages/shared/forks/ReactFeatureFlags.native-oss.js").read_text()
    assert "enableTrustedTypesIntegration: boolean = true" in content, (
        "ReactFeatureFlags.native-oss.js: enableTrustedTypesIntegration should be true"
    )


# [pr_diff] fail_to_pass
def test_test_renderer_flag_enabled():
    """ReactFeatureFlags.test-renderer.js must have enableTrustedTypesIntegration = true."""
    content = Path(f"{REPO}/packages/shared/forks/ReactFeatureFlags.test-renderer.js").read_text()
    assert "enableTrustedTypesIntegration: boolean = true" in content, (
        "ReactFeatureFlags.test-renderer.js: enableTrustedTypesIntegration should be true"
    )


# [pr_diff] fail_to_pass
def test_test_renderer_native_fb_flag_enabled():
    """ReactFeatureFlags.test-renderer.native-fb.js must have enableTrustedTypesIntegration = true.

    This file uses untyped exports (no `: boolean` annotation).
    """
    content = Path(
        f"{REPO}/packages/shared/forks/ReactFeatureFlags.test-renderer.native-fb.js"
    ).read_text()
    assert "enableTrustedTypesIntegration = true" in content, (
        "ReactFeatureFlags.test-renderer.native-fb.js: enableTrustedTypesIntegration should be true"
    )


# [pr_diff] fail_to_pass
def test_test_renderer_www_flag_enabled():
    """ReactFeatureFlags.test-renderer.www.js must have enableTrustedTypesIntegration = true."""
    content = Path(
        f"{REPO}/packages/shared/forks/ReactFeatureFlags.test-renderer.www.js"
    ).read_text()
    assert "enableTrustedTypesIntegration: boolean = true" in content, (
        "ReactFeatureFlags.test-renderer.www.js: enableTrustedTypesIntegration should be true"
    )


# [pr_diff] fail_to_pass
def test_www_flag_enabled():
    """ReactFeatureFlags.www.js must export enableTrustedTypesIntegration = true directly (not via dynamic)."""
    content = Path(f"{REPO}/packages/shared/forks/ReactFeatureFlags.www.js").read_text()
    assert "enableTrustedTypesIntegration: boolean = true" in content, (
        "ReactFeatureFlags.www.js: enableTrustedTypesIntegration should be a direct static export = true"
    )


# [pr_diff] fail_to_pass
def test_www_dynamic_flag_removed():
    """enableTrustedTypesIntegration must be removed from www-dynamic.js (it is now static everywhere)."""
    content = Path(
        f"{REPO}/packages/shared/forks/ReactFeatureFlags.www-dynamic.js"
    ).read_text()
    assert "enableTrustedTypesIntegration" not in content, (
        "ReactFeatureFlags.www-dynamic.js must not declare enableTrustedTypesIntegration "
        "(it is now statically true in all configs, no longer a dynamic variant)"
    )


# [pr_diff] fail_to_pass
def test_www_not_importing_from_dynamic():
    """ReactFeatureFlags.www.js must not destructure enableTrustedTypesIntegration from the dynamic module."""
    content = Path(f"{REPO}/packages/shared/forks/ReactFeatureFlags.www.js").read_text()
    # The www.js file imports some flags from www-dynamic via `export const { ... } = ...`
    # enableTrustedTypesIntegration must not be in that destructuring block
    match = re.search(r"export const \{([^}]+)\}", content, re.DOTALL)
    if match:
        destructured = match.group(1)
        assert "enableTrustedTypesIntegration" not in destructured, (
            "ReactFeatureFlags.www.js must not import enableTrustedTypesIntegration "
            "from the dynamic module"
        )
