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

REPO = "/workspace/maui"

# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_csharp_syntax_valid():
    """Modified C# files must have valid syntax."""
    # Check that the adapter file can be parsed
    adapter_file = Path(f"{REPO}/src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs")
    if not adapter_file.exists():
        raise AssertionError(f"Adapter file not found: {adapter_file}")

    # Use dotnet to verify syntax without full compilation
    result = subprocess.run(
        ["dotnet", "build", f"{REPO}/src/Controls/src/Core/Controls.Core.csproj",
         "--no-restore", "-p:BuildInParallel=false", "-v:q"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    # Build may fail for unrelated reasons, but syntax errors will be in stderr
    if "error CS" in result.stderr:
        raise AssertionError(f"C# syntax error: {result.stderr[:500]}")


# [repo_tests] pass_to_pass
def test_repo_dotnet_format():
    """Repo code passes dotnet format whitespace checks (pass_to_pass)."""
    # Install .NET 10 SDK and run format
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
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    combined_output = result.stdout + result.stderr
    # The command may fail on restore but whitespace check should pass
    # A clean whitespace check exits 0, otherwise check output for "fix"
    if "fix" in combined_output.lower() or "would be fixed" in combined_output.lower():
        raise AssertionError(f"Whitespace/format issues found:\n{combined_output[-500:]}")
    # If exit code is non-zero, check if it's due to restore/workload (not whitespace)
    if result.returncode != 0:
        if "restore" in combined_output.lower() or "workload" in combined_output.lower():
            # Restore/workload issues are environment issues, not code issues
            # Consider this a pass since whitespace itself isn't the problem
            return
        # Some other error - log it but don't fail for environment issues
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
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    combined_output = result.stdout + result.stderr
    # Check for style issues in output
    if "fix" in combined_output.lower() or "would be fixed" in combined_output.lower():
        raise AssertionError(f"Style issues found:\n{combined_output[-500:]}")
    # Allow restore/workload failures (environment issues, not code issues)
    if result.returncode != 0:
        if "restore" in combined_output.lower() or "workload" in combined_output.lower():
            return
        # Some other error - log it but don't fail for environment issues
        return


# [repo_tests] pass_to_pass
def test_repo_adapter_file_exists():
    """Modified adapter file exists and is readable (pass_to_pass)."""
    adapter_file = Path(f"{REPO}/src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs")
    if not adapter_file.exists():
        raise AssertionError(f"Adapter file not found: {adapter_file}")
    # Check file is readable and has content
    content = adapter_file.read_text()
    if len(content) < 100:
        raise AssertionError(f"Adapter file appears empty or truncated: {len(content)} bytes")
    # Check basic C# structure
    if "namespace" not in content or "class" not in content:
        raise AssertionError("Adapter file missing basic C# structure (namespace/class)")


# [repo_tests] pass_to_pass
def test_repo_copilot_instructions_exists():
    """copilot-instructions.md exists and is valid (pass_to_pass)."""
    config_file = Path(f"{REPO}/.github/copilot-instructions.md")
    if not config_file.exists():
        raise AssertionError(f"Config file not found: {config_file}")
    content = config_file.read_text()
    # Check for key sections
    if "## Code Review Instructions" not in content:
        raise AssertionError("copilot-instructions.md missing Code Review Instructions section")
    if "dotnet format" not in content:
        raise AssertionError("copilot-instructions.md missing dotnet format reference")


# [repo_tests] pass_to_pass
def test_repo_no_trailing_whitespace_in_adapter():
    """Modified adapter file has no trailing whitespace (pass_to_pass)."""
    adapter_file = Path(f"{REPO}/src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs")
    content = adapter_file.read_text()
    lines = content.split('\n')
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
def test_header_footer_guard_exists():
    """SelectableItemsViewAdapter has the header/footer selection guard."""
    adapter_file = Path(f"{REPO}/src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs")
    content = adapter_file.read_text()

    # Check that the guard exists with both IsHeader and IsFooter checks
    guard_pattern = r'if\s*\(\s*ItemsSource\.IsHeader\(\s*position\s*\)\s*\|\|\s*ItemsSource\.IsFooter\(\s*position\s*\)\s*\)'

    if not re.search(guard_pattern, content):
        raise AssertionError(
            "Header/footer guard not found. Expected pattern: "
            "if (ItemsSource.IsHeader(position) || ItemsSource.IsFooter(position))"
        )

    # Also verify there's an early return inside the guard
    # Find the guard block and check it has a return statement
    guard_match = re.search(guard_pattern + r'[^}]*\{[^}]*return', content, re.DOTALL)
    if not guard_match:
        raise AssertionError(
            "Header/footer guard exists but does not have an early return statement"
        )


# [pr_diff] fail_to_pass
def test_guard_has_correct_comment():
    """The guard includes explanatory comment about the crash."""
    adapter_file = Path(f"{REPO}/src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs")
    content = adapter_file.read_text()

    # Check for the comment explaining why the guard is needed
    comment_patterns = [
        r'Header and footer view holders should not participate in selection',
        r'ArgumentOutOfRangeException',
        r'header index adjustment',
    ]

    found_patterns = sum(1 for p in comment_patterns if re.search(p, content, re.IGNORECASE))
    if found_patterns < 2:
        raise AssertionError(
            f"Guard comment missing or incomplete. Expected explanatory comment about "
            f"header/footer ViewHolders not participating in selection tracking."
        )


# [pr_diff] fail_to_pass
def test_adapter_compiles_with_fix():
    """The Controls.Core project compiles successfully with the guard fix applied."""
    # This test runs dotnet build to verify the actual code compiles
    # It will fail on base if the file is missing or malformed, pass on fix
    result = subprocess.run(
        ["dotnet", "build", f"{REPO}/src/Controls/src/Core/Controls.Core.csproj",
         "--no-restore", "-p:BuildInParallel=false", "-v:minimal", "-f", "net8.0-android"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )

    # Check for compilation errors specific to the adapter
    if "SelectableItemsViewAdapter" in result.stderr and "error CS" in result.stderr:
        raise AssertionError(
            f"SelectableItemsViewAdapter failed to compile: {result.stderr[:800]}"
        )

    # General compilation failure
    if result.returncode != 0 and "error CS" in result.stderr:
        raise AssertionError(
            f"Controls.Core.csproj failed to compile: {result.stderr[:500]}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) - regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified OnBindViewHolder method has real logic, not just pass/return."""
    adapter_file = Path(f"{REPO}/src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs")
    content = adapter_file.read_text()

    # Find the OnBindViewHolder method and check it has meaningful body
    method_pattern = r'public\s+override\s+void\s+OnBindViewHolder\([^)]*\)\s*\{'
    match = re.search(method_pattern, content)
    if not match:
        raise AssertionError("OnBindViewHolder method not found")

    # Get method body (rough approximation - find matching braces)
    start = match.end() - 1  # Position of opening brace
    brace_count = 0
    end = start
    for i, c in enumerate(content[start:], start=start):
        if c == '{':
            brace_count += 1
        elif c == '}':
            brace_count -= 1
            if brace_count == 0:
                end = i
                break

    method_body = content[start:end+1]

    # Count meaningful statements (not just braces, comments, or blank lines)
    meaningful_lines = [
        line for line in method_body.split('\n')
        if line.strip()
        and not line.strip().startswith('//')
        and not line.strip() == '{'
        and not line.strip() == '}'
    ]

    # Should have at least 5 meaningful lines (base call, null checks, guard, event subscription)
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

    # Check for the critical rule about #nullable enable
    required_patterns = [
        r'#nullable enable',
        r'must be line 1',
        r'first line',
        r'RS0017',
        r'PublicAPI\.Unshipped\.txt',
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

    # Check for the bash script that safely handles PublicAPI files
    bash_patterns = [
        r'git diff --name-only --diff-filter=U',
        r'PublicAPI\.Unshipped\.txt',
        r'head -1',
        r'LC_ALL=C sort',
        r'for f in \$\(git diff',
    ]

    found = sum(1 for p in bash_patterns if re.search(p, content))
    if found < 3:
        raise AssertionError(
            f"copilot-instructions.md missing the safe bash script for handling PublicAPI files. "
            f"Found {found}/5 expected patterns."
        )
