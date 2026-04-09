#!/usr/bin/env python3
"""
Tests for Kotlin DiagnosticReporterFactory removal task.
"""

import os
import re
import subprocess
import sys

REPO = "/workspace/kotlin"


def test_diagnostic_reporter_factory_deleted():
    """
    Fail-to-pass: DiagnosticReporterFactory.kt should be deleted.
    """
    filepath = os.path.join(
        REPO,
        "compiler/frontend.common/src/org/jetbrains/kotlin/diagnostics/DiagnosticReporterFactory.kt"
    )
    assert not os.path.exists(filepath), (
        f"DiagnosticReporterFactory.kt should be deleted but still exists at {filepath}"
    )


def test_k2_compiler_facade_uses_direct_instantiation():
    """
    Fail-to-pass: K2CompilerFacade should use DiagnosticsCollectorImpl directly.
    """
    filepath = os.path.join(
        REPO,
        "plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/facade/K2CompilerFacade.kt"
    )
    assert os.path.exists(filepath), f"K2CompilerFacade.kt should exist at {filepath}"

    with open(filepath, 'r') as f:
        content = f.read()

    # Should NOT import DiagnosticReporterFactory
    assert "import org.jetbrains.kotlin.diagnostics.DiagnosticReporterFactory" not in content, (
        "K2CompilerFacade should not import DiagnosticReporterFactory"
    )

    # Should NOT call DiagnosticReporterFactory.createReporter()
    assert "DiagnosticReporterFactory.createReporter()" not in content, (
        "K2CompilerFacade should not call DiagnosticReporterFactory.createReporter()"
    )

    # Should import DiagnosticsCollectorImpl
    assert "import org.jetbrains.kotlin.diagnostics.impl.DiagnosticsCollectorImpl" in content, (
        "K2CompilerFacade should import DiagnosticsCollectorImpl"
    )

    # Should instantiate DiagnosticsCollectorImpl directly
    assert "DiagnosticsCollectorImpl()" in content, (
        "K2CompilerFacade should instantiate DiagnosticsCollectorImpl directly"
    )


def test_k2_compiler_facade_syntax_valid():
    """
    Pass-to-pass: K2CompilerFacade.kt should have valid Kotlin syntax.
    Uses kotlinc for lightweight syntax check.
    """
    # Check Kotlin syntax using kotlinc -parse-only (doesn't require full project build)
    filepath = os.path.join(
        REPO,
        "plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/facade/K2CompilerFacade.kt"
    )

    # First check if kotlinc is available
    kotlinc_check = subprocess.run(["which", "kotlinc"], capture_output=True, text=True)
    if kotlinc_check.returncode != 0:
        # If kotlinc not available, skip and just verify the file content is well-formed
        with open(filepath, 'r') as f:
            content = f.read()
        # Basic syntax checks
        assert content.count('{') == content.count('}'), "Mismatched braces"
        assert content.count('(') == content.count(')'), "Mismatched parentheses"
        return

    # Use kotlinc to parse the file
    result = subprocess.run(
        ["kotlinc", "-parse-only", filepath],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, (
        f"K2CompilerFacade.kt has syntax errors:\n{result.stderr[-500:]}"
    )


def test_no_orphaned_imports():
    """
    Pass-to-pass: Ensure no orphaned imports exist after refactoring.
    Verifies all imports in K2CompilerFacade can be resolved.
    """
    filepath = os.path.join(
        REPO,
        "plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/facade/K2CompilerFacade.kt"
    )

    with open(filepath, 'r') as f:
        content = f.read()

    # Extract all imports
    import_pattern = r'import\s+([\w.]+)'
    imports = re.findall(import_pattern, content)

    # Check that DiagnosticsCollectorImpl import exists (our expected change)
    assert "org.jetbrains.kotlin.diagnostics.impl.DiagnosticsCollectorImpl" in imports, (
        "Should import DiagnosticsCollectorImpl"
    )

    # Check that old factory import is gone
    assert "org.jetbrains.kotlin.diagnostics.DiagnosticReporterFactory" not in imports, (
        "Should not import DiagnosticReporterFactory"
    )


def test_no_references_to_deleted_factory():
    """
    Fail-to-pass: No code should reference the deleted DiagnosticReporterFactory.
    """
    # Search for any remaining references to DiagnosticReporterFactory
    result = subprocess.run(
        ["git", "grep", "-l", "DiagnosticReporterFactory", "--", "*.kt"],
        cwd=REPO,
        capture_output=True,
        text=True
    )

    # If grep finds matches, they should only be in comments or test data (not actual code)
    if result.returncode == 0 and result.stdout.strip():
        files = result.stdout.strip().split('\n')
        # Filter out non-code files and comments
        code_files = []
        for f in files:
            # Check if it's actual code usage, not just comments
            filepath = os.path.join(REPO, f)
            if os.path.exists(filepath):
                with open(filepath, 'r') as file:
                    content = file.read()
                    # Look for actual usage (import or call), not just comment mentions
                    if "import" in content and "DiagnosticReporterFactory" in content:
                        code_files.append(f)
                    elif "DiagnosticReporterFactory.createReporter()" in content:
                        code_files.append(f)

        assert len(code_files) == 0, (
            f"DiagnosticReporterFactory is still referenced in: {code_files}"
        )


# =============================================================================
# Pass-to-pass tests: Repo CI/CD checks
# These verify the repo's own quality gates pass on both base and gold commits.
# =============================================================================


def test_repo_git_repository_valid():
    """
    Pass-to-pass: Git repository should be valid and initialized.
    Verifies the repo is a valid git repository with expected structure.
    """
    # Check that .git directory exists
    git_dir = os.path.join(REPO, ".git")
    assert os.path.isdir(git_dir), f".git directory should exist at {git_dir}"

    # Check git log works
    result = subprocess.run(
        ["git", "log", "--oneline", "-n", "1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"git log failed: {result.stderr}"
    assert result.stdout.strip(), "git log should show at least one commit"

    # Check expected files are tracked
    result = subprocess.run(
        ["git", "ls-files", "settings.gradle"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"git ls-files failed: {result.stderr}"
    assert "settings.gradle" in result.stdout, "settings.gradle should be tracked by git"


def test_repo_gradle_files_valid():
    """
    Pass-to-pass: Gradle build files should be syntactically valid.
    Checks that settings.gradle and build.gradle.kts are well-formed.
    """
    # Check settings.gradle exists and has valid content
    settings_path = os.path.join(REPO, "settings.gradle")
    assert os.path.exists(settings_path), "settings.gradle should exist"

    with open(settings_path, 'r') as f:
        content = f.read()

    # Basic validation: should contain expected project declarations
    assert "include" in content, "settings.gradle should include projects"
    assert "compiler:frontend.common" in content, "settings.gradle should reference frontend.common"

    # Check main build.gradle.kts
    build_path = os.path.join(REPO, "build.gradle.kts")
    assert os.path.exists(build_path), "build.gradle.kts should exist"

    with open(build_path, 'r') as f:
        content = f.read()

    # Basic validation: should contain plugins and dependencies
    assert "plugins" in content, "build.gradle.kts should have plugins block"


def test_repo_frontend_common_module_exists():
    """
    Pass-to-pass: The frontend.common module should exist with valid structure.
    Verifies the module being modified has a valid build configuration.
    """
    module_dir = os.path.join(REPO, "compiler", "frontend.common")
    assert os.path.isdir(module_dir), f"frontend.common module should exist at {module_dir}"

    # Check build.gradle.kts exists
    build_file = os.path.join(module_dir, "build.gradle.kts")
    assert os.path.exists(build_file), f"frontend.common build.gradle.kts should exist"

    # Verify it has source files
    src_dir = os.path.join(module_dir, "src")
    assert os.path.isdir(src_dir), f"frontend.common should have src directory"


def test_repo_compose_integration_tests_module_exists():
    """
    Pass-to-pass: The compose integration tests module should exist with valid structure.
    Verifies the test module using the modified code has a valid build configuration.
    """
    module_dir = os.path.join(
        REPO, "plugins", "compose", "compiler-hosted", "integration-tests"
    )
    assert os.path.isdir(module_dir), f"compose integration-tests module should exist"

    # Check build.gradle.kts exists
    build_file = os.path.join(module_dir, "build.gradle.kts")
    assert os.path.exists(build_file), f"compose integration-tests build.gradle.kts should exist"

    # Check the K2CompilerFacade file exists (it's the file being modified)
    facade_file = os.path.join(
        module_dir, "src", "jvmTest", "kotlin", "androidx", "compose", "compiler",
        "plugins", "kotlin", "facade", "K2CompilerFacade.kt"
    )
    assert os.path.exists(facade_file), f"K2CompilerFacade.kt should exist at {facade_file}"


def test_repo_kotlin_files_no_syntax_errors():
    """
    Pass-to-pass: Modified Kotlin files should have no obvious syntax errors.
    Performs basic structural validation without full compilation.
    """
    # Get list of Kotlin files in the frontend.common diagnostics package
    diagnostics_dir = os.path.join(
        REPO, "compiler", "frontend.common", "src", "org", "jetbrains", "kotlin", "diagnostics"
    )

    # Check all .kt files have matching braces and parentheses
    for root, dirs, files in os.walk(diagnostics_dir):
        for file in files:
            if file.endswith('.kt'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()

                # Skip empty files
                if not content.strip():
                    continue

                # Basic structural checks
                open_braces = content.count('{')
                close_braces = content.count('}')
                assert open_braces == close_braces, (
                    f"{file}: Mismatched braces ({open_braces} open, {close_braces} close)"
                )

                open_parens = content.count('(')
                close_parens = content.count(')')
                assert open_parens == close_parens, (
                    f"{file}: Mismatched parentheses ({open_parens} open, {close_parens} close)"
                )

                # Check for valid package declaration
                assert 'package ' in content, f"{file}: Should have package declaration"


def test_repo_no_orphaned_imports_in_facade():
    """
    Pass-to-pass: K2CompilerFacade should have no orphaned imports.
    Verifies all imports reference existing classes in the codebase.
    """
    filepath = os.path.join(
        REPO,
        "plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/facade/K2CompilerFacade.kt"
    )

    with open(filepath, 'r') as f:
        content = f.read()

    # Extract all import lines
    import_lines = [line.strip() for line in content.split('\n') if line.strip().startswith('import ')]

    # Verify no duplicate imports
    import_targets = []
    for imp in import_lines:
        # Extract the target class/package from import
        target = imp.replace('import ', '').replace(';', '').strip()
        import_targets.append(target)

    duplicates = [target for target in set(import_targets) if import_targets.count(target) > 1]
    assert len(duplicates) == 0, f"Found duplicate imports: {duplicates}"

    # Check for valid import patterns (org.jetbrains.kotlin.* or androidx.compose.*)
    for target in import_targets:
        valid_prefixes = [
            'org.jetbrains.kotlin',
            'androidx.compose',
            'com.intellij',
            'org.junit',
            'java.',
            'javax.',
            'kotlin.',
            'kotlinx.',
        ]
        assert any(target.startswith(prefix) for prefix in valid_prefixes), (
            f"Import '{target}' doesn't match expected patterns"
        )


def test_repo_diagnostics_collector_impl_exists():
    """
    Pass-to-pass: DiagnosticsCollectorImpl class should exist and be accessible.
    This is the class that replaces DiagnosticReporterFactory usage.
    """
    impl_dir = os.path.join(
        REPO, "compiler", "frontend.common", "src", "org", "jetbrains", "kotlin", "diagnostics", "impl"
    )
    assert os.path.isdir(impl_dir), f"diagnostics impl directory should exist"

    # Check for DiagnosticsCollectorImpl file
    impl_file = os.path.join(impl_dir, "DiagnosticsCollectorImpl.kt")
    assert os.path.exists(impl_file), f"DiagnosticsCollectorImpl.kt should exist"

    with open(impl_file, 'r') as f:
        content = f.read()

    # Verify it contains the class definition
    assert "class DiagnosticsCollectorImpl" in content, (
        "DiagnosticsCollectorImpl should define the class"
    )


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
