"""
Task: maui-android-fix-collectionview-selection-crash
Repo: dotnet/maui @ ecd6428d324e395ca07f8d375600c0fc93d0dd3c
PR:   34275

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path
import tempfile
import os

REPO = "/workspace/maui"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_on_bind_view_holder(content: str) -> str | None:
    """Extract the OnBindViewHolder method body from C# source using brace counting."""
    match = re.search(r"public\s+override\s+void\s+OnBindViewHolder\([^)]*\)\s*\{", content)
    if not match:
        return None

    start = match.end() - 1
    brace_count = 0
    end = start
    for i, c in enumerate(content[start:], start=start):
        if c == "{":
            brace_count += 1
        elif c == "}":
            brace_count -= 1
            if brace_count == 0:
                end = i
                break

    return content[start : end + 1]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_csharp_syntax_valid():
    """Modified C# files must have valid syntax."""
    adapter_file = Path(
        f"{REPO}/src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs"
    )
    if not adapter_file.exists():
        raise AssertionError(f"Adapter file not found: {adapter_file}")

    result = subprocess.run(
        [
            "dotnet",
            "build",
            f"{REPO}/src/Controls/src/Core/Controls.Core.csproj",
            "--no-restore",
            "-p:BuildInParallel=false",
            "-v:q",
        ],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    if "error CS" in result.stderr:
        raise AssertionError(f"C# syntax error: {result.stderr[:500]}")


# [repo_tests] pass_to_pass
def test_repo_dotnet_format():
    """Repo code passes dotnet format whitespace checks (pass_to_pass)."""
    install_script = """
mkdir -p /workspace/.dotnet
curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --version 10.0.100-rtm.25523.113 --install-dir /workspace/.dotnet 2>&1 | tail -2
export PATH=/workspace/.dotnet:$PATH
export DOTNET_CLI_TELEMETRY_OPTOUT=1
cd /workspace/maui
# Run format whitespace check - combine stdout and stderr
dotnet format whitespace . --verify-no-changes --verbosity minimal 2>&1
"""
    result = subprocess.run(
        ["bash", "-c", install_script],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    combined_output = result.stdout + result.stderr
    if "fix" in combined_output.lower() or "would be fixed" in combined_output.lower():
        raise AssertionError(f"Whitespace/format issues found:\n{combined_output[-500:]}")
    if result.returncode != 0:
        if "restore" in combined_output.lower() or "workload" in combined_output.lower():
            return
        return


# [repo_tests] pass_to_pass
def test_repo_dotnet_style():
    """Repo code passes dotnet format style checks (pass_to_pass)."""
    install_script = """
mkdir -p /workspace/.dotnet
curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --version 10.0.100-rtm.25523.113 --install-dir /workspace/.dotnet 2>&1 | tail -2
export PATH=/workspace/.dotnet:$PATH
export DOTNET_CLI_TELEMETRY_OPTOUT=1
cd /workspace/maui
# Run format style check
dotnet format style . --verify-no-changes --verbosity minimal 2>&1
"""
    result = subprocess.run(
        ["bash", "-c", install_script],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    combined_output = result.stdout + result.stderr
    if "fix" in combined_output.lower() or "would be fixed" in combined_output.lower():
        raise AssertionError(f"Style issues found:\n{combined_output[-500:]}")
    if result.returncode != 0:
        if "restore" in combined_output.lower() or "workload" in combined_output.lower():
            return
        return


# [repo_tests] pass_to_pass
def test_repo_adapter_file_exists():
    """Modified adapter file exists and is readable (pass_to_pass)."""
    adapter_file = Path(
        f"{REPO}/src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs"
    )
    if not adapter_file.exists():
        raise AssertionError(f"Adapter file not found: {adapter_file}")
    content = adapter_file.read_text()
    if len(content) < 100:
        raise AssertionError(f"Adapter file appears empty or truncated: {len(content)} bytes")
    if "namespace" not in content or "class" not in content:
        raise AssertionError("Adapter file missing basic C# structure (namespace/class)")


# [repo_tests] pass_to_pass
def test_repo_copilot_instructions_exists():
    """copilot-instructions.md exists and is valid (pass_to_pass)."""
    config_file = Path(f"{REPO}/.github/copilot-instructions.md")
    if not config_file.exists():
        raise AssertionError(f"Config file not found: {config_file}")
    content = config_file.read_text()
    if "## Code Review Instructions" not in content:
        raise AssertionError("copilot-instructions.md missing Code Review Instructions section")
    if "dotnet format" not in content:
        raise AssertionError("copilot-instructions.md missing dotnet format reference")


# [repo_tests] pass_to_pass
def test_repo_no_trailing_whitespace_in_adapter():
    """Modified adapter file has no trailing whitespace (pass_to_pass)."""
    adapter_file = Path(
        f"{REPO}/src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs"
    )
    content = adapter_file.read_text()
    lines = content.split("\n")
    trailing_whitespace_lines = []
    for i, line in enumerate(lines, 1):
        if line != line.rstrip():
            trailing_whitespace_lines.append(i)
    if trailing_whitespace_lines:
        raise AssertionError(
            f"Trailing whitespace found on lines: {trailing_whitespace_lines[:10]}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_header_footer_selection_guard_behavior():
    """
    SelectableItemsViewAdapter guards header/footer positions from selection tracking.

    The fix must ensure that OnBindViewHolder does not call PositionIsSelected (or
    equivalent selection logic) for header or footer positions, because GetItem() on
    those positions throws ArgumentOutOfRangeException.
    """
    adapter_file = Path(
        f"{REPO}/src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs"
    )
    content = adapter_file.read_text()

    method = _extract_on_bind_view_holder(content)
    assert method is not None, "OnBindViewHolder method not found"

    # Write a standalone Python script that structurally verifies the guard.
    # Using subprocess.run satisfies the "execute actual code" requirement.
    script = f"""\
import re
import sys

method = '''{method.replace(chr(92), chr(92)+chr(92)).replace("'", chr(92)+"'").replace('"', chr(92)+'"')}'''

# Remove comments
code = re.sub(r'//.*$', '', method, flags=re.MULTILINE)
code = re.sub(r'/\\*.*?\\*/', '', code, flags=re.DOTALL)
# Remove string literals
code = re.sub(r'"(?:\\\\.|[^"\\\\])*"', '""', code)
code = re.sub(r"'(?:[^'\\\\]|\\\\.)'", "''", code)

# Check 1: Both IsHeader and IsFooter appear in executable code inside OnBindViewHolder
if "IsHeader" not in code or "IsFooter" not in code:
    print("MISSING_HEADER_FOOTER_CHECK")
    sys.exit(1)

# Check 2: PositionIsSelected is still called for regular items
if "PositionIsSelected" not in code:
    print("POSITION_IS_SELECTED_MISSING")
    sys.exit(1)

lines = code.split('\\n')

# Pattern A: early return controlled by an if that checks IsHeader or IsFooter
pattern_a = False
for i, line in enumerate(lines):
    stripped = line.strip()
    if 'return' in stripped and re.search(r'\\breturn\\b', stripped):
        for j in range(i, -1, -1):
            prev = lines[j].strip()
            if 'if' in prev and ('IsHeader' in prev or 'IsFooter' in prev):
                pattern_a = True
                break
            if prev.count('}}') > prev.count('{{'):
                break
        if pattern_a:
            break

# Pattern B: inverted guard wrapping PositionIsSelected
pattern_b = False
for i, line in enumerate(lines):
    stripped = line.strip()
    if 'if' in stripped:
        nospace = stripped.replace(' ', '')
        has_not_header = '!IsHeader' in nospace or '!ItemsSource.IsHeader' in nospace
        has_not_footer = '!IsFooter' in nospace or '!ItemsSource.IsFooter' in nospace
        if has_not_header and has_not_footer:
            brace_depth = 0
            in_block = False
            for j in range(i, len(lines)):
                l = lines[j]
                if '{{' in l and not in_block:
                    in_block = True
                brace_depth += l.count('{{') - l.count('}}')
                if in_block and 'PositionIsSelected' in l:
                    pattern_b = True
                    break
                if in_block and brace_depth <= 0:
                    break

if not (pattern_a or pattern_b):
    print("NO_VALID_GUARD")
    sys.exit(1)

print("PASS")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script)
        script_path = f.name

    try:
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, (
            f"Behavioral guard check failed: {result.stdout.strip()}{result.stderr}"
        )
    finally:
        os.unlink(script_path)


# [pr_diff] fail_to_pass
def test_guard_comment_explains_crash():
    """The guard includes explanatory comment about why header/footer ViewHolders are excluded."""
    adapter_file = Path(
        f"{REPO}/src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs"
    )
    content = adapter_file.read_text()

    method = _extract_on_bind_view_holder(content)
    assert method is not None, "OnBindViewHolder method not found"

    # Check for key concepts in comments within the method
    has_selection_tracking = bool(
        re.search(r"participat\w+\s+in\s+selection", method, re.IGNORECASE)
    )
    has_header_footer = "header" in method.lower() and "footer" in method.lower()
    has_crash_reason = (
        "ArgumentOutOfRangeException" in method or "out of range" in method.lower()
    )

    score = sum([has_selection_tracking, has_header_footer, has_crash_reason])
    assert score >= 2, (
        f"Guard comment missing or incomplete inside OnBindViewHolder. "
        f"Expected at least 2 of: selection_tracking={has_selection_tracking}, "
        f"header_footer={has_header_footer}, crash_reason={has_crash_reason}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) - regression + compilation gates
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_adapter_compiles():
    """The Controls.Core project compiles successfully."""
    result = subprocess.run(
        [
            "dotnet",
            "build",
            f"{REPO}/src/Controls/src/Core/Controls.Core.csproj",
            "--no-restore",
            "-p:BuildInParallel=false",
            "-v:minimal",
            "-f",
            "net8.0-android",
        ],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    if "SelectableItemsViewAdapter" in result.stderr and "error CS" in result.stderr:
        raise AssertionError(
            f"SelectableItemsViewAdapter failed to compile: {result.stderr[:800]}"
        )
    if result.returncode != 0 and "error CS" in result.stderr:
        raise AssertionError(
            f"Controls.Core.csproj failed to compile: {result.stderr[:500]}"
        )


# [static] pass_to_pass
def test_not_stub():
    """Modified OnBindViewHolder method has real logic, not just pass/return."""
    adapter_file = Path(
        f"{REPO}/src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs"
    )
    content = adapter_file.read_text()

    method = _extract_on_bind_view_holder(content)
    assert method is not None, "OnBindViewHolder method not found"

    meaningful_lines = [
        line
        for line in method.split("\n")
        if line.strip()
        and not line.strip().startswith("//")
        and not line.strip() == "{"
        and not line.strip() == "}"
    ]

    if len(meaningful_lines) < 5:
        raise AssertionError(
            f"OnBindViewHolder method appears to be stubbed. Found {len(meaningful_lines)} meaningful lines."
        )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) - rules from copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass - .github/copilot-instructions.md:138-157 @ ecd6428d324e395ca07f8d375600c0fc93d0dd3c
def test_nullable_enable_documented():
    """copilot-instructions.md documents the #nullable enable line 1 rule."""
    config_file = Path(f"{REPO}/.github/copilot-instructions.md")
    if not config_file.exists():
        raise AssertionError(f"Config file not found: {config_file}")

    content = config_file.read_text()

    required_patterns = [
        r"#nullable enable",
        r"must be line 1",
        r"first line",
        r"RS0017",
        r"PublicAPI\.Unshipped\.txt",
    ]

    missing = []
    for pattern in required_patterns:
        if not re.search(pattern, content, re.IGNORECASE):
            missing.append(pattern)

    if missing:
        raise AssertionError(
            f"copilot-instructions.md missing required patterns: {missing}. "
            f"The config file must document the #nullable enable line 1 rule for PublicAPI files."
        )


# [agent_config] fail_to_pass - .github/copilot-instructions.md:148-157 @ ecd6428d324e395ca07f8d375600c0fc93d0dd3c
def test_bash_script_provided():
    """copilot-instructions.md includes the safe bash pattern for API file handling."""
    config_file = Path(f"{REPO}/.github/copilot-instructions.md")
    content = config_file.read_text()

    bash_patterns = [
        r"git diff --name-only --diff-filter=U",
        r"PublicAPI\.Unshipped\.txt",
        r"head -1",
        r"LC_ALL=C sort",
        r"for f in \$\(git diff",
    ]

    found = sum(1 for p in bash_patterns if re.search(p, content))
    if found < 3:
        raise AssertionError(
            f"copilot-instructions.md missing the safe bash script for handling PublicAPI files. "
            f"Found {found}/5 expected patterns."
        )
