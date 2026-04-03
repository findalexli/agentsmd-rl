"""
Task: biome-docs-break-down-skills-improve
Repo: biomejs/biome @ eb57e3a1df36bf1bbe612f84a68ded658d9b7d00
PR:   9613

Break down and improve agent skills: extract changeset and pull-request
into dedicated skills, add Code Comments guidance to biome-developer,
add non-interactive changeset command to justfile.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/biome"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_justfile_syntax():
    """justfile must be parseable (no syntax errors introduced)."""
    content = Path(f"{REPO}/justfile").read_text()
    # Basic check: file is non-empty and still has key recipes
    assert "new-changeset:" in content, "justfile missing existing new-changeset recipe"
    assert "ready:" in content, "justfile missing existing ready recipe"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_justfile_has_new_changeset_empty_recipe():
    """justfile must have a new-changeset-empty recipe."""
    content = Path(f"{REPO}/justfile").read_text()
    assert "new-changeset-empty:" in content, \
        "justfile should define a 'new-changeset-empty' recipe"


# [pr_diff] fail_to_pass
def test_justfile_changeset_empty_uses_pnpm():
    """The new-changeset-empty recipe must invoke pnpm changeset --empty."""
    content = Path(f"{REPO}/justfile").read_text()
    # Find the recipe body
    lines = content.split("\n")
    found_recipe = False
    recipe_body = []
    for line in lines:
        if line.startswith("new-changeset-empty:"):
            found_recipe = True
            continue
        if found_recipe:
            if line.startswith("  ") or line.startswith("\t"):
                recipe_body.append(line.strip())
            elif line.strip() == "":
                continue
            else:
                break
    assert found_recipe, "new-changeset-empty recipe not found"
    body = " ".join(recipe_body)
    assert "changeset" in body and "--empty" in body, \
        f"Recipe body should run changeset with --empty flag, got: {body}"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — config file update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_skills_intact():
    """Other existing skill files should still be present."""
    for skill_dir in ["biome-developer", "testing-codegen", "lint-rule-development",
                      "formatter-development", "parser-development"]:
        skill_path = Path(f"{REPO}/.claude/skills/{skill_dir}/SKILL.md")
        assert skill_path.exists(), f"Existing skill {skill_dir}/SKILL.md should still exist"
