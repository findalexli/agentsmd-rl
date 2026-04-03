"""
Task: openai-agents-js-skill-rename-scope
Repo: openai/openai-agents-js @ 41c1b89f650a9d18aeb76677f965dcfb06087c90
PR:   836

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/openai-agents-js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / YAML frontmatter checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — skill rename and scoping
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_renamed():
    """verify-changes skill must be renamed to code-change-verification."""
    new_path = Path(REPO) / ".codex/skills/code-change-verification/SKILL.md"
    old_path = Path(REPO) / ".codex/skills/verify-changes/SKILL.md"
    assert new_path.exists(), \
        "Expected .codex/skills/code-change-verification/SKILL.md to exist"
    assert not old_path.exists(), \
        "Old .codex/skills/verify-changes/SKILL.md should be removed"


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass
def test_run_sh_message_updated():
    """run.sh success message must reference code-change-verification."""
    run_sh = Path(REPO) / ".codex/skills/code-change-verification/scripts/run.sh"
    content = run_sh.read_text()
    assert "code-change-verification" in content, \
        "run.sh should print 'code-change-verification' in its output"
    assert "verify-changes:" not in content, \
        "run.sh should not reference old 'verify-changes' name"


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config edit — AGENTS.md updates (config_edit origin)
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_run_sh_has_verification_commands():
    """run.sh must still contain the core verification commands."""
    new_path = Path(REPO) / ".codex/skills/code-change-verification/scripts/run.sh"
    old_path = Path(REPO) / ".codex/skills/verify-changes/scripts/run.sh"
    run_sh = new_path if new_path.exists() else old_path
    content = run_sh.read_text()
    assert "pnpm" in content, "run.sh must invoke pnpm commands"
    assert "pnpm test" in content, "run.sh must include pnpm test"
    assert "pnpm lint" in content, "run.sh must include pnpm lint"
    assert "pnpm build" in content or "pnpm -r build-check" in content, \
        "run.sh must include a build step"
