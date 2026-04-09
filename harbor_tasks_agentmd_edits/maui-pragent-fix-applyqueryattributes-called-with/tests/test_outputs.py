"""
Task: maui-pragent-fix-applyqueryattributes-called-with
Repo: dotnet/maui @ f73f0f7dabecaa2af50231522313e609ff78dcb7
PR:   33451

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/maui"


def _run_shell(cmd: list[str], cwd: str = REPO, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_shell_navigation_manager_compiles():
    """Modified ShellNavigationManager.cs must have valid C# syntax."""
    file_path = Path(f"{REPO}/src/Controls/src/Core/Shell/ShellNavigationManager.cs")
    assert file_path.exists(), f"File not found: {file_path}"

    # Use dotnet to verify syntax
    result = _run_shell(
        ["dotnet", "build", "src/Controls/src/Core/Controls.Core.csproj", "--no-restore", "-v:q"],
        timeout=180,
    )
    assert result.returncode == 0, f"Build failed: {result.stdout}\n{result.stderr}"


# [static] pass_to_pass
def test_issue33415_test_file_compiles():
    """Added Issue33415.cs test file must have valid C# syntax."""
    # The test file should exist after the fix
    test_file = Path(f"{REPO}/src/Controls/tests/TestCases.HostApp/Issues/Issue33415.cs")
    assert test_file.exists(), f"Test file not found: {test_file}"

    # Basic syntax check - file should parse as C#
    content = test_file.read_text()
    assert "class Issue33415" in content, "Missing Issue33415 class definition"
    assert "ApplyQueryAttributes" in content, "Missing ApplyQueryAttributes reference"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_fix_has_empty_query_guard_shellcontent():
    """ShellContent path has guard: skip ApplyQueryAttributes if empty and popping."""
    file_path = Path(f"{REPO}/src/Controls/src/Core/Shell/ShellNavigationManager.cs")
    content = file_path.read_text()

    # Look for the fix pattern: mergedData.Count > 0 || !isPopping before ApplyQueryAttributes
    # This is the key fix for Path 1 (ShellContent case)
    pattern = r"if\s*\(\s*mergedData\.Count\s*>\s*0\s*\|\|\s*!isPopping\s*\)"
    matches = re.findall(pattern, content)

    assert len(matches) >= 1, (
        f"Expected at least one guard check 'if (mergedData.Count > 0 || !isPopping)' "
        f"in ShellNavigationManager.cs, found {len(matches)}. Fix not applied correctly."
    )


# [pr_diff] fail_to_pass
def test_fix_has_empty_query_guard_islastitem():
    """isLastItem path has guard: skip SetValue if empty and popping."""
    file_path = Path(f"{REPO}/src/Controls/src/Core/Shell/ShellNavigationManager.cs")
    content = file_path.read_text()

    # Look for the second fix: setting QueryAttributesProperty with guard
    # The pattern should show the guard before element.SetValue
    lines = content.split("\n")

    found_islastitem_guard = False
    for i, line in enumerate(lines):
        if "isLastItem" in line and "else if" in line:
            # Check following lines for the guard pattern
            subsequent = "\n".join(lines[i:i+10])
            if "mergedData.Count > 0 || !isPopping" in subsequent:
                found_islastitem_guard = True
                break

    assert found_islastitem_guard, (
        "Expected guard check in isLastItem path before setting QueryAttributesProperty. "
        "The fix should skip setting query attributes when data is empty and popping back."
    )


# [pr_diff] fail_to_pass
def test_fix_has_explanatory_comment():
    """Fix includes explanatory comment about query.Clear() behavior."""
    file_path = Path(f"{REPO}/src/Controls/src/Core/Shell/ShellNavigationManager.cs")
    content = file_path.read_text()

    # Look for the explanatory comment
    expected_comment = "query.Clear()"
    assert expected_comment in content, (
        f"Expected explanatory comment mentioning '{expected_comment}' in the fix. "
        "The comment should explain why the guard is needed."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified ApplyQueryAttributes method has real logic, not just pass/return."""
    file_path = Path(f"{REPO}/src/Controls/src/Core/Shell/ShellNavigationManager.cs")
    content = file_path.read_text()

    # Find the ApplyQueryAttributes method and verify it has substantial logic
    # Count braces to find method body
    method_start = content.find("public static void ApplyQueryAttributes")
    assert method_start != -1, "ApplyQueryAttributes method not found"

    # Extract method body - find matching braces
    brace_start = content.find("{", method_start)
    brace_count = 0
    method_end = brace_start

    for i, char in enumerate(content[brace_start:], start=brace_start):
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1
            if brace_count == 0:
                method_end = i
                break

    method_body = content[brace_start:method_end+1]

    # Should have multiple statements, not just a stub
    # Count non-whitespace, non-brace lines
    meaningful_lines = [
        line for line in method_body.split("\n")
        if line.strip() and not line.strip().startswith("//") and line.strip() not in ("{", "}")
    ]

    assert len(meaningful_lines) >= 5, (
        f"ApplyQueryAttributes method appears to be a stub with only {len(meaningful_lines)} "
        f"meaningful lines. Expected at least 5 lines of logic."
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .github/copilot-instructions.md:141-160 @ f73f0f7dabecaa2af50231522313e609ff78dcb7
def test_nullable_enable_documented():
    """copilot-instructions.md documents the #nullable enable must be line 1 rule."""
    config_path = Path(f"{REPO}/.github/copilot-instructions.md")
    assert config_path.exists(), f"Config file not found: {config_path}"

    content = config_path.read_text()

    # Check for the critical nullable enable rule
    assert "#nullable enable" in content, (
        "Missing #nullable enable documentation in copilot-instructions.md"
    )
    assert "must be line 1" in content or "first line" in content.lower(), (
        "Missing 'must be line 1' or 'first line' documentation for #nullable enable"
    )


# [agent_config] fail_to_pass — .github/copilot-instructions.md:148-157 @ f73f0f7dabecaa2af50231522313e609ff78dcb7
def test_bash_script_for_publicapi():
    """copilot-instructions.md includes safe bash pattern for PublicAPI.Unshipped.txt handling."""
    config_path = Path(f"{REPO}/.github/copilot-instructions.md")
    content = config_path.read_text()

    # Look for the safe bash pattern elements
    has_for_loop = "for f in $(git diff --name-only" in content
    has_header_extract = "head -1" in content and "$HEADER" in content
    has_grep_v = "grep -v" in content and "<<<<<<" in content

    assert has_for_loop, "Missing for-loop pattern for PublicAPI.Unshipped.txt file handling"
    assert has_header_extract, "Missing HEADER extraction pattern for PublicAPI.Unshipped.txt"
    assert has_grep_v, "Missing grep -v pattern for conflict marker removal"
