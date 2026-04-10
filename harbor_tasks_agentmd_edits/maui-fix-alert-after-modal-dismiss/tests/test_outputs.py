"""
Task: maui-fix-alert-after-modal-dismiss
Repo: dotnet/maui @ 39325cec7d8a6de66e4608471b7843c7dfe3b4e1
PR:   32872

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/maui"

ALERT_MANAGER_REL = "src/Controls/src/Core/Platform/AlertManager/AlertManager.iOS.cs"
COPILOT_REL = ".github/copilot-instructions.md"
SKILL_REL = ".github/skills/pr-finalize/SKILL.md"
EXAMPLE_REL = ".github/skills/pr-finalize/references/complete-example.md"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified C# and markdown files have basic syntax sanity."""
    content = Path(REPO, ALERT_MANAGER_REL).read_text()
    opens = content.count("{")
    closes = content.count("}")
    assert opens == closes, (
        f"AlertManager.iOS.cs: unbalanced braces ({opens} open vs {closes} close)"
    )

    for rel in [COPILOT_REL, SKILL_REL, EXAMPLE_REL]:
        md = Path(REPO, rel).read_text()
        # Check for actual merge conflict markers, not code examples
        # Split by code blocks (``` or indented) and only check narrative text
        import re

        # Remove code blocks before checking for conflict markers
        text_without_code = re.sub(r'```[\s\S]*?```', '', md)
        text_without_code = re.sub(r'~~~[\s\S]*?~~~', '', text_without_code)
        # Also remove indented code blocks (4+ spaces)
        text_without_code = re.sub(r'^(    |\t).*', '', text_without_code, flags=re.MULTILINE)

        assert "<<<<<<" not in text_without_code, f"{rel}: merge conflict marker found"
        assert ">>>>>>" not in text_without_code, f"{rel}: merge conflict marker found"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral test for the C# fix
# ---------------------------------------------------------------------------

def test_isbeingdismissed_check_in_while_loop():
    """GetTopUIViewController must check IsBeingDismissed before following
    the PresentedViewController chain.

    Parses the C# method in a subprocess, extracts the while-loop condition,
    and verifies it is a compound expression that rejects dismissing VCs.
    Without this check, during modal dismissal, PresentedViewController
    remains non-null until the animation completes, causing the method to
    return a view controller that iOS silently ignores for presentation.
    """
    r = _run_py(r"""
import re, json, sys

content = open(
    "src/Controls/src/Core/Platform/AlertManager/AlertManager.iOS.cs"
).read()

# Locate GetTopUIViewController method
m = re.search(
    r"static\s+UIViewController\s+GetTopUIViewController\s*\([^)]*\)\s*\{",
    content,
)
if not m:
    print(json.dumps({"error": "GetTopUIViewController not found"}))
    sys.exit(1)

# Extract the while loop condition within the method
after = content[m.start():]
wm = re.search(r"while\s*\((.*?)\)\s*\{", after, re.DOTALL)
if not wm:
    print(json.dumps({"error": "while loop not found in method"}))
    sys.exit(1)

cond = wm.group(1).strip()

checks = {
    "has_presented_vc": "PresentedViewController" in cond,
    "has_isbeingdismissed": "IsBeingDismissed" in cond,
    # Match negation with optional chaining: !x?.y.IsBeingDismissed or !x.y.IsBeingDismissed
    "has_negation": bool(re.search(r"!\s*\S+\.IsBeingDismissed", cond)),
    "is_compound": "&&" in cond,
}

failures = [k for k, v in checks.items() if not v]
if failures:
    print(json.dumps({
        "error": f"Failed: {', '.join(failures)}",
        "condition": cond,
    }))
    sys.exit(1)

print(json.dumps({"status": "PASS"}))
""")
    assert r.returncode == 0, f"While-loop check failed:\n{r.stderr}\n{r.stdout}"
    data = json.loads(r.stdout.strip())
    assert data.get("status") == "PASS", f"Condition validation failed: {data}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — traversal preserved (still a structural check)
# ---------------------------------------------------------------------------

def test_while_loop_preserves_traversal():
    """The while loop must still traverse the VC hierarchy for normal
    (non-dismissing) presented view controllers.

    The fix should only stop traversal when a VC is being dismissed,
    not remove the traversal entirely.
    """
    content = Path(REPO, ALERT_MANAGER_REL).read_text()

    while_match = re.search(
        r"while\s*\(.*?\)\s*\{(.*?)^\t\t\t\t\}",
        content,
        re.DOTALL | re.MULTILINE,
    )
    assert while_match, "while loop block not found"

    body = while_match.group(1)

    assert "topUIViewController" in body, (
        "While loop body must still traverse by assigning topUIViewController"
    )
    assert "PresentedViewController" in body, (
        "While loop body must still use PresentedViewController for traversal"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

def test_copilot_instructions_removes_opening_prs_section():
    """copilot-instructions.md must not have the 'Opening PRs' section
    that required a NOTE block at the top of PR descriptions.

    Uses subprocess to parse the file and confirm both the heading and
    the NOTE block template text are absent.
    """
    r = _run_py("""
import json, sys

content = open(".github/copilot-instructions.md").read()
errors = []
if "### Opening PRs" in content:
    errors.append("'### Opening PRs' heading still present")
if "test the resulting artifacts" in content:
    errors.append("NOTE block template text still present")

if errors:
    print(json.dumps({"error": "; ".join(errors)}))
    sys.exit(1)

print(json.dumps({"status": "PASS"}))
""")
    assert r.returncode == 0, f"Config check failed:\n{r.stderr}\n{r.stdout}"
    data = json.loads(r.stdout.strip())
    assert data.get("status") == "PASS"


def test_skill_md_removes_note_from_description_requirements():
    """pr-finalize SKILL.md must not require the NOTE block in PR
    descriptions. Parses the Description Requirements section in a
    subprocess and confirms the NOTE block instructions are gone.
    """
    r = _run_py(r"""
import re, json, sys

content = open(".github/skills/pr-finalize/SKILL.md").read()
dm = re.search(r"## Description Requirements(.*?)(?=\n## |\Z)", content, re.DOTALL)
if not dm:
    print(json.dumps({"error": "Description Requirements section not found"}))
    sys.exit(1)

section = dm.group(1)
errors = []
if "Start with the required NOTE block" in section:
    errors.append("NOTE block instruction still in description requirements")
if "test the resulting artifacts" in section:
    errors.append("NOTE block template text still present")

if errors:
    print(json.dumps({"error": "; ".join(errors)}))
    sys.exit(1)

print(json.dumps({"status": "PASS"}))
""")
    assert r.returncode == 0, f"Config check failed:\n{r.stderr}\n{r.stdout}"
    data = json.loads(r.stdout.strip())
    assert data.get("status") == "PASS"


def test_complete_example_removes_note_block():
    """complete-example.md must not include the NOTE block in the
    example PR description. Uses subprocess to verify the NOTE block
    text is absent while substantive content remains.
    """
    r = _run_py("""
import json, sys

content = open(
    ".github/skills/pr-finalize/references/complete-example.md"
).read()
errors = []
if "test the resulting artifacts" in content:
    errors.append("NOTE block template still present")
if "Root Cause" not in content and "Description of Change" not in content:
    errors.append("Example PR sections missing — file may be corrupted")

if errors:
    print(json.dumps({"error": "; ".join(errors)}))
    sys.exit(1)

print(json.dumps({"status": "PASS"}))
""")
    assert r.returncode == 0, f"Config check failed:\n{r.stderr}\n{r.stdout}"
    data = json.loads(r.stdout.strip())
    assert data.get("status") == "PASS"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub / regression
# ---------------------------------------------------------------------------

def test_existing_alert_manager_logic_intact():
    """The rest of GetTopUIViewController must remain intact — it must
    still return a UIViewController and use RootViewController as the
    starting point.
    """
    content = Path(REPO, ALERT_MANAGER_REL).read_text()

    # Find the method and extract its body by counting braces
    method_start = re.search(
        r"static\s+UIViewController\s+GetTopUIViewController\s*\([^)]*\)\s*\{",
        content,
    )
    assert method_start, "GetTopUIViewController method not found"

    start_pos = method_start.end()

    # Count braces to find the end of the method body
    brace_count = 1
    pos = start_pos
    while brace_count > 0 and pos < len(content):
        if content[pos] == '{':
            brace_count += 1
        elif content[pos] == '}':
            brace_count -= 1
        pos += 1

    body = content[start_pos:pos-1]  # -1 to exclude the final closing brace

    assert "RootViewController" in body, (
        "GetTopUIViewController must still start from RootViewController"
    )
    assert "return" in body, (
        "GetTopUIViewController must still return a UIViewController"
    )


def test_copilot_instructions_key_sections_intact():
    """Key sections of copilot-instructions.md must remain intact after
    removing the Opening PRs section.
    """
    content = Path(REPO, COPILOT_REL).read_text()

    assert "## Code Review Instructions" in content, (
        "Code Review Instructions section must remain"
    )
    assert "## Repository Overview" in content, (
        "Repository Overview section must remain"
    )
    assert "## Custom Agents and Skills" in content, (
        "Custom Agents and Skills section must remain"
    )


def test_skill_md_never_approve_rule_intact():
    """The CRITICAL rule about never approving PRs must remain in SKILL.md.
    Removing the NOTE block should not affect this important safety rule.
    """
    content = Path(REPO, SKILL_REL).read_text()

    assert "NEVER" in content and "approve" in content.lower(), (
        "SKILL.md must retain the NEVER approve rule"
    )
    assert "Code Review" in content, (
        "SKILL.md must retain the Code Review section"
    )


def test_repo_xml_validation():
    """XAML files in the repo must be valid XML (pass_to_pass).

    Uses Python's xml.etree.ElementTree to verify XAML files are well-formed.
    This catches syntax errors in the XAML files that would break the build.
    """
    r = _run_py(r"""
import xml.etree.ElementTree as ET
import json
import sys
import glob
import os

# Get list of XAML files in the test issues directory
xaml_files = glob.glob(
    "src/Controls/tests/TestCases.HostApp/Issues/*.xaml"
)[:20]

errors = []
for f in xaml_files:
    try:
        ET.parse(f)
    except ET.ParseError as e:
        errors.append(f"{f}: {e}")

if errors:
    print(json.dumps({"error": "; ".join(errors)}))
    sys.exit(1)

print(json.dumps({
    "status": "PASS",
    "checked": len(xaml_files)
}))
""")
    assert r.returncode == 0, f"XML validation failed:\n{r.stderr}\n{r.stdout}"
    data = json.loads(r.stdout.strip())
    assert data.get("status") == "PASS", f"XML validation failed: {data}"


def test_repo_json_validation():
    """JSON config files must be valid (pass_to_pass).

    Validates global.json and other config files are parseable.
    This ensures the repo's configuration is not corrupted.
    """
    r = _run_py(r"""
import json
import sys
import glob
import os

json_files = [
    "global.json",
    "github-merge-flow-net10.jsonc",
    "github-merge-flow-net11.jsonc",
]

errors = []
for f in json_files:
    if not os.path.exists(f):
        continue
    try:
        # Read and strip comments for .jsonc files
        with open(f) as fp:
            content = fp.read()
        # Remove single-line comments for jsonc
        lines = [l for l in content.split('\n') if not l.strip().startswith('//')]
        json.loads('\n'.join(lines))
    except json.JSONDecodeError as e:
        errors.append(f"{f}: {e}")

if errors:
    print(json.dumps({"error": "; ".join(errors)}))
    sys.exit(1)

print(json.dumps({"status": "PASS"}))
""")
    assert r.returncode == 0, f"JSON validation failed:\n{r.stderr}\n{r.stdout}"
    data = json.loads(r.stdout.strip())
    assert data.get("status") == "PASS", f"JSON validation failed: {data}"


def test_repo_alertmanager_cs_syntax():
    """AlertManager.iOS.cs must have valid C# structure (pass_to_pass).

    Checks brace balance, namespace declarations, and method structure
    using regex parsing - a lightweight syntax validation.
    """
    r = _run_py(r"""
import re
import json
import sys
import os

content = open(
    "src/Controls/src/Core/Platform/AlertManager/AlertManager.iOS.cs"
).read()

errors = []

# Check brace balance
open_braces = content.count('{')
close_braces = content.count('}')
if open_braces != close_braces:
    errors.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")

# Check namespace declaration
if "namespace Microsoft.Maui.Controls.Platform" not in content:
    errors.append("Missing correct namespace declaration")

# Check class structure
if "static UIViewController GetTopUIViewController" not in content:
    errors.append("GetTopUIViewController method not found")

# Check for basic method structure (base or fixed version)
if "while (topUIViewController?.PresentedViewController is not null" not in content:
    errors.append("While loop structure not found")

if errors:
    print(json.dumps({"error": "; ".join(errors)}))
    sys.exit(1)

print(json.dumps({
    "status": "PASS",
    "braces": open_braces
}))
""")
    assert r.returncode == 0, f"C# syntax check failed:\n{r.stderr}\n{r.stdout}"
    data = json.loads(r.stdout.strip())
    assert data.get("status") == "PASS", f"C# syntax check failed: {data}"
