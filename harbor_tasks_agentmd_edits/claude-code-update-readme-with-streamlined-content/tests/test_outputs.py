"""
Task: claude-code-update-readme-with-streamlined-content
Repo: anthropics/claude-code @ 0b881fcb4d7e0d223584aca58b27055084fffd0c
PR:   1537

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/claude-code"
README_PATH = f"{REPO}/README.md"
GIF_PATH = f"{REPO}/demo.gif"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests (all use subprocess.run)
# ---------------------------------------------------------------------------

def test_demo_gif_exists():
    """The demo.gif file exists and is a valid GIF file."""
    code = f"""
import sys
from pathlib import Path

gif_path = Path("{GIF_PATH}")
if not gif_path.exists():
    print("FAIL: demo.gif not found", file=sys.stderr)
    sys.exit(1)
if gif_path.stat().st_size == 0:
    print("FAIL: demo.gif is empty", file=sys.stderr)
    sys.exit(1)
# Verify it's actually a GIF by checking magic bytes
with open(gif_path, 'rb') as f:
    magic = f.read(6)
    if magic not in (b'GIF89a', b'GIF87a'):
        print(f"FAIL: Not a valid GIF file (magic bytes: {{magic}})", file=sys.stderr)
        sys.exit(1)
print("PASS: demo.gif exists and is valid")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_readme_has_gif_reference():
    """README.md contains the demo GIF reference with correct HTML tag."""
    code = f"""
import sys
from pathlib import Path

readme_path = Path("{README_PATH}")
content = readme_path.read_text()

# Check for the exact HTML img tag as specified in the PR
if '<img src="./demo.gif" />' not in content:
    print("FAIL: README missing correct demo.gif reference", file=sys.stderr)
    sys.exit(1)
print("PASS: README has correct demo.gif reference")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_readme_streamlined_description():
    """README has concise one-paragraph description instead of bullet list."""
    code = f"""
import sys
from pathlib import Path

readme_path = Path("{README_PATH}")
content = readme_path.read_text()

# Check old bullet points are removed
old_patterns = [
    "- Edit files and fix bugs",
    "- Answer questions about",
    "- Execute and fix tests",
    "- Search through git history",
]
for pattern in old_patterns:
    if pattern in content:
        print(f"FAIL: Old bullet pattern still present: {{pattern}}", file=sys.stderr)
        sys.exit(1)

# Check new description mentions terminal/IDE/GitHub
description_section = content.split("##")[0] if "##" in content else content
if "tag @claude on Github" not in description_section:
    print("FAIL: New description missing 'tag @claude on Github'", file=sys.stderr)
    sys.exit(1)

print("PASS: README has streamlined description")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_readme_simplified_get_started():
    """README has simplified 2-step get started section."""
    code = f"""
import sys
import re
from pathlib import Path

readme_path = Path("{README_PATH}")
content = readme_path.read_text()

# Check old npm prefix and OAuth warnings are removed
old_patterns = [
    "NPM prefix",
    "non-privileged user",
    "Complete the one-time OAuth",
]
for pattern in old_patterns:
    if pattern in content:
        print(f"FAIL: Old content still present: {{pattern}}", file=sys.stderr)
        sys.exit(1)

# Verify the Get started section exists
if "## Get started" not in content:
    print("FAIL: Missing '## Get started' section", file=sys.stderr)
    sys.exit(1)

# Extract the Get started section and count numbered steps
get_started_match = re.search(r'## Get started\\s+(.*?)(?=## |\\Z)', content, re.DOTALL)
if not get_started_match:
    print("FAIL: Could not parse Get started section", file=sys.stderr)
    sys.exit(1)

get_started_content = get_started_match.group(1)
# Count numbered list items (1. 2. etc.)
steps = re.findall(r'^\\d+\\.', get_started_content, re.MULTILINE)
if len(steps) != 2:
    print(f"FAIL: Expected 2 steps, found {{len(steps)}}: {{steps}}", file=sys.stderr)
    sys.exit(1)

print("PASS: README has simplified 2-step Get started section")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_readme_reporting_bugs_heading():
    """README has 'Reporting Bugs' as H2 (##) not H3 (###)."""
    code = f"""
import sys
from pathlib import Path

readme_path = Path("{README_PATH}")
content = readme_path.read_text()
lines = content.split('\\n')

found_h2 = False
found_h3 = False
for line in lines:
    stripped = line.strip()
    if stripped == "## Reporting Bugs":
        found_h2 = True
    if stripped == "### Reporting Bugs":
        found_h3 = True

if not found_h2:
    print("FAIL: Missing '## Reporting Bugs' (H2)", file=sys.stderr)
    sys.exit(1)
if found_h3:
    print("FAIL: Still has old '### Reporting Bugs' (H3)", file=sys.stderr)
    sys.exit(1)

print("PASS: Reporting Bugs is correctly H2")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_readme_data_usage_heading():
    """README has 'How we use your data' as H3 (###) not H4 (####)."""
    code = f"""
import sys
from pathlib import Path

readme_path = Path("{README_PATH}")
content = readme_path.read_text()
lines = content.split('\\n')

found_h3 = False
found_h4 = False
for line in lines:
    stripped = line.strip()
    if stripped == "### How we use your data":
        found_h3 = True
    if stripped == "#### How we use your data":
        found_h4 = True

if not found_h3:
    print("FAIL: Missing '### How we use your data' (H3)", file=sys.stderr)
    sys.exit(1)
if found_h4:
    print("FAIL: Still has old '#### How we use your data' (H4)", file=sys.stderr)
    sys.exit(1)

print("PASS: How we use your data is correctly H3")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-regression checks (also use subprocess.run)
# ---------------------------------------------------------------------------

def test_readme_has_key_elements():
    """README still contains essential elements that should not be removed."""
    code = f"""
import sys
from pathlib import Path

readme_path = Path("{README_PATH}")
content = readme_path.read_text()

required_elements = [
    "# Claude Code",
    "npm install -g @anthropic-ai/claude-code",
    "official documentation",
    "## Get started",
    "## Reporting Bugs",
]

for element in required_elements:
    if element not in content:
        print(f"FAIL: Missing essential element: {{element}}", file=sys.stderr)
        sys.exit(1)

print("PASS: README contains all essential elements")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_readme_valid_markdown():
    """README is valid markdown with proper structure."""
    code = f"""
import sys
from pathlib import Path

readme_path = Path("{README_PATH}")
content = readme_path.read_text()

# Basic markdown structure checks
if not content.strip().startswith("# Claude Code"):
    print("FAIL: README should start with main title", file=sys.stderr)
    sys.exit(1)

if "## Get started" not in content:
    print("FAIL: README missing 'Get started' section", file=sys.stderr)
    sys.exit(1)

if "```sh" not in content:
    print("FAIL: README missing shell code block", file=sys.stderr)
    sys.exit(1)

# Check for balanced backticks
if content.count("```") % 2 != 0:
    print("FAIL: Unbalanced code block backticks", file=sys.stderr)
    sys.exit(1)

print("PASS: README has valid markdown structure")
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout
