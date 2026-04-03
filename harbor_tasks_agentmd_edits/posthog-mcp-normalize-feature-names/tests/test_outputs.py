"""
Task: posthog-mcp-normalize-feature-names
Repo: PostHog/posthog @ 283294a8e1c595e5762fa55a8d18b844c4667f2c
PR:   51901

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
from pathlib import Path

REPO = "/workspace/posthog"
MCP = f"{REPO}/services/mcp"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """JSON schema files must be valid JSON."""
    for name in [
        "tool-definitions.json",
        "tool-definitions-all.json",
        "tool-definitions-v2.json",
    ]:
        p = Path(MCP) / "schema" / name
        data = json.loads(p.read_text())
        assert isinstance(data, dict), f"{name} should be a JSON object"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — schema normalization
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_schema_feature_names_use_underscores():
    """All feature fields in schema JSON files must use underscores, not hyphens."""
    hyphenated_features = {"error-tracking", "llm-analytics", "data-schema"}
    for name in [
        "tool-definitions.json",
        "tool-definitions-all.json",
        "tool-definitions-v2.json",
    ]:
        p = Path(MCP) / "schema" / name
        data = json.loads(p.read_text())
        for tool_name, defn in data.items():
            feat = defn.get("feature", "")
            assert feat not in hyphenated_features, (
                f"{name}: tool '{tool_name}' has hyphenated feature '{feat}', "
                f"expected underscore variant '{feat.replace('-', '_')}'"
            )


# [pr_diff] fail_to_pass
def test_feature_name_normalization_defined():
    """toolDefinitions.ts must define logic to normalize hyphens to underscores."""
    src = Path(f"{MCP}/src/tools/toolDefinitions.ts").read_text()
    # Must have code that replaces hyphens with underscores (or equivalent)
    has_hyphen_replacement = bool(re.search(r"replace(?:All)?\s*\(\s*[/\"'].*-", src))
    assert has_hyphen_replacement, (
        "toolDefinitions.ts should have logic to replace hyphens in feature names"
    )


# [pr_diff] fail_to_pass
def test_feature_filtering_uses_normalization():
    """Feature filtering must not use direct string comparison for features."""
    src = Path(f"{MCP}/src/tools/toolDefinitions.ts").read_text()
    # The old broken pattern: features.includes(definition.feature)
    # This direct comparison fails when conventions differ (hyphens vs underscores)
    has_direct_includes = "features.includes(definition.feature)" in src
    assert not has_direct_includes, (
        "Feature filtering should use normalized comparison, "
        "not direct features.includes(definition.feature)"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_tool_definitions_structure():
    """Tool definitions have required fields (feature, category, description)."""
    p = Path(MCP) / "schema" / "tool-definitions.json"
    data = json.loads(p.read_text())
    for tool_name, defn in data.items():
        assert "feature" in defn, f"{tool_name} missing 'feature' field"
        assert "category" in defn, f"{tool_name} missing 'category' field"
        assert "description" in defn, f"{tool_name} missing 'description' field"
