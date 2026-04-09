"""
Task: posthog-featllma-expose-evaluation-summary-endpoint
Repo: PostHog/posthog @ c68338921ad4d5598a9830cca90c9e1f34c2dc8f
PR:   53656

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/posthog"
TOOLS_YAML = Path(REPO) / "products" / "llm_analytics" / "mcp" / "tools.yaml"
SKILLS_README = Path(REPO) / "products" / "llm_analytics" / "skills" / "README.md"
SKILL_FILE = (
    Path(REPO) / "products" / "llm_analytics" / "skills"
    / "exploring-llm-evaluations" / "SKILL.md"
)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_yaml_valid_syntax():
    """tools.yaml must parse as valid YAML without errors."""
    r = subprocess.run(
        ["python3", "-c", """
import yaml
data = yaml.safe_load(open('products/llm_analytics/mcp/tools.yaml'))
assert isinstance(data, dict), f"Expected dict, got {type(data)}"
assert 'tools' in data, "Missing 'tools' key"
assert isinstance(data['tools'], dict), "tools must be a mapping"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"YAML parse failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tool_enabled_in_yaml():
    """llm-analytics-evaluation-summary-create must be enabled in tools.yaml."""
    r = subprocess.run(
        ["python3", "-c", """
import yaml
data = yaml.safe_load(open('products/llm_analytics/mcp/tools.yaml'))
tool = data['tools']['llm-analytics-evaluation-summary-create']
assert tool.get('enabled') is True, (
    f"Tool enabled={tool.get('enabled')}, expected True"
)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_tool_has_description_and_title():
    """Enabled tool must have title and description metadata."""
    r = subprocess.run(
        ["python3", "-c", """
import yaml
data = yaml.safe_load(open('products/llm_analytics/mcp/tools.yaml'))
tool = data['tools']['llm-analytics-evaluation-summary-create']
assert 'title' in tool, "Missing 'title' field"
assert 'description' in tool, "Missing 'description' field"
assert len(str(tool['title'])) > 0, "Title is empty"
assert len(str(tool['description'])) > 10, "Description too short"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_skill_file_exists():
    """Exploring LLM evaluations skill file must exist with evaluation content."""
    r = subprocess.run(
        ["python3", "-c", """
from pathlib import Path
skill = Path('products/llm_analytics/skills/exploring-llm-evaluations/SKILL.md')
assert skill.exists(), f"Skill file not found: {skill}"
content = skill.read_text()
assert len(content) > 100, f"Skill file too short ({len(content)} chars)"
assert 'evaluation' in content.lower(), "Skill file doesn't mention evaluations"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_skills_readme_references_evaluations():
    """Skills README must list the exploring-llm-evaluations skill."""
    content = SKILLS_README.read_text()
    assert "exploring-llm-evaluations" in content, \
        "Skills README does not reference exploring-llm-evaluations"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .agents/skills/implementing-mcp-tools/SKILL.md:116-146
def test_tool_has_required_yaml_fields():
    """Enabled MCP tool must have scopes and annotations per implementing-mcp-tools guide."""
    r = subprocess.run(
        ["python3", "-c", """
import yaml
data = yaml.safe_load(open('products/llm_analytics/mcp/tools.yaml'))
tool = data['tools']['llm-analytics-evaluation-summary-create']

# Per implementing-mcp-tools SKILL.md "Key fields" section,
# enabled tools must have scopes and annotations.
assert 'scopes' in tool, "Missing 'scopes' (required per MCP tools guide)"
assert isinstance(tool['scopes'], list) and len(tool['scopes']) > 0, (
    "Scopes must be a non-empty list"
)

assert 'annotations' in tool, "Missing 'annotations' (required per MCP tools guide)"
ann = tool['annotations']
assert 'readOnly' in ann, "Missing annotations.readOnly"
assert 'destructive' in ann, "Missing annotations.destructive"
assert 'idempotent' in ann, "Missing annotations.idempotent"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [agent_config] fail_to_pass — .agents/skills/writing-skills/SKILL.md:42-49
def test_skill_has_frontmatter():
    """Skill file must have name and description frontmatter per writing-skills guide."""
    r = subprocess.run(
        ["python3", "-c", """
from pathlib import Path

skill = Path('products/llm_analytics/skills/exploring-llm-evaluations/SKILL.md')
assert skill.exists(), "Skill file not found"
content = skill.read_text()

# Check YAML frontmatter delimited by ---
assert content.startswith('---'), "Missing YAML frontmatter delimiter"
end = content.index('---', 3)
frontmatter = content[3:end]

assert 'name:' in frontmatter, "Missing 'name' in frontmatter"
assert 'description:' in frontmatter, "Missing 'description' in frontmatter"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout
