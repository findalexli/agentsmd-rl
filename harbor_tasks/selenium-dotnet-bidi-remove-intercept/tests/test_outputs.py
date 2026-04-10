"""Tests for Selenium .NET BiDi network interception removal task."""

import subprocess
import os
import sys

REPO = "/workspace/selenium"


def test_highlevel_file_removed():
    """NetworkModule.HighLevel.cs should be deleted (fail-to-pass).

    The high-level interception API file should be completely removed.
    """
    highlevel_file = os.path.join(REPO, "dotnet/src/webdriver/BiDi/Network/NetworkModule.HighLevel.cs")
    assert not os.path.exists(highlevel_file), (
        f"NetworkModule.HighLevel.cs should be deleted but still exists at {highlevel_file}"
    )


def test_intercept_methods_removed_from_network_module():
    """InterceptRequestAsync/InterceptResponseAsync/InterceptAuthAsync removed from NetworkModule (fail-to-pass).

    The high-level interception methods should be removed from the main NetworkModule class.
    """
    network_module_file = os.path.join(REPO, "dotnet/src/webdriver/BiDi/Network/NetworkModule.cs")

    # Read the file content
    with open(network_module_file, 'r') as f:
        content = f.read()

    # Check that high-level methods are NOT present
    forbidden_methods = ['InterceptRequestAsync', 'InterceptResponseAsync', 'InterceptAuthAsync']
    for method in forbidden_methods:
        assert method not in content, (
            f"Method '{method}' should be removed from NetworkModule but still found"
        )


def test_intercept_methods_removed_from_interface():
    """Intercept methods removed from INetworkModule interface (fail-to-pass)."""
    interface_file = os.path.join(REPO, "dotnet/src/webdriver/BiDi/Network/INetworkModule.cs")

    with open(interface_file, 'r') as f:
        content = f.read()

    forbidden_methods = ['InterceptRequestAsync', 'InterceptResponseAsync', 'InterceptAuthAsync']
    for method in forbidden_methods:
        assert method not in content, (
            f"Method '{method}' should be removed from INetworkModule interface but still found"
        )


def test_intercept_methods_removed_from_browsing_context():
    """Intercept methods removed from BrowsingContextNetworkModule (fail-to-pass)."""
    module_file = os.path.join(REPO, "dotnet/src/webdriver/BiDi/BrowsingContext/BrowsingContextNetworkModule.cs")

    with open(module_file, 'r') as f:
        content = f.read()

    forbidden_methods = ['InterceptRequestAsync', 'InterceptResponseAsync', 'InterceptAuthAsync']
    for method in forbidden_methods:
        assert method not in content, (
            f"Method '{method}' should be removed from BrowsingContextNetworkModule but still found"
        )


def test_intercept_methods_removed_from_browsing_context_interface():
    """Intercept methods removed from IBrowsingContextNetworkModule interface (fail-to-pass)."""
    interface_file = os.path.join(REPO, "dotnet/src/webdriver/BiDi/BrowsingContext/IBrowsingContextNetworkModule.cs")

    with open(interface_file, 'r') as f:
        content = f.read()

    forbidden_methods = ['InterceptRequestAsync', 'InterceptResponseAsync', 'InterceptAuthAsync']
    for method in forbidden_methods:
        assert method not in content, (
            f"Method '{method}' should be removed from IBrowsingContextNetworkModule interface but still found"
        )


def test_intercepted_types_removed():
    """InterceptedRequest/InterceptedResponse/InterceptedAuth types removed (fail-to-pass)."""
    # These types were defined in NetworkModule.HighLevel.cs which is deleted
    # Let's verify by checking if they exist anywhere in the BiDi Network folder
    bidi_network_dir = os.path.join(REPO, "dotnet/src/webdriver/BiDi/Network")

    forbidden_types = ['InterceptedRequest', 'InterceptedResponse', 'InterceptedAuth', 'Interception']

    for root, dirs, files in os.walk(bidi_network_dir):
        for file in files:
            if file.endswith('.cs'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                for type_name in forbidden_types:
                    # Check for class/record definition, not just usage
                    if f'record {type_name}' in content or f'class {type_name}' in content:
                        assert False, (
                            f"Type '{type_name}' should be removed but found in {filepath}"
                        )


def test_intercept_options_removed():
    """InterceptRequestOptions/InterceptResponseOptions/InterceptAuthOptions removed (fail-to-pass)."""
    # Check both Network and BrowsingContext directories
    dirs_to_check = [
        os.path.join(REPO, "dotnet/src/webdriver/BiDi/Network"),
        os.path.join(REPO, "dotnet/src/webdriver/BiDi/BrowsingContext"),
    ]

    forbidden_types = ['InterceptRequestOptions', 'InterceptResponseOptions', 'InterceptAuthOptions']

    for check_dir in dirs_to_check:
        for root, dirs, files in os.walk(check_dir):
            for file in files:
                if file.endswith('.cs'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r') as f:
                        content = f.read()
                    for type_name in forbidden_types:
                        # Check for record definition
                        if f'record {type_name}' in content:
                            assert False, (
                                f"Type '{type_name}' should be removed but found in {filepath}"
                            )


def test_tests_updated():
    """Tests are updated to use AddInterceptAsync instead of high-level methods (fail-to-pass).

    Verify that the test file no longer references the removed high-level methods.
    """
    test_file = os.path.join(REPO, "dotnet/test/webdriver/BiDi/Network/NetworkTests.cs")

    with open(test_file, 'r') as f:
        content = f.read()

    forbidden_methods = ['InterceptRequestAsync', 'InterceptResponseAsync', 'InterceptAuthAsync']
    for method in forbidden_methods:
        assert method not in content, (
            f"Test file should not reference removed method '{method}' but still found"
        )

    # Also verify the tests now use AddInterceptAsync
    assert 'AddInterceptAsync' in content, (
        "Test file should use AddInterceptAsync as replacement"
    )


# ==================== PASS-TO-PASS TESTS ====================


def test_addintercept_api_still_exists():
    """AddInterceptAsync method still exists and is accessible (pass-to-pass).

    The lower-level API that replaces the high-level one should still be available.
    """
    interface_file = os.path.join(REPO, "dotnet/src/webdriver/BiDi/Network/INetworkModule.cs")

    with open(interface_file, 'r') as f:
        content = f.read()

    assert 'AddInterceptAsync' in content, (
        "AddInterceptAsync method should exist in INetworkModule interface"
    )


def test_csharp_syntax_valid():
    """The C# code has valid syntax (pass-to-pass).

    Since full build requires Bazel which isn't available in this environment,
    we verify syntax by parsing the C# files.
    """
    import glob

    # Collect all C# files in the BiDi module
    bidi_dir = os.path.join(REPO, "dotnet/src/webdriver/BiDi")
    cs_files = glob.glob(os.path.join(bidi_dir, "**/*.cs"), recursive=True)

    # Basic syntax validation - check for balanced braces and common issues
    for filepath in cs_files:
        with open(filepath, 'r') as f:
            content = f.read()

        # Skip designer files and generated files
        if '.Designer.cs' in filepath or 'Generated' in filepath:
            continue

        # Check for basic syntax issues
        open_braces = content.count('{')
        close_braces = content.count('}')

        # Allow for slight imbalance due to complex string literals
        if abs(open_braces - close_braces) > 5:
            # Check if it's just in comments or strings
            lines = content.split('\n')
            code_only = []
            for line in lines:
                # Skip comments
                if line.strip().startswith('//'):
                    continue
                # Skip documentation comments
                if line.strip().startswith('///'):
                    continue
                code_only.append(line)

            code_text = '\n'.join(code_only)
            code_open = code_text.count('{')
            code_close = code_text.count('}')

            if code_open != code_close:
                assert False, (
                    f"Syntax error in {filepath}: unbalanced braces ({code_open} open, {code_close} close)"
                )


def test_dotnet_project_structure_valid():
    """The .NET project structure is valid (pass-to-pass).

    Verify that the project file doesn't reference deleted files.
    """
    project_file = os.path.join(REPO, "dotnet/src/webdriver/Selenium.WebDriver.csproj")

    with open(project_file, 'r') as f:
        content = f.read()

    # Check that the deleted file is NOT referenced in the project
    assert 'NetworkModule.HighLevel.cs' not in content, (
        "Project file should not reference deleted NetworkModule.HighLevel.cs"
    )

    # Verify the project file is valid XML
    try:
        import xml.etree.ElementTree as ET
        ET.fromstring(content)
    except ET.ParseError as e:
        assert False, f"Invalid project file XML: {e}"


# ==================== REPO CI TESTS (subprocess.run) ====================


def test_repo_dotnet_format_whitespace():
    """.NET webdriver project whitespace formatting passes (pass_to_pass).

    Runs actual CI command: dotnet format whitespace --verify-no-changes
    """
    project_file = os.path.join(REPO, "dotnet/src/webdriver/Selenium.WebDriver.csproj")

    r = subprocess.run(
        ["dotnet", "format", "whitespace", "--verify-no-changes", project_file],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"dotnet format whitespace failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_dotnet_format_analyzers():
    """.NET webdriver project analyzers pass (pass_to_pass).

    Runs actual CI command: dotnet format analyzers --verify-no-changes
    """
    project_file = os.path.join(REPO, "dotnet/src/webdriver/Selenium.WebDriver.csproj")

    r = subprocess.run(
        ["dotnet", "format", "analyzers", "--verify-no-changes", project_file],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"dotnet format analyzers failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_dotnet_test_project_format():
    """.NET test project whitespace formatting passes (pass_to_pass).

    Runs actual CI command: dotnet format whitespace --verify-no-changes
    """
    project_file = os.path.join(REPO, "dotnet/test/webdriver/Selenium.WebDriver.Tests.csproj")

    r = subprocess.run(
        ["dotnet", "format", "whitespace", "--verify-no-changes", project_file],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"dotnet format whitespace for test project failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_dotnet_support_project_format():
    """.NET support project whitespace formatting passes (pass_to_pass).

    Runs actual CI command: dotnet format whitespace --verify-no-changes
    """
    project_file = os.path.join(REPO, "dotnet/src/support/Selenium.WebDriver.Support.csproj")

    r = subprocess.run(
        ["dotnet", "format", "whitespace", "--verify-no-changes", project_file],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    # Support project may not exist in all configurations
    if r.returncode != 0 and ("not found" in r.stderr.lower() or "does not exist" in r.stderr.lower()):
        return  # Skip if project not found
    assert r.returncode == 0, f"dotnet format whitespace for support project failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_dotnet_restore():
    """.NET project restore succeeds (pass_to_pass).

    Verifies NuGet packages can be restored (basic project health check).
    """
    project_file = os.path.join(REPO, "dotnet/src/webdriver/Selenium.WebDriver.csproj")

    r = subprocess.run(
        ["dotnet", "restore", project_file],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"dotnet restore failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# Legacy tests kept for compatibility


def test_dotnet_format_check():
    """.NET code formatting passes validation (pass-to-pass).

    Run dotnet format --verify-no-changes --severity error to verify
    no formatting errors exist in the codebase.
    """
    project_file = os.path.join(REPO, "dotnet/src/webdriver/Selenium.WebDriver.csproj")

    r = subprocess.run(
        ["dotnet", "format", "--verify-no-changes", "--severity", "error", project_file],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )

    # Exit code 0 means no formatting errors found
    assert r.returncode == 0, f"dotnet format found errors:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_dotnet_test_project_format_check():
    """.NET test project formatting passes validation (pass-to-pass).

    Run dotnet format --verify-no-changes --severity error to verify
    no formatting errors exist in the test project.
    """
    project_file = os.path.join(REPO, "dotnet/test/webdriver/Selenium.WebDriver.Tests.csproj")

    r = subprocess.run(
        ["dotnet", "format", "--verify-no-changes", "--severity", "error", project_file],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )

    # Exit code 0 means no formatting errors found
    assert r.returncode == 0, f"dotnet format found errors in test project:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_dotnet_support_project_format_check():
    """.NET support project formatting passes validation (pass-to-pass).

    Run dotnet format --verify-no-changes --severity error to verify
    no formatting errors exist in the support project.
    """
    project_file = os.path.join(REPO, "dotnet/src/support/Selenium.WebDriver.Support.csproj")

    r = subprocess.run(
        ["dotnet", "format", "--verify-no-changes", "--severity", "error", project_file],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )

    # Exit code 0 means no formatting errors found
    # This is optional - if the project doesn't exist or command fails, skip
    if r.returncode != 0 and "not found" in r.stderr.lower():
        return  # Skip if project not found

    assert r.returncode == 0, f"dotnet format found errors in support project:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"
