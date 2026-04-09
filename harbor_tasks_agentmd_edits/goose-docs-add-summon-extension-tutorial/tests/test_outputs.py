"""
Task: goose-docs-add-summon-extension-tutorial
Repo: block/goose @ e2d174ac1d4ed3304d9949f04572803467d343cb
PR:   #7310

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/goose"
DOCS = f"{REPO}/documentation/docs"
MCP = f"{DOCS}/mcp"


def _run(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_summon_mcp_file_created():
    """New summon-mcp.md documentation file exists with proper frontmatter."""
    r = _run(f"""
import re
from pathlib import Path

p = Path("{MCP}/summon-mcp.md")
assert p.exists(), f"File not found: {{p}}"
content = p.read_text()
assert len(content) > 500, "File too small, likely incomplete"

# Validate YAML frontmatter
match = re.match(r'---\\n(.*?)\\n---', content, re.DOTALL)
assert match, "No YAML frontmatter found"
fm = match.group(1)
assert 'title:' in fm, "Missing 'title' in frontmatter"
assert 'Summon' in fm, "Frontmatter should mention Summon"
assert 'description:' in fm, "Missing 'description' in frontmatter"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_summon_mcp_example_content():
    """summon-mcp.md has Configuration, Example Usage, and references skills/recipes."""
    r = _run(f"""
from pathlib import Path

content = Path("{MCP}/summon-mcp.md").read_text()
assert '## Configuration' in content, "Missing Configuration section"
assert '## Example Usage' in content, "Missing Example Usage section"
assert 'skill' in content.lower(), "Should reference skills"
assert 'recipe' in content.lower(), "Should reference recipes"
assert 'subagent' in content.lower(), "Should reference subagents"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_skills_mcp_deprecated():
    """skills-mcp.md has deprecation caution with link to Summon extension."""
    r = _run(f"""
from pathlib import Path

content = Path("{MCP}/skills-mcp.md").read_text()
# Check for Docusaurus caution admonition
assert 'Deprecated' in content, "Missing deprecation notice"
assert 'summon-mcp' in content, "Should link to Summon extension as replacement"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_using_extensions_list_summon():
    """using-extensions.md lists Summon in built-in extensions instead of Skills."""
    r = _run(f"""
from pathlib import Path

content = Path("{DOCS}/getting-started/using-extensions.md").read_text()
assert 'summon-mcp' in content, "Should link to summon-mcp"
assert 'Summon' in content, "Should reference Summon extension"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_using_skills_guide_summon():
    """using-skills.md references Summon extension instead of Skills."""
    r = _run(f"""
from pathlib import Path

content = Path("{DOCS}/guides/context-engineering/using-skills.md").read_text()
assert 'summon-mcp' in content, "Should link to summon-mcp"
assert 'Summon' in content, "Should reference Summon extension"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_playwright_tutorial_summon():
    """playwright-skill.md references Summon extension with correct component."""
    r = _run(f"""
from pathlib import Path

content = Path("{DOCS}/tutorials/playwright-skill.md").read_text()
assert 'summon-mcp' in content, "Should link to summon-mcp"
assert 'extensionName="Summon"' in content, 'Should have extensionName="Summon"'
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_remotion_tutorial_summon():
    """remotion-video-creation.md references Summon extension."""
    r = _run(f"""
from pathlib import Path

content = Path("{DOCS}/tutorials/remotion-video-creation.md").read_text()
assert 'summon-mcp' in content, "Should link to summon-mcp"
assert 'Summon' in content, "Should reference Summon extension"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_summon_retro_image():
    """summon-retro-site.png screenshot exists in static directory."""
    r = _run(f"""
from pathlib import Path

img = Path("{REPO}/documentation/static/img/summon-retro-site.png")
assert img.exists(), "summon-retro-site.png not found in static/img/"
assert img.stat().st_size > 1000, "Image file is too small"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and gold
# ---------------------------------------------------------------------------

def test_documentation_npm_test():
    """Repo's documentation npm test passes (pass_to_pass)."""
    install_node = """
curl -fsSL https://deb.nodesource.com/setup_20.x | bash - 2>/dev/null
apt-get install -y nodejs 2>/dev/null
"""
    r = subprocess.run(
        ["bash", "-c", install_node],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Install npm deps and run tests
    r = subprocess.run(
        ["bash", "-c", f"cd {REPO}/documentation && npm ci --silent 2>&1 | tail -3 && npm test"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Documentation npm test failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_documentation_build():
    """Repo's documentation build passes (pass_to_pass)."""
    install_node = """
curl -fsSL https://deb.nodesource.com/setup_20.x | bash - 2>/dev/null
apt-get install -y nodejs 2>/dev/null
"""
    r = subprocess.run(
        ["bash", "-c", install_node],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Install npm deps and run build
    r = subprocess.run(
        ["bash", "-c", f"cd {REPO}/documentation && npm ci --silent 2>&1 | tail -3 && npm run build 2>&1 | tail -30"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Documentation build failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + validation
# ---------------------------------------------------------------------------


def test_existing_markdown_valid():
    """Pre-existing markdown files still parse correctly after changes."""
    r = _run(f"""
from pathlib import Path
import re

files = [
    "{MCP}/skills-mcp.md",
    "{DOCS}/getting-started/using-extensions.md",
    "{DOCS}/guides/context-engineering/using-skills.md",
    "{DOCS}/tutorials/playwright-skill.md",
    "{DOCS}/tutorials/remotion-video-creation.md",
]

for f in files:
    p = Path(f)
    assert p.exists(), f"Missing: {{f}}"
    content = p.read_text()
    assert len(content) > 50, f"File too small: {{f}}"
    assert '\\x00' not in content, f"Null bytes in: {{f}}"
    # Validate frontmatter if present
    if content.startswith('---'):
        match = re.match(r'---\\n(.*?)\\n---', content, re.DOTALL)
        assert match, f"Invalid frontmatter in: {{f}}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout
