"""Behavioral checks for axonhub-feat-add-cli-skill-close (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/axonhub")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axonhub-cli/SKILL.md')
    assert 'npx @axonhub/graphql-cli mutate \'mutation { createChannel(input: { type: openai, name: "my-channel", baseURL: "https://api.openai.com", credentials: { apiKey: "sk-xxx" }, supportedModels: ["gpt-4o"], ' in text, "expected to find: " + 'npx @axonhub/graphql-cli mutate \'mutation { createChannel(input: { type: openai, name: "my-channel", baseURL: "https://api.openai.com", credentials: { apiKey: "sk-xxx" }, supportedModels: ["gpt-4o"], '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axonhub-cli/SKILL.md')
    assert '- **Always use `find` without `--detail` first** to get an overview of matching names, then use `find --detail` on specific results to see full definitions with fields and arguments. This avoids overw' in text, "expected to find: " + '- **Always use `find` without `--detail` first** to get an overview of matching names, then use `find --detail` on specific results to see full definitions with fields and arguments. This avoids overw'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/axonhub-cli/SKILL.md')
    assert 'description: "Manages AxonHub via its GraphQL API using graphql-cli. Use when asked to query, manage, or operate AxonHub resources (channels, API keys, users, projects, system settings) from the comma' in text, "expected to find: " + 'description: "Manages AxonHub via its GraphQL API using graphql-cli. Use when asked to query, manage, or operate AxonHub resources (channels, API keys, users, projects, system settings) from the comma'[:80]

