"""
Task: posthog-featllma-enable-clustering-read-tools
Repo: PostHog/posthog @ d67b05b91702b8d6c5fcf03a1361d1afe7daf287
PR:   53107

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

import yaml

REPO = "/workspace/posthog"

SCRIPT_DIR = str(
    Path(REPO)
    / "products"
    / "llm_analytics"
    / "skills"
    / "exploring-llm-clusters"
    / "scripts"
)


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess within the repo."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified YAML and Python files parse without errors."""
    tools_path = Path(REPO) / "products" / "llm_analytics" / "mcp" / "tools.yaml"
    data = yaml.safe_load(tools_path.read_text())
    assert isinstance(data, dict), "tools.yaml must parse as a YAML mapping"
    assert "tools" in data, "tools.yaml must have a 'tools' key"

    script_path = Path(SCRIPT_DIR) / "print_clusters.py"
    if script_path.exists():
        import py_compile
        py_compile.compile(str(script_path), doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — MCP tool enablement
# ---------------------------------------------------------------------------

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

def test_ruff_excludes_skill_scripts():
    """pyproject.toml ruff exclude must include skill scripts path."""
    pyproject = Path(REPO) / "pyproject.toml"
    content = pyproject.read_text()
    assert re.search(
        r"products/\*/skills/\*/scripts", content
    ), "pyproject.toml must exclude products/*/skills/*/scripts from ruff"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — print_clusters.py functionality via subprocess
# ---------------------------------------------------------------------------

def test_print_clusters_parses_sql_result():
    """print_clusters.py parse_result extracts clusters from SQL result format."""
    test_input = json.dumps({
        "columns": ["run_id", "level", "clusters"],
        "results": [
            [
                "123_trace_20260328_100000",
                "trace",
                json.dumps([
                    {"cluster_id": 0, "size": 10, "title": "Auth flows",
                     "description": "Login traces", "traces": {}},
                    {"cluster_id": 1, "size": 5, "title": "Search queries",
                     "description": "Search traces", "traces": {}},
                ]),
            ]
        ],
    })

    r = _run_python(f"""
import json, sys
sys.path.insert(0, {SCRIPT_DIR!r})
from print_clusters import parse_result

sql_result = json.loads({test_input!r})
clusters, meta = parse_result(sql_result)
assert len(clusters) == 2, f"Expected 2 clusters, got {{len(clusters)}}"
assert clusters[0]["cluster_id"] == 0
assert clusters[1]["title"] == "Search queries"
assert meta.get("run_id") == "123_trace_20260328_100000"
assert meta.get("level") == "trace"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_print_clusters_parses_direct_array():
    """print_clusters.py parse_result handles direct clusters array input."""
    direct_json = json.dumps([
        {"cluster_id": -1, "size": 3, "title": "Noise", "traces": {}},
        {"cluster_id": 0, "size": 20, "title": "Main", "traces": {}},
    ])

    r = _run_python(f"""
import json, sys
sys.path.insert(0, {SCRIPT_DIR!r})
from print_clusters import parse_result

direct = json.loads({direct_json!r})
clusters, meta = parse_result(direct)
assert len(clusters) == 2, f"Expected 2 clusters, got {{len(clusters)}}"
assert clusters[0]["cluster_id"] == -1, "First cluster should be noise"
assert meta == {{}}, "Direct array should have empty metadata"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_print_clusters_script_output():
    """print_clusters.py produces readable cluster summary when run as main."""
    script_path = Path(SCRIPT_DIR) / "print_clusters.py"
    assert script_path.exists(), "print_clusters.py must exist"

    test_file = Path(REPO) / "_eval_test_clusters.json"
    test_data = [
        {
            "cluster_id": 0, "size": 15, "title": "Auth flows",
            "description": "Login and signup traces",
            "traces": {
                "trace-1": {"distance_to_centroid": 0.1, "rank": 0,
                            "x": 1.0, "y": 2.0, "timestamp": "2026-03-28T10:00:00Z"},
            },
        },
        {
            "cluster_id": -1, "size": 3, "title": "Noise",
            "description": "Outlier traces", "traces": {},
        },
    ]
    try:
        test_file.write_text(json.dumps(test_data))
        r = subprocess.run(
            ["python3", str(script_path), str(test_file)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Script failed: {r.stderr}"
        assert "Auth flows" in r.stdout, "Output must include cluster title"
        assert "NOISE/OUTLIERS" in r.stdout, "Output must label noise cluster"
    finally:
        test_file.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — SKILL.md created with correct content
# ---------------------------------------------------------------------------

def test_skill_md_frontmatter():
    """SKILL.md must have YAML frontmatter with correct name and description."""
    skill_path = (
        Path(REPO) / "products" / "llm_analytics" / "skills"
        / "exploring-llm-clusters" / "SKILL.md"
    )
    assert skill_path.exists(), "SKILL.md must exist"
    content = skill_path.read_text()

    fm_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    assert fm_match, "SKILL.md must have YAML frontmatter"
    fm = yaml.safe_load(fm_match.group(1))
    assert fm.get("name") == "exploring-llm-clusters", (
        f"SKILL.md name must be 'exploring-llm-clusters', got {fm.get('name')}"
    )
    assert fm.get("description"), "SKILL.md must have a description in frontmatter"


def test_skill_md_references_tools():
    """SKILL.md must reference clustering MCP tools and execute-sql."""
    skill_path = (
        Path(REPO) / "products" / "llm_analytics" / "skills"
        / "exploring-llm-clusters" / "SKILL.md"
    )
    content = skill_path.read_text()

    assert "clustering-jobs-list" in content, (
        "SKILL.md must mention the clustering-jobs-list tool"
    )
    assert "clustering-jobs-retrieve" in content, (
        "SKILL.md must mention the clustering-jobs-retrieve tool"
    )
    assert "execute-sql" in content, (
        "SKILL.md must mention execute-sql for querying cluster events"
    )


def test_skill_md_documents_events():
    """SKILL.md must document cluster event types and key properties."""
    skill_path = (
        Path(REPO) / "products" / "llm_analytics" / "skills"
        / "exploring-llm-clusters" / "SKILL.md"
    )
    content = skill_path.read_text()

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


def test_skill_md_includes_sql():
    """SKILL.md must include SQL query patterns for exploring cluster events."""
    skill_path = (
        Path(REPO) / "products" / "llm_analytics" / "skills"
        / "exploring-llm-clusters" / "SKILL.md"
    )
    content = skill_path.read_text()

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
