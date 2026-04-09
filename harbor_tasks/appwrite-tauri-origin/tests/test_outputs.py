"""Test tauri:// origin scheme support in Appwrite Origin validator."""

import subprocess
import sys
import os

# Path to the appwrite repository
REPO = "/workspace/appwrite"
PLATFORM_FILE = f"{REPO}/src/Appwrite/Network/Platform.php"
ORIGIN_FILE = f"{REPO}/src/Appwrite/Network/Validator/Origin.php"


def test_php_syntax_valid():
    """Verify modified PHP files have valid syntax."""
    files = [PLATFORM_FILE, ORIGIN_FILE]
    for filepath in files:
        result = subprocess.run(
            ['php', '-l', filepath],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, f"PHP syntax error in {filepath}:\n{result.stderr}"


def test_tauri_localhost_valid():
    """Test that tauri://localhost is accepted when localhost is in allowed hostnames."""
    # Use PHP to test the Origin validator
    php_code = '''
<?php
require_once 'vendor/autoload.php';

use Appwrite\\Network\\Validator\\Origin;

$validator = new Origin(['localhost'], 'tauri');
$result = $validator->isValid('tauri://localhost');
echo $result ? "PASS" : "FAIL";
'''
    result = subprocess.run(
        ['php', '-r', php_code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.stdout.strip() == "PASS", f"tauri://localhost should be valid. Output: {result.stdout}, Error: {result.stderr}"


def test_tauri_unregistered_host_invalid():
    """Test that tauri://example.com is rejected with proper error message."""
    php_code = '''
<?php
require_once 'vendor/autoload.php';

use Appwrite\\Network\\Validator\\Origin;

$validator = new Origin(['localhost'], 'tauri');
$result = $validator->isValid('tauri://example.com');
$description = $validator->getDescription();
echo "Result: " . ($result ? "valid" : "invalid") . "\n";
echo "Description: " . $description . "\n";
'''
    result = subprocess.run(
        ['php', '-r', php_code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    output = result.stdout.strip()
    assert "Result: invalid" in output, f"tauri://example.com should be invalid. Output: {output}"
    assert "Web (Tauri)" in output, f"Error message should reference 'Web (Tauri)' platform. Output: {output}"
    assert "example.com" in output, f"Error message should mention the unregistered host. Output: {output}"


def test_tauri_different_hosts():
    """Test tauri:// scheme with various hostnames."""
    test_cases = [
        (['localhost', 'app.example.com'], 'tauri://localhost', True),
        (['localhost', 'app.example.com'], 'tauri://app.example.com', True),
        (['localhost'], 'tauri://evil.com', False),
        (['myapp.local'], 'tauri://myapp.local', True),
    ]

    for allowed_hosts, origin, expected_valid in test_cases:
        hosts_str = "', '".join(allowed_hosts)
        php_code = f'''<?php
require_once 'vendor/autoload.php';
use Appwrite\\Network\\Validator\\Origin;
$validator = new Origin(['{hosts_str}'], 'tauri');
$result = $validator->isValid('{origin}');
echo $result ? "VALID" : "INVALID";
'''
        result = subprocess.run(
            ['php', '-r', php_code],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30
        )
        actual = result.stdout.strip() == "VALID"
        assert actual == expected_valid, \
            f"Origin {origin} with allowed hosts {allowed_hosts}: expected {expected_valid}, got {actual}"


def test_tauri_constant_exists():
    """Verify SCHEME_TAURI constant is defined in Platform class."""
    php_code = '''
<?php
require_once 'vendor/autoload.php';
use Appwrite\\Network\\Platform;
echo defined('Appwrite\\Network\\Platform::SCHEME_TAURI') ? "DEFINED" : "UNDEFINED";
'''
    result = subprocess.run(
        ['php', '-r', php_code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.stdout.strip() == "DEFINED", "SCHEME_TAURI constant should be defined in Platform class"


def test_tauri_platform_name():
    """Verify Tauri platform name mapping exists and is correct."""
    php_code = '''
<?php
require_once 'vendor/autoload.php';
use Appwrite\\Network\\Platform;
$names = Platform::getSchemeNames();
echo $names[Platform::SCHEME_TAURI] ?? "NOT_FOUND";
'''
    result = subprocess.run(
        ['php', '-r', php_code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.stdout.strip() == "Web (Tauri)", \
        f"Tauri platform name should be 'Web (Tauri)', got: {result.stdout.strip()}"


def test_other_web_platforms_still_work():
    """Ensure adding tauri doesn't break existing web platform validation."""
    php_code = '''
<?php
require_once 'vendor/autoload.php';
use Appwrite\\Network\\Validator\\Origin;

$results = [];

// Test http
$validator = new Origin(['localhost'], 'http');
$results[] = $validator->isValid('http://localhost') ? "http_ok" : "http_fail";

// Test https
$validator = new Origin(['example.com'], 'https');
$results[] = $validator->isValid('https://example.com') ? "https_ok" : "https_fail";

// Test chrome extension
$validator = new Origin(['abc123'], 'chrome-extension');
$results[] = $validator->isValid('chrome-extension://abc123') ? "chrome_ok" : "chrome_fail";

echo implode("|", $results);
'''
    result = subprocess.run(
        ['php', '-r', php_code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    output = result.stdout.strip()
    assert "http_ok" in output, f"http:// validation broken: {output}"
    assert "https_ok" in output, f"https:// validation broken: {output}"
    assert "chrome_ok" in output, f"chrome-extension:// validation broken: {output}"


def test_unit_tests_pass():
    """Run the repository's own unit tests for Origin validator."""
    result = subprocess.run(
        ['php', 'vendor/bin/phpunit', 'tests/unit/Network/Validators/OriginTest.php'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Unit tests failed:\n{result.stdout}\n{result.stderr}"


def test_composer_validate_p2p():
    """Repo's composer.json is valid (pass_to_pass)."""
    result = subprocess.run(
        ['composer', 'validate', '--no-check-publish'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"composer validate failed:\n{result.stdout}\n{result.stderr}"


def test_unit_tests_network_p2p():
    """Repo's Network unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ['php', 'vendor/bin/phpunit', 'tests/unit/Network/Validators/OriginTest.php',
         '--filter', 'testValues|testGetAllowedHostnames|testGetAllowedSchemes|testSetAllowedHostnames|testSetAllowedSchemes'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Network unit tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"
