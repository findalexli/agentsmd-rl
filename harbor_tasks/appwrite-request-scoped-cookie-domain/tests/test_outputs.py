#!/usr/bin/env python3
"""
Tests for appwrite request-scoped cookie domain refactor.
Validates that domainVerification and cookieDomain moved from global Config
to request-scoped resources.
"""

import subprocess
import sys
import re
from pathlib import Path

REPO = Path("/workspace/appwrite")


def test_cookie_domain_resource_exists():
    """Verify cookieDomain resource is defined in app/init/resources.php"""
    resources_file = REPO / "app/init/resources.php"
    content = resources_file.read_text()

    # Check for the Http::setResource call for cookieDomain
    assert "Http::setResource('cookieDomain'" in content, \
        "cookieDomain resource not defined in resources.php"

    # Check it has the correct dependencies
    assert "function (Request $request, Document $project)" in content or \
           "Request $request, Document $project" in content, \
        "cookieDomain resource should depend on request and project"

    # Check it handles localhost/IPs correctly
    assert "FILTER_VALIDATE_IP" in content, \
        "cookieDomain should handle IP address detection"
    assert "localhost" in content, \
        "cookieDomain should handle localhost detection"


def test_domain_verification_resource_exists():
    """Verify domainVerification resource is defined in app/init/resources.php"""
    resources_file = REPO / "app/init/resources.php"
    content = resources_file.read_text()

    # Check for the Http::setResource call for domainVerification
    assert "Http::setResource('domainVerification'" in content, \
        "domainVerification resource not defined in resources.php"

    # Check it depends on request
    assert "Request $request" in content, \
        "domainVerification resource should depend on request"

    # Check it uses Domain class
    assert "Domain($request->getHostname())" in content, \
        "domainVerification should use Domain class to compare hostnames"


def test_domain_class_imported():
    """Verify Domain class is imported in resources.php"""
    resources_file = REPO / "app/init/resources.php"
    content = resources_file.read_text()

    # Check for the import
    assert "use Utopia\\Domains\\Domain;" in content, \
        "Domain class must be imported in resources.php"


def test_general_php_no_config_mutations():
    """Verify general.php no longer sets domainVerification/cookieDomain on Config"""
    general_file = REPO / "app/controllers/general.php"
    content = general_file.read_text()

    # Check that Config::setParam for these specific values is removed
    assert "Config::setParam('domainVerification'" not in content, \
        "general.php should not set domainVerification on Config"
    assert "Config::setParam('cookieDomain'" not in content, \
        "general.php should not set cookieDomain on Config"


def test_account_controller_uses_injection():
    """Verify account.php controllers inject domainVerification and cookieDomain"""
    account_file = REPO / "app/controllers/api/account.php"
    content = account_file.read_text()

    # Check that inject calls exist
    assert "->inject('domainVerification')" in content, \
        "account.php should inject domainVerification"
    assert "->inject('cookieDomain')" in content, \
        "account.php should inject cookieDomain"

    # Check that action callbacks accept these as parameters
    assert "bool $domainVerification, ?string $cookieDomain" in content or \
           "bool $domainVerification,?string $cookieDomain" in content or \
           ("bool $domainVerification" in content and "?string $cookieDomain" in content), \
        "account.php action should declare domainVerification and cookieDomain parameters"


def test_account_controller_no_global_config():
    """Verify account.php no longer reads domainVerification/cookieDomain from Config"""
    account_file = REPO / "app/controllers/api/account.php"
    content = account_file.read_text()

    # Should not use Config::getParam for these values
    assert "Config::getParam('domainVerification')" not in content, \
        "account.php should not read domainVerification from Config::getParam()"
    assert "Config::getParam('cookieDomain')" not in content, \
        "account.php should not read cookieDomain from Config::getParam()"


def test_teams_membership_uses_injection():
    """Verify Teams membership status update uses injected values"""
    teams_file = REPO / "src/Appwrite/Platform/Modules/Teams/Http/Memberships/Status/Update.php"
    content = teams_file.read_text()

    # Check inject calls exist
    assert "->inject('domainVerification')" in content, \
        "Teams Update.php should inject domainVerification"
    assert "->inject('cookieDomain')" in content, \
        "Teams Update.php should inject cookieDomain"

    # Check action method signature
    assert "bool $domainVerification, ?string $cookieDomain" in content or \
           "Token $proofForToken, bool $domainVerification, ?string $cookieDomain" in content, \
        "Teams Update.php action should declare domainVerification and cookieDomain parameters"


def test_teams_membership_no_global_config():
    """Verify Teams membership status update no longer uses Config for these values"""
    teams_file = REPO / "src/Appwrite/Platform/Modules/Teams/Http/Memberships/Status/Update.php"
    content = teams_file.read_text()

    # Should not use Config::getParam for these
    assert "Config::getParam('domainVerification')" not in content, \
        "Teams Update.php should not read domainVerification from Config::getParam()"
    assert "Config::getParam('cookieDomain')" not in content, \
        "Teams Update.php should not read cookieDomain from Config::getParam()"


def test_create_session_closure_uses_params():
    """Verify the createSession closure accepts domainVerification and cookieDomain"""
    account_file = REPO / "app/controllers/api/account.php"
    content = account_file.read_text()

    # Find the createSession closure definition - should have both new params
    pattern = r"\$createSession\s*=\s*function\s*\([^)]*bool\s+\$domainVerification[^)]*\?string\s+\$cookieDomain"
    assert re.search(pattern, content, re.DOTALL), \
        "createSession closure should accept bool $domainVerification and ?string $cookieDomain parameters"


def test_php_syntax_valid():
    """Verify all modified PHP files have valid syntax"""
    files = [
        "app/init/resources.php",
        "app/controllers/general.php",
        "app/controllers/api/account.php",
        "src/Appwrite/Platform/Modules/Teams/Http/Memberships/Status/Update.php",
    ]

    for file in files:
        path = REPO / file
        if path.exists():
            result = subprocess.run(
                ["php", "-l", str(path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            assert result.returncode == 0, \
                f"PHP syntax error in {file}: {result.stderr}"


def test_repo_composer_validate():
    """Repo's composer.json is valid (pass_to_pass)."""
    result = subprocess.run(
        ["composer", "validate"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"composer validate failed:\n{result.stderr}"


def test_repo_php_syntax_modified_files():
    """All modified PHP files have valid syntax via php -l (pass_to_pass)."""
    modified_files = [
        "app/init/resources.php",
        "app/controllers/general.php",
        "app/controllers/api/account.php",
        "src/Appwrite/Platform/Modules/Teams/Http/Memberships/Status/Update.php",
    ]

    for file in modified_files:
        path = REPO / file
        result = subprocess.run(
            ["php", "-l", str(path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PHP syntax error in {file}:\n{result.stderr}"


def test_repo_composer_audit():
    """Repo's composer audit passes (pass_to_pass)."""
    result = subprocess.run(
        ["composer", "audit"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Exit 0 is success, but exit code can be non-zero if no packages to audit
    # Composer audit returns 0 on success or when skipping due to no packages
    assert result.returncode == 0 or "No packages - skipping audit" in result.stdout, \
        f"composer audit failed:\n{result.stderr}"


def test_repo_php_lint():
    """Repo's PHP code passes Pint linting (pass_to_pass)."""
    # Install dependencies first (stateless container), then run lint
    result = subprocess.run(
        ["bash", "-c", "composer install --ignore-platform-reqs -q 2>/dev/null && vendor/bin/pint --test --config pint.json"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, f"PHP lint (pint) failed:\n{result.stderr[-500:]}"


def test_repo_phpstan_analyze():
    """Repo's PHP code passes PHPStan static analysis (pass_to_pass)."""
    # Install dependencies first (stateless container), then run phpstan
    result = subprocess.run(
        ["bash", "-c", "composer install --ignore-platform-reqs -q 2>/dev/null && vendor/bin/phpstan analyse -c phpstan.neon --memory-limit=512M --no-progress"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, f"PHPStan analysis failed:\n{result.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
