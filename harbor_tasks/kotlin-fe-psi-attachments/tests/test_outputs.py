"""Test that the PSI attachment exception improvement is correctly implemented."""

import subprocess
import re
import sys
import pytest

REPO = "/workspace/kotlin"
TARGET_FILE = "compiler/frontend.common/src/org/jetbrains/kotlin/diagnostics/KtDiagnostic.kt"

def run_cmd(cmd, cwd=REPO):
    """Run a command and return the result."""
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return result


# =============================================================================
# PASS-TO-PASS TESTS: Verify CI checks pass on base commit AND after fix
# These ensure the fix doesn't break existing functionality
# =============================================================================

def test_p2p_frontend_common_compiles():
    """Repo CI: compiler:frontend.common compiles successfully (p2p).

    This is the module being modified. Verifies it compiles without errors.
    """
    result = subprocess.run(
        ["./gradlew", ":compiler:frontend.common:compileKotlin", "--no-daemon", "-q"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900,  # ~11 minutes for clean build
    )
    assert result.returncode == 0, f"Compilation failed:\nstdout: {result.stdout[-1000:]}\nstderr: {result.stderr[-1000:]}"


def test_p2p_frontend_common_classes_exist():
    """Repo CI: compiler:frontend.common produces class files (p2p).

    Lightweight check that compilation produces expected outputs.
    """
    result = subprocess.run(
        ["./gradlew", ":compiler:frontend.common:classes", "--no-daemon", "-q"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert result.returncode == 0, f"Classes task failed:\nstderr: {result.stderr[-500:]}"


def test_p2p_kotlin_file_syntax_valid():
    """Repo CI: KtDiagnostic.kt has no syntax errors (p2p).

    Verifies the Kotlin file can be parsed without syntax errors.
    Uses kotlinc if available, otherwise skips and relies on gradle compilation test.
    """
    import shutil

    # Check if kotlinc is available
    kotlinc = shutil.which("kotlinc")
    if not kotlinc:
        pytest.skip("kotlinc not available in Docker image - relying on gradle compile test instead")

    # Check that the file parses by using kotlinc
    target_path = f"{REPO}/{TARGET_FILE}"
    result = subprocess.run(
        [kotlinc, "-d", "/tmp/compiled", "-no-reflect", "-no-stdlib",
         "-cp", "compiler/frontend.common/build/classes/java/main:compiler/frontend.common/build/classes/kotlin/main",
         target_path],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    # kotlinc may fail due to dependencies, but syntax errors would be in stderr
    # If it fails with "unresolved reference" or similar, that's a dependency issue not syntax
    syntax_errors = ["expecting", "unexpected", "syntax", "illegal", "invalid token"]
    for err in syntax_errors:
        assert err not in result.stderr.lower(), f"Syntax error found: {result.stderr[:500]}"


def test_p2p_no_gradle_configuration_errors():
    """Repo CI: Gradle configuration has no errors for the module (p2p).

    Verifies that the module's build.gradle.kts is valid.
    """
    result = subprocess.run(
        ["./gradlew", ":compiler:frontend.common:help", "--no-daemon"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,  # Longer timeout for first-time Gradle download
    )
    # Check for configuration errors
    assert "Configuration error" not in result.stderr, f"Configuration error: {result.stderr[:500]}"
    assert result.returncode == 0, f"Gradle help failed: {result.stderr[:500]}"


def test_p2p_gradlew_available():
    """Repo CI: Gradle wrapper is available and executable (p2p).

    Quick sanity check that the build system is properly set up.
    """
    # Check gradlew exists and is executable
    result = subprocess.run(
        ["test", "-x", "./gradlew"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, "gradlew is not available or not executable"


def test_p2p_target_file_exists():
    """Repo CI: Target file exists in the expected location (p2p).

    Verifies that KtDiagnostic.kt exists in the compiler frontend.common module.
    """
    import os
    full_path = os.path.join(REPO, TARGET_FILE)
    assert os.path.exists(full_path), f"Target file {TARGET_FILE} does not exist"


def test_p2p_module_build_file_exists():
    """Repo CI: Module build file exists (p2p).

    Verifies that compiler/frontend.common/build.gradle.kts exists.
    """
    import os
    build_file = os.path.join(REPO, "compiler/frontend.common/build.gradle.kts")
    assert os.path.exists(build_file), "Module build.gradle.kts does not exist"


# =============================================================================
# FAIL-TO-PASS TESTS: Verify the fix works correctly
# =============================================================================

def test_kotlin_file_compiles():
    """Verify the modified Kotlin file compiles successfully."""
    # Compile the specific module containing the changed file
    result = run_cmd("./gradlew :compiler:frontend.common:compileKotlin --no-daemon -q 2>&1 | tail -50", cwd=REPO)

    # Check for compilation success (no errors in the specific file)
    # Gradle returns 0 on success, but we also check output for "error" related to our file
    error_patterns = [
        r"KtDiagnostic\.kt.*error",
        r"KtDiagnostic\.kt.*Exception",
        r"unresolved reference: requireWithAttachment",
        r"unresolved reference: withPsiEntry",
    ]

    for pattern in error_patterns:
        assert not re.search(pattern, result.stdout, re.IGNORECASE), \
            f"Compilation error found: {result.stdout}"
        assert not re.search(pattern, result.stderr, re.IGNORECASE), \
            f"Compilation error found: {result.stderr}"

def test_require_with_attachment_imported():
    """Verify that requireWithAttachment is imported."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Check for the import statement
    assert "import org.jetbrains.kotlin.utils.exceptions.requireWithAttachment" in content, \
        "Missing import for requireWithAttachment"

def test_with_psi_entry_imported():
    """Verify that withPsiEntry is imported."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Check for the import statement
    assert "import org.jetbrains.kotlin.utils.exceptions.withPsiEntry" in content, \
        "Missing import for withPsiEntry"

def test_require_with_attachment_used_in_function():
    """Verify that requireWithAttachment is used in checkPsiTypeConsistency function."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Find the checkPsiTypeConsistency function
    func_match = re.search(
        r"private fun KtPsiDiagnostic\.checkPsiTypeConsistency\(\) \{[^}]+\{[^}]+\}[^}]*\}",
        content,
        re.DOTALL
    )

    # If that pattern doesn't match, try a simpler check
    if not func_match:
        # Just check the function exists and contains requireWithAttachment
        func_start = content.find("private fun KtPsiDiagnostic.checkPsiTypeConsistency()")
        assert func_start != -1, "checkPsiTypeConsistency function not found"

        # Extract a chunk of code after the function start
        func_chunk = content[func_start:func_start + 1500]
        assert "requireWithAttachment" in func_chunk, \
            "requireWithAttachment not used in checkPsiTypeConsistency function"
    else:
        func_body = func_match.group(0)
        assert "requireWithAttachment" in func_body, \
            "requireWithAttachment not used in checkPsiTypeConsistency function"

def test_with_psi_entry_called_for_psi_element():
    """Verify that withPsiEntry is called for psiElement."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Find the checkPsiTypeConsistency function
    func_start = content.find("private fun KtPsiDiagnostic.checkPsiTypeConsistency()")
    assert func_start != -1, "checkPsiTypeConsistency function not found"

    # Extract function body (rough approximation)
    func_chunk = content[func_start:func_start + 1500]

    # Check for withPsiEntry("psi", psiElement) or withPsiEntry("psi", element.psi)
    psi_entry_pattern = r'withPsiEntry\s*\(\s*["\']psi["\']\s*,\s*(psiElement|element\.psi)\s*\)'
    assert re.search(psi_entry_pattern, func_chunk), \
        "withPsiEntry not called for psi element in the attachment block"

def test_with_psi_entry_called_for_file():
    """Verify that withPsiEntry is called for the file."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Find the checkPsiTypeConsistency function
    func_start = content.find("private fun KtPsiDiagnostic.checkPsiTypeConsistency()")
    assert func_start != -1, "checkPsiTypeConsistency function not found"

    # Extract function body (rough approximation)
    func_chunk = content[func_start:func_start + 1500]

    # Check for withPsiEntry("file", psiFile)
    file_entry_pattern = r'withPsiEntry\s*\(\s*["\']file["\']\s*,\s*psiFile\s*\)'
    assert re.search(file_entry_pattern, func_chunk), \
        "withPsiEntry not called for psiFile in the attachment block"

def test_old_require_not_used():
    """Verify that the old require block is no longer used."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Find the checkPsiTypeConsistency function
    func_start = content.find("private fun KtPsiDiagnostic.checkPsiTypeConsistency()")
    assert func_start != -1, "checkPsiTypeConsistency function not found"

    # Extract function body
    func_chunk = content[func_start:func_start + 1500]

    # The old pattern was: require(factory.psiType.isInstance(element.psi)) { ... }
    # Check that old pattern is NOT present (single-argument require with element.psi)
    old_pattern = r'require\s*\(\s*factory\.psiType\.isInstance\s*\(\s*element\.psi\s*\)\s*\)'
    assert not re.search(old_pattern, func_chunk), \
        "Old require pattern still present - should use requireWithAttachment"

def test_error_message_preserved():
    """Verify that the error message is preserved in the new implementation."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Find the checkPsiTypeConsistency function
    func_start = content.find("private fun KtPsiDiagnostic.checkPsiTypeConsistency()")
    assert func_start != -1, "checkPsiTypeConsistency function not found"

    # Extract function body
    func_chunk = content[func_start:func_start + 1500]

    # Check that the error message content is preserved
    # The message should reference psiElement::class, factory.psiType, and factory
    assert "is not a subtype of" in func_chunk, \
        "Error message 'is not a subtype of' not found"
    assert "factory" in func_chunk, \
        "Reference to factory not found in error message"
    assert "psiType" in func_chunk, \
        "Reference to psiType not found in error message"
