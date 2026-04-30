"""Behavioral checks for azure-search-openai-javascript-add-agentsmd-file-for-ai (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/azure-search-openai-javascript")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is a ChatGPT + Enterprise data application built with Azure OpenAI and Azure AI Search, implementing the Retrieval Augmented Generation (RAG) pattern. The application allows users to chat with th' in text, "expected to find: " + 'This is a ChatGPT + Enterprise data application built with Azure OpenAI and Azure AI Search, implementing the Retrieval Augmented Generation (RAG) pattern. The application allows users to chat with th'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The search API implements the [HTTP protocol for AI chat apps](https://aka.ms/chatprotocol). It can be swapped with compatible backends like the Python implementation from [azure-search-openai-demo](h' in text, "expected to find: " + 'The search API implements the [HTTP protocol for AI chat apps](https://aka.ms/chatprotocol). It can be swapped with compatible backends like the Python implementation from [azure-search-openai-demo](h'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '3. **Data indexing**: After deploying, ensure data is indexed by running the index-data script. This is done automatically by the `postup` hook but may need to be run manually if you change the data.' in text, "expected to find: " + '3. **Data indexing**: After deploying, ensure data is indexed by running the index-data script. This is done automatically by the `postup` hook but may need to be run manually if you change the data.'[:80]

