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
require_once 'vendor/autoload.php';

use Appwrite\\Network\\Validator\\Origin;

$validator = new Origin(['localhost'], ['tauri']);
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
require_once 'vendor/autoload.php';

use Appwrite\\Network\\Validator\\Origin;

$validator = new Origin(['localhost'], ['tauri']);
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
        php_code = f'''require_once 'vendor/autoload.php';
use Appwrite\\Network\\Validator\\Origin;
$validator = new Origin(['{hosts_str}'], ['tauri']);
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
require_once 'vendor/autoload.php';
use Appwrite\\Network\\Platform;
echo Platform::getNameByScheme(Platform::SCHEME_TAURI);
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
require_once 'vendor/autoload.php';
use Appwrite\\Network\\Validator\\Origin;
use Appwrite\\Network\\Platform;

$results = [];

// Test http - note: http and https are web platforms that use allowedHostnames
$validator = new Origin(['localhost'], [Platform::SCHEME_HTTP, Platform::SCHEME_HTTPS]);
$results[] = $validator->isValid('http://localhost') ? "http_ok" : "http_fail";

// Test https
$validator = new Origin(['example.com'], [Platform::SCHEME_HTTPS]);
$results[] = $validator->isValid('https://example.com') ? "https_ok" : "https_fail";

// Test chrome extension - chrome-extension is a web platform, so allowedHostnames should contain the extension ID
$validator = new Origin(['abc123'], [Platform::SCHEME_CHROME_EXTENSION]);
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


def test_phpstan_network_p2p():
    """Repo's PHPStan static analysis passes on Network directory (pass_to_pass)."""
    result = subprocess.run(
        ['php', 'vendor/bin/phpstan', 'analyse', '-c', 'phpstan.neon',
         '--memory-limit=512M', 'src/Appwrite/Network/', '--no-progress'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"PHPStan analysis failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_pint_lint_network_p2p():
    """Repo's Pint lint check passes on Network directory (pass_to_pass)."""
    result = subprocess.run(
        ['php', 'vendor/bin/pint', '--test', '--config', 'pint.json',
         'src/Appwrite/Network/'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"Pint lint check failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_cors_unit_tests_p2p():
    """Repo's CORS unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ['php', 'vendor/bin/phpunit', 'tests/unit/Network/CorsTest.php'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"CORS unit tests failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_email_validator_unit_tests_p2p():
    """Repo's Email validator unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ['php', 'vendor/bin/phpunit', 'tests/unit/Network/Validators/EmailTest.php'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"Email validator unit tests failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_platform_unit_tests_p2p():
    """Repo's Platform unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ['php', 'vendor/bin/phpunit', 'tests/unit/Platform/'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Platform unit tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"


def test_detector_unit_tests_p2p():
    """Repo's Detector unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ['php', 'vendor/bin/phpunit', 'tests/unit/Detector/'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"Detector unit tests failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_template_unit_tests_p2p():
    """Repo's Template unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ['php', 'vendor/bin/phpunit', 'tests/unit/Template/'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"Template unit tests failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_filter_unit_tests_p2p():
    """Repo's Filter unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ['php', 'vendor/bin/phpunit', 'tests/unit/Filter/'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"Filter unit tests failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_openssl_unit_tests_p2p():
    """Repo's OpenSSL unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ['php', 'vendor/bin/phpunit', 'tests/unit/OpenSSL/'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"OpenSSL unit tests failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_task_unit_tests_p2p():
    """Repo's Task unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ['php', 'vendor/bin/phpunit', 'tests/unit/Task/'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"Task unit tests failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"
