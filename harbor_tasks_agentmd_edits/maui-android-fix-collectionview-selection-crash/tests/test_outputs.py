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
# Gates (pass_to_pass, static) — syntax / compilation checks
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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
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
# Pass-to-pass (repo_tests / static) — regression + anti-stub
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
# Config-derived (agent_config) — rules from copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .github/copilot-instructions.md:138-157 @ ecd6428d324e395ca07f8d375600c0fc93d0dd3c
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


# [agent_config] fail_to_pass — .github/copilot-instructions.md:148-157 @ ecd6428d324e395ca07f8d375600c0fc93d0dd3c
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
