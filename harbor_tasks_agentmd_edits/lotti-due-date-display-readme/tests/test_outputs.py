"""
Task: lotti-due-date-display-readme
Repo: matthiasn/lotti @ 88b2b0e5c762e01aeeefbf27dcc339c05a63a0a4
PR:   2565

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/lotti"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Dart files must not have obvious syntax errors (balanced braces)."""
    for rel_path in [
        "lib/features/journal/ui/widgets/list_cards/modern_task_card.dart",
        "lib/features/tasks/ui/header/task_due_date_wrapper.dart",
    ]:
        src = Path(f"{REPO}/{rel_path}").read_text()
        # Basic brace-balance check for Dart
        assert src.count("{") == src.count("}"), (
            f"{rel_path}: unbalanced braces ({src.count('{')} open vs {src.count('}')} close)"
        )
        assert src.count("(") == src.count(")"), (
            f"{rel_path}: unbalanced parens ({src.count('(')} open vs {src.count(')')} close)"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_task_card_hides_due_date_for_completed():
    """ModernTaskCard._buildDateRow must skip due date for completed/rejected tasks."""
    src = Path(
        f"{REPO}/lib/features/journal/ui/widgets/list_cards/modern_task_card.dart"
    ).read_text()

    # The fix must introduce a check for completed/rejected status in _buildDateRow.
    # We look for references to TaskDone/TaskRejected or done/rejected status
    # within the _buildDateRow method context (near hasDueDate logic).
    has_date_row = "_buildDateRow" in src
    assert has_date_row, "modern_task_card.dart must contain _buildDateRow method"

    # Extract the _buildDateRow method body (from method signature to next method or end)
    date_row_match = re.search(
        r"_buildDateRow\(.*?\{(.*?)(?=\n  Widget |\n  \w+ _|\Z)",
        src,
        re.DOTALL,
    )
    assert date_row_match, "_buildDateRow method body not found"
    method_body = date_row_match.group(1)

    # The method must check for completed/done or rejected task status
    checks_done = bool(
        re.search(r"TaskDone|TaskStatus\.done|status.*done|isDone|isCompleted", method_body, re.IGNORECASE)
    )
    checks_rejected = bool(
        re.search(r"TaskRejected|TaskStatus\.rejected|status.*rejected|isRejected|isCompleted", method_body, re.IGNORECASE)
    )
    assert checks_done, (
        "_buildDateRow must check for completed (done) task status to hide due date"
    )
    assert checks_rejected, (
        "_buildDateRow must check for rejected task status to hide due date"
    )

    # The hasDueDate assignment must be gated by the status check
    # (not just checking showDueDate && task.data.due != null)
    has_due_date_line = [
        line for line in method_body.split("\n")
        if "hasDueDate" in line and "=" in line and "showDueDate" in line
    ]
    assert len(has_due_date_line) > 0, "hasDueDate assignment not found"
    # The line must reference the completed/status variable
    due_date_assign = has_due_date_line[0]
    assert re.search(r"isCompleted|isDone|isRejected|status", due_date_assign, re.IGNORECASE), (
        "hasDueDate must be gated by task completion status, not just showDueDate && due != null"
    )


# [pr_diff] fail_to_pass
def test_due_date_wrapper_disables_urgency_for_completed():
    """TaskDueDateWrapper must disable urgency colors for completed/rejected tasks."""
    src = Path(
        f"{REPO}/lib/features/tasks/ui/header/task_due_date_wrapper.dart"
    ).read_text()

    # Must reference TaskDone/TaskRejected or equivalent completed check
    has_completed_check = bool(
        re.search(r"TaskDone|TaskRejected|isCompleted|isDone|isRejected", src)
    )
    assert has_completed_check, (
        "task_due_date_wrapper.dart must check for completed/rejected task status"
    )

    # The isUrgent parameter must be conditioned on completed status
    # Before fix: isUrgent: status.isUrgent
    # After fix: isUrgent: !isCompleted && status.isUrgent (or equivalent)
    is_urgent_lines = [line.strip() for line in src.split("\n") if "isUrgent" in line and ":" in line]
    assert len(is_urgent_lines) > 0, "isUrgent parameter assignment not found"

    # At least one isUrgent line must reference the completed status
    urgency_gated = any(
        re.search(r"isCompleted|isDone|isRejected|completed|rejected", line)
        for line in is_urgent_lines
    )
    assert urgency_gated, (
        "isUrgent must be gated by completion status "
        "(e.g., !isCompleted && status.isUrgent)"
    )

    # The urgentColor must also be conditioned
    color_lines = [line.strip() for line in src.split("\n") if "urgentColor" in line and ":" in line]
    assert len(color_lines) > 0, "urgentColor parameter assignment not found"
    color_gated = any(
        re.search(r"isCompleted|isDone|isRejected|completed|rejected|null", line)
        for line in color_lines
    )
    assert color_gated, (
        "urgentColor must be conditioned on completion status "
        "(e.g., isCompleted ? null : status.urgentColor)"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — config/documentation update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must NOT still say "Coming Soon: Deep Dive Series"
    assert "Coming Soon: Deep Dive" not in readme, (
        "README still says 'Coming Soon: Deep Dive Series' — "
        "should be updated to reflect the launched blog series"
    )

    # Must reference "Meet Lotti" blog series
    assert "meet lotti" in readme.lower() or "meet-lotti" in readme.lower(), (
        "README should reference the 'Meet Lotti' blog series"
    )

    # Must contain a link to the actual blog post on substack
    assert "matthiasnehlsen.substack.com/p/meet-lotti" in readme, (
        "README should link to the Meet Lotti blog post"
    )


# [config_edit] fail_to_pass

    # Must mention due date changes
    assert "due date" in lower, (
        "CHANGELOG should mention 'due date' changes"
    )

    # Must mention completed or rejected tasks
    has_completed = "completed" in lower or "done" in lower
    has_rejected = "rejected" in lower
    assert has_completed or has_rejected, (
        "CHANGELOG should reference completed/rejected tasks "
        "in context of due date visibility changes"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:last-section @ 88b2b0e
