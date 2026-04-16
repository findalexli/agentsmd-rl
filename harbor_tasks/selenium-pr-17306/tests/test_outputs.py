"""
Tests for SeleniumHQ/selenium#17306: [dotnet] [bidi] Testing infra for custom module

This PR makes internal types public and removes InternalsVisibleTo, enabling
external module extensibility.
"""

import os
import subprocess

REPO = "/workspace/selenium"


# =============================================================================
# FAIL-TO-PASS TESTS
# These must FAIL on the base commit and PASS after the fix
# =============================================================================

def test_command_class_is_public():
    """Command<TParameters, TResult> class must be public (fail_to_pass)."""
    file_path = os.path.join(REPO, "dotnet/src/webdriver/BiDi/Command.cs")
    with open(file_path, 'r') as f:
        content = f.read()

    # The class declaration should be public, not internal
    assert "public abstract class Command<TParameters, TResult>" in content, \
        "Command<TParameters, TResult> must be declared as public, not internal"


def test_parameters_record_is_public():
    """Parameters record must be public (fail_to_pass)."""
    file_path = os.path.join(REPO, "dotnet/src/webdriver/BiDi/Command.cs")
    with open(file_path, 'r') as f:
        content = f.read()

    # The record declaration should be public, not internal
    assert "public record Parameters" in content, \
        "Parameters record must be declared as public, not internal"


def test_ilogger_interface_is_public():
    """ILogger interface must be public (fail_to_pass)."""
    file_path = os.path.join(REPO, "dotnet/src/webdriver/Internal/Logging/ILogger.cs")
    with open(file_path, 'r') as f:
        content = f.read()

    # The interface declaration should be public, not internal
    assert "public interface ILogger" in content, \
        "ILogger interface must be declared as public, not internal"


def test_log_current_context_is_public():
    """Log.CurrentContext property must be public (fail_to_pass)."""
    file_path = os.path.join(REPO, "dotnet/src/webdriver/Internal/Logging/Log.cs")
    with open(file_path, 'r') as f:
        content = f.read()

    # Look for public static ILogContext CurrentContext
    assert "public static ILogContext CurrentContext" in content, \
        "Log.CurrentContext must be declared as public, not internal"


def test_log_getlogger_generic_is_public():
    """Log.GetLogger<T>() method must be public (fail_to_pass)."""
    file_path = os.path.join(REPO, "dotnet/src/webdriver/Internal/Logging/Log.cs")
    with open(file_path, 'r') as f:
        content = f.read()

    # Look for public static ILogger GetLogger<T>()
    assert "public static ILogger GetLogger<T>()" in content, \
        "Log.GetLogger<T>() must be declared as public, not internal"


def test_log_getlogger_type_is_public():
    """Log.GetLogger(Type) method must be public (fail_to_pass)."""
    file_path = os.path.join(REPO, "dotnet/src/webdriver/Internal/Logging/Log.cs")
    with open(file_path, 'r') as f:
        content = f.read()

    # Look for public static ILogger GetLogger(Type type)
    assert "public static ILogger GetLogger(Type type)" in content, \
        "Log.GetLogger(Type) must be declared as public, not internal"


def test_ilogcontext_getlogger_methods_are_public():
    """ILogContext.GetLogger methods must be public (fail_to_pass)."""
    file_path = os.path.join(REPO, "dotnet/src/webdriver/Internal/Logging/ILogContext.cs")
    with open(file_path, 'r') as f:
        content = f.read()

    # The interface methods should NOT have 'internal' modifier
    # In C#, interface members without explicit modifier are public
    # So we check that 'internal ILogger GetLogger' is NOT present
    assert "internal ILogger GetLogger" not in content, \
        "ILogContext.GetLogger methods must not have internal modifier"


def test_internals_visible_to_removed_from_csproj():
    """InternalsVisibleTo must be removed from csproj (fail_to_pass)."""
    file_path = os.path.join(REPO, "dotnet/src/webdriver/Selenium.WebDriver.csproj")
    with open(file_path, 'r') as f:
        content = f.read()

    assert "InternalsVisibleTo" not in content, \
        "InternalsVisibleTo attribute must be removed from Selenium.WebDriver.csproj"


def test_internals_visible_to_removed_from_bazel():
    """internals_visible_to must be removed from BUILD.bazel (fail_to_pass)."""
    file_path = os.path.join(REPO, "dotnet/src/webdriver/BUILD.bazel")
    with open(file_path, 'r') as f:
        content = f.read()

    assert "internals_visible_to" not in content, \
        "internals_visible_to must be removed from BUILD.bazel"


# =============================================================================
# PASS-TO-PASS TESTS
# These must PASS both before and after the fix
# =============================================================================

def test_command_base_class_exists():
    """Command base class exists and is public (pass_to_pass)."""
    file_path = os.path.join(REPO, "dotnet/src/webdriver/BiDi/Command.cs")
    with open(file_path, 'r') as f:
        content = f.read()

    # The base Command class should exist with protected constructor
    assert "protected Command(string method)" in content, \
        "Command base class with protected constructor must exist"


def test_log_class_exists():
    """Log class with public CreateContext method exists (pass_to_pass)."""
    file_path = os.path.join(REPO, "dotnet/src/webdriver/Internal/Logging/Log.cs")
    with open(file_path, 'r') as f:
        content = f.read()

    # Log.CreateContext should be public
    assert "public static ILogContext CreateContext" in content, \
        "Log.CreateContext must be public"


def test_ilogcontext_interface_is_public():
    """ILogContext interface is public (pass_to_pass)."""
    file_path = os.path.join(REPO, "dotnet/src/webdriver/Internal/Logging/ILogContext.cs")
    with open(file_path, 'r') as f:
        content = f.read()

    assert "public interface ILogContext" in content, \
        "ILogContext interface must be public"


def test_repo_dotnet_format_whitespace():
    """Dotnet format whitespace check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        [
            "dotnet", "format", "whitespace",
            "src/webdriver/Selenium.WebDriver.csproj",
            "--verify-no-changes",
            "--include", "src/webdriver/BiDi/", "src/webdriver/Internal/Logging/"
        ],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=os.path.join(REPO, "dotnet"),
    )
    assert r.returncode == 0, f"Whitespace format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_dotnet_format_style():
    """Dotnet format style check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        [
            "dotnet", "format", "style",
            "src/webdriver/Selenium.WebDriver.csproj",
            "--verify-no-changes",
            "--include", "src/webdriver/BiDi/", "src/webdriver/Internal/Logging/"
        ],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=os.path.join(REPO, "dotnet"),
    )
    assert r.returncode == 0, f"Style format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_dotnet_restore():
    """Dotnet restore succeeds for webdriver project (pass_to_pass)."""
    r = subprocess.run(
        [
            "dotnet", "restore",
            "src/webdriver/Selenium.WebDriver.csproj"
        ],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=os.path.join(REPO, "dotnet"),
    )
    assert r.returncode == 0, f"dotnet restore failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
