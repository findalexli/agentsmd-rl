"""Tests for Maven Toolchain support in kotlin-maven-plugin."""

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/kotlin")
TARGET_FILE = REPO / "libraries/tools/kotlin-maven-plugin/src/main/java/org/jetbrains/kotlin/maven/K2JVMCompileMojo.java"
PLUGIN_DIR = REPO / "libraries/tools/kotlin-maven-plugin"


def test_toolchain_manager_field_exists():
    """ToolchainManager field with @Component annotation exists."""
    content = TARGET_FILE.read_text()

    # Check for ToolchainManager import
    assert "import org.apache.maven.toolchain.ToolchainManager;" in content, \
        "ToolchainManager import missing"

    # Check for @Component annotated ToolchainManager field
    assert "@Component" in content, "@Component annotation missing"
    assert "protected ToolchainManager toolchainManager;" in content, \
        "ToolchainManager field missing"


def test_jdk_toolchain_parameter_exists():
    """jdkToolchain parameter with @Parameter annotation exists."""
    content = TARGET_FILE.read_text()

    # Check for jdkToolchain parameter field
    assert "protected Map<String, String> jdkToolchain;" in content, \
        "jdkToolchain parameter field missing"


def test_get_toolchain_method_exists():
    """getToolchain() method exists and queries toolchains properly."""
    content = TARGET_FILE.read_text()

    # Check method signature
    assert "private @Nullable Toolchain getToolchain()" in content, \
        "getToolchain() method missing or wrong signature"

    # Check it uses jdkToolchain parameter
    assert "if (jdkToolchain != null)" in content, \
        "getToolchain() should check jdkToolchain parameter"

    # Check it calls toolchainManager.getToolchains
    assert "toolchainManager.getToolchains(session, \"jdk\", jdkToolchain)" in content, \
        "getToolchain() should call toolchainManager.getToolchains()"

    # Check fallback to build context toolchain
    assert "toolchainManager.getToolchainFromBuildContext(\"jdk\", session)" in content, \
        "getToolchain() should fallback to getToolchainFromBuildContext()"


def test_get_toolchain_jdk_home_method_exists():
    """getToolchainJdkHome() method exists and extracts JDK home from toolchain."""
    content = TARGET_FILE.read_text()

    # Check method signature
    assert "private @Nullable String getToolchainJdkHome()" in content, \
        "getToolchainJdkHome() method missing or wrong signature"

    # Check it calls getToolchain()
    assert "Toolchain toolchain = getToolchain();" in content, \
        "getToolchainJdkHome() should call getToolchain()"

    # Check it finds javac tool
    assert 'toolchain.findTool("javac")' in content, \
        "getToolchainJdkHome() should find javac tool"

    # Check it traverses up from javac to get JDK home
    assert "javac.getParentFile()" in content, \
        "getToolchainJdkHome() should traverse from javac to JDK home"


def test_jdk_home_takes_precedence_over_toolchain():
    """When jdkHome is set, it takes precedence over toolchain and logs warning."""
    content = TARGET_FILE.read_text()

    # Check that warning message exists
    assert "Toolchains are ignored, overwritten by 'jdkHome' parameter" in content, \
        "Should log warning when jdkHome overrides toolchain"

    # Check that the info messages exist
    assert "Overriding JDK home path with:" in content, \
        "Should log info when using jdkHome"
    assert "Overriding JDK home path with toolchain JDK:" in content, \
        "Should log info when using toolchain JDK"

    # Check the precedence logic exists - jdkHome checked first
    # Look for the pattern where jdkHome is checked, then toolchainJdkHome
    jdk_home_pattern = r'if\s*\(\s*jdkHome\s*!=\s*null\s*\)'
    assert re.search(jdk_home_pattern, content), \
        "Should check jdkHome first in conditional"

    # Check that setJdkHome is called for both cases
    assert "arguments.setJdkHome(jdkHome)" in content, \
        "Should call setJdkHome with jdkHome"
    assert "arguments.setJdkHome(toolchainJdkHome)" in content, \
        "Should call setJdkHome with toolchainJdkHome"


def test_toolchain_imports_exist():
    """Required toolchain imports are present."""
    content = TARGET_FILE.read_text()

    # Check for Toolchain import
    assert "import org.apache.maven.toolchain.Toolchain;" in content, \
        "Toolchain import missing"

    # Check for ToolchainManager import
    assert "import org.apache.maven.toolchain.ToolchainManager;" in content, \
        "ToolchainManager import missing"


# =============================================================================
# Pass-to-pass tests - verify repository health (work on base commit)
# =============================================================================


def test_repo_file_exists():
    """Target Java file exists and is readable (pass_to_pass)."""
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"
    assert TARGET_FILE.is_file(), f"Target is not a file: {TARGET_FILE}"
    content = TARGET_FILE.read_text()
    assert len(content) > 0, "Target file is empty"
    assert "class K2JVMCompileMojo" in content, "K2JVMCompileMojo class not found"


def test_repo_pom_exists():
    """Maven pom.xml exists and is valid XML (pass_to_pass)."""
    pom_file = PLUGIN_DIR / "pom.xml"
    assert pom_file.exists(), f"pom.xml not found: {pom_file}"
    content = pom_file.read_text()
    assert "<project" in content, "Invalid pom.xml - missing <project> tag"
    assert "<artifactId>kotlin-maven-plugin</artifactId>" in content, \
        "pom.xml missing kotlin-maven-plugin artifactId"


def test_repo_directory_structure():
    """Maven plugin directory has expected structure (pass_to_pass)."""
    assert PLUGIN_DIR.exists(), f"Plugin directory not found: {PLUGIN_DIR}"

    # Check standard Maven directories
    src_main = PLUGIN_DIR / "src/main/java"
    src_test = PLUGIN_DIR / "src/test"
    assert src_main.exists(), f"src/main/java not found"
    assert src_test.exists(), f"src/test not found"

    # Check package structure
    pkg_dir = src_main / "org/jetbrains/kotlin/maven"
    assert pkg_dir.exists(), f"Package directory not found: {pkg_dir}"


def test_repo_java_syntax_valid():
    """Target file has valid Java syntax structure (pass_to_pass)."""
    content = TARGET_FILE.read_text()

    # Check basic Java structure
    assert content.count("{") > 0, "No opening braces found"
    assert content.count("}") > 0, "No closing braces found"

    # Check class declaration
    assert "public class K2JVMCompileMojo" in content, \
        "K2JVMCompileMojo class declaration not found"

    # Check package declaration
    assert "package org.jetbrains.kotlin.maven;" in content, \
        "Package declaration not found"

    # Check imports are present
    assert content.count("import ") > 0, "No imports found"

    # Check method declarations exist
    assert "protected void configureSpecificCompilerArguments" in content, \
        "configureSpecificCompilerArguments method not found"


def test_maven_available():
    """Maven is installed and functional (pass_to_pass)."""
    r = subprocess.run(
        ["mvn", "--version"],
        capture_output=True, text=True, timeout=30
    )
    assert r.returncode == 0, f"Maven not available: {r.stderr}"
    assert "Apache Maven" in r.stdout, "Unexpected Maven version output"


def test_java_available():
    """Java is installed and functional (pass_to_pass)."""
    r = subprocess.run(
        ["java", "-version"],
        capture_output=True, text=True, timeout=30
    )
    assert r.returncode == 0, f"Java not available: {r.stderr}"
    # Java outputs version to stderr
    version_output = r.stderr + r.stdout
    assert "openjdk" in version_output.lower() or "java" in version_output.lower(), \
        "Unexpected Java version output"


def test_pom_validation():
    """Maven can validate the pom.xml (pass_to_pass)."""
    r = subprocess.run(
        ["mvn", "help:evaluate", "-Dexpression=project.artifactId", "-q", "-DforceStdout"],
        capture_output=True, text=True, timeout=120, cwd=str(PLUGIN_DIR)
    )
    # This may fail due to missing SNAPSHOT deps, but should parse pom
    # We accept non-zero returncode as long as it's not a parse error
    error_msg = r.stderr.lower()
    assert "parse" not in error_msg or "pom.xml" not in error_msg, \
        f"POM parsing error: {r.stderr[:500]}"
