"""
Task: posthog-mcp-tool-name-validation
Repo: PostHog/posthog @ 2f7a8ee722e5d451dd2c242c722ea818cc325485
PR:   51937

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import shutil
from pathlib import Path

REPO = "/workspace/posthog"


def _ensure_deps():
    """Ensure pnpm is available and dependencies are installed."""
    # Install pnpm if not available
    if not shutil.which("pnpm"):
        r = subprocess.run(["npm", "install", "-g", "pnpm"], capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            raise RuntimeError(f"Failed to install pnpm: {r.stderr}")

    # Check if node_modules exists
    if not (Path(REPO) / "node_modules").exists():
        # Install dependencies
        r = subprocess.run(
            ["pnpm", "--filter=@posthog/mcp...", "--filter=./products/*", "install", "--frozen-lockfile"],
            capture_output=True, text=True, timeout=300, cwd=REPO,
        )
        if r.returncode != 0:
            raise RuntimeError(f"Failed to install dependencies: {r.stderr[-500:]}")


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
    _ensure_deps()
    r = subprocess.run(
        ["pnpm", "typecheck"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/services/mcp",
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


def test_repo_lint_tool_names():
    """MCP tool name linting passes (pass_to_pass)."""
    _ensure_deps()
    r = subprocess.run(
        ["pnpm", "lint-tool-names"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/services/mcp",
    )
    assert r.returncode == 0, f"Lint tool names failed:\n{r.stderr[-500:]}"


def test_repo_unit_tests():
    """MCP unit tests pass (pass_to_pass)."""
    _ensure_deps()
    r = subprocess.run(
        ["pnpm", "test", "run"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/services/mcp",
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"


def test_repo_build():
    """MCP package build passes (pass_to_pass)."""
    _ensure_deps()
    r = subprocess.run(
        ["pnpm", "build"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/services/mcp",
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


def test_repo_format():
    """MCP package formatting and linting passes (pass_to_pass)."""
    _ensure_deps()
    r = subprocess.run(
        ["pnpm", "format"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/services/mcp",
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


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
    """CategoryConfigSchema rejects invalid tool name keys via regex validation."""
    # Test with an invalid tool name (uppercase) - should fail Zod validation
    r = _run_node("""
import { CategoryConfigSchema } from './services/mcp/scripts/yaml-config-schema.ts';

// Valid kebab-case key should work
try {
    const valid = CategoryConfigSchema.parse({
        category: 'test',
        feature: 'test',
        url_prefix: 'https://example.com',
        tools: { 'valid-tool-name': { enabled: true, scopes: [] } }
    });
    process.stdout.write('valid_ok');
} catch (e) {
    process.stderr.write('Valid key unexpectedly rejected: ' + e.message);
    process.exit(1);
}

// Invalid uppercase key should be rejected
try {
    CategoryConfigSchema.parse({
        category: 'test',
        feature: 'test',
        url_prefix: 'https://example.com',
        tools: { 'INVALID_TOOL': { enabled: true, scopes: [] } }
    });
    process.stderr.write('Invalid key unexpectedly accepted');
    process.exit(1);
} catch (e) {
    if (e.message.includes('kebab') || e.message.includes('pattern') || e.message.includes('regex')) {
        process.stdout.write('invalid_rejected_ok');
    } else {
        process.stderr.write('Wrong error: ' + e.message);
        process.exit(1);
    }
}
""")
    assert r.returncode == 0, f"Schema validation test failed: {r.stderr}"
    assert "valid_ok" in r.stdout, "Valid tool name key should be accepted"
    assert "invalid_rejected_ok" in r.stdout, "Invalid tool name key should be rejected"


def test_zod_schema_validates_feature_field():
    """CategoryConfigSchema rejects invalid feature field values via regex validation."""
    r = _run_node("""
import { CategoryConfigSchema } from './services/mcp/scripts/yaml-config-schema.ts';

// Valid snake_case feature should work
try {
    CategoryConfigSchema.parse({
        category: 'test',
        feature: 'valid_feature',
        url_prefix: 'https://example.com',
        tools: { 'valid-tool': { enabled: true, scopes: [] } }
    });
    process.stdout.write('valid_ok');
} catch (e) {
    process.stderr.write('Valid feature unexpectedly rejected: ' + e.message);
    process.exit(1);
}

// Invalid feature (uppercase) should be rejected
try {
    CategoryConfigSchema.parse({
        category: 'test',
        feature: 'INVALID_FEATURE',
        url_prefix: 'https://example.com',
        tools: { 'valid-tool': { enabled: true, scopes: [] } }
    });
    process.stderr.write('Invalid feature unexpectedly accepted');
    process.exit(1);
} catch (e) {
    if (e.message.includes('snake') || e.message.includes('pattern') || e.message.includes('regex') || e.message.includes('feature')) {
        process.stdout.write('invalid_rejected_ok');
    } else {
        process.stderr.write('Wrong error: ' + e.message);
        process.exit(1);
    }
}
""")
    assert r.returncode == 0, f"Schema validation test failed: {r.stderr}"
    assert "valid_ok" in r.stdout, "Valid feature field should be accepted"
    assert "invalid_rejected_ok" in r.stdout, "Invalid feature field should be rejected"


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
    # Verify the test checks pattern and length for tool names
    # The test should import pattern-related exports and check them
    content_lower = content.lower()
    assert "pattern" in content_lower or "regex" in content_lower, \
        "Test must check pattern validation for tool names"
    assert "map" in content_lower, "Test must validate TOOL_MAP or GENERATED_TOOL_MAP"
    assert "length" in content_lower, "Test must check length constraint"


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