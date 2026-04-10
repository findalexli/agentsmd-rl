"""
Task: posthog-llm-clustering-skill
Repo: PostHog/posthog @ d67b05b91702b8d6c5fcf03a1361d1afe7daf287
PR:   53107

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "/workspace/posthog"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / configuration validation
# ---------------------------------------------------------------------------

def test_tools_yaml_valid():
    """tools.yaml must be valid YAML."""
    import yaml
    tools_yaml = Path(f"{REPO}/products/llm_analytics/mcp/tools.yaml")
    if not tools_yaml.exists():
        return
    content = tools_yaml.read_text()
    parsed = yaml.safe_load(content)
    assert "tools" in parsed, "tools.yaml missing 'tools' key"


def test_pyproject_toml_valid():
    """pyproject.toml must be valid TOML."""
    import tomllib
    pyproject = Path(f"{REPO}/pyproject.toml")
    content = pyproject.read_text()
    parsed = tomllib.loads(content)
    assert "tool" in parsed, "pyproject.toml missing 'tool' section"


def test_package_json_valid():
    """package.json must be valid JSON."""
    package_json = Path(f"{REPO}/package.json")
    content = package_json.read_text()
    parsed = json.loads(content)
    assert "lint-staged" in parsed, "package.json missing 'lint-staged' section"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral/config tests
# ---------------------------------------------------------------------------

def test_clustering_jobs_list_enabled():
    """llm-analytics-clustering-jobs-list tool must be enabled via YAML parsing."""
    result = subprocess.run(
        [sys.executable, "-c", f"""
import yaml
with open("{REPO}/products/llm_analytics/mcp/tools.yaml") as f:
    data = yaml.safe_load(f)
tool = data.get("tools", {{}}).get("llm-analytics-clustering-jobs-list", {{}})
assert tool.get("enabled") is True, "Tool not enabled"
assert tool.get("title") == "List clustering jobs", "Wrong title"
assert "llm_analytics:read" in tool.get("scopes", []), "Missing scope"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "PASS" in result.stdout


def test_clustering_jobs_retrieve_enabled():
    """llm-analytics-clustering-jobs-retrieve tool must be enabled via YAML parsing."""
    result = subprocess.run(
        [sys.executable, "-c", f"""
import yaml
with open("{REPO}/products/llm_analytics/mcp/tools.yaml") as f:
    data = yaml.safe_load(f)
tool = data.get("tools", {{}}).get("llm-analytics-clustering-jobs-retrieve", {{}})
assert tool.get("enabled") is True, "Tool not enabled"
assert tool.get("title") == "Get clustering job", "Wrong title"
assert "llm_analytics:read" in tool.get("scopes", []), "Missing scope"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "PASS" in result.stdout


def test_skill_directory_exists():
    """The exploring-llm-clusters skill directory must exist."""
    skill_dir = Path(f"{REPO}/products/llm_analytics/skills/exploring-llm-clusters")
    assert skill_dir.exists(), f"Skill directory does not exist: {skill_dir}"
    assert skill_dir.is_dir(), f"Skill path is not a directory: {skill_dir}"


def test_skill_md_exists_with_frontmatter():
    """SKILL.md must exist with proper frontmatter via YAML parsing."""
    result = subprocess.run(
        [sys.executable, "-c", f"""
import re
with open("{REPO}/products/llm_analytics/skills/exploring-llm-clusters/SKILL.md") as f:
    content = f.read()
# Check frontmatter
assert content.startswith("---"), "Missing frontmatter start"
fm_match = re.search(r'^---\\s*\\n(.*?)\\s*\\n---', content, re.DOTALL)
assert fm_match, "Missing frontmatter block"
fm = fm_match.group(1)
assert "name: exploring-llm-clusters" in fm, "Missing skill name"
assert "description:" in fm, "Missing description"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "PASS" in result.stdout


def test_skill_md_has_required_sections():
    """SKILL.md must document tools, clustering concepts, and workflows."""
    skill_md = Path(f"{REPO}/products/llm_analytics/skills/exploring-llm-clusters/SKILL.md")
    if not skill_md.exists():
        pytest.skip("SKILL.md not found")

    content = skill_md.read_text().lower()

    assert "## tools" in content, "Missing Tools section"
    assert "## how clustering works" in content, "Missing How clustering works section"
    assert "## workflow" in content or "## workflow:" in content, "Missing Workflow section"
    assert "## investigation patterns" in content, "Missing Investigation patterns section"
    assert "## tips" in content, "Missing Tips section"


def test_print_clusters_script_exists():
    """print_clusters.py helper script must exist."""
    script_path = Path(f"{REPO}/products/llm_analytics/skills/exploring-llm-clusters/scripts/print_clusters.py")
    assert script_path.exists(), "print_clusters.py does not exist"


def test_print_clusters_script_runnable():
    """print_clusters.py must execute without syntax errors."""
    script_path = Path(f"{REPO}/products/llm_analytics/skills/exploring-llm-clusters/scripts/print_clusters.py")
    if not script_path.exists():
        pytest.skip("print_clusters.py not found")

    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(script_path)],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, f"Script has syntax errors: {result.stderr}"


def test_print_clusters_script_functional():
    """print_clusters.py must correctly parse and format cluster data via subprocess execution."""
    script_path = Path(f"{REPO}/products/llm_analytics/skills/exploring-llm-clusters/scripts/print_clusters.py")
    if not script_path.exists():
        pytest.skip("print_clusters.py not found")

    # Create test cluster data - direct array format
    test_data = [
        {
            "cluster_id": 0,
            "size": 42,
            "title": "Test Cluster",
            "description": "Test description",
            "traces": {
                "trace-1": {"distance_to_centroid": 0.123, "rank": 0, "timestamp": "2026-03-28T10:00:00Z"}
            }
        },
        {
            "cluster_id": -1,
            "size": 5,
            "title": "Noise",
            "description": "Outliers",
            "traces": {}
        }
    ]

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_path = f.name

    try:
        # Execute the script via subprocess with the test data
        result = subprocess.run(
            [sys.executable, str(script_path), temp_path],
            capture_output=True, text=True, timeout=30,
        )
        output = result.stdout

        # Verify the output contains expected formatted content
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert "2 clusters" in output.lower() or "clusters" in output, "Output missing cluster summary"
        assert "Test Cluster" in output, "Output missing cluster title"
        assert "NOISE/OUTLIERS" in output or "(NOISE/OUTLIERS)" in output, "Output missing noise cluster labeling"
        assert "trace-1" in output or "dist=" in output, "Output missing trace details"
        assert "42 items" in output or "Size:  42" in output, "Output missing cluster size"
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_print_clusters_sql_format():
    """print_clusters.py must handle SQL result format via subprocess execution."""
    script_path = Path(f"{REPO}/products/llm_analytics/skills/exploring-llm-clusters/scripts/print_clusters.py")
    if not script_path.exists():
        pytest.skip("print_clusters.py not found")

    # Create SQL result format test data
    clusters_data = [
        {
            "cluster_id": 1,
            "size": 100,
            "title": "SQL Test Cluster",
            "description": "From SQL query",
            "traces": {"t1": {"rank": 0, "distance_to_centroid": 0.5}}
        }
    ]

    sql_result = {
        "results": [
            ["run-123", "trace", "job-456", "My Job", "2026-01-01", "2026-01-02", 150, json.dumps(clusters_data), "{}"]
        ],
        "columns": ["run_id", "level", "job_id", "job_name", "window_start", "window_end", "total_items", "clusters", "params"]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sql_result, f)
        temp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), temp_path],
            capture_output=True, text=True, timeout=30,
        )
        output = result.stdout

        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert "SQL Test Cluster" in output, "Output missing cluster title from SQL format"
        assert "run-123" in output or "Run:" in output, "Output missing run metadata"
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_pyproject_toml_has_ruff_exclusion():
    """pyproject.toml must exclude skill scripts from ruff via TOML parsing."""
    result = subprocess.run(
        [sys.executable, "-c", f"""
import tomllib
with open("{REPO}/pyproject.toml", "rb") as f:
    data = tomllib.load(f)
exclude = data.get("tool", {{}}).get("ruff", {{}}).get("exclude", [])
found = any("skills/*/scripts" in str(p) for p in exclude)
assert found, "Missing ruff exclusion for products/*/skills/*/scripts"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "PASS" in result.stdout


def test_package_json_has_lint_staged_exclusion():
    """package.json lint-staged must exclude skill scripts via JSON parsing."""
    result = subprocess.run(
        [sys.executable, "-c", f"""
import json
with open("{REPO}/package.json") as f:
    data = json.load(f)
lint_staged = data.get("lint-staged", {{}})
found = any("products/*/skills/*/scripts" in str(p) for p in lint_staged.keys())
assert found, "lint-staged missing exclusion for products/*/skills/*/scripts"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "PASS" in result.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural consistency
# ---------------------------------------------------------------------------

def test_skill_md_consistent_style():
    """SKILL.md follows existing skill documentation style."""
    skill_md = Path(f"{REPO}/products/llm_analytics/skills/exploring-llm-clusters/SKILL.md")
    if not skill_md.exists():
        pytest.skip("SKILL.md not found")

    content = skill_md.read_text()

    # Check for Markdown table format in Tools section
    assert "|" in content, "Missing table format in Tools section"

    # Check for code blocks
    assert "```" in content, "Missing code blocks"

    # Check for headers
    assert content.count("#") >= 5, "Insufficient header structure"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands
# ---------------------------------------------------------------------------

def test_repo_python_syntax():
    """Repo Python files compile without syntax errors (pass_to_pass)."""
    files_to_check = [
        f"{REPO}/products/llm_analytics/__init__.py",
        f"{REPO}/products/llm_analytics/backend/__init__.py",
    ]
    for filepath in files_to_check:
        if Path(filepath).exists():
            r = subprocess.run(
                [sys.executable, "-m", "py_compile", filepath],
                capture_output=True, text=True, timeout=30,
            )
            assert r.returncode == 0, f"Syntax error in {filepath}: {r.stderr}"


def test_repo_yaml_parses():
    """tools.yaml parses correctly via subprocess + pyyaml (pass_to_pass)."""
    # Install pyyaml and test YAML parsing in one subprocess
    r = subprocess.run(
        [sys.executable, "-c", f"""
import subprocess
import sys
# First install pyyaml
result = subprocess.run([sys.executable, "-m", "pip", "install", "pyyaml", "--quiet", "--break-system-packages"], capture_output=True)
# Then parse YAML
import yaml
with open("{REPO}/products/llm_analytics/mcp/tools.yaml") as f:
    data = yaml.safe_load(f)
assert "tools" in data, "Missing tools key"
print("YAML valid")
"""],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"YAML parsing failed: {r.stderr}"


def test_repo_clustering_tests_syntax():
    """Clustering test files have valid Python syntax (pass_to_pass)."""
    test_files = [
        f"{REPO}/products/llm_analytics/backend/api/test/test_clustering_job.py",
        f"{REPO}/products/llm_analytics/backend/api/test/test_clustering_config.py",
    ]
    for filepath in test_files:
        if Path(filepath).exists():
            r = subprocess.run(
                [sys.executable, "-m", "py_compile", filepath],
                capture_output=True, text=True, timeout=30,
            )
            assert r.returncode == 0, f"Syntax error in {filepath}: {r.stderr}"


# ---------------------------------------------------------------------------
# Imports (for pytest)
# ---------------------------------------------------------------------------

import pytest  # noqa: F401, E402
