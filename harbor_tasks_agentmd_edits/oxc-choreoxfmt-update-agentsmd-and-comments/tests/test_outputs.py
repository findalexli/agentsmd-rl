"""
Task: oxc-choreoxfmt-update-agentsmd-and-comments
Repo: oxc-project/oxc @ 828b56a30708f7db749405f245262ca53125fc1b
PR:   20637

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path
import re

REPO = "/workspace/oxc"
AGENTS_MD = Path(f"{REPO}/apps/oxfmt/AGENTS.md")


def _get_agents_md_content() -> str:
    """Read AGENTS.md content."""
    return AGENTS_MD.read_text()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file existence / syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_agents_md_exists():
    """AGENTS.md file exists in the correct location."""
    assert AGENTS_MD.exists(), f"AGENTS.md not found at {AGENTS_MD}"


# [static] pass_to_pass
def test_agents_md_valid_markdown():
    """AGENTS.md is valid markdown (no syntax errors)."""
    content = _get_agents_md_content()
    # Basic markdown validation: file should be parseable and have structure
    assert len(content) > 0, "AGENTS.md is empty"
    # Check for common markdown structural elements
    assert "#" in content, "No headers found in AGENTS.md"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_comparing_with_prettier_section_exists():
    """The 'Comparing with Prettier' section is added to AGENTS.md."""
    content = _get_agents_md_content()
    # Look for the section header
    assert "## Comparing with Prettier" in content, \
        "Missing '## Comparing with Prettier' section header"


# [pr_diff] fail_to_pass
def test_prettier_section_content():
    """The Prettier comparison section contains the required documentation."""
    content = _get_agents_md_content()

    # Find the Comparing with Prettier section
    section_match = re.search(
        r"## Comparing with Prettier(.*?)(?=^## |\Z)",
        content,
        re.MULTILINE | re.DOTALL
    )
    assert section_match, "Could not extract 'Comparing with Prettier' section"
    section = section_match.group(1)

    # Check for key content elements
    assert "oxfmt and Prettier have different default printWidth" in section, \
        "Missing explanation about different default printWidth values"
    assert 'Example fmt.json: { "printWidth": 80 }' in section, \
        "Missing example fmt.json configuration"


# [pr_diff] fail_to_pass
def test_prettier_section_code_examples():
    """The Prettier comparison section contains the correct code examples."""
    content = _get_agents_md_content()

    # Find the Comparing with Prettier section
    section_match = re.search(
        r"## Comparing with Prettier(.*?)(?=^## |\Z)",
        content,
        re.MULTILINE | re.DOTALL
    )
    assert section_match, "Could not extract 'Comparing with Prettier' section"
    section = section_match.group(1)

    # Check for the code block with both commands
    assert "cat <file> | node ./dist/cli.js --config=fmt.json --stdin-filepath=<file>" in section, \
        "Missing oxfmt command example"
    assert "npx prettier --config=fmt.json <file>" in section, \
        "Missing prettier command example"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_agents_md_structure_preserved():
    """AGENTS.md maintains its original structure with the new section inserted."""
    content = _get_agents_md_content()

    # The original structure should be preserved
    assert "# Coding agent guides for `apps/oxfmt`" in content, \
        "Missing main title"
    assert "## Overview" in content, \
        "Missing Overview section"
    assert "## Test Organization" in content, \
        "Missing Test Organization section"

    # The new section should be placed before Test Organization
    prettier_pos = content.find("## Comparing with Prettier")
    test_org_pos = content.find("## Test Organization")
    assert prettier_pos != -1, "Comparing with Prettier section not found"
    assert test_org_pos != -1, "Test Organization section not found"
    assert prettier_pos < test_org_pos, \
        "Comparing with Prettier section should come before Test Organization"


# [static] pass_to_pass
def test_no_stub_content():
    """The added content is not a stub (has meaningful documentation)."""
    content = _get_agents_md_content()

    # Find the Comparing with Prettier section
    section_match = re.search(
        r"## Comparing with Prettier(.*?)(?=^## |\Z)",
        content,
        re.MULTILINE | re.DOTALL
    )
    assert section_match, "Could not extract 'Comparing with Prettier' section"
    section = section_match.group(1)

    # Section should have substantial content (more than just a placeholder)
    assert len(section.strip()) > 200, \
        "Section content is too short to be meaningful documentation"

    # Should have code blocks
    assert "```" in section, "Missing code blocks in the section"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_cargo_check():
    """Cargo check passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "ck"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_test():
    """Cargo test passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "--all-features"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_lint():
    """Cargo clippy lint passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "lint", "--", "--deny", "warnings"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo lint failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

# This task is about updating AGENTS.md itself, so there are no agent_config
# checks derived from rules. The task IS the config edit.
