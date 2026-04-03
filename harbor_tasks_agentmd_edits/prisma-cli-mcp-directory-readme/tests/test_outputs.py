"""
Task: prisma-cli-mcp-directory-readme
Repo: prisma/prisma @ 057e587d5f31ad2361dfbc66d8c57406a13f86bc
PR:   #27631

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
from pathlib import Path

REPO = "/workspace/prisma"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — MCP.ts moved to mcp/ subdirectory
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_mcp_moved_to_subdirectory():
    """MCP.ts must exist at packages/cli/src/mcp/MCP.ts."""
    mcp_file = Path(REPO) / "packages/cli/src/mcp/MCP.ts"
    assert mcp_file.exists(), f"MCP.ts not found at {mcp_file}"
    content = mcp_file.read_text()
    # Verify it's the real MCP module, not an empty file
    assert "class Mcp" in content, "MCP.ts should contain the Mcp class"
    assert "McpServer" in content, "MCP.ts should use McpServer"


# [pr_diff] fail_to_pass
def test_old_mcp_file_removed():
    """Old MCP.ts at packages/cli/src/MCP.ts must be removed after move."""
    old_file = Path(REPO) / "packages/cli/src/MCP.ts"
    assert not old_file.exists(), (
        f"Old MCP.ts still exists at {old_file} — it should be moved to packages/cli/src/mcp/MCP.ts"
    )


# [pr_diff] fail_to_pass
def test_bin_imports_from_mcp_directory():
    """bin.ts must import Mcp from the new ./mcp/MCP path."""
    bin_ts = Path(REPO) / "packages/cli/src/bin.ts"
    content = bin_ts.read_text()
    assert "./mcp/MCP" in content, (
        "bin.ts should import Mcp from './mcp/MCP', not './MCP'"
    )


# [pr_diff] fail_to_pass
def test_pdp_tools_removed():
    """PDP MCP tools must be removed from MCP.ts (managed by remote MCP server now)."""
    mcp_file = Path(REPO) / "packages/cli/src/mcp/MCP.ts"
    content = mcp_file.read_text()
    assert "Prisma-Postgres-account-status" not in content, (
        "Prisma-Postgres-account-status tool should be removed"
    )
    assert "Create-Prisma-Postgres-Database" not in content, (
        "Create-Prisma-Postgres-Database tool should be removed"
    )
    assert "Prisma-Login" not in content, (
        "Prisma-Login tool should be removed"
    )


# [pr_diff] fail_to_pass
def test_relative_imports_updated():
    """MCP.ts relative imports must be adjusted for the new directory depth."""
    mcp_file = Path(REPO) / "packages/cli/src/mcp/MCP.ts"
    content = mcp_file.read_text()
    # Now one level deeper, so ../package.json becomes ../../package.json
    assert "../../package.json" in content, (
        "MCP.ts should import from '../../package.json' (adjusted for mcp/ subdirectory)"
    )
    assert "../platform/_lib/help" in content, (
        "MCP.ts should import from '../platform/_lib/help' (adjusted for mcp/ subdirectory)"
    )


# [pr_diff] fail_to_pass
def test_mcp_keyword_in_package_json():
    """packages/cli/package.json keywords must include 'MCP'."""
    pkg_path = Path(REPO) / "packages/cli/package.json"
    pkg = json.loads(pkg_path.read_text())
    keywords = pkg.get("keywords", [])
    assert "MCP" in keywords, (
        f"package.json keywords should include 'MCP', got: {keywords}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — core MCP tools must be preserved
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — README.md documentation
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
