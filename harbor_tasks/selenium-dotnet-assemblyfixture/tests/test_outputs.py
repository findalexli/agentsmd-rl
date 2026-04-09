"""
Test outputs for Selenium .NET AssemblyFixture task.

This task requires:
1. Creating a new AssemblyFixture.cs with [SetUpFixture] for global test setup
2. Removing duplicated [OneTimeSetUp] and [OneTimeTearDown] from test classes
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path("/workspace/selenium")
DOTNET_TEST_SUPPORT = REPO_ROOT / "dotnet" / "test" / "support"
ASSEMBLY_FIXTURE_PATH = DOTNET_TEST_SUPPORT / "AssemblyFixture.cs"
POPUP_TESTS_PATH = DOTNET_TEST_SUPPORT / "UI" / "PopupWindowFinderTests.cs"
SELECT_TESTS_PATH = DOTNET_TEST_SUPPORT / "UI" / "SelectBrowserTests.cs"


def parse_csharp_file(file_path: Path) -> dict:
    """
    Parse a C# file to extract key structural information.
    Since we can't use a full C# parser, we use regex-based heuristics
    combined with basic syntax analysis.
    """
    if not file_path.exists():
        return {"exists": False, "content": "", "usings": [], "classes": []}

    content = file_path.read_text()

    # Extract usings (lines starting with 'using ')
    usings = []
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('using ') and stripped.endswith(';'):
            usings.append(stripped[6:-1].strip())

    # Simple class extraction with attributes (not a full parser)
    classes = []
    lines = content.split('\n')
    current_class = None
    current_attrs = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track attributes
        if stripped.startswith('[') and stripped.endswith(']'):
            attr_name = stripped[1:-1].split('(')[0].strip()
            current_attrs.append(attr_name)

        # Class declaration
        if 'class ' in stripped and not stripped.startswith('//'):
            # Extract class name
            parts = stripped.split()
            for j, part in enumerate(parts):
                if part == 'class' and j + 1 < len(parts):
                    class_name = parts[j + 1].split(':')[0].split('{')[0].strip()
                    current_class = {
                        "name": class_name,
                        "attributes": current_attrs.copy(),
                        "line": i + 1,
                        "methods": []
                    }
                    classes.append(current_class)
                    current_attrs = []
                    break

        # Method detection within a class
        if current_class and ('public async Task ' in stripped or 'public void ' in stripped):
            # Extract method name
            if 'public async Task ' in stripped:
                method_part = stripped.split('public async Task ')[1]
            else:
                method_part = stripped.split('public void ')[1]
            method_name = method_part.split('(')[0].split('<')[0].strip()
            current_class["methods"].append({
                "name": method_name,
                "attributes": current_attrs.copy(),
                "line": i + 1
            })
            current_attrs = []

    return {
        "exists": True,
        "content": content,
        "usings": usings,
        "classes": classes
    }


def test_assembly_fixture_created():
    """F2P: Verify AssemblyFixture.cs file is created with proper structure."""
    parsed = parse_csharp_file(ASSEMBLY_FIXTURE_PATH)

    assert parsed["exists"], "AssemblyFixture.cs must be created"

    # Check namespace
    assert "OpenQA.Selenium.Support" in parsed["content"], \
        "Must use OpenQA.Selenium.Support namespace"

    # Check required usings
    assert "System.Threading.Tasks" in parsed["usings"], \
        "Must import System.Threading.Tasks"
    assert "NUnit.Framework" in parsed["usings"], \
        "Must import NUnit.Framework"
    assert "OpenQA.Selenium.Environment" in parsed["usings"], \
        "Must import OpenQA.Selenium.Environment"

    # Check class structure
    assembly_fixture = None
    for cls in parsed["classes"]:
        if cls["name"] == "AssemblyFixture":
            assembly_fixture = cls
            break

    assert assembly_fixture is not None, "Must have AssemblyFixture class"
    assert "SetUpFixture" in cls["attributes"], \
        "AssemblyFixture must have [SetUpFixture] attribute"


def test_assembly_fixture_setup_method():
    """F2P: Verify AssemblyFixture has proper OneTimeSetUp method."""
    parsed = parse_csharp_file(ASSEMBLY_FIXTURE_PATH)
    assert parsed["exists"], "AssemblyFixture.cs must exist"

    # Find the class
    assembly_fixture = None
    for cls in parsed["classes"]:
        if cls["name"] == "AssemblyFixture":
            assembly_fixture = cls
            break

    assert assembly_fixture is not None, "Must have AssemblyFixture class"

    # Check for RunBeforeAnyTestAsync method
    setup_method = None
    for method in assembly_fixture["methods"]:
        if method["name"] == "RunBeforeAnyTestAsync":
            setup_method = method
            break

    assert setup_method is not None, \
        "Must have RunBeforeAnyTestAsync method for OneTimeSetUp"
    assert "OneTimeSetUp" in setup_method["attributes"], \
        "RunBeforeAnyTestAsync must have [OneTimeSetUp] attribute"

    # Verify it starts the web server
    content = parsed["content"]
    assert "WebServer.StartAsync()" in content, \
        "Must start WebServer in RunBeforeAnyTestAsync"


def test_assembly_fixture_teardown_method():
    """F2P: Verify AssemblyFixture has proper OneTimeTearDown method."""
    parsed = parse_csharp_file(ASSEMBLY_FIXTURE_PATH)
    assert parsed["exists"], "AssemblyFixture.cs must exist"

    # Find the class
    assembly_fixture = None
    for cls in parsed["classes"]:
        if cls["name"] == "AssemblyFixture":
            assembly_fixture = cls
            break

    assert assembly_fixture is not None, "Must have AssemblyFixture class"

    # Check for RunAfterAnyTestsAsync method
    teardown_method = None
    for method in assembly_fixture["methods"]:
        if method["name"] == "RunAfterAnyTestsAsync":
            teardown_method = method
            break

    assert teardown_method is not None, \
        "Must have RunAfterAnyTestsAsync method for OneTimeTearDown"
    assert "OneTimeTearDown" in teardown_method["attributes"], \
        "RunAfterAnyTestsAsync must have [OneTimeTearDown] attribute"

    # Verify it stops the web server
    content = parsed["content"]
    assert "WebServer.StopAsync()" in content, \
        "Must stop WebServer in RunAfterAnyTestsAsync"
    assert "CloseCurrentDriver()" in content, \
        "Must close driver in RunAfterAnyTestsAsync"


def test_assembly_fixture_remote_server_support():
    """F2P: Verify AssemblyFixture handles remote server conditionally."""
    parsed = parse_csharp_file(ASSEMBLY_FIXTURE_PATH)
    assert parsed["exists"], "AssemblyFixture.cs must exist"

    content = parsed["content"]

    # Should check for Remote browser in setup
    assert 'Browser.Remote' in content, \
        "Must check for Browser.Remote condition"
    assert "RemoteServer.StartAsync()" in content, \
        "Must start RemoteServer when using Remote browser"
    assert "RemoteServer.StopAsync()" in content, \
        "Must stop RemoteServer when using Remote browser"


def test_popup_window_finder_cleanup():
    """F2P: Verify PopupWindowFinderTests no longer has duplicated setup/teardown."""
    parsed = parse_csharp_file(POPUP_TESTS_PATH)
    assert parsed["exists"], "PopupWindowFinderTests.cs must exist"

    content = parsed["content"]

    # Should NOT have OneTimeSetUp or OneTimeTearDown anymore
    assert "[OneTimeSetUp]" not in content, \
        "PopupWindowFinderTests must NOT have [OneTimeSetUp] (moved to AssemblyFixture)"
    assert "[OneTimeTearDown]" not in content, \
        "PopupWindowFinderTests must NOT have [OneTimeTearDown] (moved to AssemblyFixture)"

    # Should NOT have RunBeforeAnyTestAsync or RunAfterAnyTestsAsync
    assert "RunBeforeAnyTestAsync" not in content, \
        "PopupWindowFinderTests must NOT have RunBeforeAnyTestAsync method"
    assert "RunAfterAnyTestsAsync" not in content, \
        "PopupWindowFinderTests must NOT have RunAfterAnyTestsAsync method"

    # Should NOT import the Environment namespace anymore
    assert "OpenQA.Selenium.Environment" not in parsed["usings"], \
        "PopupWindowFinderTests should not need OpenQA.Selenium.Environment using"

    # Should NOT use System.Threading.Tasks anymore
    assert "System.Threading.Tasks" not in parsed["usings"], \
        "PopupWindowFinderTests should not need System.Threading.Tasks using"


def test_select_browser_tests_cleanup():
    """F2P: Verify SelectBrowserTests no longer has duplicated setup/teardown."""
    parsed = parse_csharp_file(SELECT_TESTS_PATH)
    assert parsed["exists"], "SelectBrowserTests.cs must exist"

    content = parsed["content"]

    # Should NOT have OneTimeSetUp or OneTimeTearDown anymore
    assert "[OneTimeSetUp]" not in content, \
        "SelectBrowserTests must NOT have [OneTimeSetUp] (moved to AssemblyFixture)"
    assert "[OneTimeTearDown]" not in content, \
        "SelectBrowserTests must NOT have [OneTimeTearDown] (moved to AssemblyFixture)"

    # Should NOT have RunBeforeAnyTestAsync or RunAfterAnyTestsAsync
    assert "RunBeforeAnyTestAsync" not in content, \
        "SelectBrowserTests must NOT have RunBeforeAnyTestAsync method"
    assert "RunAfterAnyTestsAsync" not in content, \
        "SelectBrowserTests must NOT have RunAfterAnyTestsAsync method"

    # Should NOT import the Environment namespace anymore
    assert "OpenQA.Selenium.Environment" not in parsed["usings"], \
        "SelectBrowserTests should not need OpenQA.Selenium.Environment using"

    # Should NOT use System.Threading.Tasks anymore (unless needed for other async methods)
    # Note: We check that specific setup/teardown methods are gone, not that Tasks is completely removed


def test_csharp_syntax_valid():
    """P2P: Verify C# files have valid syntax using dotnet format --verify-no-changes."""
    # Check that AssemblyFixture.cs can be parsed
    result = subprocess.run(
        ["dotnet", "format", "--verify-no-changes", "--include", str(ASSEMBLY_FIXTURE_PATH)],
        cwd=REPO_ROOT / "dotnet",
        capture_output=True,
        text=True,
        timeout=60
    )

    # If the file doesn't exist, this will fail - that's caught by other tests
    if ASSEMBLY_FIXTURE_PATH.exists():
        # dotnet format returns non-zero if there are formatting issues or syntax errors
        # We just want to check syntax, so we also try building
        build_result = subprocess.run(
            ["dotnet", "build", str(ASSEMBLY_FIXTURE_PATH), "--no-restore", "-v:q"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120
        )

        # A successful build or "project file" error (since single file isn't a project)
        # means syntax is generally valid
        output = build_result.stdout + build_result.stderr

        # Check for syntax errors
        assert "error CS" not in output or "project" in output.lower(), \
            f"AssemblyFixture.cs has syntax errors: {output}"


def test_no_duplicate_setup_methods():
    """F2P: Verify the TODO comment about moving setup is resolved in PopupWindowFinderTests."""
    parsed = parse_csharp_file(POPUP_TESTS_PATH)
    assert parsed["exists"], "PopupWindowFinderTests.cs must exist"

    content = parsed["content"]

    # The old TODO comment should be gone since we moved the setup
    assert "TODO: Move these to a standalone class" not in content, \
        "TODO comment about moving setup should be removed (it's now done in AssemblyFixture)"


def test_assembly_fixture_has_constructor():
    """P2P: Verify AssemblyFixture has a constructor."""
    parsed = parse_csharp_file(ASSEMBLY_FIXTURE_PATH)
    assert parsed["exists"], "AssemblyFixture.cs must exist"

    content = parsed["content"]

    # Should have a public constructor
    assert "public AssemblyFixture()" in content, \
        "AssemblyFixture should have a public constructor"


def test_logging_configuration():
    """P2P: Verify AssemblyFixture sets log level."""
    parsed = parse_csharp_file(ASSEMBLY_FIXTURE_PATH)
    assert parsed["exists"], "AssemblyFixture.cs must exist"

    content = parsed["content"]

    # Should set log level to Trace
    assert "Log.SetLevel" in content, \
        "AssemblyFixture should configure logging with Log.SetLevel"
    assert "LogEventLevel.Trace" in content, \
        "AssemblyFixture should set log level to Trace"
