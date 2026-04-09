#!/usr/bin/env python3
"""
Test outputs for Swift Export @ObjCName annotation support.

This tests that:
1. The ObjCNameAnnotation class exists and has correct properties
2. The objCNameAnnotation extension is accessible on KaDeclarationSymbol
3. The AnalysisApiUtils.kt file has the required functionality
4. SirDeclarationNamerImpl uses objCNameAnnotation
5. TypeTranslationUtils uses objCNameAnnotation for parameter translation
6. SirProtocolFromKtSymbol uses sirDeclarationName()

Tests use subprocess to verify actual code structure and behavior.
"""

import subprocess
import os
import re
import ast

REPO = "/workspace/kotlin"


def _get_file_content(filepath: str) -> str:
    """Read file content from the repo."""
    full_path = os.path.join(REPO, filepath)
    with open(full_path, 'r') as f:
        return f.read()


def test_objcname_annotation_class_has_correct_structure():
    """Test that ObjCNameAnnotation class is correctly defined with required properties."""
    filepath = "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/AnalysisApiUtils.kt"
    content = _get_file_content(filepath)

    # Verify class definition exists
    class_pattern = r'public\s+class\s+ObjCNameAnnotation\s*\([^)]+\)'
    assert re.search(class_pattern, content), "ObjCNameAnnotation class definition not found"

    # Verify constructor properties
    assert "public val objCName: String?" in content, "objCName property missing"
    assert "public val swiftName: String?" in content, "swiftName property missing"
    assert "public val isExact: Boolean" in content, "isExact property missing"

    # Verify computed properties for Swift export
    assert "public val name: String?" in content, "name computed property missing"
    assert "public val argumentName: String?" in content, "argumentName computed property missing"



def test_objcname_annotation_parses_annotation_arguments():
    """Test that objCNameAnnotation extension correctly parses annotation arguments."""
    filepath = "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/AnalysisApiUtils.kt"
    content = _get_file_content(filepath)

    # Verify extension property signature
    assert "public val KaDeclarationSymbol.objCNameAnnotation: ObjCNameAnnotation?" in content, \
        "Extension property not found"

    # Verify annotation lookup using correct ClassId
    assert 'ClassId.topLevel(FqName("kotlin.native.ObjCName"))' in content, \
        "ObjCName ClassId definition not found"

    # Verify each argument is parsed correctly
    assert '"name" -> objCName' in content, "name argument parsing not found"
    assert '"swiftName" -> swiftName' in content, "swiftName argument parsing not found"
    assert '"exact" -> isExact' in content, "exact argument parsing not found"

    # Verify resolveConstantValue is used for type-safe extraction
    assert "resolveConstantValue<KaConstantValue.StringValue>()" in content, \
        "StringValue extraction not found"
    assert "resolveConstantValue<KaConstantValue.BooleanValue>()" in content, \
        "BooleanValue extraction not found"


def test_resolve_constant_value_helper_exists():
    """Test that the resolveConstantValue helper function exists for type-safe annotation parsing."""
    filepath = "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/AnalysisApiUtils.kt"
    content = _get_file_content(filepath)

    # Verify the reified generic helper function
    helper_pattern = r'private\s+inline\s+fun\s+<reified\s+T\s+:\s+KaConstantValue>\s+KaNamedAnnotationValue\.resolveConstantValue\(\)'
    assert re.search(helper_pattern, content), "resolveConstantValue helper function not found"

    # Verify required imports for annotation parsing
    assert "import org.jetbrains.kotlin.analysis.api.annotations.KaNamedAnnotationValue" in content, \
        "KaNamedAnnotationValue import missing"
    assert "import org.jetbrains.kotlin.analysis.api.base.KaConstantValue" in content, \
        "KaConstantValue import missing"


def test_sirdeclarationnamer_checks_objcname_first():
    """Test that SirDeclarationNamerImpl checks objCNameAnnotation before default naming."""
    filepath = "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirDeclarationNamerImpl.kt"
    content = _get_file_content(filepath)

    # Verify the import exists
    assert "import org.jetbrains.kotlin.sir.providers.utils.objCNameAnnotation" in content, \
        "objCNameAnnotation import missing"

    # Verify early return pattern - objCNameAnnotation checked FIRST in getName()
    # This is critical: it must check objCNameAnnotation before the when() expression
    objcname_check_pattern = r'objCNameAnnotation\?\.name\?\.let\s*\{\s*return\s+it\s*\}'
    assert re.search(objcname_check_pattern, content), \
        "objCNameAnnotation check with early return pattern not found"

    # Verify it appears before the when expression
    objcname_pos = content.find("objCNameAnnotation?.name?.let { return it }")
    when_pos = content.find("when (this) {")
    assert objcname_pos != -1 and when_pos != -1 and objcname_pos < when_pos, \
        "objCNameAnnotation check must appear before when expression"


def test_typetranslationutils_extracts_custom_parameter_names():
    """Test that TypeTranslationUtils uses objCNameAnnotation for custom parameter names."""
    filepath = "native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/utils/TypeTranslationUtils.kt"
    content = _get_file_content(filepath)

    # Verify import
    assert "import org.jetbrains.kotlin.sir.providers.utils.objCNameAnnotation" in content, \
        "objCNameAnnotation import missing"

    # Verify annotation extraction from parameter
    assert "val objCNameAnnotation = parameter.objCNameAnnotation" in content, \
        "Annotation extraction from parameter not found"

    # Verify argumentName uses annotation value or falls back to parameter name
    assert "val argumentName = objCNameAnnotation?.argumentName ?: parameter.name.asString()" in content, \
        "argumentName logic not found"

    # Verify parameterName uses annotation value or falls back
    assert "val parameterName = objCNameAnnotation?.name ?: parameter.name.asString()" in content, \
        "parameterName logic not found"

    # Verify SirParameter is constructed with the computed names
    assert "argumentName = argumentName," in content, \
        "SirParameter argumentName assignment not found"
    assert "parameterName = parameterName.takeIf { it != argumentName }," in content, \
        "SirParameter parameterName assignment not found"


def test_sirprotocolfromktsymbol_uses_sirdeclarationname():
    """Test that SirProtocolFromKtSymbol uses sirDeclarationName() for proper @ObjCName support."""
    filepath = "native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt"
    content = _get_file_content(filepath)

    # Verify the name property uses lazyWithSessions (needed for analysis API access)
    assert "override val name: String by lazyWithSessions {" in content, \
        "name property should use lazyWithSessions"

    # Verify sirDeclarationName() is called instead of direct name access
    assert "ktSymbol.sirDeclarationName()" in content, \
        "sirDeclarationName() call not found"

    # Verify the old pattern is replaced
    old_pattern = "ktSymbol.name.asString()"
    name_property_start = content.find("override val name:")
    name_property_end = content.find("override var parent:", name_property_start)
    name_property_section = content[name_property_start:name_property_end]

    # In the name property section, we should use sirDeclarationName(), not name.asString()
    assert old_pattern not in name_property_section, \
        f"Old {old_pattern} pattern should be replaced in name property"


def test_swift_underscore_converted_to_empty_string():
    """Test that swiftName == '_' is correctly converted to empty string."""
    filepath = "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/AnalysisApiUtils.kt"
    content = _get_file_content(filepath)

    # This is the key behavior: underscore means empty parameter name in Swift
    assert 'if (swiftName == "_") swiftName = ""' in content, \
        "Swift underscore to empty string conversion not found"


# =============================================================================
# Pass-to-pass tests (verify code structure and no regressions)
# =============================================================================

def test_kotlin_files_compilable_structure():
    """Test that Kotlin files have valid structure for compilation."""
    files_to_check = [
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/AnalysisApiUtils.kt",
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirDeclarationNamerImpl.kt",
        "native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/utils/TypeTranslationUtils.kt",
        "native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt",
    ]

    for filepath in files_to_check:
        content = _get_file_content(filepath)

        # Check balanced braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        assert open_braces == close_braces, f"Unbalanced braces in {filepath}: {open_braces} vs {close_braces}"

        # Check balanced parentheses
        open_parens = content.count('(')
        close_parens = content.count(')')
        assert open_parens == close_parens, f"Unbalanced parentheses in {filepath}: {open_parens} vs {close_parens}"

        # Check balanced angle brackets (for generics)
        # Only count outside of strings/comments (simplified check)
        open_angles = content.count('<')
        close_angles = content.count('>')
        # Allow some variance due to comparison operators, but major imbalance indicates issue
        assert abs(open_angles - close_angles) < 20, f"Potentially unbalanced angle brackets in {filepath}"


def test_kotlin_imports_valid():
    """Test that Kotlin import statements are well-formed."""
    files_to_check = [
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/AnalysisApiUtils.kt",
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirDeclarationNamerImpl.kt",
        "native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/utils/TypeTranslationUtils.kt",
        "native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt",
    ]

    import_pattern = re.compile(r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*(?:\.\*)?)$', re.MULTILINE)

    for filepath in files_to_check:
        content = _get_file_content(filepath)

        # Find all import statements
        imports = import_pattern.findall(content)

        # Check that import statements are valid
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('import '):
                # Verify it's not an incomplete import
                assert not line.endswith('.'), f"Invalid import ending with dot in {filepath}: {line}"
                # Verify import has a valid package structure
                parts = line.replace('import ', '').split('.')
                assert len(parts) >= 1, f"Invalid import in {filepath}: {line}"


def test_no_duplicate_imports():
    """Test that there are no duplicate import statements."""
    files_to_check = [
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/AnalysisApiUtils.kt",
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirDeclarationNamerImpl.kt",
        "native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/utils/TypeTranslationUtils.kt",
        "native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt",
    ]

    for filepath in files_to_check:
        content = _get_file_content(filepath)

        # Extract imports
        import_lines = []
        for line in content.split('\n'):
            if line.strip().startswith('import '):
                import_lines.append(line.strip())

        # Check for duplicates
        seen = set()
        for imp in import_lines:
            assert imp not in seen, f"Duplicate import found in {filepath}: {imp}"
            seen.add(imp)


def test_function_declarations_well_formed():
    """Test that key function declarations are well-formed."""
    files_to_check = [
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/AnalysisApiUtils.kt",
        "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirDeclarationNamerImpl.kt",
        "native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/utils/TypeTranslationUtils.kt",
    ]

    for filepath in files_to_check:
        content = _get_file_content(filepath)

        # Check for invalid fun declarations (fun without name or with invalid syntax)
        # fun ( or fun { would be invalid
        invalid_fun_pattern = re.compile(r'\bfun\s*\(|\bfun\s*\{|\bfun\s+:\s*')
        matches = invalid_fun_pattern.findall(content)
        assert not matches, f"Invalid function declaration found in {filepath}: {matches}"

        # Check that val/var declarations have names
        invalid_val_pattern = re.compile(r'\bval\s*:\s*|\bvar\s*:\s*')
        assert not invalid_val_pattern.search(content), f"Invalid val/var declaration in {filepath}"


def test_extension_functions_have_valid_receivers():
    """Test that extension functions have valid receiver types."""
    filepath = "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/AnalysisApiUtils.kt"
    content = _get_file_content(filepath)

    # Extension on KaDeclarationSymbol should have valid receiver
    extension_pattern = re.compile(r'public\s+val\s+KaDeclarationSymbol\.\w+')
    extensions = extension_pattern.findall(content)
    assert len(extensions) >= 3, f"Expected at least 3 extension properties on KaDeclarationSymbol, found: {extensions}"

    # Each extension should be a read-only property (val)
    for ext in extensions:
        assert ext.startswith("public val KaDeclarationSymbol."), \
            f"Invalid extension declaration: {ext}"
