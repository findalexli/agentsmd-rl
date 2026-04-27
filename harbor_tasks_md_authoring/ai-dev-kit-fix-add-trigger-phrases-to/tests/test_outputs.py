"""Behavioral checks for ai-dev-kit-fix-add-trigger-phrases-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai-dev-kit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('databricks-skills/databricks-config/SKILL.md')
    assert 'description: "Manage Databricks workspace connections: check current workspace, switch profiles, list available workspaces, or authenticate to a new workspace. Use when the user mentions \\"switch work' in text, "expected to find: " + 'description: "Manage Databricks workspace connections: check current workspace, switch profiles, list available workspaces, or authenticate to a new workspace. Use when the user mentions \\"switch work'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('databricks-skills/databricks-docs/SKILL.md')
    assert 'description: "Databricks documentation reference via llms.txt index. Use when other skills do not cover a topic, looking up unfamiliar Databricks features, or needing authoritative docs on APIs, confi' in text, "expected to find: " + 'description: "Databricks documentation reference via llms.txt index. Use when other skills do not cover a topic, looking up unfamiliar Databricks features, or needing authoritative docs on APIs, confi'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('databricks-skills/databricks-lakebase-autoscale/SKILL.md')
    assert 'description: "Patterns and best practices for Lakebase Autoscaling (next-gen managed PostgreSQL). Use when creating or managing Lakebase Autoscaling projects, configuring autoscaling compute or scale-' in text, "expected to find: " + 'description: "Patterns and best practices for Lakebase Autoscaling (next-gen managed PostgreSQL). Use when creating or managing Lakebase Autoscaling projects, configuring autoscaling compute or scale-'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('databricks-skills/databricks-lakebase-provisioned/SKILL.md')
    assert 'description: "Patterns and best practices for Lakebase Provisioned (Databricks managed PostgreSQL) for OLTP workloads. Use when creating Lakebase instances, connecting applications or Databricks Apps ' in text, "expected to find: " + 'description: "Patterns and best practices for Lakebase Provisioned (Databricks managed PostgreSQL) for OLTP workloads. Use when creating Lakebase instances, connecting applications or Databricks Apps '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('databricks-skills/databricks-spark-structured-streaming/SKILL.md')
    assert 'description: "Comprehensive guide to Spark Structured Streaming for production workloads. Use when building streaming pipelines, working with Kafka ingestion, implementing Real-Time Mode (RTM), config' in text, "expected to find: " + 'description: "Comprehensive guide to Spark Structured Streaming for production workloads. Use when building streaming pipelines, working with Kafka ingestion, implementing Real-Time Mode (RTM), config'[:80]

