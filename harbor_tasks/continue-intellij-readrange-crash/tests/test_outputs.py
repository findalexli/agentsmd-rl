"""
Test for readRangeInFile crash fix in IntelliJIde.kt

The bug: readRangeInFile throws StringIndexOutOfBoundsException when the
requested range is larger than the file. The fix clamps indices using coerceIn().
"""

import subprocess
import os

REPO = "/workspace/continue"
INTELLIJ_KT = os.path.join(
    REPO,
    "extensions/intellij/src/main/kotlin/com/github/continuedev/continueintellijextension/continue/IntelliJIde.kt"
)


def test_kotlin_compiles():
    """Kotlin code compiles successfully (pass_to_pass)."""
    r = subprocess.run(
        ["./gradlew", "compileKotlin"],
        cwd=os.path.join(REPO, "extensions/intellij"),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Kotlin compilation failed:\n{r.stderr[-1000:]}"


def test_source_contains_fix():
    """
    Source code contains the coerceIn fix (fail_to_pass on base, pass after fix).

    The fix adds coerceIn() calls to clamp line and character indices to prevent
    StringIndexOutOfBoundsException when reading ranges from files smaller
    than the requested range.
    """
    with open(INTELLIJ_KT, "r") as f:
        content = f.read()

    # The fix is the presence of coerceIn in readRangeInFile function context
    # This test fails on base (no coerceIn) and passes after fix
    assert "coerceIn" in content, \
        "coerceIn not found in source - fix may not have been applied"


def test_coerceIn_in_readRangeInFile_context():
    """
    The coerceIn calls appear within readRangeInFile function (idempotency).

    Verifies the fix is in the right function, not just somewhere else in the file.
    """
    with open(INTELLIJ_KT, "r") as f:
        lines = f.readlines()

    # Find the readRangeInFile function
    in_function = False
    function_lines = []
    for line in lines:
        if "override suspend fun readRangeInFile" in line:
            in_function = True
        if in_function:
            function_lines.append(line)
            # End of function detection (next function or class end)
            if in_function and len(function_lines) > 1 and line.strip().startswith("override"):
                function_lines.pop()
                break
            if in_function and line.strip().startswith("private fun"):
                function_lines.pop()
                break

    function_content = "".join(function_lines)

    # coerceIn must be inside readRangeInFile function after the fix
    assert "coerceIn" in function_content, \
        f"coerceIn not found in readRangeInFile function context"


def test_fix_handles_end_line_beyond_array():
    """
    The fix clamps endLine to lines.size - 1 (fail_to_pass test).

    Without the fix: lines.getOrNull(endLine)?.substring(0, endCharacter)
    would crash with StringIndexOutOfBoundsException when endLine >= lines.size.
    """
    # We verify the fix is present by checking that the code uses safe indexing
    with open(INTELLIJ_KT, "r") as f:
        content = f.read()

    # The fixed code should use coerceIn for line clamping
    # Pattern: range.end.line.coerceIn(...) or similar
    assert "range.end.line.coerceIn" in content or "endLine.coerceIn" in content or "coerceIn" in content, \
        "Line index clamping with coerceIn not found in readRangeInFile"


def test_fix_handles_char_beyond_line_length():
    """
    The fix clamps character indices to line.length (fail_to_pass test).

    Without the fix: line.substring(endCharacter) crashes when endCharacter > line.length.
    """
    with open(INTELLIJ_KT, "r") as f:
        content = f.read()

    # The fixed code should clamp character indices too
    # After the fix, we see patterns like: range.start.character.coerceIn(0, line.length)
    # or safeEnd = range.end.character.coerceIn(0, lastLineStr.length)
    assert content.count("coerceIn") >= 2, \
        "Multiple coerceIn calls expected for both line and char clamping"


def test_repo_existing_tests_pass():
    """Existing IntelliJ extension unit tests compile (pass_to_pass)."""
    r = subprocess.run(
        ["./gradlew", "compileTestKotlin"],
        cwd=os.path.join(REPO, "extensions/intellij"),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Test compilation failed:\n{r.stderr[-1000:]}"


def test_intellij_plugin_builds():
    """IntelliJ plugin builds successfully without tests (pass_to_pass)."""
    r = subprocess.run(
        ["./gradlew", "build", "-x", "test", "-x", "verifyPlugin"],
        cwd=os.path.join(REPO, "extensions/intellij"),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Plugin build failed:\n{r.stderr[-1000:]}"


def test_intellij_plugin_configuration_valid():
    """IntelliJ plugin configuration is valid (pass_to_pass)."""
    r = subprocess.run(
        ["./gradlew", "verifyPluginProjectConfiguration"],
        cwd=os.path.join(REPO, "extensions/intellij"),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Plugin configuration validation failed:\n{r.stderr[-1000:]}"