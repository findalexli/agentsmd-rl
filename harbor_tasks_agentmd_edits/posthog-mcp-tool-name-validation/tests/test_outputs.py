"""
Task: posthog-mcp-tool-name-validation
Repo: PostHog/posthog @ 2f7a8ee722e5d451dd2c242c722ea818cc325485
PR:   51937

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/posthog"


def _read(relpath: str) -> str:
    return (Path(REPO) / relpath).read_text()


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


def test_syntax_check():
    """Modified TypeScript files have balanced braces."""
    for relpath in [
        "services/mcp/scripts/yaml-config-schema.ts",
        "services/mcp/scripts/lint-tool-names.ts",
    ]:
        content = _read(relpath)
        assert content.count("{") == content.count("}"), f"Unbalanced braces in {relpath}"
        assert content.count("(") == content.count(")"), f"Unbalanced parens in {relpath}"


def test_repo_typecheck():
    """MCP package TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "typecheck"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/services/mcp",
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


def test_repo_lint_tool_names():
    """MCP tool name linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "lint-tool-names"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/services/mcp",
    )
    assert r.returncode == 0, f"Lint tool names failed:\n{r.stderr[-500:]}"


def test_repo_unit_tests():
    """MCP unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "test", "run"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/services/mcp",
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_tool_name_pattern_validation():
    """TOOL_NAME_PATTERN regex correctly validates tool names in Node.js runtime."""
    r = _run_node("""
import { readFileSync } from 'node:fs';

const content = readFileSync('services/mcp/scripts/yaml-config-schema.ts', 'utf-8');

// Find the TOOL_NAME_PATTERN line and extract the regex between slashes
const lines = content.split('\\n');
const patLine = lines.find(l => l.includes('TOOL_NAME_PATTERN') && l.includes('= /'));
if (!patLine) { process.stderr.write('TOOL_NAME_PATTERN not found'); process.exit(1); }
const first = patLine.indexOf('= /') + 3;
const last = patLine.lastIndexOf('/');
const pat = new RegExp(patLine.slice(first, last));

const results = {};

// Must accept valid lowercase kebab-case
for (const name of ['cohorts-create', 'feature-flags-list', 'a', 'a1', 'dashboard-get']) {
    results[name] = pat.test(name);
}
// Must reject invalid names
for (const name of ['-leading', 'trailing-', 'UPPERCASE', 'has space', 'under_score']) {
    results[name] = pat.test(name);
}

process.stdout.write(JSON.stringify(results));
""")
    assert r.returncode == 0, f"Node execution failed: {r.stderr}"
    data = json.loads(r.stdout.strip())

    for name in ["cohorts-create", "feature-flags-list", "a", "a1", "dashboard-get"]:
        assert data[name] is True, f"TOOL_NAME_PATTERN should accept '{name}'"
    for name in ["-leading", "trailing-", "UPPERCASE", "has space", "under_score"]:
        assert data[name] is False, f"TOOL_NAME_PATTERN should reject '{name}'"


def test_feature_name_pattern_validation():
    """FEATURE_NAME_PATTERN regex correctly validates feature names in Node.js runtime."""
    r = _run_node("""
import { readFileSync } from 'node:fs';

const content = readFileSync('services/mcp/scripts/yaml-config-schema.ts', 'utf-8');

const lines = content.split('\\n');
const patLine = lines.find(l => l.includes('FEATURE_NAME_PATTERN') && l.includes('= /'));
if (!patLine) { process.stderr.write('FEATURE_NAME_PATTERN not found'); process.exit(1); }
const first = patLine.indexOf('= /') + 3;
const last = patLine.lastIndexOf('/');
const pat = new RegExp(patLine.slice(first, last));

const results = {};

for (const name of ['error_tracking', 'feature_flags', 'surveys', 'a']) {
    results[name] = pat.test(name);
}
for (const name of ['_leading', '1starts_with_digit', 'UPPER', 'kebab-case']) {
    results[name] = pat.test(name);
}

process.stdout.write(JSON.stringify(results));
""")
    assert r.returncode == 0, f"Node execution failed: {r.stderr}"
    data = json.loads(r.stdout.strip())

    for name in ["error_tracking", "feature_flags", "surveys", "a"]:
        assert data[name] is True, f"FEATURE_NAME_PATTERN should accept '{name}'"
    for name in ["_leading", "1starts_with_digit", "UPPER", "kebab-case"]:
        assert data[name] is False, f"FEATURE_NAME_PATTERN should reject '{name}'"


def test_zod_schema_validates_tool_name_keys():
    """CategoryConfigSchema uses regex validation on tool name record keys."""
    content = _read("services/mcp/scripts/yaml-config-schema.ts")
    schema_section = content[content.index("CategoryConfigSchema"):]
    assert ".regex(" in schema_section, \
        "CategoryConfigSchema must use .regex() validation on tool name keys"
    assert "TOOL_NAME_PATTERN" in schema_section, \
        "CategoryConfigSchema must reference TOOL_NAME_PATTERN for tool key validation"


def test_zod_schema_validates_feature_field():
    """CategoryConfigSchema uses regex validation on the feature field."""
    content = _read("services/mcp/scripts/yaml-config-schema.ts")
    schema_section = content[content.index("CategoryConfigSchema"):]
    assert "FEATURE_NAME_PATTERN" in schema_section, \
        "CategoryConfigSchema must reference FEATURE_NAME_PATTERN for feature field validation"


def test_lint_validates_json_definitions():
    """lint-tool-names.ts validates JSON definition files, not just YAML."""
    content = _read("services/mcp/scripts/lint-tool-names.ts")
    assert "tool-definitions.json" in content, \
        "Linter must validate handwritten tool-definitions.json"
    assert "tool-definitions-v2.json" in content, \
        "Linter must validate handwritten tool-definitions-v2.json"
    assert "generated-tool-definitions.json" in content, \
        "Linter must validate generated-tool-definitions.json"


def test_lint_uses_pattern_validation():
    """lint-tool-names.ts imports and uses TOOL_NAME_PATTERN for pattern checks."""
    content = _read("services/mcp/scripts/lint-tool-names.ts")
    assert "TOOL_NAME_PATTERN" in content, \
        "Linter must import TOOL_NAME_PATTERN"
    assert "validateToolName" in content or "TOOL_NAME_PATTERN.test" in content, \
        "Linter must use TOOL_NAME_PATTERN for validation"


def test_vitest_file_created():
    """A vitest test file validates runtime TOOL_MAP entries against name constraints."""
    test_file = Path(REPO) / "services/mcp/tests/unit/tool-name-validation.test.ts"
    content = test_file.read_text()
    assert "TOOL_NAME_PATTERN" in content, "Test must reference TOOL_NAME_PATTERN"
    assert "TOOL_MAP" in content, "Test must validate entries from TOOL_MAP"
    assert "MAX_TOOL_NAME_LENGTH" in content, "Test must check length constraint"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — documentation updates
# ---------------------------------------------------------------------------


def test_skill_md_documents_naming():
    """SKILL.md documents tool naming constraints including format, length, and client compat."""
    content = _read(".agents/skills/implementing-mcp-tools/SKILL.md")
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


def test_handbook_documents_feature_naming():
    """Handbook page documents feature identifier naming and pattern validation."""
    content = _read("docs/published/handbook/engineering/ai/implementing-mcp-tools.md")
    content_lower = content.lower()

    assert "feature identifier" in content_lower or "feature identifiers" in content_lower, \
        "Handbook must document feature identifier naming"
    assert "snake_case" in content_lower or "snake case" in content_lower, \
        "Handbook must specify snake_case format for feature identifiers"
    assert "pattern" in content_lower or "[a-z0-9" in content, \
        "Handbook must document the character pattern validation"
