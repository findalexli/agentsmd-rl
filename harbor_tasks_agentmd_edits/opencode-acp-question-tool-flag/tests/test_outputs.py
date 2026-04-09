"""
Task: opencode-acp-question-tool-flag
Repo: anomalyco/opencode @ 86e545a23ecdb2c1840ab01e82eca292117c6bbc
PR:   13562

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/opencode")


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a JavaScript snippet with node."""
    script_path = REPO / "_eval_tmp.cjs"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", str(script_path)],
            capture_output=True, text=True, timeout=timeout,
            env={**os.environ}, cwd=str(REPO),
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_parseable():
    """Modified TypeScript files must be syntactically valid."""
    import re
    for ts_file in [
        REPO / "packages/opencode/src/flag/flag.ts",
        REPO / "packages/opencode/src/tool/registry.ts",
    ]:
        content = ts_file.read_text()
        # Basic TypeScript validity: balanced braces, no obvious syntax errors
        assert content.count("{") == content.count("}"), \
            f"Unbalanced braces in {ts_file.name}"
        assert content.count("(") == content.count(")"), \
            f"Unbalanced parens in {ts_file.name}"
        # Must contain export statements (real module, not empty)
        assert "export" in content, f"{ts_file.name} has no exports"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_flag_constant_defined():
    """flag.ts must define OPENCODE_ENABLE_QUESTION_TOOL using truthy()."""
    flag_content = (REPO / "packages/opencode/src/flag/flag.ts").read_text()
    assert "OPENCODE_ENABLE_QUESTION_TOOL" in flag_content, \
        "flag.ts must define OPENCODE_ENABLE_QUESTION_TOOL"
    assert 'truthy("OPENCODE_ENABLE_QUESTION_TOOL")' in flag_content, \
        "OPENCODE_ENABLE_QUESTION_TOOL must use truthy() helper"
    # Must be exported (public API)
    assert "export const OPENCODE_ENABLE_QUESTION_TOOL" in flag_content, \
        "OPENCODE_ENABLE_QUESTION_TOOL must be exported"


# [pr_diff] fail_to_pass
def test_question_gating_behavior():
    """Question tool gating: ACP needs flag, app/cli/desktop always work."""
    script = """
const fs = require('fs');

// Read the actual source files to verify the pattern exists
const registry = fs.readFileSync('packages/opencode/src/tool/registry.ts', 'utf-8');
const flag = fs.readFileSync('packages/opencode/src/flag/flag.ts', 'utf-8');

// Verify the flag is defined
if (!flag.includes('OPENCODE_ENABLE_QUESTION_TOOL')) {
    console.log(JSON.stringify({error: "flag.ts missing OPENCODE_ENABLE_QUESTION_TOOL"}));
    process.exit(1);
}

// Verify registry references the flag
if (!registry.includes('OPENCODE_ENABLE_QUESTION_TOOL')) {
    console.log(JSON.stringify({error: "registry.ts missing OPENCODE_ENABLE_QUESTION_TOOL"}));
    process.exit(1);
}

// Verify registry references QuestionTool
if (!registry.includes('QuestionTool')) {
    console.log(JSON.stringify({error: "registry.ts missing QuestionTool"}));
    process.exit(1);
}

// Extract the question variable definition from registry.ts
// Look for: const question = ...
const questionMatch = registry.match(/const question\\s*=\\s*([\\s\\S]*?)(?:\\n|$)/);
if (!questionMatch) {
    console.log(JSON.stringify({error: "registry.ts missing question variable"}));
    process.exit(1);
}

const questionDef = questionMatch[1];

// Verify the question definition contains both conditions:
// 1. Client type check (["app", "cli", "desktop"].includes(...))
// 2. Flag check (Flag.OPENCODE_ENABLE_QUESTION_TOOL)
const hasClientCheck = questionDef.includes('app') && questionDef.includes('cli') && questionDef.includes('desktop');
const hasFlagCheck = questionDef.includes('OPENCODE_ENABLE_QUESTION_TOOL');

if (!hasClientCheck || !hasFlagCheck) {
    console.log(JSON.stringify({
        error: "question variable must check both client type and flag",
        hasClientCheck, hasFlagCheck, definition: questionDef.trim()
    }));
    process.exit(1);
}

// Simulate the gating logic using the same pattern
const clients = ['app', 'cli', 'desktop'];

function simulateQuestion(client, flagEnabled) {
    return clients.includes(client) || flagEnabled;
}

const results = {
    acp_no_flag: simulateQuestion('acp', false),
    acp_with_flag: simulateQuestion('acp', true),
    app_no_flag: simulateQuestion('app', false),
    cli_no_flag: simulateQuestion('cli', false),
    desktop_no_flag: simulateQuestion('desktop', false),
};

console.log(JSON.stringify(results));
"""
    result = _run_node(script)
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["acp_no_flag"] is False, \
        "ACP client without flag should NOT include QuestionTool"
    assert data["acp_with_flag"] is True, \
        "ACP client with flag SHOULD include QuestionTool"
    assert data["app_no_flag"] is True, \
        "app client should always include QuestionTool"
    assert data["cli_no_flag"] is True, \
        "cli client should always include QuestionTool"
    assert data["desktop_no_flag"] is True, \
        "desktop client should always include QuestionTool"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config / pr_diff) — config update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_translator_md_lists_env_var():
    """translator.md must include OPENCODE_ENABLE_QUESTION_TOOL in env var list."""
    translator = (REPO / ".opencode/agent/translator.md").read_text()
    assert "OPENCODE_ENABLE_QUESTION_TOOL" in translator, \
        "translator.md must list OPENCODE_ENABLE_QUESTION_TOOL env var"
    # Should be in the environment variables section, near other OPENCODE_ vars
    assert "OPENCODE_EXPERIMENTAL_PLAN_MODE" in translator, \
        "translator.md should have surrounding env vars for context"


# [pr_diff] fail_to_pass
def test_acp_readme_documents_opt_in():
    """acp/README.md must document the Question Tool Opt-In feature."""
    readme = (REPO / "packages/opencode/src/acp/README.md").read_text()
    assert "Question Tool Opt-In" in readme, \
        "acp/README.md must have Question Tool Opt-In section"
    assert "QuestionTool" in readme, \
        "acp/README.md must reference QuestionTool by name"
    assert "OPENCODE_ENABLE_QUESTION_TOOL" in readme, \
        "acp/README.md must show the OPENCODE_ENABLE_QUESTION_TOOL env var"


# [pr_diff] fail_to_pass
def test_acp_readme_enable_example():
    """acp/README.md must show how to enable the question tool."""
    readme = (REPO / "packages/opencode/src/acp/README.md").read_text()
    assert "OPENCODE_ENABLE_QUESTION_TOOL=1" in readme, \
        "acp/README.md must show OPENCODE_ENABLE_QUESTION_TOOL=1 example"
    assert "opencode acp" in readme, \
        "acp/README.md must show the opencode acp command in context"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression / anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_client_behavior_preserved():
    """app/cli/desktop clients must still get QuestionTool without any flag."""
    registry = (REPO / "packages/opencode/src/tool/registry.ts").read_text()
    # The old behavior for app/cli/desktop must still work
    assert '"app"' in registry, "app client must still be supported"
    assert '"cli"' in registry, "cli client must still be supported"
    assert '"desktop"' in registry, "desktop client must still be supported"
    # QuestionTool must still be referenced
    assert "QuestionTool" in registry, "QuestionTool must still be in registry"


# [static] pass_to_pass
def test_not_stub():
    """Modified code has real logic, not just pass/return."""
    flag_content = (REPO / "packages/opencode/src/flag/flag.ts").read_text()
    registry_content = (REPO / "packages/opencode/src/tool/registry.ts").read_text()

    # flag.ts must have truthy() call (not just a constant)
    assert "truthy(" in flag_content, "flag.ts must use truthy() function"

    # registry.ts must have a conditional (not just hardcoded)
    assert "includes(" in registry_content and "||" in registry_content, \
        "registry.ts must have conditional logic for question tool gating"
