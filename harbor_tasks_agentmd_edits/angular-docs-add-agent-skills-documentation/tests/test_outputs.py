"""
Task: angular-docs-add-agent-skills-documentation
Repo: angular/angular @ 9d79ec6866645393bc8b01881e7e2165dd29d02d
PR:   67831

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/angular"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Navigation entries TypeScript file has balanced braces."""
    nav_file = Path(REPO) / "adev/src/app/routing/navigation-entries/index.ts"
    content = nav_file.read_text()
    # Basic brace balance check
    assert content.count("{") == content.count("}"), "Unbalanced curly braces"
    assert content.count("[") == content.count("]"), "Unbalanced square brackets"
    assert content.count("(") == content.count(")"), "Unbalanced parentheses"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavior tests (navigation config)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agent_skills_nav_entry():
    """Navigation must include an 'Agent Skills' entry with correct path."""
    nav_file = Path(REPO) / "adev/src/app/routing/navigation-entries/index.ts"
    content = nav_file.read_text()
    assert "'Agent Skills'" in content or '"Agent Skills"' in content, \
        "Navigation must have an 'Agent Skills' label"
    assert "ai/agent-skills" in content, \
        "Navigation must have 'ai/agent-skills' path"


# [pr_diff] fail_to_pass
def test_agent_skills_has_new_status():
    """The Agent Skills nav entry should be marked with status 'new'."""
    nav_file = Path(REPO) / "adev/src/app/routing/navigation-entries/index.ts"
    content = nav_file.read_text()
    # Find the Agent Skills block and check it has status: 'new'
    match = re.search(
        r"label:\s*['\"]Agent Skills['\"].*?(?=label:|$)",
        content,
        re.DOTALL,
    )
    assert match, "Agent Skills entry not found in navigation"
    block = match.group(0)
    assert "status" in block and "new" in block, \
        "Agent Skills entry should have status: 'new'"


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — documentation / config file updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — AGENTS.md compliance
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass
def test_commit_guidelines_reference():
    """AGENTS.md references commit guidelines — ensure they still exist."""
    contributing = Path(REPO) / "contributing-docs/commit-message-guidelines.md"
    assert contributing.exists(), \
        "Commit message guidelines doc must still exist (referenced by AGENTS.md)"
