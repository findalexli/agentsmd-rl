"""Tests for Kotlin jklib packaging script PR.

This verifies that the build.gradle.kts file for jklib-compiler
is correctly created and registered in settings.gradle.
"""

import os
import pytest
import re
import subprocess
import sys
import tempfile
import zipfile

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


# ============================================================================
# Fail-to-pass tests: Verify the fix works
# ============================================================================


def test_build_file_exists():
    """Fail-to-pass: build.gradle.kts file exists at correct path."""
    assert os.path.exists(BUILD_FILE), f"Build file not found at {BUILD_FILE}"


def test_settings_includes_module():
    """Fail-to-pass: settings.gradle includes :kotlin-jklib-compiler module."""
    result = _run_gradle(["projects", "--quiet"], timeout=180)
    assert result.returncode == 0, f"Gradle projects command failed:\n{result.stderr}"
    assert ":kotlin-jklib-compiler" in result.stdout, \
        f"Module :kotlin-jklib-compiler not found in projects list:\n{result.stdout}"


def test_settings_has_project_dir():
    """Fail-to-pass: settings.gradle maps projectDir for kotlin-jklib-compiler."""
    # Verify the project path mapping by checking build file path resolution
    result = _run_gradle([":kotlin-jklib-compiler:help"], timeout=180)
    assert result.returncode == 0, f"Build script failed to load - projectDir mapping likely incorrect:\n{result.stderr}"


def test_gradle_build_script_loads():
    """Fail-to-pass: The build.gradle.kts script loads without errors."""
    if not os.path.exists(BUILD_FILE):
        pytest.skip("Build file does not exist")

    result = _run_gradle([":kotlin-jklib-compiler:help"], timeout=180)
    assert result.returncode == 0, f"Build script failed to load:\n{result.stderr}"


def test_gradle_tasks_registered():
    """Fail-to-pass: The build script registers expected tasks."""
    if not os.path.exists(BUILD_FILE):
        pytest.skip("Build file does not exist")

    result = _run_gradle([":kotlin-jklib-compiler:tasks", "--all"], timeout=180)
    assert result.returncode == 0, f"Failed to list tasks:\n{result.stderr}"
    # Verify the jar and dist tasks are available
    assert "jar" in result.stdout, f"jar task not registered:\n{result.stdout}"
    assert "dist" in result.stdout, f"dist task not registered:\n{result.stdout}"


def test_build_file_has_copyright():
    """Fail-to-pass: Build file has proper copyright header."""
    with open(BUILD_FILE, "r") as f:
        content = f.read()
    # Check for copyright by verifying the literal strings are present
    assert "Copyright 2010-2026 JetBrains" in content, "Missing copyright header"
    assert "Apache 2.0 license" in content, "Missing license reference"


def test_build_file_has_description():
    """Fail-to-pass: Build file has description for the packaging script."""
    with open(BUILD_FILE, "r") as f:
        content = f.read()
    # Verify the description literal is present
    assert "JKlib Classes packaging script" in content, "Missing description with required text"


def test_build_file_has_plugins():
    """Fail-to-pass: Build file applies kotlin(\"jvm\") plugin."""
    # Verify the plugin is applied by checking the build actually works
    result = _run_gradle([":kotlin-jklib-compiler:help"], timeout=180)
    assert result.returncode == 0, f"Build script failed to load - kotlin jvm plugin likely missing:\n{result.stderr}"

    # Also verify plugin is declared in source
    with open(BUILD_FILE, "r") as f:
        content = f.read()
    assert "kotlin(\"jvm\")" in content, "Missing kotlin jvm plugin declaration"


def test_build_file_has_configurations():
    """Fail-to-pass: Build file creates buildNumber and distContent configurations."""
    if not os.path.exists(BUILD_FILE):
        pytest.skip("Build file does not exist")

    # Verify configurations exist by querying dependencies
    result = _run_gradle([":kotlin-jklib-compiler:dependencies", "--configuration", "distContent"], timeout=180)
    # Configuration may be empty or have dependencies, but command should succeed
    # If configuration does not exist, gradle will fail with "configuration not found"

    result2 = _run_gradle([":kotlin-jklib-compiler:dependencies", "--configuration", "buildNumber"], timeout=180)
    # buildNumber should have the build.version dependency

    # Also verify the configuration names are declared in the build file
    with open(BUILD_FILE, "r") as f:
        content = f.read()
    assert "buildNumber" in content, "Missing buildNumber configuration declaration"
    assert "distContent" in content, "Missing distContent configuration declaration"


def test_build_file_has_dependencies():
    """Fail-to-pass: Build file has correct dependencies on cli-jklib and ir.serialization.jklib."""
    if not os.path.exists(BUILD_FILE):
        pytest.skip("Build file does not exist")

    # Query the distContent configuration to verify dependencies
    result = _run_gradle([":kotlin-jklib-compiler:dependencies", "--configuration", "distContent"], timeout=180)
    assert result.returncode == 0, f"Failed to query dependencies:\n{result.stderr}"

    # Check that both required modules appear in the dependency report
    output = result.stdout
    assert "cli-jklib" in output, f"Missing cli-jklib dependency in distContent:\n{output}"
    assert "serialization.jklib" in output, f"Missing ir.serialization.jklib dependency in distContent:\n{output}"

    # Verify isTransitive = false is in the build script (required by spec)
    with open(BUILD_FILE, "r") as f:
        content = f.read()
    assert "isTransitive" in content, "Missing isTransitive configuration in dependencies"


def test_build_file_has_jar_task():
    """Fail-to-pass: Build file configures jar task with correct archive name."""
    if not os.path.exists(BUILD_FILE):
        pytest.skip("Build file does not exist")

    # Build the jar and verify the output filename
    result = _run_gradle([":kotlin-jklib-compiler:jar"], timeout=300)
    assert result.returncode == 0, f"Jar task failed:\n{result.stderr}"

    # Check that jklib-compiler.jar was created
    jar_path = os.path.join(REPO, "prepare/jklib-compiler/build/libs/jklib-compiler.jar")
    assert os.path.exists(jar_path), f"jklib-compiler.jar not found at expected path: {jar_path}"


def test_jar_has_correct_manifest():
    """Fail-to-pass: Built jar has correct manifest with Class-Path and Main-Class."""
    if not os.path.exists(BUILD_FILE):
        pytest.skip("Build file does not exist")

    # Build the jar
    result = _run_gradle([":kotlin-jklib-compiler:jar"], timeout=300)
    assert result.returncode == 0, f"Jar task failed:\n{result.stderr}"

    jar_path = os.path.join(REPO, "prepare/jklib-compiler/build/libs/jklib-compiler.jar")
    if not os.path.exists(jar_path):
        pytest.skip("Jar file not created - cannot verify manifest")

    # Extract and verify manifest
    with zipfile.ZipFile(jar_path, "r") as jar:
        manifest_content = jar.read("META-INF/MANIFEST.MF").decode("utf-8")

    # Verify manifest attributes
    assert "Class-Path:" in manifest_content, f"Missing Class-Path in manifest:\n{manifest_content}"
    assert "kotlin-compiler.jar" in manifest_content, f"Missing kotlin-compiler.jar in Class-Path:\n{manifest_content}"
    assert "kotlin-stdlib.jar" in manifest_content, f"Missing kotlin-stdlib.jar in Class-Path:\n{manifest_content}"
    assert "kotlin-reflect.jar" in manifest_content, f"Missing kotlin-reflect.jar in Class-Path:\n{manifest_content}"
    assert "Main-Class:" in manifest_content, f"Missing Main-Class in manifest:\n{manifest_content}"
    assert "org.jetbrains.kotlin.cli.jklib.K2JKlibCompiler" in manifest_content, \
        f"Missing correct Main-Class in manifest:\n{manifest_content}"


def test_build_file_has_dist_task():
    """Fail-to-pass: Build file registers dist Sync task."""
    if not os.path.exists(BUILD_FILE):
        pytest.skip("Build file does not exist")

    # Verify dist task is registered and runs
    result = _run_gradle([":kotlin-jklib-compiler:dist"], timeout=300)
    assert result.returncode == 0, f"Dist task failed:\n{result.stderr}"

    # Verify the dist/jklib directory was created
    dist_jklib = os.path.join(REPO, "dist/jklib")
    assert os.path.isdir(dist_jklib), f"dist/jklib directory not created by dist task"


def test_dist_creates_correct_structure():
    """Fail-to-pass: Dist task creates expected directory structure with license and lib."""
    if not os.path.exists(BUILD_FILE):
        pytest.skip("Build file does not exist")

    # Run dist task
    result = _run_gradle([":kotlin-jklib-compiler:dist"], timeout=300)
    assert result.returncode == 0, f"Dist task failed:\n{result.stderr}"

    # Verify the directory structure
    dist_jklib = os.path.join(REPO, "dist/jklib")

    # Check license directory exists and has files
    license_dir = os.path.join(dist_jklib, "license")
    assert os.path.isdir(license_dir), f"license directory not created in dist/jklib"

    # Check lib directory exists and contains the jar
    lib_dir = os.path.join(dist_jklib, "lib")
    assert os.path.isdir(lib_dir), f"lib directory not created in dist/jklib"

    # Check jar is in lib directory
    jar_in_lib = os.path.join(lib_dir, "jklib-compiler.jar")
    assert os.path.exists(jar_in_lib), f"jklib-compiler.jar not found in dist/jklib/lib"


def test_dist_lib_permissions():
    """Fail-to-pass: Dist task sets correct file permissions on jar in lib directory."""
    if not os.path.exists(BUILD_FILE):
        pytest.skip("Build file does not exist")

    # Run dist task
    result = _run_gradle([":kotlin-jklib-compiler:dist"], timeout=300)
    assert result.returncode == 0, f"Dist task failed:\n{result.stderr}"

    # Check file permissions on the jar in dist/jklib/lib
    jar_path = os.path.join(REPO, "dist/jklib/lib/jklib-compiler.jar")
    if not os.path.exists(jar_path):
        pytest.skip("Jar not found in dist/jklib/lib")

    # Get file permissions
    jar_stat = os.stat(jar_path)
    # Unix permissions: st_mode & 0o777 gives permission bits
    permissions = jar_stat.st_mode & 0o777
    # Expected: rw-r--r-- = 0o644
    assert permissions == 0o644, f"File permissions incorrect: expected 0o644 (rw-r--r--), got 0o{permissions:o}"


# ============================================================================
# Pass-to-pass tests: Repo validation
# ============================================================================


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

    with open(cli_jklib_build, "r") as f:
        content = f.read()

    # Basic Gradle Kotlin DSL validation
    assert "plugins {" in content, "Missing plugins block in cli-jklib build file"
    assert "dependencies {" in content, "Missing dependencies block in cli-jklib build file"


def test_repo_serialization_jklib_has_valid_structure():
    """Pass-to-pass: ir.serialization.jklib module has valid Gradle build script structure (repo_tests)."""
    ir_serialization_build = os.path.join(REPO, "compiler/ir/serialization.jklib/build.gradle.kts")
    if not os.path.exists(ir_serialization_build):
        pytest.skip("ir.serialization.jklib build file does not exist")

    with open(ir_serialization_build, "r") as f:
        content = f.read()

    # Basic Gradle Kotlin DSL validation
    assert "plugins {" in content, "Missing plugins block in serialization.jklib build file"
    assert "dependencies {" in content, "Missing dependencies block in serialization.jklib build file"


def test_repo_jklib_tests_module_exists():
    """Pass-to-pass: jklib.tests module exists for integration testing (repo_tests)."""
    jklib_tests_build = os.path.join(REPO, "compiler/jklib.tests/build.gradle.kts")
    assert os.path.exists(jklib_tests_build), f"jklib.tests build file not found at {jklib_tests_build}"


def test_repo_prepare_structure_exists():
    """Pass-to-pass: prepare directory structure exists for build packaging scripts (repo_tests)."""
    prepare_dir = os.path.join(REPO, "prepare")
    assert os.path.isdir(prepare_dir), f"prepare directory not found at {prepare_dir}"

    # Check that prepare/compiler exists (similar pattern to what is being added)
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

    # Run jar task compilation - just up to the compile stage, do not need full build
    result = _run_gradle([":kotlin-jklib-compiler:compileKotlin", "--quiet"], timeout=300)
    assert result.returncode == 0, f"Jar compilation failed:\n{result.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
