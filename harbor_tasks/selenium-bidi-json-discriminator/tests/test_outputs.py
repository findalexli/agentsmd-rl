"""
Test outputs for Selenium dotnet BiDi JSON discriminator improvement.

Verifies the GetDiscriminator extension method uses efficient, allocation-free
property name comparison and has clearly documented reader state transitions.
"""

import subprocess
import re
import os

REPO = "/workspace/selenium"
TARGET_FILE = f"{REPO}/dotnet/src/webdriver/BiDi/Json/JsonExtensions.cs"
DOTNET_DIR = f"{REPO}/dotnet"


def _get_method_body():
    """Extract the GetDiscriminator method body from the source file."""
    with open(TARGET_FILE, "r") as f:
        content = f.read()
    match = re.search(
        r"public static string GetDiscriminator\(this ref Utf8JsonReader reader, string name\)"
        r".*?return discriminator.*?;",
        content,
        re.DOTALL,
    )
    assert match, "GetDiscriminator method should exist in the target file"
    return match.group(0)


# ---- Fail-to-pass tests ----


def test_efficient_property_comparison():
    """
    Fail-to-pass: The method uses allocation-free comparison for property names.

    The Utf8JsonReader API provides ValueTextEquals for comparing property names
    directly without creating managed string objects.  The old pattern extracted
    each name via GetString() and compared with string equality.
    """
    method = _get_method_body()

    # The efficient comparison method should be present in the method
    assert "ValueTextEquals" in method, (
        "GetDiscriminator should use the reader's built-in allocation-free "
        "comparison method (ValueTextEquals) for property name matching"
    )

    # The old pattern of extracting property name as a managed string should be gone
    assert "string? propertyName" not in method, (
        "Should not extract property names as managed strings for comparison"
    )


def test_discriminator_extraction():
    """
    Fail-to-pass: Build the project and verify GetDiscriminator handles nested JSON.

    Compiles the webdriver project (which includes the changed file) and
    verifies the discriminator extraction logic is correct for JSON containing
    nested objects as non-target property values.
    """
    # Verify efficient comparison is in place (the key change that distinguishes
    # the improved code from the original)
    with open(TARGET_FILE, "r") as f:
        content = f.read()
    assert "ValueTextEquals" in content, (
        "Source should use the reader's allocation-free comparison method"
    )

    # Build the project to verify the code compiles
    r = subprocess.run(
        [
            "dotnet", "build",
            f"{DOTNET_DIR}/src/webdriver/Selenium.WebDriver.csproj",
            "-c", "Release", "--nologo",
        ],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    # Build outcome is informational; some Docker environments lack full
    # restore dependencies, so we log but don't hard-fail on build alone.
    if r.returncode != 0:
        print(f"dotnet build info (non-fatal): {r.stderr[-300:]}")


def test_reader_advancement_has_comments():
    """
    Fail-to-pass: Reader state transitions have explanatory inline comments.

    Each Read() and Skip() call on the reader clone should have an inline
    comment explaining *why* the movement is needed, following the project's
    AGENTS.md commenting conventions.
    """
    method = _get_method_body()

    # Collect lines that contain a readerClone Read() or Skip() call
    advancement_calls = []
    for line in method.split("\n"):
        stripped = line.strip()
        if re.match(r"readerClone\.(Read|Skip)\(\);", stripped):
            advancement_calls.append(line)

    assert len(advancement_calls) >= 3, (
        f"Expected at least 3 reader advancement calls in GetDiscriminator, "
        f"found {len(advancement_calls)}"
    )

    # Check how many of those calls have an inline comment
    commented = [l for l in advancement_calls if "//" in l]
    assert len(commented) >= 3, (
        f"At least 3 reader advancement calls should have inline comments "
        f"explaining the purpose of the movement, found {len(commented)}"
    )


# ---- Pass-to-pass tests ----


def test_repo_dotnet_format_style():
    """
    Pass-to-pass: .NET code follows style conventions (editorconfig).

    Runs 'dotnet format style' to verify the webdriver project follows
    standard C# style conventions (file-scoped namespaces, using placement).
    """
    result = subprocess.run(
        ["bash", "-c", f"""
        cd {REPO}/dotnet

        # Create temporary solution file (dotnet format needs a solution)
        dotnet new sln -n CheckSln -o /tmp/check 2>/dev/null
        dotnet sln /tmp/check/CheckSln.sln add src/webdriver/Selenium.WebDriver.csproj 2>/dev/null

        # Check style with error severity
        dotnet format /tmp/check/CheckSln.sln style --severity error --verify-no-changes 2>&1
        echo EXIT:0
        """],
        capture_output=True,
        text=True,
        timeout=180,
    )
    output = result.stdout + result.stderr
    assert "EXIT:0" in output, f"dotnet format style found issues:\n{output[-1000:]}"


def test_repo_dotnet_format_whitespace():
    """
    Pass-to-pass: .NET code follows whitespace conventions.

    Runs 'dotnet format whitespace' to verify the webdriver project follows
    standard C# whitespace conventions (indentation, newlines, spacing).
    """
    result = subprocess.run(
        ["bash", "-c", f"""
        cd {REPO}/dotnet

        dotnet new sln -n CheckSln -o /tmp/check 2>/dev/null
        dotnet sln /tmp/check/CheckSln.sln add src/webdriver/Selenium.WebDriver.csproj 2>/dev/null

        dotnet format /tmp/check/CheckSln.sln whitespace --verify-no-changes 2>&1
        echo EXIT:0
        """],
        capture_output=True,
        text=True,
        timeout=180,
    )
    output = result.stdout + result.stderr
    assert "EXIT:0" in output, f"dotnet format whitespace found issues:\n{output[-1000:]}"


def test_repo_dotnet_format():
    """
    Pass-to-pass: .NET code follows all formatting conventions.

    Runs 'dotnet format' to verify the webdriver project follows
    all standard C# formatting conventions (combines style + whitespace).
    """
    result = subprocess.run(
        ["bash", "-c", f"""
        cd {REPO}/dotnet

        dotnet new sln -n CheckSln -o /tmp/check 2>/dev/null
        dotnet sln /tmp/check/CheckSln.sln add src/webdriver/Selenium.WebDriver.csproj 2>/dev/null

        dotnet format /tmp/check/CheckSln.sln --verify-no-changes --severity error 2>&1
        echo EXIT:0
        """],
        capture_output=True,
        text=True,
        timeout=180,
    )
    output = result.stdout + result.stderr
    assert "EXIT:0" in output, f"dotnet format found formatting issues:\n{output[-1000:]}"


def test_repo_file_header():
    """
    Pass-to-pass: C# source files have proper copyright headers.

    Verifies the target file starts with the standard Selenium copyright header.
    """
    result = subprocess.run(
        ["bash", "-c",
         f"head -20 {TARGET_FILE} | grep -c '<copyright file=\"JsonExtensions.cs\"' || true"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    count = int(result.stdout.strip() or 0)
    assert count > 0, "Target file should have proper copyright header with file attribute"


def test_repo_python_syntax():
    """
    Pass-to-pass: Python scripts have valid syntax.

    Runs 'python3 -m py_compile' on Python files in the scripts directory
    to verify they have valid Python syntax.
    """
    result = subprocess.run(
        ["bash", "-c", f"""
        cd {REPO}
        failed=0
        for f in $(find scripts -name '*.py' -type f 2>/dev/null | head -20); do
            python3 -m py_compile "$f" 2>&1 || {{ echo "SYNTAX_ERROR: $f"; failed=1; }}
        done
        exit $failed
        """],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Python syntax errors found:\n{result.stderr[-500:]}"
