"""
Task: trigger-dev-remove-trigger-and-poll
Repo: triggerdotdev/trigger.dev @ 21c2c136beec90c28ec46c895561f5b3c258ec06
PR:   2379

Remove the deprecated triggerAndPoll() function from the SDK, along with all
documentation and agent config references.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/trigger.dev"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must be valid (no unterminated strings, etc.)."""
    files = [
        "packages/trigger-sdk/src/v3/shared.ts",
        "packages/trigger-sdk/src/v3/tasks.ts",
        "references/v3-catalog/src/trigger/sdkUsage.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        # Basic validity: file is non-empty and has balanced braces
        assert len(content) > 100, f"{f} appears truncated"
        assert content.count("{") == content.count("}"), (
            f"{f} has unbalanced braces — likely a bad edit"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code removal tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_triggerandpoll_function_removed():
    """The triggerAndPoll function definition must be removed from shared.ts."""
    content = (Path(REPO) / "packages/trigger-sdk/src/v3/shared.ts").read_text()
    assert "async function triggerAndPoll" not in content, (
        "triggerAndPoll function definition must be removed from shared.ts"
    )


# [pr_diff] fail_to_pass
def test_triggerandpoll_not_exported():
    """triggerAndPoll must not be imported or exported from tasks.ts."""
    content = (Path(REPO) / "packages/trigger-sdk/src/v3/tasks.ts").read_text()
    assert "triggerAndPoll" not in content, (
        "triggerAndPoll must be fully removed from tasks.ts (import + tasks object)"
    )


# [pr_diff] fail_to_pass
def test_reference_usage_removed():
    """The reference usage of triggerAndPoll in sdkUsage.ts must be removed."""
    content = (Path(REPO) / "references/v3-catalog/src/trigger/sdkUsage.ts").read_text()
    assert "triggerAndPoll" not in content, (
        "triggerAndPoll usage must be removed from sdkUsage.ts"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — config/documentation update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression / preservation tests
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_other_task_methods_preserved():
    """Other task methods (trigger, batchTrigger, triggerAndWait) must still exist."""
    content = (Path(REPO) / "packages/trigger-sdk/src/v3/tasks.ts").read_text()
    for method in ["trigger", "batchTrigger", "triggerAndWait", "batchTriggerAndWait"]:
        assert method in content, f"tasks.{method} must still be exported"


# [static] pass_to_pass
def test_docs_other_methods_preserved():
    """Documentation must still reference the remaining trigger methods."""
    content = (Path(REPO) / "docs/triggering.mdx").read_text()
    assert "tasks.trigger()" in content, "docs must still document tasks.trigger()"
    assert "tasks.batchTrigger()" in content, "docs must still document tasks.batchTrigger()"
    assert "batch.trigger()" in content, "docs must still document batch.trigger()"


# [static] pass_to_pass
def test_cursor_rules_other_methods_preserved():
    """Cursor rules must still document the remaining trigger methods."""
    content = (Path(REPO) / ".cursor/rules/writing-tasks.mdc").read_text()
    assert "tasks.trigger()" in content, "cursor rules must still document tasks.trigger()"
    assert "batch.trigger()" in content, "cursor rules must still document batch.trigger()"
