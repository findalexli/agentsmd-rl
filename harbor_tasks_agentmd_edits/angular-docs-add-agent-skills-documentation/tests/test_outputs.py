"""
Task: angular-docs-add-agent-skills-documentation
Repo: angular/angular @ 9d79ec6866645393bc8b01881e7e2165dd29d02d
PR:   67831

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/angular"

NAV_TS = Path(REPO) / "adev/src/app/routing/navigation-entries/index.ts"
AGENT_SKILLS_MD = Path(REPO) / "adev/src/content/ai/agent-skills.md"
OVERVIEW_MD = Path(REPO) / "adev/src/content/ai/overview.md"
DEV_SKILLS_README = Path(REPO) / "skills/dev-skills/README.md"


def _extract_build_with_ai_children(ts_content: str) -> list[dict]:
    """Parse the 'Build with AI' navigation children from the TS file."""
    match = re.search(
        r"label:\s*['\"]Build with AI['\"].*?children:\s*\[",
        ts_content,
        re.DOTALL,
    )
    if not match:
        return []

    # Walk to the matching closing bracket
    start = match.end()
    depth = 1
    pos = start
    while pos < len(ts_content) and depth > 0:
        if ts_content[pos] == "[":
            depth += 1
        elif ts_content[pos] == "]":
            depth -= 1
        pos += 1
    children_block = ts_content[start : pos - 1]

    # Parse each { label: '...', path: '...', ... } entry
    entries = []
    for m in re.finditer(r"\{[^}]*label:\s*['\"]([^'\"]+)['\"][^}]*\}", children_block, re.DOTALL):
        block = m.group(0)
        entry = {"label": m.group(1)}

        path_m = re.search(r"path:\s*['\"]([^'\"]+)['\"]", block)
        if path_m:
            entry["path"] = path_m.group(1)

        status_m = re.search(r"status:\s*['\"]([^'\"]+)['\"]", block)
        if status_m:
            entry["status"] = status_m.group(1)

        entries.append(entry)

    return entries


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structure checks
# ---------------------------------------------------------------------------


def test_syntax_check():
    """Navigation entries TypeScript file has balanced braces."""
    content = NAV_TS.read_text()
    assert content.count("{") == content.count("}"), "Unbalanced curly braces"
    assert content.count("[") == content.count("]"), "Unbalanced square brackets"
    assert content.count("(") == content.count(")"), "Unbalanced parentheses"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — navigation and documentation behavioral tests
# ---------------------------------------------------------------------------


def test_agent_skills_nav_entry():
    """Navigation includes Agent Skills entry with correct path (parsed via subprocess)."""
    script = f"""
import re, json
from pathlib import Path

content = Path("{NAV_TS}").read_text()

# Locate "Build with AI" children array
match = re.search(r"label:\\s*['\\\"]Build with AI['\\\"].*?children:\\s*\\[", content, re.DOTALL)
if not match:
    raise AssertionError("Build with AI section not found in navigation")

start = match.end()
depth = 1
pos = start
while pos < len(content) and depth > 0:
    if content[pos] == '[': depth += 1
    elif content[pos] == ']': depth -= 1
    pos += 1
block = content[start:pos-1]

# Find Agent Skills entry and its path
agent = re.search(r"label:\\s*['\\\"]Agent Skills['\\\"]", block)
if not agent:
    raise AssertionError("Agent Skills entry not found")

tail = block[agent.start():agent.start()+300]
path_m = re.search(r"path:\\s*['\\\"]([^'\\\"]+)['\\\"]", tail)
if not path_m:
    raise AssertionError("Agent Skills entry has no path")

result = {{"label": "Agent Skills", "path": path_m.group(1)}}
print(json.dumps(result))
"""
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Navigation parse failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["path"] == "ai/agent-skills", \
        f"Expected path 'ai/agent-skills', got '{data['path']}'"


def test_agent_skills_has_new_status():
    """Agent Skills nav entry is marked with status 'new'."""
    content = NAV_TS.read_text()
    children = _extract_build_with_ai_children(content)

    agent_entry = next((e for e in children if e["label"] == "Agent Skills"), None)
    assert agent_entry is not None, "Agent Skills entry not found in navigation"
    assert agent_entry.get("status") == "new", \
        f"Expected status 'new', got '{agent_entry.get('status')}'"


def test_agent_skills_doc_exists():
    """Agent Skills documentation page exists with required content."""
    assert AGENT_SKILLS_MD.exists(), "adev/src/content/ai/agent-skills.md must exist"
    content = AGENT_SKILLS_MD.read_text()

    assert "# Agent Skills" in content, "Must have 'Agent Skills' heading"
    assert "angular-developer" in content, "Must mention angular-developer skill"
    assert "angular-new-app" in content, "Must mention angular-new-app skill"
    assert "## Available Skills" in content, "Must have 'Available Skills' section"
    assert "## Using Agent Skills" in content, "Must have 'Using Agent Skills' section"


def test_overview_links_agent_skills():
    """AI overview page links to the new agent-skills documentation."""
    assert OVERVIEW_MD.exists(), "adev/src/content/ai/overview.md must exist"
    content = OVERVIEW_MD.read_text()

    pill_match = re.search(r'<docs-pill\s+href=["\']ai/agent-skills["\']', content)
    assert pill_match, "Overview must have a <docs-pill> linking to 'ai/agent-skills'"
    title_match = re.search(r'<docs-pill\s+href=["\']ai/agent-skills["\']\s+title=["\']Agent Skills["\']', content)
    assert title_match, "docs-pill must have title 'Agent Skills'"


def test_design_patterns_after_agent_skills():
    """Design Patterns entry appears after Agent Skills in navigation order."""
    script = f"""
import re, json
from pathlib import Path

content = Path("{NAV_TS}").read_text()

match = re.search(r"label:\\s*['\\\"]Build with AI['\\\"].*?children:\\s*\\[", content, re.DOTALL)
if not match:
    raise AssertionError("Build with AI section not found")

start = match.end()
depth = 1
pos = start
while pos < len(content) and depth > 0:
    if content[pos] == '[': depth += 1
    elif content[pos] == ']': depth -= 1
    pos += 1
block = content[start:pos-1]

# Find label positions — use finditer to get label positions in order
labels = [(m.start(), m.group(1)) for m in re.finditer(r"label:\\s*['\\\"]([^'\\\"]+)['\\\"]", block)]
agent_idx = next((i for i, (_, l) in enumerate(labels) if l == "Agent Skills"), None)
design_idx = next((i for i, (_, l) in enumerate(labels) if l == "Design Patterns"), None)

if agent_idx is None:
    raise AssertionError("Agent Skills not found in Build with AI children")
if design_idx is None:
    raise AssertionError("Design Patterns not found in Build with AI children")
if design_idx < agent_idx:
    raise AssertionError(f"Design Patterns (idx {{design_idx}}) must come after Agent Skills (idx {{agent_idx}})")

print(json.dumps({{"valid": True, "agent_idx": agent_idx, "design_idx": design_idx}}))
"""
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Navigation order check failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["valid"], "Design Patterns must appear after Agent Skills"


def test_dev_skills_readme_exists():
    """skills/dev-skills/README.md documents Angular skills and contributions."""
    assert DEV_SKILLS_README.exists(), "skills/dev-skills/README.md must exist"
    content = DEV_SKILLS_README.read_text()

    assert "Angular Skills" in content, "Must have Angular Skills heading or title"
    assert "angular-developer" in content, "Must document angular-developer skill"
    assert "angular-new-app" in content, "Must document angular-new-app skill"
    assert "Contributions" in content, "Must have Contributions section"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — AGENTS.md compliance
# ---------------------------------------------------------------------------


def test_commit_guidelines_reference():
    """AGENTS.md references commit guidelines — ensure they still exist."""
    contributing = Path(REPO) / "contributing-docs/commit-message-guidelines.md"
    assert contributing.exists(), \
        "Commit message guidelines doc must still exist (referenced by AGENTS.md)"
