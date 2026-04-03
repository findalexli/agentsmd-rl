"""
Task: posthog-mcp-tool-name-validation
Repo: PostHog/posthog @ 2f7a8ee722e5d451dd2c242c722ea818cc325485
PR:   51937

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/posthog"


def _read(relpath: str) -> str:
    return (Path(REPO) / relpath).read_text()


def _extract_js_regex(content: str, var_name: str) -> str | None:
    """Extract a regex body from TS like: export const VAR = /pattern/"""
    m = re.search(rf"export\s+const\s+{var_name}\s*=\s*/(.+?)/", content)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files have balanced braces."""
    for relpath in [
        "services/mcp/scripts/yaml-config-schema.ts",
        "services/mcp/scripts/lint-tool-names.ts",
    ]:
        content = _read(relpath)
        assert content.count("{") == content.count("}"), f"Unbalanced braces in {relpath}"
        assert content.count("(") == content.count(")"), f"Unbalanced parens in {relpath}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tool_name_pattern_validation():
    """TOOL_NAME_PATTERN regex must accept valid kebab-case and reject invalid names."""
    content = _read("services/mcp/scripts/yaml-config-schema.ts")
    pat_str = _extract_js_regex(content, "TOOL_NAME_PATTERN")
    assert pat_str is not None, "TOOL_NAME_PATTERN must be exported from yaml-config-schema.ts"

    pat = re.compile(pat_str)

    # Must accept valid lowercase kebab-case
    for valid in ["cohorts-create", "feature-flags-list", "a", "a1", "dashboard-get"]:
        assert pat.match(valid), f"TOOL_NAME_PATTERN should accept '{valid}'"

    # Must reject invalid names
    for invalid in ["-leading", "trailing-", "UPPERCASE", "has space", "under_score", ""]:
        assert not pat.match(invalid), f"TOOL_NAME_PATTERN should reject '{invalid}'"


# [pr_diff] fail_to_pass
def test_feature_name_pattern_validation():
    """FEATURE_NAME_PATTERN regex must accept valid snake_case and reject invalid names."""
    content = _read("services/mcp/scripts/yaml-config-schema.ts")
    pat_str = _extract_js_regex(content, "FEATURE_NAME_PATTERN")
    assert pat_str is not None, "FEATURE_NAME_PATTERN must be exported from yaml-config-schema.ts"

    pat = re.compile(pat_str)

    # Must accept valid lowercase snake_case starting with letter
    for valid in ["error_tracking", "feature_flags", "surveys", "a"]:
        assert pat.match(valid), f"FEATURE_NAME_PATTERN should accept '{valid}'"

    # Must reject invalid names
    for invalid in ["_leading", "1starts_with_digit", "UPPER", "kebab-case", ""]:
        assert not pat.match(invalid), f"FEATURE_NAME_PATTERN should reject '{invalid}'"


# [pr_diff] fail_to_pass
def test_zod_schema_validates_tool_name_keys():
    """CategoryConfigSchema must use regex validation on tool name record keys."""
    content = _read("services/mcp/scripts/yaml-config-schema.ts")

    # The schema must validate tool name keys with TOOL_NAME_PATTERN
    assert "TOOL_NAME_PATTERN" in content, "Schema file must define TOOL_NAME_PATTERN"

    # Check that CategoryConfigSchema's tools field applies regex to its keys
    schema_section = content[content.index("CategoryConfigSchema"):]
    assert ".regex(" in schema_section, \
        "CategoryConfigSchema must use .regex() validation on tool name keys"
    assert "TOOL_NAME_PATTERN" in schema_section, \
        "CategoryConfigSchema must reference TOOL_NAME_PATTERN for tool key validation"


# [pr_diff] fail_to_pass
def test_zod_schema_validates_feature_field():
    """CategoryConfigSchema must use regex validation on the feature field."""
    content = _read("services/mcp/scripts/yaml-config-schema.ts")

    schema_section = content[content.index("CategoryConfigSchema"):]
    assert "FEATURE_NAME_PATTERN" in schema_section, \
        "CategoryConfigSchema must reference FEATURE_NAME_PATTERN for feature field validation"


# [pr_diff] fail_to_pass
def test_lint_validates_json_definitions():
    """lint-tool-names.ts must validate JSON definition files, not just YAML."""
    content = _read("services/mcp/scripts/lint-tool-names.ts")

    assert "tool-definitions.json" in content, \
        "Linter must validate handwritten tool-definitions.json"
    assert "tool-definitions-v2.json" in content, \
        "Linter must validate handwritten tool-definitions-v2.json"
    assert "generated-tool-definitions.json" in content, \
        "Linter must validate generated-tool-definitions.json"


# [pr_diff] fail_to_pass
def test_lint_uses_pattern_validation():
    """lint-tool-names.ts must import and use TOOL_NAME_PATTERN for pattern checks."""
    content = _read("services/mcp/scripts/lint-tool-names.ts")

    assert "TOOL_NAME_PATTERN" in content, \
        "Linter must import TOOL_NAME_PATTERN"
    assert "validateToolName" in content or "TOOL_NAME_PATTERN.test" in content, \
        "Linter must use TOOL_NAME_PATTERN for validation (via helper or direct .test())"


# [pr_diff] fail_to_pass
def test_vitest_file_created():
    """A vitest test file must exist for runtime tool name validation."""
    test_file = Path(REPO) / "services/mcp/tests/unit/tool-name-validation.test.ts"
    content = test_file.read_text()

    assert "TOOL_NAME_PATTERN" in content, \
        "Test must reference TOOL_NAME_PATTERN"
    assert "TOOL_MAP" in content, \
        "Test must validate entries from TOOL_MAP"
    assert "MAX_TOOL_NAME_LENGTH" in content, \
        "Test must check length constraint"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — documentation / config file updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    content_lower = content.lower()
    assert "naming constraint" in content_lower or "tool naming" in content_lower, \
        "SKILL.md must have a section on tool naming constraints"

    assert "kebab-case" in content_lower or "kebab case" in content_lower, \
        "SKILL.md must document kebab-case format for tool names"

    assert "52" in content, \
        "SKILL.md must document the 52-character tool name length limit"

    assert "cursor" in content_lower, \
        "SKILL.md must mention Cursor's tool name limit"

    assert "feature" in content_lower and "snake" in content_lower, \
        "SKILL.md must document snake_case format for feature identifiers"


# [config_edit] fail_to_pass

    content_lower = content.lower()

    assert "feature identifier" in content_lower or "feature identifiers" in content_lower, \
        "Handbook must document feature identifier naming"

    assert "snake_case" in content_lower or "snake case" in content_lower, \
        "Handbook must specify snake_case format for feature identifiers"

    assert "pattern" in content_lower or "[a-z0-9" in content, \
        "Handbook must document the character pattern validation"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — AGENTS.md / CLAUDE.md compliance
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass
