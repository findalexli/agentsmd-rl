"""
Task: posthog-llm-clustering-mcp-skill
Repo: PostHog/posthog @ d67b05b91702b8d6c5fcf03a1361d1afe7daf287
PR:   53107

Enable clustering read MCP tools and add exploring-llm-clusters skill.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

REPO = "/workspace/posthog"
TOOLS_YAML = os.path.join(REPO, "products", "llm_analytics", "mcp", "tools.yaml")
SKILL_DIR = os.path.join(REPO, "products", "llm_analytics", "skills", "exploring-llm-clusters")
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")
PRINT_CLUSTERS = os.path.join(SKILL_DIR, "scripts", "print_clusters.py")
PYPROJECT = os.path.join(REPO, "pyproject.toml")
PACKAGE_JSON = os.path.join(REPO, "package.json")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_tools_yaml() -> dict:
    with open(TOOLS_YAML) as f:
        return yaml.safe_load(f)


def _run_print_clusters(data: dict, timeout: int = 15) -> subprocess.CompletedProcess:
    """Write data to a temp JSON file, run print_clusters.py on it."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        tmppath = f.name
    try:
        return subprocess.run(
            [sys.executable, PRINT_CLUSTERS, tmppath],
            capture_output=True, text=True, timeout=timeout,
        )
    finally:
        os.unlink(tmppath)


# Sample cluster data for testing print_clusters.py
SAMPLE_CLUSTERS = [
    {
        "cluster_id": 0,
        "size": 42,
        "title": "User authentication flows",
        "description": "Traces involving login, signup, and token refresh operations",
        "traces": {
            "trace-001": {"distance_to_centroid": 0.1, "rank": 0, "x": -2.0, "y": 1.5, "timestamp": "2026-03-28T10:00:00Z"},
            "trace-002": {"distance_to_centroid": 0.3, "rank": 1, "x": -2.1, "y": 1.4, "timestamp": "2026-03-28T11:00:00Z"},
        },
        "centroid_x": -2.05,
        "centroid_y": 1.45,
    },
    {
        "cluster_id": -1,
        "size": 5,
        "title": "Noise",
        "description": "Outlier traces",
        "traces": {
            "trace-003": {"distance_to_centroid": 2.0, "rank": 0, "x": 10.0, "y": -5.0, "timestamp": "2026-03-28T12:00:00Z"},
        },
        "centroid_x": 10.0,
        "centroid_y": -5.0,
    },
]


# ---------------------------------------------------------------------------
# Code behavior tests (fail-to-pass, pr_diff)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_clustering_list_tool_enabled():
    """tools.yaml enables llm-analytics-clustering-jobs-list with scopes and annotations."""
    data = _load_tools_yaml()
    tools = data.get("tools", {})
    tool = tools.get("llm-analytics-clustering-jobs-list", {})
    assert tool.get("enabled") is True, "clustering-jobs-list must be enabled"
    scopes = tool.get("scopes", [])
    assert "llm_analytics:read" in scopes, "must have llm_analytics:read scope"
    ann = tool.get("annotations", {})
    assert ann.get("readOnly") is True, "must be readOnly"
    assert ann.get("destructive") is False, "must be non-destructive"
    assert tool.get("title"), "must have a title"
    assert tool.get("description"), "must have a description"


# [pr_diff] fail_to_pass
def test_clustering_retrieve_tool_enabled():
    """tools.yaml enables llm-analytics-clustering-jobs-retrieve with scopes and annotations."""
    data = _load_tools_yaml()
    tools = data.get("tools", {})
    tool = tools.get("llm-analytics-clustering-jobs-retrieve", {})
    assert tool.get("enabled") is True, "clustering-jobs-retrieve must be enabled"
    scopes = tool.get("scopes", [])
    assert "llm_analytics:read" in scopes, "must have llm_analytics:read scope"
    ann = tool.get("annotations", {})
    assert ann.get("readOnly") is True, "must be readOnly"
    assert ann.get("destructive") is False, "must be non-destructive"
    assert tool.get("title"), "must have a title"
    assert tool.get("description"), "must have a description"


# [pr_diff] fail_to_pass
def test_print_clusters_direct_array():
    """print_clusters.py correctly parses a direct cluster array and prints summary."""
    r = _run_print_clusters(SAMPLE_CLUSTERS)
    assert r.returncode == 0, f"print_clusters.py failed: {r.stderr}"
    output = r.stdout
    assert "2 clusters" in output, f"Expected '2 clusters', got: {output[:200]}"
    assert "47 total items" in output, f"Expected '47 total items', got: {output[:200]}"
    assert "User authentication flows" in output, "Should show cluster title"
    assert "NOISE/OUTLIERS" in output, "Noise cluster should be labeled"
    assert "trace-001" in output, "Top traces should be listed"


# [pr_diff] fail_to_pass
def test_print_clusters_sql_result():
    """print_clusters.py correctly parses SQL result format with metadata."""
    sql_result = {
        "columns": ["run_id", "level", "clusters", "total_items"],
        "results": [[
            "1_trace_20260328_100000",
            "trace",
            json.dumps(SAMPLE_CLUSTERS),
            47,
        ]],
    }
    r = _run_print_clusters(sql_result)
    assert r.returncode == 0, f"print_clusters.py failed on SQL format: {r.stderr}"
    output = r.stdout
    assert "1_trace_20260328_100000" in output, "Should show run_id from metadata"
    assert "trace" in output, "Should show level from metadata"
    assert "User authentication flows" in output, "Should parse clusters from SQL column"


# [pr_diff] fail_to_pass
def test_pyproject_ruff_excludes_skills():
    """pyproject.toml excludes skill scripts from ruff linting."""
    content = Path(PYPROJECT).read_text()
    assert "products/*/skills/*/scripts" in content, \
        "pyproject.toml must exclude 'products/*/skills/*/scripts' from ruff"


# [pr_diff] fail_to_pass
def test_package_json_excludes_skills():
    """package.json lint-staged excludes skill scripts from Python linting."""
    content = Path(PACKAGE_JSON).read_text()
    assert "products/*/skills/*/scripts/*" in content, \
        "package.json must exclude skill scripts from lint-staged glob"


# ---------------------------------------------------------------------------
# Config/documentation update tests (fail-to-pass)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_frontmatter():
    """SKILL.md has required frontmatter (name and description)."""
    assert Path(SKILL_MD).is_file(), "SKILL.md must exist"
    content = Path(SKILL_MD).read_text()
    assert content.startswith("---"), "SKILL.md must have YAML frontmatter"
    # Parse frontmatter
    parts = content.split("---", 2)
    assert len(parts) >= 3, "SKILL.md must have opening and closing frontmatter delimiters"
    fm = yaml.safe_load(parts[1])
    assert fm.get("name"), "Frontmatter must have 'name'"
    assert fm.get("description"), "Frontmatter must have 'description'"
    # Name should be lowercase kebab-case
    name = fm["name"]
    assert name == name.lower(), f"Skill name must be lowercase: {name}"
    assert " " not in name, f"Skill name must be kebab-case (no spaces): {name}"


# [pr_diff] fail_to_pass
def test_skill_md_cluster_documentation():
    """SKILL.md documents cluster event schema with key event properties."""
    content = Path(SKILL_MD).read_text()
    # Must document the cluster event names
    assert "$ai_trace_clusters" in content, "Must document $ai_trace_clusters event"
    assert "$ai_generation_clusters" in content, "Must document $ai_generation_clusters event"
    # Must document key cluster properties
    assert "$ai_clustering_run_id" in content, "Must document $ai_clustering_run_id property"
    assert "$ai_clusters" in content, "Must document $ai_clusters property"
    assert "cluster_id" in content, "Must document cluster_id field"
    # Must explain the noise cluster
    assert "-1" in content, "Must document noise/outlier cluster (cluster_id: -1)"


# [pr_diff] fail_to_pass
def test_skill_md_investigation_workflow():
    """SKILL.md provides investigation workflows for exploring clusters."""
    content = Path(SKILL_MD).read_text()
    # Must have SQL query patterns (the core of the skill)
    assert "SELECT" in content.upper(), "Must include SQL query examples"
    assert "events" in content.lower(), "SQL must query events table"
    # Must reference the MCP tools
    assert "clustering-jobs-list" in content or "clustering_jobs_list" in content, \
        "Must reference clustering-jobs-list tool"
    assert "clustering-jobs-retrieve" in content or "clustering_jobs_retrieve" in content, \
        "Must reference clustering-jobs-retrieve tool"
    # Must have investigation patterns (common questions/answers)
    assert "cost" in content.lower() or "latency" in content.lower(), \
        "Should cover cost/latency investigation patterns"


# ---------------------------------------------------------------------------
# Agent config compliance (pass-to-pass, agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .agents/skills/writing-skills/SKILL.md:44
def test_skill_name_convention():
    """Skill name follows writing-skills convention: lowercase kebab-case, gerund form."""
    content = Path(SKILL_MD).read_text()
    parts = content.split("---", 2)
    fm = yaml.safe_load(parts[1])
    name = fm.get("name", "")
    # Gerund form: should end in -ing or -ings (e.g., "exploring-llm-clusters")
    # Check for a component ending in -ing
    parts = name.split("-")
    has_gerund = any(p.endswith("ing") for p in parts)
    assert has_gerund, \
        f"Skill name should use gerund form (e.g., 'exploring-*') per writing-skills guide: {name}"
    # Kebab-case: only lowercase letters, digits, hyphens
    for ch in name:
        assert ch in "abcdefghijklmnopqrstuvwxyz0123456789-", \
            f"Skill name must be lowercase kebab-case, found '{ch}'"
