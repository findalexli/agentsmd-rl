"""
Task: posthog-featllma-enable-clustering-read-tools
Repo: PostHog/posthog @ d67b05b91702b8d6c5fcf03a1361d1afe7daf287
PR:   53107

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import sys
from pathlib import Path

import yaml

REPO = "/workspace/posthog"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified YAML and Python files parse without errors."""
    # tools.yaml parses as valid YAML
    tools_path = Path(REPO) / "products" / "llm_analytics" / "mcp" / "tools.yaml"
    data = yaml.safe_load(tools_path.read_text())
    assert isinstance(data, dict), "tools.yaml must parse as a YAML mapping"
    assert "tools" in data, "tools.yaml must have a 'tools' key"

    # print_clusters.py compiles as valid Python
    script_path = (
        Path(REPO)
        / "products"
        / "llm_analytics"
        / "skills"
        / "exploring-llm-clusters"
        / "scripts"
        / "print_clusters.py"
    )
    if script_path.exists():
        import py_compile

        py_compile.compile(str(script_path), doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests: MCP tool enablement
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_clustering_list_tool_enabled():
    """clustering-jobs-list tool must be enabled with read scope and readOnly annotation."""
    tools_path = Path(REPO) / "products" / "llm_analytics" / "mcp" / "tools.yaml"
    data = yaml.safe_load(tools_path.read_text())
    tools = data["tools"]

    tool = tools.get("llm-analytics-clustering-jobs-list")
    assert tool is not None, "llm-analytics-clustering-jobs-list tool must exist"
    assert tool.get("enabled") is True, "clustering-jobs-list must be enabled"
    scopes = tool.get("scopes", [])
    assert any(
        "read" in s for s in scopes
    ), f"clustering-jobs-list must have a read scope, got {scopes}"
    annotations = tool.get("annotations", {})
    assert annotations.get("readOnly") is True, "clustering-jobs-list must be readOnly"
    assert annotations.get("destructive") is False, "clustering-jobs-list must not be destructive"


# [pr_diff] fail_to_pass
def test_clustering_retrieve_tool_enabled():
    """clustering-jobs-retrieve tool must be enabled with read scope and readOnly annotation."""
    tools_path = Path(REPO) / "products" / "llm_analytics" / "mcp" / "tools.yaml"
    data = yaml.safe_load(tools_path.read_text())
    tools = data["tools"]

    tool = tools.get("llm-analytics-clustering-jobs-retrieve")
    assert tool is not None, "llm-analytics-clustering-jobs-retrieve tool must exist"
    assert tool.get("enabled") is True, "clustering-jobs-retrieve must be enabled"
    scopes = tool.get("scopes", [])
    assert any(
        "read" in s for s in scopes
    ), f"clustering-jobs-retrieve must have a read scope, got {scopes}"
    annotations = tool.get("annotations", {})
    assert annotations.get("readOnly") is True, "clustering-jobs-retrieve must be readOnly"


# [pr_diff] fail_to_pass
def test_clustering_tools_have_descriptions():
    """Both clustering tools must have meaningful descriptions mentioning cluster concepts."""
    tools_path = Path(REPO) / "products" / "llm_analytics" / "mcp" / "tools.yaml"
    data = yaml.safe_load(tools_path.read_text())
    tools = data["tools"]

    list_tool = tools["llm-analytics-clustering-jobs-list"]
    desc_list = (list_tool.get("description") or "").lower()
    assert "clustering" in desc_list or "cluster" in desc_list, (
        "list tool description must mention clustering"
    )
    assert "job" in desc_list or "configuration" in desc_list, (
        "list tool description must mention jobs or configurations"
    )

    ret_tool = tools["llm-analytics-clustering-jobs-retrieve"]
    desc_ret = (ret_tool.get("description") or "").lower()
    assert "clustering" in desc_ret or "cluster" in desc_ret, (
        "retrieve tool description must mention clustering"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — lint exclusion for skill scripts
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_ruff_excludes_skill_scripts():
    """pyproject.toml ruff exclude must include skill scripts path."""
    pyproject = Path(REPO) / "pyproject.toml"
    content = pyproject.read_text()
    assert re.search(
        r"products/\*/skills/\*/scripts", content
    ), "pyproject.toml must exclude products/*/skills/*/scripts from ruff"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — print_clusters.py functionality
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_print_clusters_parses_sql_result():
    """print_clusters.py parse_result must extract clusters from SQL result format."""
    script_dir = (
        Path(REPO)
        / "products"
        / "llm_analytics"
        / "skills"
        / "exploring-llm-clusters"
        / "scripts"
    )
    sys.path.insert(0, str(script_dir))
    try:
        import importlib

        mod = importlib.import_module("print_clusters")

        sql_result = {
            "columns": ["run_id", "level", "clusters"],
            "results": [
                [
                    "123_trace_20260328_100000",
                    "trace",
                    json.dumps(
                        [
                            {
                                "cluster_id": 0,
                                "size": 10,
                                "title": "Auth flows",
                                "description": "Login traces",
                                "traces": {},
                            },
                            {
                                "cluster_id": 1,
                                "size": 5,
                                "title": "Search queries",
                                "description": "Search traces",
                                "traces": {},
                            },
                        ]
                    ),
                ]
            ],
        }

        clusters, meta = mod.parse_result(sql_result)
        assert len(clusters) == 2, f"Expected 2 clusters, got {len(clusters)}"
        assert clusters[0]["cluster_id"] == 0
        assert clusters[1]["title"] == "Search queries"
        assert meta.get("run_id") == "123_trace_20260328_100000"
        assert meta.get("level") == "trace"
    finally:
        sys.path.pop(0)
        if "print_clusters" in sys.modules:
            del sys.modules["print_clusters"]


# [pr_diff] fail_to_pass
def test_print_clusters_parses_direct_array():
    """print_clusters.py parse_result must handle a direct clusters array."""
    script_dir = (
        Path(REPO)
        / "products"
        / "llm_analytics"
        / "skills"
        / "exploring-llm-clusters"
        / "scripts"
    )
    sys.path.insert(0, str(script_dir))
    try:
        import importlib

        mod = importlib.import_module("print_clusters")

        direct = [
            {"cluster_id": -1, "size": 3, "title": "Noise", "traces": {}},
            {"cluster_id": 0, "size": 20, "title": "Main", "traces": {}},
        ]

        clusters, meta = mod.parse_result(direct)
        assert len(clusters) == 2, f"Expected 2 clusters, got {len(clusters)}"
        assert clusters[0]["cluster_id"] == -1, "First cluster should be noise"
        assert meta == {}, "Direct array should have empty metadata"
    finally:
        sys.path.pop(0)
        if "print_clusters" in sys.modules:
            del sys.modules["print_clusters"]


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — SKILL.md created with correct content
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    fm_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    assert fm_match, "SKILL.md must have YAML frontmatter"
    fm = yaml.safe_load(fm_match.group(1))
    assert fm.get("name") == "exploring-llm-clusters", (
        f"SKILL.md name must be 'exploring-llm-clusters', got {fm.get('name')}"
    )
    assert fm.get("description"), "SKILL.md must have a description in frontmatter"


# [config_edit] fail_to_pass

    assert "clustering-jobs-list" in content, (
        "SKILL.md must mention the clustering-jobs-list tool"
    )
    assert "clustering-jobs-retrieve" in content, (
        "SKILL.md must mention the clustering-jobs-retrieve tool"
    )
    assert "execute-sql" in content, (
        "SKILL.md must mention execute-sql for querying cluster events"
    )


# [config_edit] fail_to_pass

    assert "$ai_trace_clusters" in content, (
        "SKILL.md must document $ai_trace_clusters event type"
    )
    assert "$ai_generation_clusters" in content, (
        "SKILL.md must document $ai_generation_clusters event type"
    )
    assert "$ai_clustering_run_id" in content, (
        "SKILL.md must document $ai_clustering_run_id property"
    )
    assert "cluster_id" in content, "SKILL.md must document cluster_id field"


# [config_edit] fail_to_pass

    assert "SELECT" in content, "SKILL.md must include SQL query examples"
    assert "FROM events" in content, (
        "SKILL.md must include SQL queries against events table"
    )
    assert re.search(
        r"WHERE.*event.*\$ai_trace_clusters", content, re.DOTALL
    ), "SKILL.md must show SQL filtering on $ai_trace_clusters"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — tool naming conventions
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass
def test_tool_names_valid():
    """All enabled tool names must be kebab-case and <= 52 chars per MCP naming rules."""
    tools_path = Path(REPO) / "products" / "llm_analytics" / "mcp" / "tools.yaml"
    data = yaml.safe_load(tools_path.read_text())
    tools = data["tools"]

    kebab_re = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
    for name, cfg in tools.items():
        if cfg.get("enabled"):
            assert len(name) <= 52, f"Tool name '{name}' exceeds 52 chars ({len(name)})"
            assert kebab_re.match(name), f"Tool name '{name}' is not valid kebab-case"


# [agent_config] pass_to_pass
def test_skill_name_gerund_kebab():
    """Skill directory name must be kebab-case with gerund form per writing-skills guide."""
    skill_dir = (
        Path(REPO)
        / "products"
        / "llm_analytics"
        / "skills"
        / "exploring-llm-clusters"
    )
    assert skill_dir.is_dir(), "Skill directory must exist at expected path"
    dirname = skill_dir.name
    assert re.match(
        r"^[a-z0-9]+(-[a-z0-9]+)*$", dirname
    ), f"Skill directory '{dirname}' must be kebab-case"
    assert re.match(
        r"^[a-z]+-?[a-z]*ing", dirname
    ), f"Skill directory '{dirname}' should use gerund form (e.g. exploring-*)"
