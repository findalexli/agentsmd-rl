"""
Task: posthog-mcp-add-tool-name-pattern-validation
Repo: PostHog/posthog @ 2f7a8ee722e5d451dd2c242c722ea818cc325485
PR:   51937

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/posthog"


def _run_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a TypeScript snippet via node --experimental-strip-types."""
    script_path = Path(REPO) / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", str(script_path)],
            capture_output=True, text=True, timeout=timeout,
            cwd=REPO,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files parse without syntax errors."""
    schema_path = Path(REPO) / "services/mcp/scripts/yaml-config-schema.ts"
    assert schema_path.exists(), "yaml-config-schema.ts does not exist"
    result = _run_ts(
        "import { MAX_TOOL_NAME_LENGTH } from "
        "'./services/mcp/scripts/yaml-config-schema.ts'\n"
        "console.log('ok', MAX_TOOL_NAME_LENGTH)\n"
    )
    assert result.returncode == 0, f"yaml-config-schema.ts failed to import: {result.stderr}"


# [static] pass_to_pass
def test_max_tool_name_length_preserved():
    """MAX_TOOL_NAME_LENGTH constant must remain 52."""
    result = _run_ts(
        "import { MAX_TOOL_NAME_LENGTH } from "
        "'./services/mcp/scripts/yaml-config-schema.ts'\n"
        "console.log(JSON.stringify({ val: MAX_TOOL_NAME_LENGTH }))\n"
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["val"] == 52, f"Expected 52, got {data['val']}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI commands from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_mcp_typecheck():
    """MCP package TypeScript typecheck passes on modified files (pass_to_pass)."""
    # Only typecheck the specific files modified by the PR, since the full
    # package typecheck requires React dependencies for frontend mcp-apps
    schema_path = Path(REPO) / "services/mcp/scripts/yaml-config-schema.ts"
    lint_path = Path(REPO) / "services/mcp/scripts/lint-tool-names.ts"

    for f in [schema_path, lint_path]:
        r = subprocess.run(
            ["pnpm", "--filter=@posthog/mcp", "exec", "tsc", "--noEmit", "--skipLibCheck", str(f)],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"TypeScript check failed for {f}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_mcp_lint_tool_names():
    """MCP lint-tool-names passes on existing definitions (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "--filter=@posthog/mcp", "lint-tool-names"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"MCP lint-tool-names failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_mcp_unit_tests():
    """MCP unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "--filter=@posthog/mcp", "test", "--run"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"MCP unit tests failed:\n{r.stderr[-1000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tool_name_pattern_validates():
    """TOOL_NAME_PATTERN accepts valid kebab-case and rejects invalid names."""
    result = _run_ts("""
import { TOOL_NAME_PATTERN } from './services/mcp/scripts/yaml-config-schema.ts'

const valid = ["cohorts-create", "dashboard-get", "feature-flags-list", "a", "a1b2"]
const invalid = ["-leading", "trailing-", "UPPER-case", "has space", "has.dot", "under_score"]

const results = {
    valid: valid.map(n => ({ name: n, ok: TOOL_NAME_PATTERN.test(n) })),
    invalid: invalid.map(n => ({ name: n, ok: TOOL_NAME_PATTERN.test(n) })),
}
console.log(JSON.stringify(results))
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    for item in data["valid"]:
        assert item["ok"], f"TOOL_NAME_PATTERN should accept '{item['name']}'"
    for item in data["invalid"]:
        assert not item["ok"], f"TOOL_NAME_PATTERN should reject '{item['name']}'"


# [pr_diff] fail_to_pass
def test_feature_name_pattern_validates():
    """FEATURE_NAME_PATTERN accepts valid snake_case and rejects invalid identifiers."""
    result = _run_ts("""
import { FEATURE_NAME_PATTERN } from './services/mcp/scripts/yaml-config-schema.ts'

const valid = ["error_tracking", "feature_flags", "surveys", "abc"]
const invalid = ["1starts_digit", "HAS_UPPER", "has-hyphen", "has space"]

const results = {
    valid: valid.map(n => ({ name: n, ok: FEATURE_NAME_PATTERN.test(n) })),
    invalid: invalid.map(n => ({ name: n, ok: FEATURE_NAME_PATTERN.test(n) })),
}
console.log(JSON.stringify(results))
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    for item in data["valid"]:
        assert item["ok"], f"FEATURE_NAME_PATTERN should accept '{item['name']}'"
    for item in data["invalid"]:
        assert not item["ok"], f"FEATURE_NAME_PATTERN should reject '{item['name']}'"


# [pr_diff] fail_to_pass
def test_schema_rejects_invalid_tool_name():
    """CategoryConfigSchema rejects tool names that violate kebab-case pattern."""
    result = _run_ts("""
import { CategoryConfigSchema } from './services/mcp/scripts/yaml-config-schema.ts'

const validConfig = {
    category: "Test",
    feature: "test_feature",
    url_prefix: "/test",
    tools: {
        "valid-tool": { operation: "test_op", enabled: false }
    }
}

const invalidToolName = {
    ...validConfig,
    tools: {
        "INVALID_TOOL": { operation: "test_op", enabled: false }
    }
}

const invalidFeatureName = {
    ...validConfig,
    feature: "bad-feature",
}

const results = {
    validOk: CategoryConfigSchema.safeParse(validConfig).success,
    invalidToolOk: CategoryConfigSchema.safeParse(invalidToolName).success,
    invalidFeatureOk: CategoryConfigSchema.safeParse(invalidFeatureName).success,
}
console.log(JSON.stringify(results))
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["validOk"], "Schema should accept valid config"
    assert not data["invalidToolOk"], "Schema should reject invalid tool name (uppercase)"
    assert not data["invalidFeatureOk"], "Schema should reject invalid feature name (hyphen)"


# [pr_diff] fail_to_pass
def test_lint_validates_json_definitions():
    """lint-tool-names.ts validates JSON definition files, not just YAML."""
    lint_path = Path(REPO) / "services/mcp/scripts/lint-tool-names.ts"
    content = lint_path.read_text()
    assert "tool-definitions.json" in content, \
        "lint-tool-names.ts should validate tool-definitions.json"
    assert "tool-definitions-v2.json" in content, \
        "lint-tool-names.ts should validate tool-definitions-v2.json"
    assert "generated-tool-definitions.json" in content, \
        "lint-tool-names.ts should validate generated-tool-definitions.json"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_naming_constraints():
    """SKILL.md must document tool naming constraints with pattern and length info."""
    skill_path = Path(REPO) / ".agents/skills/implementing-mcp-tools/SKILL.md"
    content = skill_path.read_text()
    assert "naming constraints" in content.lower() or "tool naming" in content.lower(), \
        "SKILL.md should have a section about tool naming constraints"
    assert "kebab-case" in content.lower() or "[a-z0-9-]" in content, \
        "SKILL.md should document the kebab-case tool name pattern"
    assert "52" in content, \
        "SKILL.md should mention the 52-character limit"
    assert "snake_case" in content.lower() or "[a-z0-9_]" in content, \
        "SKILL.md should document feature identifier format"


# [pr_diff] fail_to_pass
def test_handbook_pattern_validation():
    """Handbook doc must document pattern validation for tool names and feature identifiers."""
    handbook_path = Path(REPO) / "docs/published/handbook/engineering/ai/implementing-mcp-tools.md"
    content = handbook_path.read_text()
    assert "[a-z0-9-]" in content or "lowercase kebab-case" in content, \
        "Handbook should document the kebab-case pattern for tool names"
    assert "snake_case" in content.lower() or "[a-z0-9_]" in content, \
        "Handbook should document feature identifier format"
    assert "feature identifier" in content.lower() or "feature name" in content.lower(), \
        "Handbook should have a section about feature identifier naming"
