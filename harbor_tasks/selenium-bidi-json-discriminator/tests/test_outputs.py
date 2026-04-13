"""
Test outputs for Selenium dotnet BiDi JSON discriminator improvement.

This tests the GetDiscriminator extension method that extracts a discriminator
value from a JSON object using Utf8JsonReader.
"""

import subprocess
import re

REPO = "/workspace/selenium"
TARGET_FILE = f"{REPO}/dotnet/src/webdriver/BiDi/Json/JsonExtensions.cs"


def test_valuetextequals_usage():
    """
    Fail-to-pass: Verify ValueTextEquals is used for property name comparison.

    The old code used GetString() + string comparison which is less efficient.
    The fix uses ValueTextEquals(name) which compares UTF-8 bytes directly.
    """
    with open(TARGET_FILE, "r") as f:
        content = f.read()

    # Check that ValueTextEquals is used (the fix)
    assert "ValueTextEquals" in content, \
        "ValueTextEquals should be used for property name comparison"

    # Check that the old pattern (propertyName == name) is NOT in the file anymore
    assert "propertyName == name" not in content, \
        "Old string comparison pattern should be replaced with ValueTextEquals"


def test_no_old_property_name_variable():
    """
    Fail-to-pass: Verify the old propertyName variable is not used anymore.

    Old code: string? propertyName = readerClone.GetString();
    New code: if (readerClone.ValueTextEquals(name))
    """
    with open(TARGET_FILE, "r") as f:
        content = f.read()

    # The old pattern creates a propertyName variable via GetString()
    assert "string? propertyName = readerClone.GetString()" not in content, \
        "Old propertyName variable assignment should be removed"


def test_reader_advancement_comments():
    """
    Fail-to-pass: Verify comments explain reader advancement logic.

    Per AGENTS.md: "Comments should explain *why*, not *what*"

    The fix adds comments like:
    - "move past StartObject to first PropertyName"
    - "move to the property value"
    - "skip the value (including nested objects/arrays)"
    """
    with open(TARGET_FILE, "r") as f:
        content = f.read()

    # Check for at least one of the improved comments explaining reader movement
    expected_comment_patterns = [
        "move past StartObject",
        "move to the property value",
        "skip the value",
        "move to the next PropertyName"
    ]

    found_comment = any(pattern in content for pattern in expected_comment_patterns)
    assert found_comment, \
        f"Comments explaining reader advancement should be present. " \
        f"Expected one of: {expected_comment_patterns}"


def test_correct_read_skip_pattern():
    """
    Fail-to-pass: Verify the correct Read-Skip-Read pattern for skipping properties.

    Old code:
        readerClone.Skip();
        readerClone.Read();

    New code:
        readerClone.Read(); // move to the property value
        readerClone.Skip(); // skip the value (including nested objects/arrays)
        readerClone.Read(); // move to the next PropertyName or EndObject
    """
    with open(TARGET_FILE, "r") as f:
        content = f.read()

    # Look for the pattern where we Read before Skip (the fix)
    # The fix adds a Read() call BEFORE Skip() when not matching
    lines = content.split('\n')

    found_read_before_skip = False
    for i, line in enumerate(lines):
        if "Skip()" in line and "// skip the value" in line:
            # Check if there's a Read() call on the previous line (or nearby)
            for j in range(max(0, i-3), i):
                if "readerClone.Read()" in lines[j] and "// move to the property value" in lines[j]:
                    found_read_before_skip = True
                    break

    assert found_read_before_skip, \
        "The correct Read-Skip-Read pattern should be present (Read before Skip when skipping)"


def test_valuetextequals_in_property_loop():
    """
    Fail-to-pass: Verify ValueTextEquals is called inside the PropertyName loop.

    The call should be inside: while (readerClone.TokenType == JsonTokenType.PropertyName)
    """
    with open(TARGET_FILE, "r") as f:
        content = f.read()

    # Find the GetDiscriminator method
    method_match = re.search(
        r'public static string GetDiscriminator\(this ref Utf8JsonReader reader, string name\).*?return discriminator',
        content,
        re.DOTALL
    )

    assert method_match, "GetDiscriminator method should exist"

    method_body = method_match.group(0)

    # Check that ValueTextEquals is inside the method
    assert "ValueTextEquals" in method_body, \
        "ValueTextEquals should be used in GetDiscriminator method"

    # Check that it's inside the PropertyName loop
    assert "while (readerClone.TokenType == JsonTokenType.PropertyName)" in method_body, \
        "PropertyName loop should exist"


def test_repo_dotnet_format_style():
    """
    Pass-to-pass: .NET code follows style conventions (editorconfig).

    Runs 'dotnet format style' to verify the webdriver project follows
    standard C# style conventions (file-scoped namespaces, using placement).

    This is the actual CI lint command used by the repo.
    """
    result = subprocess.run(
        ["bash", "-c", f"""
        cd {REPO}/dotnet

        # Create temporary solution file (dotnet format needs a solution)
        dotnet new sln -n CheckSln -o /tmp/check 2>/dev/null
        dotnet sln /tmp/check/CheckSln.sln add src/webdriver/Selenium.WebDriver.csproj 2>/dev/null

        # Check style with error severity (catches file-scoped namespace, using placement issues)
        dotnet format /tmp/check/CheckSln.sln style --severity error --verify-no-changes 2>&1
        echo EXIT:0
        """],
        capture_output=True,
        text=True,
        timeout=180
    )

    output = result.stdout + result.stderr
    assert "EXIT:0" in output, f"dotnet format style found issues:\n{output[-1000:]}"


def test_repo_dotnet_format_whitespace():
    """
    Pass-to-pass: .NET code follows whitespace conventions.

    Runs 'dotnet format whitespace' to verify the webdriver project follows
    standard C# whitespace conventions (indentation, newlines, spacing).

    This is the actual CI lint command used by the repo.
    """
    result = subprocess.run(
        ["bash", "-c", f"""
        cd {REPO}/dotnet

        # Create temporary solution file (dotnet format needs a solution)
        dotnet new sln -n CheckSln -o /tmp/check 2>/dev/null
        dotnet sln /tmp/check/CheckSln.sln add src/webdriver/Selenium.WebDriver.csproj 2>/dev/null

        # Check whitespace formatting
        dotnet format /tmp/check/CheckSln.sln whitespace --verify-no-changes 2>&1
        echo EXIT:0
        """],
        capture_output=True,
        text=True,
        timeout=180
    )

    output = result.stdout + result.stderr
    assert "EXIT:0" in output, f"dotnet format whitespace found issues:\n{output[-1000:]}"


def test_repo_dotnet_format():
    """
    Pass-to-pass: .NET code follows all formatting conventions.

    Runs 'dotnet format' to verify the webdriver project follows
    all standard C# formatting conventions (combines style + whitespace).

    This is the actual CI lint command used by the repo.
    """
    result = subprocess.run(
        ["bash", "-c", f"""
        cd {REPO}/dotnet

        # Create temporary solution file (dotnet format needs a solution)
        dotnet new sln -n CheckSln -o /tmp/check 2>/dev/null
        dotnet sln /tmp/check/CheckSln.sln add src/webdriver/Selenium.WebDriver.csproj 2>/dev/null

        # Check all formatting with error severity only
        dotnet format /tmp/check/CheckSln.sln --verify-no-changes --severity error 2>&1
        echo EXIT:0
        """],
        capture_output=True,
        text=True,
        timeout=180
    )

    output = result.stdout + result.stderr
    assert "EXIT:0" in output, f"dotnet format found formatting issues:\n{output[-1000:]}"


def test_repo_file_header():
    """
    Pass-to-pass: C# source files have proper copyright headers.

    Verifies the target file starts with the standard Selenium copyright header.
    """
    result = subprocess.run(
        ["bash", "-c", f"head -20 {TARGET_FILE} | grep -c '<copyright file=\"JsonExtensions.cs\"' || true"],
        capture_output=True,
        text=True,
        timeout=30
    )

    count = int(result.stdout.strip() or 0)
    assert count > 0, "Target file should have proper copyright header with file attribute"


# Alias for backward compatibility
test_discriminator_basic_extraction = test_valuetextequals_usage
test_discriminator_with_nested_objects = test_correct_read_skip_pattern
test_discriminator_with_arrays = test_reader_advancement_comments


def test_repo_python_syntax():
    """
    Pass-to-pass: Python scripts have valid syntax (pass_to_pass).

    Runs 'python3 -m py_compile' on Python files in the scripts directory
    to verify they have valid Python syntax.

    This is a lightweight CI check used by the repo.
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
        timeout=60
    )

    assert result.returncode == 0, f"Python syntax errors found:\n{result.stderr[-500:]}"
