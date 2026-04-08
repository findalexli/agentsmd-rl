"""
Task: lotti-fix-flickering-projects-page
Repo: matthiasn/lotti @ 33bd45088097cadb36fbc6930f611513cef0ba2e
PR:   2882

Verify: (1) skipLoadingOnReload: true is a named parameter of recordAsync.when(),
        (2) feature README documents the live-refresh behavior.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/lotti"

DETAIL_PAGE = Path(REPO) / "lib/features/projects/ui/pages/project_details_page.dart"
README = Path(REPO) / "lib/features/projects/README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Dart file has balanced braces and parentheses."""
    src = DETAIL_PAGE.read_text()
    assert src.count("{") == src.count("}"), "Unbalanced braces in project_details_page.dart"
    assert src.count("(") == src.count(")"), "Unbalanced parentheses in project_details_page.dart"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral fix
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skip_loading_on_reload_in_when():
    """recordAsync.when() includes skipLoadingOnReload: true as a named parameter."""
    r = subprocess.run(
        [
            "python3", "-c",
            r"""
import re, json, sys

dart = open("/workspace/lotti/lib/features/projects/ui/pages/project_details_page.dart").read()

match = re.search(r'recordAsync\.when\(', dart)
if not match:
    print(json.dumps({"ok": False, "error": "recordAsync.when() call not found"}))
    sys.exit(0)

# Walk the parenthesised body, respecting nesting
start = match.end()
depth = 1
pos = start
while pos < len(dart) and depth > 0:
    ch = dart[pos]
    if ch == '(':
        depth += 1
    elif ch == ')':
        depth -= 1
    pos += 1

when_body = dart[start:pos - 1]

if 'skipLoadingOnReload' not in when_body:
    print(json.dumps({"ok": False, "error": "skipLoadingOnReload not found inside .when() body"}))
    sys.exit(0)

if not re.search(r'skipLoadingOnReload\s*:\s*true', when_body):
    print(json.dumps({"ok": False, "error": "skipLoadingOnReload exists but is not set to true"}))
    sys.exit(0)

print(json.dumps({"ok": True}))
""",
        ],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Parse script failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result["ok"], f"skipLoadingOnReload check failed: {result.get('error', 'unknown')}"


# [pr_diff] fail_to_pass
def test_readme_documents_reload_behavior():
    """Feature README documents the skip-loading-on-reload behavior."""
    r = subprocess.run(
        [
            "python3", "-c",
            r"""
import json, sys

readme = open("/workspace/lotti/lib/features/projects/README.md").read()
lower = readme.lower()

# The README should explain that the previous content stays mounted during reloads
# and that scroll position is preserved.
required_phrases = {
    "reload": "reload" in lower or "reloads" in lower,
    "previous_content": "previous" in lower,
    "loading_state": "loading" in lower,
}

missing = [k for k, v in required_phrases.items() if not v]
if missing:
    print(json.dumps({"ok": False, "missing": missing}))
    sys.exit(0)

# Verify the reload documentation appears near the project detail section
lines = readme.split("\n")
found_section = False
for line in lines:
    if "reload" in line.lower() and ("record" in line.lower() or "detail" in line.lower() or "project" in line.lower()):
        found_section = True
        break

if not found_section:
    print(json.dumps({"ok": False, "missing": ["reload_section_near_project_detail"]}))
    sys.exit(0)

print(json.dumps({"ok": True}))
""",
        ],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"README check script failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result["ok"], f"README missing reload documentation: {result.get('missing', [])}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_when_call_still_has_loading_error_data():
    """The .when() call retains loading, error, and data callbacks."""
    src = DETAIL_PAGE.read_text()
    # Find the .when block
    when_start = src.find("recordAsync.when(")
    assert when_start != -1, "recordAsync.when() not found"
    when_end = src.find(");", when_start)
    when_block = src[when_start:when_end]
    assert "loading:" in when_block, ".when() must still have loading callback"
    assert "error:" in when_block, ".when() must still have error callback"
    assert "data:" in when_block, ".when() must still have data callback"
