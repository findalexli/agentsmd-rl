"""
Task: vscode-merge-extensionprovided-policy
Repo: microsoft/vscode @ 4eab4042e5814c2921da2d236ef73086dc5629d0
PR:   306874

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
from pathlib import Path

REPO = "/workspace/vscode"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Pre-existing TypeScript files still have valid structure."""
    contrib = Path(REPO) / "src/vs/workbench/contrib/policyExport/electron-browser/policyExport.contribution.ts"
    assert contrib.exists(), "policyExport.contribution.ts must exist"
    content = contrib.read_text()
    assert "class PolicyExportContribution" in content, "Must contain PolicyExportContribution class"
    assert "export" in content, "Must have exports"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_export_script_handles_auth():
    """exportPolicyData.ts handles GitHub authentication (token + device flow)."""
    script = Path(REPO) / "build/lib/policies/exportPolicyData.ts"
    assert script.exists(), "build/lib/policies/exportPolicyData.ts must be created"
    content = script.read_text()

    # Must handle GITHUB_TOKEN environment variable
    assert "GITHUB_TOKEN" in content, \
        "Export script must reference GITHUB_TOKEN for distro API access"

    # Must have OAuth device flow as fallback
    assert "device" in content.lower(), \
        "Export script should implement device flow as auth fallback"

    # Must trigger transpilation before export
    assert "transpile" in content.lower(), \
        "Export script must transpile sources before running export"

    # Must invoke the --export-policy-data command
    assert "export-policy-data" in content, \
        "Export script must invoke --export-policy-data"


# [pr_diff] fail_to_pass
def test_contribution_merges_extension_policies():
    """policyExport.contribution.ts fetches distro product.json and merges extension policies."""
    contrib = Path(REPO) / "src/vs/workbench/contrib/policyExport/electron-browser/policyExport.contribution.ts"
    content = contrib.read_text()

    # Must have method to get distro product.json
    assert re.search(r'getDistroProduct', content), \
        "Must have a method to fetch distro product.json"

    # Must read extensionConfigurationPolicy from the distro
    assert "extensionConfigurationPolicy" in content, \
        "Must reference extensionConfigurationPolicy from distro product.json"

    # Must merge extension policies into the exported data (check for dedup logic)
    assert re.search(r'existingKeys|existing.*Set|has\(.*key\)', content), \
        "Must deduplicate when merging extension policies"

    # Must validate required fields on extension policy entries
    assert re.search(r'description.*category|category.*description', content), \
        "Must validate required fields (description, category) on extension policy entries"


# [pr_diff] fail_to_pass
def test_contribution_supports_test_fixture():
    """policyExport.contribution.ts supports DISTRO_PRODUCT_JSON env var for testing."""
    contrib = Path(REPO) / "src/vs/workbench/contrib/policyExport/electron-browser/policyExport.contribution.ts"
    content = contrib.read_text()

    # Must check DISTRO_PRODUCT_JSON env var for local testing
    assert "DISTRO_PRODUCT_JSON" in content, \
        "Must support DISTRO_PRODUCT_JSON env var for test fixture path"

    # Must fetch from GitHub API as fallback
    assert "api.github.com" in content or "GITHUB_TOKEN" in content, \
        "Must fall back to GitHub API when DISTRO_PRODUCT_JSON is not set"


# [pr_diff] fail_to_pass
def test_package_json_export_script():
    """package.json has an export-policy-data npm script."""
    pkg = Path(REPO) / "package.json"
    data = json.loads(pkg.read_text())
    scripts = data.get("scripts", {})
    assert "export-policy-data" in scripts, \
        "package.json must have an 'export-policy-data' script"
    # The script should reference the new build script
    script_val = scripts["export-policy-data"]
    assert "exportPolicyData" in script_val or "export" in script_val.lower(), \
        "export-policy-data script must reference the export build script"


# [pr_diff] fail_to_pass

    assert "extensionConfigurationPolicy" in data, \
        "Fixture must have extensionConfigurationPolicy key"
    policies = data["extensionConfigurationPolicy"]
    assert len(policies) >= 1, "Fixture must have at least one extension policy entry"

    # Validate structure of entries
    for key, entry in policies.items():
        assert "name" in entry, f"Entry '{key}' must have 'name'"
        assert "category" in entry, f"Entry '{key}' must have 'category'"
        assert "description" in entry, f"Entry '{key}' must have 'description'"


# [pr_diff] fail_to_pass

    assert "DISTRO_PRODUCT_JSON" in content, \
        "Integration test must set DISTRO_PRODUCT_JSON env var"
    assert "extensionPolicyFixture" in content or "Fixture" in content.lower(), \
        "Integration test must reference the extension policy fixture file"


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — SKILL.md documentation update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must explain that extension policies come from distro's product.json
    assert "extensionconfigurationpolicy" in content, \
        "SKILL.md must mention extensionConfigurationPolicy key"

    # Must explain the distro product.json is the source of truth
    assert "product.json" in content and "distro" in content, \
        "SKILL.md must explain extension policies come from distro's product.json"

    # Must explain the export/build step fetches from the distro
    assert "export" in content and ("merge" in content or "fetch" in content), \
        "SKILL.md must explain how extension policies are fetched and merged during export"


# [config_edit] fail_to_pass

    # Must show the JSON format with the extensionConfigurationPolicy structure
    full_content = skill_md.read_text()
    assert "extensionConfigurationPolicy" in full_content, \
        "SKILL.md must show the extensionConfigurationPolicy structure"

    # Must document required fields in the context of the distro format section
    # Look for a section that describes the format with field explanations
    assert "minimumversion" in content, \
        "SKILL.md must document minimumVersion as a required field"
    assert ("pascalcase" in content or "policy name" in content) and "category" in content, \
        "SKILL.md must document the name and category fields for extension policy entries"


# [config_edit] fail_to_pass

    # The old workflow was: npm run transpile-client && ./scripts/code.sh --export-policy-data
    # The new workflow should reference: npm run export-policy-data
    assert "npm run export-policy-data" in content, \
        "SKILL.md must document 'npm run export-policy-data' as the export command"

    # Should NOT still have the old two-step command as the primary workflow
    # (it's OK if it appears in historical context, but the primary instruction should be updated)
    lines = content.split("\n")
    code_blocks = []
    in_block = False
    block = []
    for line in lines:
        if line.strip().startswith("```"):
            if in_block:
                code_blocks.append("\n".join(block))
                block = []
            in_block = not in_block
        elif in_block:
            block.append(line)

    # At least one code block should contain the new command
    has_new_cmd = any("npm run export-policy-data" in b for b in code_blocks)
    assert has_new_cmd, \
        "SKILL.md code blocks must show 'npm run export-policy-data' as the export command"
