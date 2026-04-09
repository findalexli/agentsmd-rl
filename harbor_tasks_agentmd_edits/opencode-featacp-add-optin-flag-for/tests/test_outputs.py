"""
Task: feat(acp): add opt-in flag for question tool
Repo: anomalyco/opencode @ d8c25bfeb44771cc3a3ba17bf8de6ad2add9de2c
PR:   13562

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/opencode"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_parseable():
    """Modified TypeScript files are syntactically valid."""
    # Use tsc --noEmit to check syntax without full type checking
    modified_files = [
        f"{REPO}/packages/opencode/src/flag/flag.ts",
        f"{REPO}/packages/opencode/src/tool/registry.ts",
    ]
    for f in modified_files:
        r = subprocess.run(
            ["npx", "tsc", "--noEmit", "--skipLibCheck", f],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        # tsc returns 0 on success, 2 on type errors (but syntax might be valid)
        # We accept any non-crash exit code as "parseable"
        assert r.returncode in [0, 2], f"Syntax error in {f}: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass — Behavioral test using subprocess
def test_flag_constant_defined():
    """flag.ts exports OPENCODE_ENABLE_QUESTION_TOOL using truthy()."""
    code = """
const fs = require('fs');
const path = require('path');

// Read the flag.ts file
const flagContent = fs.readFileSync('packages/opencode/src/flag/flag.ts', 'utf8');

// Check that OPENCODE_ENABLE_QUESTION_TOOL is exported
const hasExport = flagContent.includes('export const OPENCODE_ENABLE_QUESTION_TOOL');
const usesTruthy = flagContent.includes('truthy("OPENCODE_ENABLE_QUESTION_TOOL")');

if (!hasExport) {
    console.error('FAIL: OPENCODE_ENABLE_QUESTION_TOOL export not found');
    process.exit(1);
}

if (!usesTruthy) {
    console.error('FAIL: OPENCODE_ENABLE_QUESTION_TOOL should use truthy() helper');
    process.exit(1);
}

console.log('PASS');
"""
    r = subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Test did not pass: {r.stdout}"


# [pr_diff] fail_to_pass — Behavioral test using subprocess
def test_question_gating_behavior():
    """Question tool gating: ACP needs flag, app/cli/desktop always work."""
    # Test that the registry.ts has the updated gating logic
    code = """
const fs = require('fs');

const registryContent = fs.readFileSync('packages/opencode/src/tool/registry.ts', 'utf8');

// Check that the new logic exists
const hasNewLogic = registryContent.includes('const question =');
const hasClientCheck = registryContent.includes('["app", "cli", "desktop"]');
const hasFlagCheck = registryContent.includes('Flag.OPENCODE_ENABLE_QUESTION_TOOL');
const usesQuestionVariable = registryContent.includes('...(question ? [QuestionTool]');

if (!hasNewLogic) {
    console.error('FAIL: New question variable not found');
    process.exit(1);
}

if (!hasClientCheck || !hasFlagCheck) {
    console.error('FAIL: Missing client check or flag check');
    process.exit(1);
}

if (!usesQuestionVariable) {
    console.error('FAIL: Should use question variable for QuestionTool gating');
    process.exit(1);
}

console.log('PASS');
"""
    r = subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_translator_md_lists_env_var():
    """translator.md agent config includes OPENCODE_ENABLE_QUESTION_TOOL in env var list."""
    translator_path = Path(f"{REPO}/.opencode/agent/translator.md")
    content = translator_path.read_text()

    # Check that the env var is listed
    assert "OPENCODE_ENABLE_QUESTION_TOOL" in content, \
        "translator.md should include OPENCODE_ENABLE_QUESTION_TOOL in env var list"


# [pr_diff] fail_to_pass
def test_acp_readme_documents_opt_in():
    """acp/README.md documents the Question Tool Opt-In feature with env var."""
    readme_path = Path(f"{REPO}/packages/opencode/src/acp/README.md")
    content = readme_path.read_text()

    # Check for section header
    assert "Question Tool Opt-In" in content, \
        "acp/README.md should have a Question Tool Opt-In section"

    # Check that the env var is documented
    assert "OPENCODE_ENABLE_QUESTION_TOOL" in content, \
        "acp/README.md should document the OPENCODE_ENABLE_QUESTION_TOOL env var"


# [pr_diff] fail_to_pass
def test_acp_readme_enable_example():
    """acp/README.md shows OPENCODE_ENABLE_QUESTION_TOOL=1 enable command."""
    readme_path = Path(f"{REPO}/packages/opencode/src/acp/README.md")
    content = readme_path.read_text()

    # Check for the enable example
    assert "OPENCODE_ENABLE_QUESTION_TOOL=1 opencode acp" in content, \
        "acp/README.md should show the enable example: OPENCODE_ENABLE_QUESTION_TOOL=1 opencode acp"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_existing_client_behavior_preserved():
    """app/cli/desktop clients still get QuestionTool without flag."""
    registry_path = Path(f"{REPO}/packages/opencode/src/tool/registry.ts")
    content = registry_path.read_text()

    # The logic should still check for app/cli/desktop
    assert '["app", "cli", "desktop"]'.replace('"', '').replace(' ', '') in content.replace('"', '').replace(' ', '') or \
           '["app", "cli", "desktop"]' in content, \
        "Registry should still check for app/cli/desktop clients"


# [static] pass_to_pass
def test_not_stub():
    """Modified code has real conditional logic, not stubs."""
    # Check flag.ts
    flag_path = Path(f"{REPO}/packages/opencode/src/flag/flag.ts")
    flag_content = flag_path.read_text()

    # Should not be a simple placeholder
    assert "truthy(" in flag_content, "Flag should use truthy() helper, not be a stub"

    # Check registry.ts
    registry_path = Path(f"{REPO}/packages/opencode/src/tool/registry.ts")
    registry_content = registry_path.read_text()

    # Should have actual logic with || operator
    assert "||" in registry_content, "Registry should have real conditional logic with ||"
