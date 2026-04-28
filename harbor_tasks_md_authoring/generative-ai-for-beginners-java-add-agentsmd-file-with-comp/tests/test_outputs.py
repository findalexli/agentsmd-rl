"""Behavioral checks for generative-ai-for-beginners-java-add-agentsmd-file-with-comp (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/generative-ai-for-beginners-java")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is an educational repository for learning Generative AI development with Java. It provides a comprehensive hands-on course covering Large Language Models (LLMs), prompt engineering, embeddings, R' in text, "expected to find: " + 'This is an educational repository for learning Generative AI development with Java. It provides a comprehensive hands-on course covering Large Language Models (LLMs), prompt engineering, embeddings, R'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Client examples in the calculator project are in `src/test/java/com/microsoft/mcp/sample/client/`' in text, "expected to find: " + '- Client examples in the calculator project are in `src/test/java/com/microsoft/mcp/sample/client/`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'mvn exec:java -Dexec.mainClass="com.microsoft.mcp.sample.client.LangChain4jClient"' in text, "expected to find: " + 'mvn exec:java -Dexec.mainClass="com.microsoft.mcp.sample.client.LangChain4jClient"'[:80]

