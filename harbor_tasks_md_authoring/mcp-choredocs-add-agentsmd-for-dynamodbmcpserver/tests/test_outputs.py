"""Behavioral checks for mcp-choredocs-add-agentsmd-for-dynamodbmcpserver (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mcp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('src/dynamodb-mcp-server/AGENTS.md')
    assert '5. **dynamodb_data_model_schema_converter** - Converts your data model (dynamodb_data_model.md) into a structured schema.json file representing your DynamoDB tables, indexes, entities, fields, and acc' in text, "expected to find: " + '5. **dynamodb_data_model_schema_converter** - Converts your data model (dynamodb_data_model.md) into a structured schema.json file representing your DynamoDB tables, indexes, entities, fields, and acc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('src/dynamodb-mcp-server/AGENTS.md')
    assert '2. **dynamodb_data_model_validation** - Automated validation using DynamoDB Local. Validates your DynamoDB data model by loading dynamodb_data_model.json, setting up DynamoDB Local, creating tables wi' in text, "expected to find: " + '2. **dynamodb_data_model_validation** - Automated validation using DynamoDB Local. Validates your DynamoDB data model by loading dynamodb_data_model.json, setting up DynamoDB Local, creating tables wi'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('src/dynamodb-mcp-server/AGENTS.md')
    assert 'This is the **AWS DynamoDB MCP Server** - an official AWS Labs Model Context Protocol (MCP) server that provides DynamoDB expert design guidance and data modeling assistance. The project is built with' in text, "expected to find: " + 'This is the **AWS DynamoDB MCP Server** - an official AWS Labs Model Context Protocol (MCP) server that provides DynamoDB expert design guidance and data modeling assistance. The project is built with'[:80]

