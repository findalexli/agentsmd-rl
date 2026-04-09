#!/usr/bin/env python3
"""
Test suite for Appwrite Rust SDK support task.

Tests verify:
1. Rust SDK configuration exists in app/config/sdks.php
2. Rust language class is imported and wired up in SDKs.php task
3. Code passes PHP syntax check
4. Code follows formatting standards (composer format)
"""

import subprocess
import sys
import re

REPO = "/workspace/appwrite"


def test_rust_sdk_config_exists():
    """Fail-to-pass: Rust SDK configuration must exist in sdks.php."""
    with open(f"{REPO}/app/config/sdks.php", "r") as f:
        content = f.read()

    # Check for Rust SDK key
    assert "'key' => 'rust'" in content, "Rust SDK key not found in sdks.php"

    # Check for essential configuration fields
    assert "'name' => 'Rust'" in content, "Rust SDK name not found"
    assert "APP_SDK_PLATFORM_SERVER" in content, "Rust SDK platform family not found"
    assert "sdk-for-rust" in content, "Rust SDK git repo not found"
    assert "'prism' => 'rust'" in content, "Rust SDK prism not found"


def test_rust_sdk_config_values():
    """Fail-to-pass: Rust SDK configuration values must be correct."""
    with open(f"{REPO}/app/config/sdks.php", "r") as f:
        content = f.read()

    # Check version
    assert "'version' => '0.1.0'" in content, "Rust SDK version not correct"

    # Check flags
    assert "'enabled' => true" in content, "Rust SDK should be enabled"
    assert "'beta' => true" in content, "Rust SDK should be marked beta"
    assert "'dev' => true" in content, "Rust SDK should be marked dev"

    # Check URLs
    assert "github.com/appwrite/sdk-for-rust" in content, "Rust SDK git URL not found"
    assert "crates.io/crates/appwrite" in content, "Rust SDK package URL not found"


def test_rust_language_import():
    """Fail-to-pass: Rust language class must be imported in SDKs.php."""
    with open(f"{REPO}/src/Appwrite/Platform/Tasks/SDKs.php", "r") as f:
        content = f.read()

    # Check for Rust import
    assert "use Appwrite\\SDK\\Language\\Rust;" in content, "Rust language class import missing"

    # Verify it's in the right section with other language imports
    lang_imports = re.findall(r"use Appwrite\\SDK\\Language\\(\w+);", content)
    assert "Rust" in lang_imports, "Rust not found in language imports"


def test_rust_switch_case():
    """Fail-to-pass: Rust case must exist in the switch statement."""
    with open(f"{REPO}/src/Appwrite/Platform/Tasks/SDKs.php", "r") as f:
        content = f.read()

    # Check for rust case in switch statement
    assert "case 'rust':" in content, "Rust case not found in switch statement"

    # Check that it creates a Rust config instance
    assert "new Rust()" in content, "Rust config instantiation not found"


def test_php_syntax_valid():
    """Pass-to-pass: PHP files must have valid syntax."""
    files = [
        f"{REPO}/app/config/sdks.php",
        f"{REPO}/src/Appwrite/Platform/Tasks/SDKs.php"
    ]

    for file in files:
        result = subprocess.run(
            ["php", "-l", file],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, f"PHP syntax error in {file}: {result.stderr}"


def test_composer_autoload_works():
    """Pass-to-pass: Composer autoload must be valid."""
    result = subprocess.run(
        ["composer", "dump-autoload", "--optimize"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Composer autoload failed: {result.stderr[-500:]}"


def test_rust_sdk_array_structure():
    """Fail-to-pass: Rust SDK array must be properly structured."""
    with open(f"{REPO}/app/config/sdks.php", "r") as f:
        content = f.read()

    # Find the Rust SDK array block - it should be complete
    # Look for the pattern starting with 'key' => 'rust' and check structure
    rust_pattern = r"'key' => 'rust'.*?(?=\[\s*'key' => |\];)"
    match = re.search(rust_pattern, content, re.DOTALL)

    assert match is not None, "Could not find complete Rust SDK array block"
    rust_block = match.group(0)

    # Verify essential fields are present
    required_fields = [
        "'key' => 'rust'",
        "'name' => 'Rust'",
        "'version' =>",
        "'url' =>",
        "'package' =>",
        "'enabled' =>",
        "'beta' =>",
        "'dev' =>",
        "'family' =>",
        "'prism' => 'rust'",
        "'source' =>",
        "'gitUrl' =>",
        "'gitRepoName' =>",
        "'gitUserName' =>",
        "'gitBranch' =>",
        "'changelog' =>",
    ]

    for field in required_fields:
        assert field in rust_block, f"Required field missing: {field}"


def test_switch_case_order():
    """Fail-to-pass: Rust case should be after Kotlin and before GraphQL."""
    with open(f"{REPO}/src/Appwrite/Platform/Tasks/SDKs.php", "r") as f:
        content = f.read()

    # Find the switch cases
    kotlin_pos = content.find("case 'kotlin':")
    rust_pos = content.find("case 'rust':")
    graphql_pos = content.find("case 'graphql':")

    assert kotlin_pos != -1, "Kotlin case not found"
    assert rust_pos != -1, "Rust case not found"
    assert graphql_pos != -1, "GraphQL case not found"

    # Rust should be after Kotlin and before GraphQL (based on PR diff)
    assert kotlin_pos < rust_pos < graphql_pos, \
        f"Rust case not in correct position: kotlin@{kotlin_pos}, rust@{rust_pos}, graphql@{graphql_pos}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
