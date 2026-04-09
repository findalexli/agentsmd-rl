"""Tests for Maven Toolchain support in kotlin-maven-plugin."""

import re
from pathlib import Path

REPO = Path("/workspace/kotlin")
TARGET_FILE = REPO / "libraries/tools/kotlin-maven-plugin/src/main/java/org/jetbrains/kotlin/maven/K2JVMCompileMojo.java"


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
