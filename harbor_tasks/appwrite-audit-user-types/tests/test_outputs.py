#!/usr/bin/env python3
"""
Test suite for Appwrite audit user types feature.
Verifies that the code changes correctly distinguish between user types:
- user: regular authenticated user
- admin: console admin (APP_MODE_ADMIN)
- guest: anonymous/unauthenticated user
- keyProject: standard/dynamic project API key
- keyAccount: account-scoped API key
- keyOrganization: organization-scoped API key
"""

import subprocess
import sys
import re
import ast
import os

REPO_PATH = "/workspace/appwrite"
CONSTANTS_PATH = f"{REPO_PATH}/app/init/constants.php"
LOG_MODEL_PATH = f"{REPO_PATH}/src/Appwrite/Utopia/Response/Model/Log.php"
API_SHARED_PATH = f"{REPO_PATH}/app/controllers/shared/api.php"
USERS_API_PATH = f"{REPO_PATH}/app/controllers/api/users.php"
MESSAGING_API_PATH = f"{REPO_PATH}/app/controllers/api/messaging.php"

XLIST_PATHS = [
    f"{REPO_PATH}/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Logs/XList.php",
    f"{REPO_PATH}/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Logs/XList.php",
    f"{REPO_PATH}/src/Appwrite/Platform/Modules/Databases/Http/Databases/Logs/XList.php",
    f"{REPO_PATH}/src/Appwrite/Platform/Modules/Databases/Http/TablesDB/Logs/XList.php",
    f"{REPO_PATH}/src/Appwrite/Platform/Modules/Teams/Http/Logs/XList.php",
]


def read_file(path):
    """Read file contents, return None if not found."""
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None


def test_constants_defined():
    """F2P: Verify all new activity type constants are defined in constants.php"""
    content = read_file(CONSTANTS_PATH)
    assert content is not None, f"Could not read {CONSTANTS_PATH}"

    # Check for new constants
    expected_constants = [
        "ACTIVITY_TYPE_USER",
        "ACTIVITY_TYPE_ADMIN",
        "ACTIVITY_TYPE_GUEST",
        "ACTIVITY_TYPE_KEY_PROJECT",
        "ACTIVITY_TYPE_KEY_ACCOUNT",
        "ACTIVITY_TYPE_KEY_ORGANIZATION",
    ]

    for const in expected_constants:
        assert f"const {const}" in content, f"Missing constant: {const}"

    # Verify ACTIVITY_TYPE_APP was removed (replaced by ACTIVITY_TYPE_KEY_PROJECT)
    assert "ACTIVITY_TYPE_APP" not in content, "Old ACTIVITY_TYPE_APP constant should be removed"

    # Verify correct values
    assert "ACTIVITY_TYPE_USER = 'user'" in content
    assert "ACTIVITY_TYPE_ADMIN = 'admin'" in content
    assert "ACTIVITY_TYPE_GUEST = 'guest'" in content
    assert "ACTIVITY_TYPE_KEY_PROJECT = 'keyProject'" in content
    assert "ACTIVITY_TYPE_KEY_ACCOUNT = 'keyAccount'" in content
    assert "ACTIVITY_TYPE_KEY_ORGANIZATION = 'keyOrganization'" in content


def test_log_model_has_usertype_field():
    """F2P: Verify Log response model includes userType field"""
    content = read_file(LOG_MODEL_PATH)
    assert content is not None, f"Could not read {LOG_MODEL_PATH}"

    # Check for userType rule
    assert "'userType'" in content, "Log model missing userType field"
    assert "User type who triggered the audit log" in content, "Missing userType description"
    assert "user, admin, guest, keyProject, keyAccount, keyOrganization" in content, "Missing userType possible values"


def test_api_controller_mode_based_user_type():
    """F2P: Verify API controller sets user type based on mode (admin vs user)"""
    content = read_file(API_SHARED_PATH)
    assert content is not None, f"Could not read {API_SHARED_PATH}"

    # Check that mode-based type assignment exists
    assert "APP_MODE_ADMIN" in content, "Missing APP_MODE_ADMIN check"
    assert "ACTIVITY_TYPE_ADMIN" in content, "Missing ACTIVITY_TYPE_ADMIN usage"
    assert "ACTIVITY_TYPE_USER" in content, "Missing ACTIVITY_TYPE_USER usage"

    # Check for conditional type assignment based on mode
    assert '$mode === APP_MODE_ADMIN' in content or "$mode === APP_MODE_ADMIN" in content, \
        "Missing mode comparison for admin type assignment"


def test_api_controller_key_type_mapping():
    """F2P: Verify API controller maps API key types correctly"""
    content = read_file(API_SHARED_PATH)
    assert content is not None, f"Could not read {API_SHARED_PATH}"

    # Check for match expression or switch for key types
    assert "API_KEY_STANDARD" in content, "Missing API_KEY_STANDARD handling"
    assert "API_KEY_ACCOUNT" in content, "Missing API_KEY_ACCOUNT handling"
    assert "API_KEY_ORGANIZATION" in content, "Missing API_KEY_ORGANIZATION handling"

    # Check that key types map to activity types
    assert "ACTIVITY_TYPE_KEY_PROJECT" in content, "Missing ACTIVITY_TYPE_KEY_PROJECT"
    assert "ACTIVITY_TYPE_KEY_ACCOUNT" in content, "Missing ACTIVITY_TYPE_KEY_ACCOUNT"
    assert "ACTIVITY_TYPE_KEY_ORGANIZATION" in content, "Missing ACTIVITY_TYPE_KEY_ORGANIZATION"


def test_api_controller_uses_mode_injection():
    """F2P: Verify API controller action injects and uses mode parameter"""
    content = read_file(API_SHARED_PATH)
    assert content is not None, f"Could not read {API_SHARED_PATH}"

    # Check for mode injection
    assert "->inject('mode')" in content, "Missing mode injection"

    # Check that action signature includes mode parameter
    assert "string $mode" in content, "Action function missing string $mode parameter"


def test_api_controller_preserves_existing_type():
    """F2P: Verify API controller only sets type when not already set"""
    content = read_file(API_SHARED_PATH)
    assert content is not None, f"Could not read {API_SHARED_PATH}"

    # Check for the guard that prevents overwriting existing type
    assert "empty($user->getAttribute('type'))" in content, \
        "Missing guard to preserve existing user type"


def test_users_api_includes_usertype_and_mode():
    """F2P: Verify users API log response includes userType and mode"""
    content = read_file(USERS_API_PATH)
    assert content is not None, f"Could not read {USERS_API_PATH}"

    # Find the section where log data is constructed
    # Should have 'userType' => $log['data']['userType']
    assert "'userType' =>" in content, "users.php missing userType in log response"
    assert "'mode' =>" in content, "users.php missing mode in log response"


def test_messaging_api_includes_usertype():
    """F2P: Verify messaging API log responses include userType"""
    content = read_file(MESSAGING_API_PATH)
    assert content is not None, f"Could not read {MESSAGING_API_PATH}"

    # Count occurrences - should be in multiple places (4 places based on diff)
    usertype_count = content.count("'userType' =>")
    assert usertype_count >= 4, f"messaging.php should have userType in at least 4 places, found {usertype_count}"


def test_xlist_endpoints_include_usertype():
    """F2P: Verify all XList log endpoints include userType in response"""
    for path in XLIST_PATHS:
        content = read_file(path)
        assert content is not None, f"Could not read {path}"

        filename = os.path.basename(os.path.dirname(path)) + "/" + os.path.basename(path)
        assert "'userType' =>" in content, f"{filename} missing userType in log response"
        assert "$log['data']['userType']" in content, f"{filename} should read userType from log data"


def test_key_project_replaces_app_type():
    """F2P: Verify ACTIVITY_TYPE_KEY_PROJECT replaces ACTIVITY_TYPE_APP in API key handling"""
    content = read_file(API_SHARED_PATH)
    assert content is not None, f"Could not read {API_SHARED_PATH}"

    # Should use ACTIVITY_TYPE_KEY_PROJECT instead of ACTIVITY_TYPE_APP
    assert "ACTIVITY_TYPE_KEY_PROJECT" in content, "Missing ACTIVITY_TYPE_KEY_PROJECT"
    assert "'type' => ACTIVITY_TYPE_KEY_PROJECT" in content, "Should set type to ACTIVITY_TYPE_KEY_PROJECT for API keys"


def test_php_syntax_valid():
    """P2P: Verify all modified PHP files have valid syntax"""
    files_to_check = [
        CONSTANTS_PATH,
        LOG_MODEL_PATH,
        API_SHARED_PATH,
        USERS_API_PATH,
        MESSAGING_API_PATH,
    ] + XLIST_PATHS

    for path in files_to_check:
        if not os.path.exists(path):
            continue

        result = subprocess.run(
            ["php", "-l", path],
            capture_output=True,
            text=True,
            cwd=REPO_PATH
        )
        assert result.returncode == 0, f"PHP syntax error in {path}: {result.stderr}"


def test_repo_phplint():
    """Repo's PHP files pass syntax check (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "find app src -name '*.php' -exec php -l {} \\; 2>&1 | grep -E '(error|Error|FAIL)' || echo 'OK'"],
        capture_output=True, text=True, timeout=60, cwd=REPO_PATH,
    )
    assert "OK" in r.stdout or r.returncode == 0, f"PHP lint failed:\n{r.stdout[-500:]}"


def test_repo_pint():
    """Repo's PHP files pass Pint code style check (pass_to_pass)."""
    r = subprocess.run(
        ["vendor/bin/pint", "--test", "--config", "pint.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"Pint check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_phpstan_modified():
    """Repo's modified files pass PHPStan static analysis (pass_to_pass)."""
    # Run PHPStan on the modified directories only
    modified_dirs = ["app/init", "app/controllers", "src/Appwrite/Utopia/Response/Model"]
    for dir_path in modified_dirs:
        if not os.path.exists(f"{REPO_PATH}/{dir_path}"):
            continue
        r = subprocess.run(
            ["./vendor/bin/phpstan", "analyse", dir_path, "--memory-limit=1G", "--no-progress"],
            capture_output=True, text=True, timeout=90, cwd=REPO_PATH,
        )
        assert r.returncode == 0, f"PHPStan check failed for {dir_path}:\n{r.stdout[-500:]}{r.stderr[-500:]}"


if __name__ == "__main__":
    # Run all tests
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
