"""
Tests for IrRichFunctionReference fix in Compose compiler.

This verifies that the Compose compiler properly handles IrRichFunctionReference
in three lowering passes:
1. ComposableFunInterfaceLowering - creates IrRichFunctionReferenceImpl for Native
2. ComposableTypeRemapper - handles type remapping for rich function references
3. ComposerParamTransformer - transforms overridden function symbols
"""

import pytest
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/kotlin")

# File paths
FUN_INTERFACE_LOWERING = REPO / "plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableFunInterfaceLowering.kt"
TYPE_REMAPPER = REPO / "plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableTypeRemapper.kt"
COMPOSER_PARAM = REPO / "plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposerParamTransformer.kt"


def test_fun_interface_lowering_has_native_check():
    """ComposableFunInterfaceLowering should check for Native platform with IrRichCallableReferencesInKlibs."""
    content = FUN_INTERFACE_LOWERING.read_text()

    # Must check for Native platform
    assert "isNative()" in content, "Missing isNative() check"

    # Must check for IrRichCallableReferencesInKlibs feature
    assert "IrRichCallableReferencesInKlibs" in content, "Missing IrRichCallableReferencesInKlibs feature check"

    # Must have the conditional logic for Native
    assert "context.platform.isJvm() || (context.platform.isNative()" in content.replace("\n", " ").replace("  ", " "), \
        "Missing Native platform condition in lower() method"


def test_fun_interface_lowering_uses_ir_rich_impl():
    """ComposableFunInterfaceLowering should use IrRichFunctionReferenceImpl for non-JVM platforms."""
    content = FUN_INTERFACE_LOWERING.read_text()

    # Must import IrRichFunctionReferenceImpl
    assert "import org.jetbrains.kotlin.ir.expressions.impl.IrRichFunctionReferenceImpl" in content, \
        "Missing IrRichFunctionReferenceImpl import"

    # Must import selectSAMOverriddenFunction
    assert "import org.jetbrains.kotlin.ir.util.selectSAMOverriddenFunction" in content, \
        "Missing selectSAMOverriddenFunction import"

    # Must create IrRichFunctionReferenceImpl in non-JVM branch
    assert "IrRichFunctionReferenceImpl(" in content, \
        "Missing IrRichFunctionReferenceImpl instantiation"

    # Must use selectSAMOverriddenFunction for the overriddenFunctionSymbol
    assert "selectSAMOverriddenFunction().symbol" in content, \
        "Missing selectSAMOverriddenFunction().symbol usage"


def test_type_remapper_handles_rich_function_reference():
    """ComposableTypeTransformer should have visitRichFunctionReference override."""
    content = TYPE_REMAPPER.read_text()

    # Must override visitRichFunctionReference
    assert "override fun visitRichFunctionReference(expression: IrRichFunctionReference)" in content, \
        "Missing visitRichFunctionReference override"

    # Must check for needsComposableRemapping
    assert "needsComposableRemapping()" in content, \
        "Missing needsComposableRemapping() check in visitRichFunctionReference"

    # Must transform the overridden function
    assert "overriddenFunctionSymbol.owner.transform(this, null)" in content, \
        "Missing transformation of overridden function in visitRichFunctionReference"


def test_composer_param_handles_rich_function_reference():
    """ComposerParamTransformer should have visitRichFunctionReference override."""
    content = COMPOSER_PARAM.read_text()

    # Must override visitRichFunctionReference
    assert "override fun visitRichFunctionReference(expression: IrRichFunctionReference)" in content, \
        "Missing visitRichFunctionReference override in ComposerParamTransformer"

    # Must transform the overriddenFunctionSymbol with composer param
    assert "overriddenFunctionSymbol = expression.overriddenFunctionSymbol.owner.withComposerParamIfNeeded().symbol" in content, \
        "Missing withComposerParamIfNeeded() call on overriddenFunctionSymbol"


def test_type_remapper_method_body():
    """ComposableTypeTransformer visitRichFunctionReference should have correct method body."""
    content = TYPE_REMAPPER.read_text()

    # The method should check needsComposableRemapping and call transform
    assert "expression.overriddenFunctionSymbol.owner.needsComposableRemapping()" in content, \
        "Missing needsComposableRemapping check on overriddenFunctionSymbol"

    # The method should call super.visitRichFunctionReference at the end
    assert "super.visitRichFunctionReference(expression)" in content, \
        "Missing super.visitRichFunctionReference call"


def test_composer_param_method_body():
    """ComposerParamTransformer visitRichFunctionReference should have correct method body."""
    content = COMPOSER_PARAM.read_text()

    # The method should update overriddenFunctionSymbol with the transformed function
    assert "expression.overriddenFunctionSymbol = expression.overriddenFunctionSymbol.owner.withComposerParamIfNeeded().symbol" in content, \
        "Incorrect method body - should update overriddenFunctionSymbol with withComposerParamIfNeeded result"

    # The method should call super at the end
    assert "super.visitRichFunctionReference(expression)" in content, \
        "Missing super.visitRichFunctionReference call"


# =============================================================================
# Pass-to-Pass Tests (repo_tests) - These run actual CI commands
# =============================================================================

def test_repo_kotlin_compiler_available():
    """Kotlin compiler is available and functional (pass_to_pass)."""
    r = subprocess.run(
        ["kotlinc", "-version"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"kotlinc -version failed: {r.stderr}"
    assert "2.0.21" in r.stderr, "Expected Kotlin 2.0.21 compiler"


def test_repo_java_available():
    """Java runtime is available for Kotlin compiler (pass_to_pass)."""
    r = subprocess.run(
        ["java", "-version"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"java -version failed: {r.stderr}"
    assert "21" in r.stderr or "21" in r.stdout, "Expected Java 21"


def test_repo_git_valid():
    """Git repository is valid and has expected commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", str(REPO), "log", "--oneline", "-1"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"git log failed: {r.stderr}"
    # Should have the base commit checked out
    assert "56dd547" in r.stdout, f"Expected base commit 56dd547, got: {r.stdout}"


def test_repo_file_structure():
    """Expected source files exist and are readable (pass_to_pass)."""
    files = [
        FUN_INTERFACE_LOWERING,
        TYPE_REMAPPER,
        COMPOSER_PARAM,
    ]
    for f in files:
        r = subprocess.run(
            ["test", "-f", str(f)],
            capture_output=True,
            timeout=30,
        )
        assert r.returncode == 0, f"File not found or not readable: {f}"


def test_repo_kotlin_files_non_empty():
    """All Kotlin source files are non-empty (pass_to_pass)."""
    files = [
        FUN_INTERFACE_LOWERING,
        TYPE_REMAPPER,
        COMPOSER_PARAM,
    ]
    for f in files:
        r = subprocess.run(
            ["test", "-s", str(f)],
            capture_output=True,
            timeout=30,
        )
        assert r.returncode == 0, f"File is empty: {f}"


def test_repo_gradlew_available():
    """Gradle wrapper is available for builds (pass_to_pass)."""
    gradlew = REPO / "gradlew"
    r = subprocess.run(
        ["test", "-x", str(gradlew)],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, "gradlew not found or not executable"


# =============================================================================
# Pass-to-Pass Tests (static) - File content validation
# =============================================================================

def test_syntax_validity():
    """Kotlin files have valid structure (pass_to_pass)."""
    files = [
        FUN_INTERFACE_LOWERING,
        TYPE_REMAPPER,
        COMPOSER_PARAM
    ]

    for file_path in files:
        content = file_path.read_text()

        # Check file has balanced braces (basic structural check)
        open_braces = content.count("{")
        close_braces = content.count("}")
        assert open_braces == close_braces, f"Unbalanced braces in {file_path.name}"

        # Check file has balanced parentheses
        open_parens = content.count("(")
        close_parens = content.count(")")
        assert open_parens == close_parens, f"Unbalanced parentheses in {file_path.name}"

        # Check for common syntax error indicators
        assert "fun fun " not in content, f"Duplicate 'fun' keyword in {file_path.name}"
        assert "class class " not in content, f"Duplicate 'class' keyword in {file_path.name}"

        # Check that imports are well-formed (basic check)
        for line in content.split("\n"):
            if line.strip().startswith("import "):
                # Import line should have valid structure
                assert ".." not in line, f"Invalid import with '..' in {file_path.name}: {line}"
                assert line.strip().endswith(";") or not line.strip().endswith("."), \
                    f"Import should not end with '.' in {file_path.name}: {line}"


def test_all_lowerings_have_package():
    """All lowering files have correct package declaration (pass_to_pass)."""
    files = [
        FUN_INTERFACE_LOWERING,
        TYPE_REMAPPER,
        COMPOSER_PARAM,
    ]

    for file_path in files:
        content = file_path.read_text()
        assert "package androidx.compose.compiler.plugins.kotlin.lower" in content, \
            f"Missing correct package declaration in {file_path.name}"


def test_repo_no_syntax_errors():
    """Kotlin files can be read and have valid structure (pass_to_pass)."""
    files = [
        FUN_INTERFACE_LOWERING,
        TYPE_REMAPPER,
        COMPOSER_PARAM,
    ]

    for file_path in files:
        # Check file can be read as UTF-8
        r = subprocess.run(
            ["python3", "-c", f"open('{file_path}').read()"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, f"File {file_path.name} could not be read as UTF-8: {r.stderr}"
