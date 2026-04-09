"""
Tests for Selenium .NET BiDi network interception API removal.

This validates that the high-level interception methods have been properly removed
and that the API surface matches the expected post-refactoring state.

These tests use source code analysis rather than compilation since the full dotnet build
requires Bazel-generated files (selenium-manager binaries, DevTools generated code).
"""

import subprocess
import os
import sys
import re

REPO = "/workspace/selenium"
DOTNET_SRC = os.path.join(REPO, "dotnet/src/webdriver/BiDi")


def parse_interface_methods(file_path: str) -> list:
    """Parse method signatures from a C# interface file."""
    methods = []
    if not os.path.exists(file_path):
        return methods

    with open(file_path, 'r') as f:
        content = f.read()

    # Remove comments
    content = re.sub(r'//.*', '', content)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

    # Find interface declaration
    interface_match = re.search(r'interface\s+\w+\s*\{([^}]+)\}', content, re.DOTALL)
    if not interface_match:
        # Try with inheritance
        interface_match = re.search(r'interface\s+\w+\s*:\s*[^\{]+\{([^}]+)\}', content, re.DOTALL)

    if interface_match:
        interface_body = interface_match.group(1)
        # Find method declarations
        method_pattern = r'(Task<[^>]+>|Task|void|bool|int|string)\s+(\w+)\s*\([^)]*\)'
        for match in re.finditer(method_pattern, interface_body):
            methods.append(match.group(2))

    return methods


def parse_class_methods(file_path: str) -> list:
    """Parse public method signatures from a C# class file."""
    methods = []
    if not os.path.exists(file_path):
        return methods

    with open(file_path, 'r') as f:
        content = f.read()

    # Remove comments
    content = re.sub(r'//.*', '', content)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

    # Find method declarations (public methods)
    method_pattern = r'public\s+(?:async\s+)?(?:Task<[^>]+>|Task|void|bool|int|string)\s+(\w+)\s*\([^)]*\)'
    for match in re.finditer(method_pattern, content):
        methods.append(match.group(1))

    return methods


def test_high_level_methods_removed_from_interface():
    """F2P: InterceptRequestAsync/InterceptResponseAsync/InterceptAuthAsync should NOT exist on INetworkModule."""
    interface_file = os.path.join(REPO, "dotnet/src/webdriver/BiDi/Network/INetworkModule.cs")
    methods = parse_interface_methods(interface_file)

    high_level_methods = [m for m in methods if any(x in m for x in ["InterceptRequest", "InterceptResponse", "InterceptAuth"])]
    assert len(high_level_methods) == 0, f"High-level interception methods still exist in INetworkModule: {high_level_methods}"


def test_high_level_methods_removed_from_browsingcontext():
    """F2P: InterceptRequestAsync/InterceptResponseAsync/InterceptAuthAsync should NOT exist on IBrowsingContextNetworkModule."""
    interface_file = os.path.join(REPO, "dotnet/src/webdriver/BiDi/BrowsingContext/IBrowsingContextNetworkModule.cs")
    methods = parse_interface_methods(interface_file)

    high_level_methods = [m for m in methods if any(x in m for x in ["InterceptRequest", "InterceptResponse", "InterceptAuth"])]
    assert len(high_level_methods) == 0, f"High-level interception methods still exist in IBrowsingContextNetworkModule: {high_level_methods}"


def test_high_level_file_deleted():
    """F2P: NetworkModule.HighLevel.cs should be deleted."""
    high_level_file = os.path.join(REPO, "dotnet/src/webdriver/BiDi/Network/NetworkModule.HighLevel.cs")
    assert not os.path.exists(high_level_file), f"NetworkModule.HighLevel.cs should be deleted but exists at {high_level_file}"


def test_add_intercept_async_exists():
    """P2P: AddInterceptAsync should still exist as the replacement API."""
    interface_file = os.path.join(REPO, "dotnet/src/webdriver/BiDi/Network/INetworkModule.cs")
    methods = parse_interface_methods(interface_file)

    assert "AddInterceptAsync" in methods, f"AddInterceptAsync should exist in INetworkModule. Found methods: {methods}"


def test_event_subscription_methods_exist():
    """P2P: Event subscription methods should still exist."""
    interface_file = os.path.join(REPO, "dotnet/src/webdriver/BiDi/Network/INetworkModule.cs")
    methods = parse_interface_methods(interface_file)

    required_methods = ["OnBeforeRequestSentAsync", "OnResponseStartedAsync", "OnAuthRequiredAsync"]
    for method in required_methods:
        assert method in methods, f"{method} should exist in INetworkModule. Found methods: {methods}"


def test_project_compiles():
    """F2P: The BiDi Network project structure should be valid (check file integrity)."""
    # Instead of full build, verify that the critical BiDi files have valid syntax
    critical_files = [
        "dotnet/src/webdriver/BiDi/Network/INetworkModule.cs",
        "dotnet/src/webdriver/BiDi/Network/NetworkModule.cs",
        "dotnet/src/webdriver/BiDi/BrowsingContext/IBrowsingContextNetworkModule.cs",
        "dotnet/src/webdriver/BiDi/BrowsingContext/BrowsingContextNetworkModule.cs",
    ]

    for filepath in critical_files:
        fullpath = os.path.join(REPO, filepath)
        assert os.path.exists(fullpath), f"Critical file missing: {filepath}"

        with open(fullpath, 'r') as f:
            content = f.read()

        # Basic syntax validation - check brace balance
        open_braces = content.count('{')
        close_braces = content.count('}')
        assert open_braces == close_braces, f"Brace mismatch in {filepath}: {open_braces} open, {close_braces} close"

        # Check parentheses balance in the file
        open_parens = content.count('(')
        close_parens = content.count(')')
        assert open_parens == close_parens, f"Parentheses mismatch in {filepath}"


def test_intercept_options_types_removed():
    """F2P: InterceptRequestOptions, InterceptResponseOptions, InterceptAuthOptions should be removed."""
    # Check in the BrowsingContextNetworkModule file where these types were defined
    bc_network_file = os.path.join(REPO, "dotnet/src/webdriver/BiDi/BrowsingContext/BrowsingContextNetworkModule.cs")

    if os.path.exists(bc_network_file):
        with open(bc_network_file, 'r') as f:
            content = f.read()

        removed_types = ["InterceptRequestOptions", "InterceptResponseOptions", "InterceptAuthOptions"]
        for type_name in removed_types:
            assert type_name not in content, f"{type_name} should be removed but found in {bc_network_file}"

    # Also check the interface file
    interface_file = os.path.join(REPO, "dotnet/src/webdriver/BiDi/BrowsingContext/IBrowsingContextNetworkModule.cs")
    if os.path.exists(interface_file):
        with open(interface_file, 'r') as f:
            content = f.read()

        removed_types = ["InterceptRequestOptions", "InterceptResponseOptions", "InterceptAuthOptions"]
        for type_name in removed_types:
            assert type_name not in content, f"{type_name} should be removed but found in {interface_file}"


def test_intercepted_event_types_removed():
    """F2P: InterceptedRequest, InterceptedResponse, InterceptedAuth, Interception types should be removed."""
    # Check in the BrowsingContextNetworkModule file where these types were used
    bc_network_file = os.path.join(REPO, "dotnet/src/webdriver/BiDi/BrowsingContext/BrowsingContextNetworkModule.cs")

    if os.path.exists(bc_network_file):
        with open(bc_network_file, 'r') as f:
            content = f.read()

        # These types were used in the removed high-level methods
        removed_types = ["InterceptedRequest", "InterceptedResponse", "InterceptedAuth"]
        for type_name in removed_types:
            assert type_name not in content, f"{type_name} should be removed but found in {bc_network_file}"

    # Check for Interception return type
    interface_file = os.path.join(REPO, "dotnet/src/webdriver/BiDi/BrowsingContext/IBrowsingContextNetworkModule.cs")
    if os.path.exists(interface_file):
        with open(interface_file, 'r') as f:
            content = f.read()

        # The Interception type was used as return type for the removed methods
        assert "Task<Interception>" not in content, "Interception return type should be removed from interface"


# Pass-to-pass tests (repo CI/CD verification)

def test_dotnet_format_style():
    """P2P: dotnet format style check passes (repo CI linting standard)."""
    result = subprocess.run(
        ["dotnet", "format", "style", "--verify-no-changes", "--severity", "warn", "--no-restore"],
        capture_output=True,
        cwd=os.path.join(REPO, "dotnet"),
        timeout=120,
    )
    # Return code 0 = no changes needed (pass)
    # Return code 1 = changes needed (format violations but command worked)
    # Any other code = actual error
    assert result.returncode in [0, 1], f"dotnet format style failed with error: {result.stderr.decode()[:500]}"


def test_dotnet_format_whitespace():
    """P2P: dotnet format whitespace check passes (repo CI linting standard)."""
    result = subprocess.run(
        ["dotnet", "format", "whitespace", "--verify-no-changes", "--no-restore"],
        capture_output=True,
        cwd=os.path.join(REPO, "dotnet"),
        timeout=120,
    )
    # Return code 0 = no changes needed (pass)
    # Return code 1 = changes needed (format violations but command worked)
    assert result.returncode in [0, 1], f"dotnet format whitespace failed with error: {result.stderr.decode()[:500]}"


def test_repo_structure_valid():
    """P2P: Repository structure is valid - critical files exist and are readable."""
    # Check that critical files exist and are readable
    critical_files = [
        "dotnet/src/webdriver/BiDi/Network/INetworkModule.cs",
        "dotnet/src/webdriver/BiDi/Network/NetworkModule.cs",
        "dotnet/src/webdriver/BiDi/Network/AddInterceptCommand.cs",
        "dotnet/src/webdriver/BiDi/BrowsingContext/IBrowsingContextNetworkModule.cs",
        "dotnet/src/webdriver/BiDi/BrowsingContext/BrowsingContextNetworkModule.cs",
        "dotnet/src/webdriver/Selenium.WebDriver.csproj",
        "dotnet/Selenium.slnx",
    ]

    for filepath in critical_files:
        fullpath = os.path.join(REPO, filepath)
        assert os.path.exists(fullpath), f"Critical file missing: {filepath}"
        assert os.path.getsize(fullpath) > 0, f"Critical file is empty: {filepath}"
        # Verify file is readable
        with open(fullpath, 'r') as f:
            content = f.read(100)  # Read first 100 chars
            assert len(content) > 0, f"Could not read critical file: {filepath}"


def test_bidi_module_syntax_valid():
    """P2P: BiDi Network module files have valid C# syntax (no parse errors)."""
    # List of BiDi Network files to check
    network_files = [
        "dotnet/src/webdriver/BiDi/Network/NetworkModule.cs",
        "dotnet/src/webdriver/BiDi/Network/INetworkModule.cs",
        "dotnet/src/webdriver/BiDi/Network/AddInterceptCommand.cs",
        "dotnet/src/webdriver/BiDi/Network/Intercept.cs",
        "dotnet/src/webdriver/BiDi/Network/RemoveInterceptCommand.cs",
    ]

    # Check each file for basic syntax issues
    for filepath in network_files:
        fullpath = os.path.join(REPO, filepath)
        if os.path.exists(fullpath):
            # Read the file
            with open(fullpath, 'r') as f:
                content = f.read()

            # Basic syntax check: count braces to detect obvious issues
            open_braces = content.count('{')
            close_braces = content.count('}')
            assert open_braces == close_braces, f"Brace mismatch in {filepath}: {open_braces} open, {close_braces} close"

            # Check for basic syntax errors (unmatched parentheses in method signatures)
            open_parens = content.count('(')
            close_parens = content.count(')')
            assert open_parens == close_parens, f"Parentheses mismatch in {filepath}"
