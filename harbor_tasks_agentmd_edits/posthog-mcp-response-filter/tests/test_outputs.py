"""
Task: posthog-mcp-response-filter
Repo: PostHog/posthog @ 631f99184cf89fc8eef5163938c1a796a0e4af1b
PR:   53198

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/posthog"


def _run_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a TypeScript snippet via node --experimental-strip-types."""
    script_path = Path(REPO) / "services" / "mcp" / "_eval_tmp.mts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path(REPO) / "services" / "mcp",
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static, repo_tests)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_mcp_typecheck():
    """MCP service TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # pnpm install deps and run typecheck
    r = subprocess.run(
        ["pnpm", "install"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "typecheck"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/services/mcp",
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_mcp_unit_tests_generate_tools():
    """MCP generate-tools unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    r = subprocess.run(
        ["pnpm", "install"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "test", "--", "--run", "tests/unit/generate-tools.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/services/mcp",
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_mcp_unit_tests_tool_filtering():
    """MCP tool-filtering unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    r = subprocess.run(
        ["pnpm", "install"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "test", "--", "--run", "tests/unit/tool-filtering.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/services/mcp",
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_mcp_lint_tool_names():
    """MCP tool name linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    r = subprocess.run(
        ["pnpm", "install"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "lint-tool-names"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/services/mcp",
    )
    assert r.returncode == 0, f"Tool name lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_mcp_lint():
    """MCP oxlint passes with no errors (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    r = subprocess.run(
        ["pnpm", "install"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "format"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/services/mcp",
    )
    assert r.returncode == 0, f"Lint/format failed:\n{r.stderr[-500:]}"


# [static] pass_to_pass
def test_tool_utils_parseable():
    """tool-utils.ts must be valid TypeScript that node can load."""
    r = _run_ts(
        "import './src/tools/tool-utils.ts'\n"
        "console.log('OK')\n"
    )
    assert r.returncode == 0, f"tool-utils.ts failed to load: {r.stderr}"
    assert "OK" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — runtime helper behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_pick_response_fields_top_level():
    """pickResponseFields keeps only specified top-level fields."""
    r = _run_ts("""
import { pickResponseFields } from './src/tools/tool-utils.ts'

const obj = { id: 1, name: 'test', filters: { a: 1 }, created_by: 'user' }
const result = pickResponseFields(obj, ['id', 'name'])
console.log(JSON.stringify(result))
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data == {"id": 1, "name": "test"}, f"Expected {{id:1, name:'test'}}, got: {data}"


# [pr_diff] fail_to_pass
def test_pick_response_fields_wildcard():
    """pickResponseFields supports wildcard dot-path patterns on arrays."""
    r = _run_ts("""
import { pickResponseFields } from './src/tools/tool-utils.ts'

const obj = {
    groups: [
        { key: 'a', properties: [1, 2], extra: 'x' },
        { key: 'b', properties: [3], extra: 'y' },
    ],
}
const result = pickResponseFields(obj, ['groups.*.key'])
console.log(JSON.stringify(result))
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data == {"groups": [{"key": "a"}, {"key": "b"}]}, f"Got: {data}"


# [pr_diff] fail_to_pass
def test_omit_response_fields_top_level():
    """omitResponseFields removes specified top-level fields."""
    r = _run_ts("""
import { omitResponseFields } from './src/tools/tool-utils.ts'

const obj = { id: 1, name: 'test', filters: { a: 1 }, created_by: 'user' }
const result = omitResponseFields(obj, ['filters', 'created_by'])
console.log(JSON.stringify(result))
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data == {"id": 1, "name": "test"}, f"Expected {{id:1, name:'test'}}, got: {data}"


# [pr_diff] fail_to_pass
def test_omit_response_fields_wildcard():
    """omitResponseFields supports wildcard dot-path patterns on arrays."""
    r = _run_ts("""
import { omitResponseFields } from './src/tools/tool-utils.ts'

const obj = {
    groups: [
        { key: 'a', properties: [1, 2], extra: 'x' },
        { key: 'b', properties: [3], extra: 'y' },
    ],
}
const result = omitResponseFields(obj, ['groups.*.properties'])
console.log(JSON.stringify(result))
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data == {
        "groups": [
            {"key": "a", "extra": "x"},
            {"key": "b", "extra": "y"},
        ]
    }, f"Got: {data}"


# [pr_diff] fail_to_pass — BEHAVIORAL: actually execute Zod schema validation
def test_response_schema_validates_include_exclude():
    """Zod schema validates response config with include/exclude mutual exclusivity."""
    # Test that the schema properly validates response configuration
    r = _run_ts("""
import { ToolConfigSchema } from './scripts/yaml-config-schema.ts'

// Test 1: Valid config with include only
const validInclude = ToolConfigSchema.parse({
    operation: 'test_op',
    enabled: true,
    response: { include: ['id', 'key', 'name'] }
})
console.log('Test1:', JSON.stringify(validInclude.response))

// Test 2: Valid config with exclude only
const validExclude = ToolConfigSchema.parse({
    operation: 'test_op',
    enabled: true,
    response: { exclude: ['filters.groups.*.properties'] }
})
console.log('Test2:', JSON.stringify(validExclude.response))

// Test 3: Invalid config with both include and exclude should fail
let caught = false
try {
    ToolConfigSchema.parse({
        operation: 'test_op',
        enabled: true,
        response: { include: ['id'], exclude: ['name'] }
    })
} catch (e) {
    caught = true
    console.log('Test3: Caught mutual exclusivity error')
}

// Test 4: Config without response is valid
const noResponse = ToolConfigSchema.parse({
    operation: 'test_op',
    enabled: true
})
console.log('Test4:', noResponse.response === undefined ? 'undefined' : 'present')

console.log('All schema tests passed:', caught)
""")
    assert r.returncode == 0, f"Schema validation failed: {r.stderr}"
    output = r.stdout.strip()
    assert "Test1:" in output, "Schema should accept include-only response config"
    assert "Test2:" in output, "Schema should accept exclude-only response config"
    assert "Test3: Caught" in output, "Schema should reject mutually exclusive include+exclude"
    assert "Test4: undefined" in output, "Schema should allow missing response config"
    assert "All schema tests passed: true" in output, "Mutual exclusivity check should have caught error"


# [pr_diff] fail_to_pass — Verify buildResponseFilter function exists and is correct
def test_build_response_filter_generates_correct_code():
    """buildResponseFilter function exists in generate-tools.ts with correct implementation."""
    generate_tools_path = Path(REPO) / "services" / "mcp" / "scripts" / "generate-tools.ts"
    full_content = generate_tools_path.read_text()

    # Verify buildResponseFilter function exists and is exported
    assert "function buildResponseFilter" in full_content,         "generate-tools.ts must have buildResponseFilter function"
    assert "export {" in full_content and "buildResponseFilter" in full_content,         "buildResponseFilter must be exported"

    # Find the function start and its opening brace (skip return type annotation)
    func_sig = "function buildResponseFilter(config: ToolConfig):"
    func_start = full_content.find(func_sig)
    assert func_start != -1, f"buildResponseFilter function signature not found: {func_sig}"

    # Find first opening brace after function signature (return type)
    first_brace = full_content.find("{", func_start)
    # Find second opening brace (actual function body)
    func_body_start = full_content.find("{", first_brace + 1)
    assert func_body_start != -1, "Could not find function body opening brace"

    # Extract function body by counting braces
    brace_count = 1
    pos = func_body_start + 1
    while brace_count > 0 and pos < len(full_content):
        if full_content[pos] == '{':
            brace_count += 1
        elif full_content[pos] == '}':
            brace_count -= 1
        pos += 1
    func_body = full_content[func_body_start:pos]

    # Verify include handling with pickResponseFields
    assert "config.response?.include" in func_body,         "buildResponseFilter must check config.response.include"
    assert "pickResponseFields" in func_body,         "buildResponseFilter must use pickResponseFields for include"
    assert "helperImport: 'pickResponseFields'" in func_body,         "buildResponseFilter must return pickResponseFields helper for include"

    # Verify exclude handling with omitResponseFields
    assert "config.response?.exclude" in func_body,         "buildResponseFilter must check config.response.exclude"
    assert "omitResponseFields" in func_body,         "buildResponseFilter must use omitResponseFields for exclude"
    assert "helperImport: 'omitResponseFields'" in func_body,         "buildResponseFilter must return omitResponseFields helper for exclude"

    # Verify empty/default return for no response config
    assert "code: ''" in func_body or 'code: ""' in func_body,         "buildResponseFilter must return empty code when no response config"
    assert "helperImport: null" in func_body,         "buildResponseFilter must return null helperImport when no response config"

    # Verify list endpoint handling with .map
    assert "config.list" in func_body,         "buildResponseFilter must check config.list for list endpoints"
    assert ".map" in func_body,         "buildResponseFilter must use .map for list endpoints"
    assert "results" in func_body,         "buildResponseFilter must reference results for list endpoints"


# [pr_diff] fail_to_pass
def test_feature_flags_yaml_response_include():
    """Feature flags tools.yaml must have response.include for get-all."""
    yaml_path = Path(REPO) / "products" / "feature_flags" / "mcp" / "tools.yaml"
    content = yaml_path.read_text()
    assert "response:" in content, \
        "tools.yaml must have a response config section"
    assert "include:" in content, \
        "tools.yaml response must use include filtering"
    for field in ["id", "key", "name", "status"]:
        assert field in content.split("response:")[1].split("feature-flag-get-definition")[0], \
            f"response.include must contain '{field}'"


# ---------------------------------------------------------------------------
# Fail-to-pass — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_documents_response_config():
    """implementing-mcp-tools SKILL.md must document the response config."""
    skill_path = (
        Path(REPO) / ".agents" / "skills" / "implementing-mcp-tools" / "SKILL.md"
    )
    content = skill_path.read_text()
    assert "response" in content.lower(), \
        "SKILL.md must mention response filtering"
    # Must document both include and exclude as options
    content_lower = content.lower()
    assert "include" in content_lower and "exclude" in content_lower, \
        "SKILL.md must document both include and exclude options"
    # Must mention dot-path or wildcard support
    assert "wildcard" in content_lower or "dot-path" in content_lower or "*" in content, \
        "SKILL.md must document wildcard/dot-path pattern support"


# [pr_diff] fail_to_pass
def test_definitions_readme_documents_response():
    """services/mcp/definitions/README.md must document response filtering."""
    readme_path = Path(REPO) / "services" / "mcp" / "definitions" / "README.md"
    content = readme_path.read_text()
    assert "response:" in content or "response" in content.lower(), \
        "definitions/README.md must mention response filtering"
    content_lower = content.lower()
    assert "include" in content_lower and "exclude" in content_lower, \
        "definitions/README.md must document both include and exclude"


# ---------------------------------------------------------------------------
# Pass-to-pass (static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_with_posthog_url_export():
    """Existing withPostHogUrl export must still be present."""
    tool_utils_path = Path(REPO) / "services" / "mcp" / "src" / "tools" / "tool-utils.ts"
    content = tool_utils_path.read_text()
    assert "export async function withPostHogUrl" in content or \
           "export function withPostHogUrl" in content, \
        "withPostHogUrl export must be preserved"


# [agent_config] pass_to_pass — .agents/skills/implementing-mcp-tools/SKILL.md:144
def test_response_schema_uses_strict():
    """Response schema object must use .strict() per SKILL.md validation rule."""
    schema_path = Path(REPO) / "services" / "mcp" / "scripts" / "yaml-config-schema.ts"
    content = schema_path.read_text()
    # If response schema exists, it must use strict()
    if "response:" not in content and "response: z" not in content:
        return  # response field not yet added — nothing to validate
    # Find the response schema block and verify it has .strict()
    response_idx = content.find("response:")
    if response_idx == -1:
        response_idx = content.find("response: z")
    # Look at the next 500 chars after 'response' for .strict()
    block = content[response_idx:response_idx + 500]
    assert ".strict()" in block, \
        "response schema object must use .strict() — SKILL.md says 'Unknown keys are rejected at build time (Zod .strict())'"
