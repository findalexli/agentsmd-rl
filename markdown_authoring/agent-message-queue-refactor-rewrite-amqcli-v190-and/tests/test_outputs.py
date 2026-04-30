"""Behavioral checks for agent-message-queue-refactor-rewrite-amqcli-v190-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-message-queue")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/amq-cli/SKILL.md')
    assert 'AMQ uses two env vars for routing: `AM_ROOT` (which mailbox tree) and `AM_ME` (which agent). Getting these wrong means messages go to the wrong place or silently disappear, so it matters to let the CL' in text, "expected to find: " + 'AMQ uses two env vars for routing: `AM_ROOT` (which mailbox tree) and `AM_ME` (which agent). Getting these wrong means messages go to the wrong place or silently disappear, so it matters to let the CL'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/amq-cli/SKILL.md')
    assert '**Session pitfall**: `coop exec` defaults to `--session collab` (i.e., `.agent-mail/collab`). Outside `coop exec`, the base root is `.agent-mail` (no session suffix). These are different mailbox trees' in text, "expected to find: " + '**Session pitfall**: `coop exec` defaults to `--session collab` (i.e., `.agent-mail/collab`). Outside `coop exec`, the base root is `.agent-mail` (no session suffix). These are different mailbox trees'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/amq-cli/SKILL.md')
    assert '**Global fallback**: Orchestrator-spawned agents often start outside the repo root where no project `.amqrc` exists. Set `AMQ_GLOBAL_ROOT` or `~/.amqrc` so `amq env` and `amq doctor` still resolve the' in text, "expected to find: " + '**Global fallback**: Orchestrator-spawned agents often start outside the repo root where no project `.amqrc` exists. Set `AMQ_GLOBAL_ROOT` or `~/.amqrc` so `amq env` and `amq doctor` still resolve the'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/amq-spec/SKILL.md')
    assert "| `phase:research` | **Before reading**: check if you've already submitted your own research on this thread. If not, do your own research and submit it first. This preserves research independence — re" in text, "expected to find: " + "| `phase:research` | **Before reading**: check if you've already submitted your own research on this thread. If not, do your own research and submit it first. This preserves research independence — re"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/amq-spec/SKILL.md')
    assert "- **Submit your own research before reading partner's** — reading first contaminates your independent perspective. Two agents who read the same code and reach the same conclusion is less valuable than" in text, "expected to find: " + "- **Submit your own research before reading partner's** — reading first contaminates your independent perspective. Two agents who read the same code and reach the same conclusion is less valuable than"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/amq-spec/SKILL.md')
    assert '- **Present the final plan to the user before executing** — the initiator owns the user relationship. After the decision phase, present the plan in chat and wait for explicit approval. Only then assig' in text, "expected to find: " + '- **Present the final plan to the user before executing** — the initiator owns the user relationship. After the decision phase, present the plan in chat and wait for explicit approval. Only then assig'[:80]

