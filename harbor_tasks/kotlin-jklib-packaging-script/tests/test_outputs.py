"""Tests for Kotlin jklib packaging script PR.

This verifies that the build.gradle.kts file for jklib-compiler
is correctly created and registered in settings.gradle.
"""

import os
import pytest
import re
import subprocess
import sys

REPO = "/workspace/kotlin"
BUILD_FILE = os.path.join(REPO, "prepare/jklib-compiler/build.gradle.kts")
SETTINGS_FILE = os.path.join(REPO, "settings.gradle")
GRADLEW = os.path.join(REPO, "gradlew")


def _run_gradle(args: list, timeout: int = 120, cwd: str = REPO) -> subprocess.CompletedProcess:
    """Execute a Gradle command in the repo directory."""
    cmd = [GRADLEW] + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )


def test_build_file_exists():
    """Fail-to-pass: build.gradle.kts file exists at correct path."""
    assert os.path.exists(BUILD_FILE), f"Build file not found at {BUILD_FILE}"


def test_settings_includes_module():
    """Fail-to-pass: settings.gradle includes :kotlin-jklib-compiler module."""
    with open(SETTINGS_FILE, 'r') as f:
        content = f.read()
    assert '":kotlin-jklib-compiler"' in content, "Missing :kotlin-jklib-compiler include"


def test_settings_has_project_dir():
    """Fail-to-pass: settings.gradle maps projectDir for kotlin-jklib-compiler."""
    with open(SETTINGS_FILE, 'r') as f:
        content = f.read()
    # Check for the projectDir mapping
    pattern = r"project\(':kotlin-jklib-compiler'\)\.projectDir\s*=\s*\"\$rootDir/prepare/jklib-compiler\""
    assert re.search(pattern, content), "Missing projectDir mapping for kotlin-jklib-compiler"


def test_gradle_module_recognized():
    """Fail-to-pass: Gradle recognizes the :kotlin-jklib-compiler module.

    This test actually runs './gradlew projects' to verify the module
    is properly registered in settings.gradle and recognized by Gradle.
    """
    result = _run_gradle(["projects", "--quiet"], timeout=180)
    assert result.returncode == 0, f"Gradle projects command failed:\n{result.stderr}"
    assert ":kotlin-jklib-compiler" in result.stdout, \
        f"Module :kotlin-jklib-compiler not found in projects list:\n{result.stdout}"


def test_gradle_build_script_loads():
    """Fail-to-pass: The build.gradle.kts script loads without errors.

    This test runs a Gradle help command on the new module to verify
    the Kotlin build script compiles and loads correctly.
    """
    if not os.path.exists(BUILD_FILE):
        pytest.skip("Build file does not exist")

    result = _run_gradle([":kotlin-jklib-compiler:help"], timeout=180)
    assert result.returncode == 0, f"Build script failed to load:\n{result.stderr}"


def test_gradle_tasks_registered():
    """Fail-to-pass: The build script registers expected tasks.

    This test verifies that the jar and dist tasks are properly registered
    by running the 'tasks' command for the module.
    """
    if not os.path.exists(BUILD_FILE):
        pytest.skip("Build file does not exist")

    result = _run_gradle([":kotlin-jklib-compiler:tasks", "--all"], timeout=180)
    assert result.returncode == 0, f"Failed to list tasks:\n{result.stderr}"
    # Verify the jar task is available
    assert "jar" in result.stdout, f"jar task not registered:\n{result.stdout}"


def test_build_file_has_copyright():
    """Fail-to-pass: Build file has proper copyright header."""
    with open(BUILD_FILE, 'r') as f:
        content = f.read()
    assert "Copyright 2010-2026 JetBrains" in content, "Missing copyright header"
    assert "Apache 2.0 license" in content, "Missing license reference"


def test_build_file_has_description():
    """Fail-to-pass: Build file has description for the packaging script."""
    with open(BUILD_FILE, 'r') as f:
        content = f.read()
    assert 'description = "JKlib Classes packaging script"' in content, "Missing description"


def test_build_file_has_plugins():
    """Fail-to-pass: Build file applies kotlin("jvm") plugin."""
    with open(BUILD_FILE, 'r') as f:
        content = f.read()
    assert 'kotlin("jvm")' in content, "Missing kotlin jvm plugin"


def test_build_file_has_configurations():
    """Fail-to-pass: Build file creates buildNumber and distContent configurations."""
    with open(BUILD_FILE, 'r') as f:
        content = f.read()
    assert "val buildNumber by configurations.creating" in content, "Missing buildNumber configuration"
    assert "val distContent by configurations.creating" in content, "Missing distContent configuration"


def test_build_file_has_dependencies():
    """Fail-to-pass: Build file has correct dependencies on cli-jklib and ir.serialization.jklib."""
    with open(BUILD_FILE, 'r') as f:
        content = f.read()
    assert ':compiler:cli-jklib' in content, "Missing cli-jklib dependency"
    assert ':compiler:ir.serialization.jklib' in content, "Missing ir.serialization.jklib dependency"
    assert 'isTransitive = false' in content, "Missing isTransitive = false"


def test_build_file_has_jar_task():
    """Fail-to-pass: Build file configures jar task with correct archive name."""
    with open(BUILD_FILE, 'r') as f:
        content = f.read()
    assert 'archiveFileName.set("jklib-compiler.jar")' in content, "Missing jar archive name"
    assert 'DuplicatesStrategy.EXCLUDE' in content, "Missing duplicates strategy EXCLUDE"


def test_build_file_has_manifest():
    """Fail-to-pass: Build file configures manifest with Class-Path and Main-Class."""
    with open(BUILD_FILE, 'r') as f:
        content = f.read()
    assert '"Class-Path" to "kotlin-compiler.jar kotlin-stdlib.jar kotlin-reflect.jar"' in content, "Missing Class-Path"
    assert '"Main-Class" to "org.jetbrains.kotlin.cli.jklib.K2JKlibCompiler"' in content, "Missing Main-Class"


def test_build_file_has_dist_task():
    """Fail-to-pass: Build file registers dist Sync task."""
    with open(BUILD_FILE, 'r') as f:
        content = f.read()
    assert 'tasks.registering(Sync::class)' in content, "Missing dist Sync task"
    assert 'destinationDir = distDir.dir("jklib").asFile' in content, "Missing destinationDir"
    assert 'DuplicatesStrategy.FAIL' in content, "Missing duplicates strategy FAIL"


def test_build_file_has_license_sync():
    """Fail-to-pass: Build file syncs license directory."""
    with open(BUILD_FILE, 'r') as f:
        content = f.read()
    assert 'into("license")' in content, "Missing license sync"
    assert 'from(licenseDir)' in content, "Missing licenseDir source"


def test_build_file_has_lib_sync():
    """Fail-to-pass: Build file syncs lib directory with jar and correct permissions."""
    with open(BUILD_FILE, 'r') as f:
        content = f.read()
    assert 'into("lib")' in content, "Missing lib sync"
    assert 'from(jar)' in content, "Missing jar source"
    assert 'unix("rw-r--r--")' in content, "Missing file permissions"


# Pass-to-pass checks: Repo validation


def test_gradle_settings_valid():
    """Pass-to-pass: Gradle settings are valid and can be loaded."""
    result = _run_gradle(["help"], timeout=60)
    assert result.returncode == 0, f"Gradle help failed:\n{result.stderr}"


def test_repo_dependency_modules_exist():
    """Pass-to-pass: Dependency modules cli-jklib and ir.serialization.jklib exist (repo_tests)."""
    # Check that cli-jklib build.gradle.kts exists
    cli_jklib_build = os.path.join(REPO, "compiler/cli/cli-jklib/build.gradle.kts")
    assert os.path.exists(cli_jklib_build), f"cli-jklib build file not found at {cli_jklib_build}"

    # Check that ir.serialization.jklib build.gradle.kts exists
    ir_serialization_build = os.path.join(REPO, "compiler/ir/serialization.jklib/build.gradle.kts")
    assert os.path.exists(ir_serialization_build), f"ir.serialization.jklib build file not found at {ir_serialization_build}"


def test_repo_cli_jklib_has_valid_structure():
    """Pass-to-pass: cli-jklib module has valid Gradle build script structure (repo_tests)."""
    cli_jklib_build = os.path.join(REPO, "compiler/cli/cli-jklib/build.gradle.kts")
    if not os.path.exists(cli_jklib_build):
        pytest.skip("cli-jklib build file does not exist")

    with open(cli_jklib_build, 'r') as f:
        content = f.read()

    # Basic Gradle Kotlin DSL validation
    assert 'plugins {' in content, "Missing plugins block in cli-jklib build file"
    assert 'dependencies {' in content, "Missing dependencies block in cli-jklib build file"


def test_repo_serialization_jklib_has_valid_structure():
    """Pass-to-pass: ir.serialization.jklib module has valid Gradle build script structure (repo_tests)."""
    ir_serialization_build = os.path.join(REPO, "compiler/ir/serialization.jklib/build.gradle.kts")
    if not os.path.exists(ir_serialization_build):
        pytest.skip("ir.serialization.jklib build file does not exist")

    with open(ir_serialization_build, 'r') as f:
        content = f.read()

    # Basic Gradle Kotlin DSL validation
    assert 'plugins {' in content, "Missing plugins block in serialization.jklib build file"
    assert 'dependencies {' in content, "Missing dependencies block in serialization.jklib build file"


def test_repo_jklib_tests_module_exists():
    """Pass-to-pass: jklib.tests module exists for integration testing (repo_tests)."""
    jklib_tests_build = os.path.join(REPO, "compiler/jklib.tests/build.gradle.kts")
    assert os.path.exists(jklib_tests_build), f"jklib.tests build file not found at {jklib_tests_build}"


def test_repo_prepare_structure_exists():
    """Pass-to-pass: prepare directory structure exists for build packaging scripts (repo_tests)."""
    prepare_dir = os.path.join(REPO, "prepare")
    assert os.path.isdir(prepare_dir), f"prepare directory not found at {prepare_dir}"

    # Check that prepare/compiler exists (similar pattern to what's being added)
    prepare_compiler = os.path.join(REPO, "prepare/compiler")
    assert os.path.isdir(prepare_compiler), f"prepare/compiler directory not found"


def test_repo_gradle_wrapper_available():
    """Pass-to-pass: Gradle wrapper is available for build commands (repo_tests)."""
    gradlew = os.path.join(REPO, "gradlew")
    gradle_wrapper_jar = os.path.join(REPO, "gradle/wrapper/gradle-wrapper.jar")

    assert os.path.exists(gradlew), "Gradle wrapper script not found"
    assert os.path.isfile(gradlew), "gradlew is not a file"
    assert os.access(gradlew, os.X_OK), "gradlew is not executable"
    assert os.path.exists(gradle_wrapper_jar), "gradle-wrapper.jar not found"


def test_repo_jar_compiles():
    """Pass-to-pass: The jklib-compiler jar task compiles without errors (repo_tests).

    This test actually runs the jar task compilation to ensure the build script
    is syntactically and structurally correct.
    """
    if not os.path.exists(BUILD_FILE):
        pytest.skip("Build file does not exist")

    # Run jar task compilation - just up to the compile stage, don't need full build
    result = _run_gradle([":kotlin-jklib-compiler:compileKotlin", "--quiet"], timeout=300)
    assert result.returncode == 0, f"Jar compilation failed:\n{result.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
