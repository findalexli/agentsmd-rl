#!/usr/bin/env python3
"""
Test suite for pulumi/pulumi#22436 - Add org commands to Python and Go Automation APIs.

This tests that the OrgGetDefault/OrgSetDefault methods exist in both Go and Python
Automation API implementations.
"""

import subprocess
import sys
import os

# Path to the pulumi repo
REPO = "/workspace/pulumi"
GO_SDK = f"{REPO}/sdk/go/auto"
PYTHON_SDK = f"{REPO}/sdk/python/lib/pulumi/automation"


def test_go_workspace_interface_has_org_methods():
    """Go Workspace interface must have OrgGetDefault and OrgSetDefault methods."""
    # Parse the workspace.go file to check for the interface methods
    with open(f"{GO_SDK}/workspace.go", "r") as f:
        content = f.read()

    assert "OrgGetDefault" in content, "Workspace interface missing OrgGetDefault method"
    assert "OrgSetDefault" in content, "Workspace interface missing OrgSetDefault method"


def test_go_local_workspace_has_org_methods():
    """Go LocalWorkspace must implement OrgGetDefault and OrgSetDefault."""
    with open(f"{GO_SDK}/local_workspace.go", "r") as f:
        content = f.read()

    # Check for method definitions
    assert "func (l *LocalWorkspace) OrgGetDefault" in content, \
        "LocalWorkspace missing OrgGetDefault implementation"
    assert "func (l *LocalWorkspace) OrgSetDefault" in content, \
        "LocalWorkspace missing OrgSetDefault implementation"

    # Check they use the correct pulumi commands
    assert '"org", "get-default"' in content, \
        "OrgGetDefault must run 'pulumi org get-default' command"
    assert '"org", "set-default"' in content, \
        "OrgSetDefault must run 'pulumi org set-default' command"


def test_go_org_methods_have_proper_error_handling():
    """Go org methods must have proper error handling with AutoError."""
    with open(f"{GO_SDK}/local_workspace.go", "r") as f:
        content = f.read()

    # Get the OrgGetDefault function implementation
    start_marker = "func (l *LocalWorkspace) OrgGetDefault"
    end_marker = "func (l *LocalWorkspace)"

    start_idx = content.find(start_marker)
    assert start_idx != -1, "OrgGetDefault not found"

    # Find the next function or end of file
    next_func_idx = content.find(end_marker, start_idx + len(start_marker))
    if next_func_idx == -1:
        func_impl = content[start_idx:]
    else:
        func_impl = content[start_idx:next_func_idx]

    # Check for error handling
    assert "newAutoError" in func_impl, "OrgGetDefault must use newAutoError for error handling"


def test_python_workspace_has_abstract_org_methods():
    """Python Workspace abstract class must declare org_get_default and org_set_default."""
    with open(f"{PYTHON_SDK}/_workspace.py", "r") as f:
        content = f.read()

    # Check for abstract method declarations
    assert "def org_get_default(self)" in content, \
        "Workspace missing abstract org_get_default method"
    assert "def org_set_default(self, org_name" in content, \
        "Workspace missing abstract org_set_default method"

    # Check they're marked as abstract
    assert "@abstractmethod" in content, "Methods must be abstract"


def test_python_local_workspace_has_org_methods():
    """Python LocalWorkspace must implement org_get_default and org_set_default."""
    with open(f"{PYTHON_SDK}/_local_workspace.py", "r") as f:
        content = f.read()

    # Check for method definitions
    assert "def org_get_default(self)" in content, \
        "LocalWorkspace missing org_get_default implementation"
    assert "def org_set_default(self, org_name" in content, \
        "LocalWorkspace missing org_set_default implementation"

    # Check they use the correct pulumi commands
    assert '["org", "get-default"]' in content, \
        "org_get_default must run 'pulumi org get-default' command"
    assert '["org", "set-default", org_name]' in content, \
        "org_set_default must run 'pulumi org set-default' command"


def test_go_syntax_valid():
    """Go code must compile without syntax errors."""
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=f"{REPO}/sdk/go",
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Go build failed:\n{result.stderr}"


def test_python_syntax_valid():
    """Python code must have valid syntax."""
    result = subprocess.run(
        ["python3", "-m", "py_compile", "_local_workspace.py", "_workspace.py"],
        cwd=PYTHON_SDK,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Python syntax check failed:\n{result.stderr}"


def test_go_auto_api_tests_exist():
    """Go auto API tests for org commands should exist."""
    with open(f"{GO_SDK}/local_workspace_test.go", "r") as f:
        content = f.read()

    assert "TestOrgGetSetDefault" in content, \
        "Go tests should include TestOrgGetSetDefault"


def test_python_auto_api_tests_exist():
    """Python auto API tests for org commands should exist."""
    test_file = f"{REPO}/sdk/python/lib/test/automation/test_local_workspace.py"
    if os.path.exists(test_file):
        with open(test_file, "r") as f:
            content = f.read()

        assert "test_org_get_set_default" in content.lower() or \
               "org_get_default" in content, \
            "Python tests should include org_get_default test"


def test_go_methods_follow_existing_patterns():
    """Go org methods should follow patterns of existing similar methods like WhoAmI."""
    with open(f"{GO_SDK}/local_workspace.go", "r") as f:
        content = f.read()

    # WhoAmI is a similar method - check our new methods follow the same pattern
    whoami_marker = "func (l *LocalWorkspace) WhoAmI"
    whoami_idx = content.find(whoami_marker)
    assert whoami_idx != -1, "Could not find WhoAmI for pattern reference"

    org_get_marker = "func (l *LocalWorkspace) OrgGetDefault"
    org_get_idx = content.find(org_get_marker)
    assert org_get_idx != -1, "OrgGetDefault not found"

    # Both should use runPulumiCmdSync
    assert "l.runPulumiCmdSync(ctx, \"whoami\")" in content
    assert "l.runPulumiCmdSync(ctx, \"org\", \"get-default\")" in content


def test_python_methods_follow_existing_patterns():
    """Python org methods should follow patterns of existing similar methods like who_am_i."""
    with open(f"{PYTHON_SDK}/_local_workspace.py", "r") as f:
        content = f.read()

    # Check that org methods follow the same pattern as who_am_i
    assert "self._run_pulumi_cmd_sync([\"whoami\"])" in content
    assert "self._run_pulumi_cmd_sync([\"org\", \"get-default\"])" in content


def test_go_interface_signature_correct():
    """Go interface methods should have correct signatures."""
    with open(f"{GO_SDK}/workspace.go", "r") as f:
        content = f.read()

    # OrgGetDefault should return (string, error)
    assert "OrgGetDefault(context.Context) (string, error)" in content, \
        "OrgGetDefault should have signature: OrgGetDefault(context.Context) (string, error)"

    # OrgSetDefault should take orgName and return error
    assert "OrgSetDefault(ctx context.Context, orgName string) error" in content, \
        "OrgSetDefault should have signature: OrgSetDefault(ctx context.Context, orgName string) error"


def test_python_docstrings_present():
    """Python methods should have proper docstrings."""
    with open(f"{PYTHON_SDK}/_workspace.py", "r") as f:
        content = f.read()

    # Check for docstrings on the abstract methods
    org_get_idx = content.find("def org_get_default")
    assert org_get_idx != -1, "org_get_default not found"

    # Look for docstring after the method definition
    section = content[org_get_idx:org_get_idx+500]
    assert '"""' in section, "org_get_default should have a docstring"
    assert "Returns the default organization" in content, \
        "org_get_default docstring should describe returning default organization"


# =============================================================================
# Pass-to-pass tests: Repo CI commands
# These tests run actual CI commands from the repository to verify the
# codebase passes linting, compilation, and other checks.
# =============================================================================


def test_go_auto_build_passes():
    """Go automation API compiles without errors (pass_to_pass)."""
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=f"{REPO}/sdk/go/auto",
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Go auto build failed:\n{result.stderr}"


def test_go_auto_vet_passes():
    """Go automation API passes go vet static analysis (pass_to_pass)."""
    result = subprocess.run(
        ["go", "vet", "./..."],
        cwd=f"{REPO}/sdk/go/auto",
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Go vet failed:\n{result.stderr}"


def test_go_auto_fmt_passes():
    """Go automation API passes gofmt formatting check (pass_to_pass)."""
    # Check main source files, excluding testdata directories with intentional errors
    source_files = [
        "cmd.go", "cmd_other.go", "cmd_windows.go", "errors.go",
        "local_workspace.go", "remote_workspace.go", "remote_stack.go",
        "stack.go", "workspace.go", "git.go", "minimum_version.go"
    ]

    for filename in source_files:
        filepath = f"{REPO}/sdk/go/auto/{filename}"
        if os.path.exists(filepath):
            result = subprocess.run(
                ["gofmt", "-l", filepath],
                capture_output=True,
                text=True,
                timeout=30
            )
            assert result.returncode == 0, f"gofmt check failed for {filename}:\n{result.stderr}"
            assert result.stdout.strip() == "", f"Go file {filename} needs formatting"


def test_go_auto_tests_compile():
    """Go automation API tests compile without errors (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-c", "./..."],
        cwd=f"{REPO}/sdk/go/auto",
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Go test compilation failed:\n{result.stderr}"


def test_python_auto_syntax_passes():
    """Python automation API has valid syntax (pass_to_pass)."""
    result = subprocess.run(
        ["python3", "-m", "py_compile", "_local_workspace.py", "_workspace.py"],
        cwd=f"{REPO}/sdk/python/lib/pulumi/automation",
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Python syntax check failed:\n{result.stderr}"


def test_go_sdk_module_tidy():
    """Go SDK module is properly tidied (pass_to_pass)."""
    result = subprocess.run(
        ["go", "mod", "tidy", "-diff"],
        cwd=f"{REPO}/sdk",
        capture_output=True,
        text=True,
        timeout=120
    )
    # -diff flag exits 0 if no changes needed, non-zero if changes needed
    assert result.returncode == 0, f"Go mod tidy check failed - module needs tidying:\n{result.stdout}\n{result.stderr}"


if __name__ == "__main__":
    # Run all tests
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
