"""
Task: lotti-due-date-display-readme
Repo: matthiasn/lotti @ 88b2b0e5c762e01aeeefbf27dcc339c05a63a0a4
PR:   2565

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/lotti"


def _analyze_dart(script: str, filepath: str) -> dict:
    """Run a Python analysis script against a Dart file, return JSON result."""
    r = subprocess.run(
        ["python3", "-c", script, filepath],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if r.returncode != 0:
        return {"ok": False, "err": r.stderr.strip() or f"exit {r.returncode}"}
    try:
        return json.loads(r.stdout.strip())
    except json.JSONDecodeError:
        return {"ok": False, "err": f"bad output: {r.stdout[:200]}"}


# ---------------------------------------------------------------------------
# pass_to_pass — syntax / structural checks
# ---------------------------------------------------------------------------


def test_syntax_check():
    """Modified Dart files have balanced braces and parens."""
    for rel in [
        "lib/features/journal/ui/widgets/list_cards/modern_task_card.dart",
        "lib/features/tasks/ui/header/task_due_date_wrapper.dart",
    ]:
        src = Path(f"{REPO}/{rel}").read_text()
        assert src.count("{") == src.count("}"), (
            f"{rel}: unbalanced braces ({src.count('{')} open vs {src.count('}')} close)"
        )
        assert src.count("(") == src.count(")"), (
            f"{rel}: unbalanced parens ({src.count('(')} open vs {src.count(')')} close)"
        )


# ---------------------------------------------------------------------------
# fail_to_pass — behavioral tests using subprocess
# ---------------------------------------------------------------------------

_ANALYZE_CARD = r"""
import json, re, sys

src = open(sys.argv[1]).read()

# Locate _buildDateRow method body
m = re.search(r'Widget _buildDateRow\(.*?\{', src)
if not m:
    print(json.dumps({"ok": False, "err": "_buildDateRow not found"}))
    sys.exit(0)

depth = 1
body_start = m.end()
body_end = len(src)
for i in range(body_start, len(src)):
    if src[i] == '{':
        depth += 1
    elif src[i] == '}':
        depth -= 1
        if depth == 0:
            body_end = i
            break

body = src[body_start:body_end]

# 1. Must reference TaskDone or TaskRejected in the method
if not re.search(r'(TaskDone|TaskRejected)', body):
    print(json.dumps({"ok": False, "err": "_buildDateRow must reference TaskDone/TaskRejected"}))
    sys.exit(0)

# 2. hasDueDate assignment must be gated by completion status (!isCompleted)
has_due_line = None
for line in body.split('\n'):
    s = line.strip()
    if 'hasDueDate' in s and '=' in s and ('final' in s or s.startswith('hasDueDate')):
        has_due_line = s
        break

if not has_due_line:
    print(json.dumps({"ok": False, "err": "hasDueDate assignment not found in _buildDateRow"}))
    sys.exit(0)

if not re.search(r'!.*(?:isCompleted|isComplete|isDone|isFinished)', has_due_line):
    print(json.dumps({"ok": False, "err": f"hasDueDate not gated by completion status: {has_due_line}"}))
    sys.exit(0)

print(json.dumps({"ok": True}))
"""


def test_task_card_hides_due_date_for_completed():
    """ModernTaskCard._buildDateRow skips due date for completed/rejected tasks."""
    card = f"{REPO}/lib/features/journal/ui/widgets/list_cards/modern_task_card.dart"
    result = _analyze_dart(_ANALYZE_CARD, card)
    assert result.get("ok"), result.get("err", "Unknown error")


_ANALYZE_WRAPPER = r"""
import json, re, sys

src = open(sys.argv[1]).read()

# 1. Must import task.dart (needed for TaskDone/TaskRejected types)
if not re.search(r"import.*package:lotti/classes/task\.dart", src):
    print(json.dumps({"ok": False, "err": "Missing import for lotti/classes/task.dart"}))
    sys.exit(0)

# 2. Must define isCompleted using TaskDone/TaskRejected
if not re.search(r'(TaskDone|TaskRejected)', src):
    print(json.dumps({"ok": False, "err": "Must reference TaskDone/TaskRejected for status check"}))
    sys.exit(0)

# 3. isUrgent must be gated by completion status (negation before status.isUrgent)
is_urgent_lines = [l for l in src.split('\n') if 'isUrgent' in l and ':' in l]
if not is_urgent_lines:
    print(json.dumps({"ok": False, "err": "isUrgent parameter not found"}))
    sys.exit(0)

gated = any(re.search(r'!.*(?:isCompleted|isComplete|isDone|isFinished).*isUrgent', l) for l in is_urgent_lines)
if not gated:
    print(json.dumps({"ok": False, "err": "isUrgent must be gated by completion status (e.g., !isCompleted && status.isUrgent)"}))
    sys.exit(0)

# 4. urgentColor must be null when task is completed
color_lines = [l for l in src.split('\n') if 'urgentColor' in l and ':' in l]
if not color_lines:
    print(json.dumps({"ok": False, "err": "urgentColor parameter not found"}))
    sys.exit(0)

null_gated = any(
    'null' in l and re.search(r'isCompleted|isComplete|isDone|isFinished', l)
    for l in color_lines
)
if not null_gated:
    print(json.dumps({"ok": False, "err": "urgentColor must be null for completed tasks (e.g., isCompleted ? null : status.urgentColor)"}))
    sys.exit(0)

print(json.dumps({"ok": True}))
"""


def test_due_date_wrapper_disables_urgency():
    """TaskDueDateWrapper disables urgency styling for completed/rejected tasks."""
    wrapper = f"{REPO}/lib/features/tasks/ui/header/task_due_date_wrapper.dart"
    result = _analyze_dart(_ANALYZE_WRAPPER, wrapper)
    assert result.get("ok"), result.get("err", "Unknown error")


def test_readme_updated():
    """README references live 'Meet Lotti' blog series with link."""
    readme = Path(f"{REPO}/README.md").read_text()
    assert "Coming Soon: Deep Dive" not in readme, (
        "README still says 'Coming Soon: Deep Dive Series' — "
        "should be updated to reflect the launched blog series"
    )
    assert "meet-lotti" in readme.lower(), (
        "README should reference the 'Meet Lotti' blog series"
    )
    assert "matthiasnehlsen.substack.com/p/meet-lotti" in readme, (
        "README should link to the Meet Lotti blog post on Substack"
    )


def test_changelog_documents_changes():
    """CHANGELOG documents due date visibility changes for completed/rejected tasks."""
    changelog = Path(f"{REPO}/CHANGELOG.md").read_text()
    lower = changelog.lower()
    assert "due date" in lower, (
        "CHANGELOG should mention 'due date' changes"
    )
    assert "completed" in lower or "rejected" in lower, (
        "CHANGELOG should reference completed/rejected tasks "
        "in context of due date visibility changes"
    )
