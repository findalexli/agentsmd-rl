"""
Task: react-eprh-prepare-for-700
Repo: facebook/react @ 9724e3e66e4ad3cc82c728e5c732c21986825b06
PR:   34757

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/react"
INDEX_TS = Path(REPO) / "packages/eslint-plugin-react-hooks/src/index.ts"
README = Path(REPO) / "packages/eslint-plugin-react-hooks/README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_legacy_configs_removed():
    """recommended-legacy and recommended-latest-legacy configs must be removed."""
    content = INDEX_TS.read_text()
    # These config names should not appear as object keys in the configs definition
    assert "'recommended-legacy'" not in content, (
        "index.ts should not define 'recommended-legacy' config"
    )
    assert "'recommended-latest-legacy'" not in content, (
        "index.ts should not define 'recommended-latest-legacy' config"
    )


# [pr_diff] fail_to_pass
def test_flat_recommended_removed():
    """flat/recommended config must be removed from configs object."""
    content = INDEX_TS.read_text()
    assert "'flat/recommended'" not in content, (
        "index.ts should not define 'flat/recommended' config"
    )


# [pr_diff] fail_to_pass
def test_recommended_uses_all_rules():
    """The 'recommended' config must use allRuleConfigs (compiler rules included)."""
    content = INDEX_TS.read_text()
    # Find the recommended config definition and verify it uses allRuleConfigs
    # Pattern: recommended config should reference allRuleConfigs, not basicRuleConfigs
    rec_match = re.search(
        r"""(?:['"]?recommended['"]?\s*[=:{]\s*\{[^}]*rules\s*:\s*)(\w+)""",
        content,
    )
    assert rec_match, "Could not find 'recommended' config definition in index.ts"
    rules_ref = rec_match.group(1)
    assert rules_ref == "allRuleConfigs", (
        f"'recommended' config should use allRuleConfigs, found: {rules_ref}"
    )


# [pr_diff] fail_to_pass
def test_plugin_meta_has_version():
    """Plugin meta object must include a version field."""
    content = INDEX_TS.read_text()
    # Look for version in the plugin meta block
    meta_match = re.search(r"meta\s*:\s*\{([\s\S]*?)\}", content)
    assert meta_match, "Could not find plugin meta block in index.ts"
    meta_body = meta_match.group(1)
    assert "version" in meta_body, (
        "Plugin meta should include a version field"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_recommended_latest_still_exists():
    """The 'recommended-latest' config must still be defined."""
    content = INDEX_TS.read_text()
    assert "'recommended-latest'" in content, (
        "index.ts must still define 'recommended-latest' config"
    )


# [static] pass_to_pass
def test_plugin_exports_structure():
    """Plugin must still export rules, configs, and meta."""
    content = INDEX_TS.read_text()
    assert "rules," in content or "rules:" in content, (
        "Plugin must export rules"
    )
    assert "configs," in content or "configs:" in content, (
        "Plugin must export configs"
    )
    assert "meta:" in content or "meta," in content, (
        "Plugin must export meta"
    )
