"""Behavioral checks for agent-squad-docs-add-claudemd-for-claude (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-squad")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '3. **`Agent`** (abstract base in `agents/agent.py` / `agents/agent.ts`) — pluggable worker. Concrete types include `BedrockLLMAgent`, `AnthropicAgent`, `OpenAIAgent`, `AmazonBedrockAgent`, `BedrockInl' in text, "expected to find: " + '3. **`Agent`** (abstract base in `agents/agent.py` / `agents/agent.ts`) — pluggable worker. Concrete types include `BedrockLLMAgent`, `AnthropicAgent`, `OpenAIAgent`, `AmazonBedrockAgent`, `BedrockInl'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "2. **`Classifier`** (in `classifiers/`) — given the user input, conversation history, and the list of registered agents' names/descriptions, picks which agent should handle the request. Implementation" in text, "expected to find: " + "2. **`Classifier`** (in `classifiers/`) — given the user input, conversation history, and the list of registered agents' names/descriptions, picks which agent should handle the request. Implementation"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Issue-first policy.** Every PR **must** be linked to an issue via `Fixes #N` / `Closes #N` / `Resolves #N` in the PR body, or via GitHub\'s "Link an issue" UI. The [pr-issue-link-checker.yml](.gith' in text, "expected to find: " + '- **Issue-first policy.** Every PR **must** be linked to an issue via `Fixes #N` / `Closes #N` / `Resolves #N` in the PR body, or via GitHub\'s "Link an issue" UI. The [pr-issue-link-checker.yml](.gith'[:80]

