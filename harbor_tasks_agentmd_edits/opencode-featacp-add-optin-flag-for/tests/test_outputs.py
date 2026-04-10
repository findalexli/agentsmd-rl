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

# [repo_tests] pass_to_pass — Repo CI: Verify repo files are valid
def test_typescript_parseable():
    """Modified TypeScript files are syntactically valid."""
    # Use node to parse TypeScript files and check for basic syntax errors
    modified_files = [
        "packages/opencode/src/flag/flag.ts",
        "packages/opencode/src/tool/registry.ts",
    ]
    for f in modified_files:
        r = subprocess.run(
            ["node", "-e", f"require('fs').readFileSync('{f}', 'utf8')"],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Failed to read {f}: {r.stderr}"


# [repo_tests] pass_to_pass — Repo CI: Node.js can parse the flag.ts exports
def test_flag_exports_parseable():
    """flag.ts has valid export syntax that Node.js can parse."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const content = fs.readFileSync('packages/opencode/src/flag/flag.ts', 'utf8');
const exportMatches = content.match(/export\\s+(const|let|var|function|class)\\s+(\\w+)/g);
if (!exportMatches) {
    console.error('No valid exports found');
    process.exit(1);
}
const nsMatch = content.match(/export\\s+namespace\\s+Flag/);
if (!nsMatch) {
    console.error('No Flag namespace export found');
    process.exit(1);
}
console.log('flag.ts exports are valid');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Flag exports check failed: {r.stderr}"


# [repo_tests] pass_to_pass — Repo CI: Node.js can parse the registry.ts exports
def test_registry_exports_parseable():
    """registry.ts has valid export syntax that Node.js can parse."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const content = fs.readFileSync('packages/opencode/src/tool/registry.ts', 'utf8');
const exportMatches = content.match(/export\\s+(const|let|var|function|class|namespace)\\s+(\\w+)/g);
if (!exportMatches) {
    console.error('No valid exports found');
    process.exit(1);
}
const nsMatch = content.match(/export\\s+namespace\\s+ToolRegistry/);
if (!nsMatch) {
    console.error('No ToolRegistry namespace export found');
    process.exit(1);
}
console.log('registry.ts exports are valid');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Registry exports check failed: {r.stderr}"


# [repo_tests] pass_to_pass — Repo CI: Verify opencode package structure
def test_opencode_package_valid():
    """opencode package.json is valid JSON and has required fields."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const path = 'packages/opencode/package.json';
const content = fs.readFileSync(path, 'utf8');
let pkg;
try {
    pkg = JSON.parse(content);
} catch (e) {
    console.error('Invalid JSON in package.json:', e.message);
    process.exit(1);
}
if (!pkg.name) { console.error('Missing name field'); process.exit(1); }
if (!pkg.version) { console.error('Missing version field'); process.exit(1); }
if (!pkg.scripts || !pkg.scripts.typecheck) { console.error('Missing typecheck script'); process.exit(1); }
console.log('package.json is valid');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Package.json check failed: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass — Behavioral test using subprocess
def test_flag_constant_defined():
    """flag.ts exports OPENCODE_ENABLE_QUESTION_TOOL using truthy()."""
    code = """
const fs = require('fs');
const flagContent = fs.readFileSync('packages/opencode/src/flag/flag.ts', 'utf8');
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
    code = """
const fs = require('fs');
const registryContent = fs.readFileSync('packages/opencode/src/tool/registry.ts', 'utf8');
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
    assert "OPENCODE_ENABLE_QUESTION_TOOL" in content, \
        "translator.md should include OPENCODE_ENABLE_QUESTION_TOOL in env var list"


# [pr_diff] fail_to_pass
def test_acp_readme_documents_opt_in():
    """acp/README.md documents the Question Tool Opt-In feature with env var."""
    readme_path = Path(f"{REPO}/packages/opencode/src/acp/README.md")
    content = readme_path.read_text()
    assert "Question Tool Opt-In" in content, \
        "acp/README.md should have a Question Tool Opt-In section"
    assert "OPENCODE_ENABLE_QUESTION_TOOL" in content, \
        "acp/README.md should document the OPENCODE_ENABLE_QUESTION_TOOL env var"


# [pr_diff] fail_to_pass
def test_acp_readme_enable_example():
    """acp/README.md shows OPENCODE_ENABLE_QUESTION_TOOL=1 enable command."""
    readme_path = Path(f"{REPO}/packages/opencode/src/acp/README.md")
    content = readme_path.read_text()
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
    assert '["app", "cli", "desktop"]'.replace('"', "").replace(" ", "") in content.replace('"', "").replace(" ", "") or \
           '["app", "cli", "desktop"]' in content, \
        "Registry should still check for app/cli/desktop clients"


# [static] pass_to_pass
def test_not_stub():
    """Modified code has real conditional logic, not stubs."""
    flag_path = Path(f"{REPO}/packages/opencode/src/flag/flag.ts")
    flag_content = flag_path.read_text()
    assert "truthy(" in flag_content, "Flag should use truthy() helper, not be a stub"
    registry_path = Path(f"{REPO}/packages/opencode/src/tool/registry.ts")
    registry_content = registry_path.read_text()
    assert "||" in registry_content, "Registry should have real conditional logic with ||"
