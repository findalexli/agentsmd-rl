"""Test that null route guards are properly implemented in API middleware."""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/appwrite")
API_PHP = REPO / "app" / "controllers" / "shared" / "api.php"


def test_null_route_guard_in_init_action():
    """
    F2P: Verify the Http::init action has a null guard after $route = $utopia->getRoute().
    Location: Around line 98-100 in app/controllers/shared/api.php
    """
    content = API_PHP.read_text()

    # Find the Http::init action section
    init_marker = "Http::init()"
    init_pos = content.find(init_marker)
    assert init_pos != -1, "Http::init() section not found"

    # Look for the guard pattern in the init action
    # The guard should be: if ($route === null) { throw new AppwriteException(...) }
    guard_pattern = "if ($route === null)"

    # Check if guard exists after init
    content_after_init = content[init_pos:init_pos + 4000]

    # The first occurrence after Http::init should be within the init action
    guard_pos = content_after_init.find(guard_pattern)
    assert guard_pos != -1, (
        "Null guard for $route not found in Http::init action. "
        "Expected: `if ($route === null)` check after `$route = $utopia->getRoute()`"
    )

    # Verify the exception thrown is GENERAL_ROUTE_NOT_FOUND
    guard_section = content_after_init[guard_pos:guard_pos + 200]
    assert "GENERAL_ROUTE_NOT_FOUND" in guard_section, (
        "Guard exists but doesn't throw GENERAL_ROUTE_NOT_FOUND exception. "
        f"Got: {guard_section[:100]}"
    )


def test_null_route_guard_in_shutdown_action():
    """
    F2P: Verify the shutdown action has a null guard after $route = $utopia->getRoute().
    Location: Around line 492-495 in app/controllers/shared/api.php
    """
    content = API_PHP.read_text()

    # Find the shutdown action - it appears after the first occurrence
    # Look for the second $route = $utopia->getRoute() call
    first_route_get = content.find("$route = $utopia->getRoute()")
    assert first_route_get != -1, "First $route = $utopia->getRoute() not found"

    second_route_get = content.find("$route = $utopia->getRoute()", first_route_get + 1)
    assert second_route_get != -1, (
        "Second $route = $utopia->getRoute() not found in shutdown action. "
        "The fix requires guards in BOTH the init and shutdown actions."
    )

    # Check for the null guard immediately after the second getRoute call
    content_after_second = content[second_route_get:second_route_get + 300]

    guard_pattern = "if ($route === null)"
    guard_pos = content_after_second.find(guard_pattern)
    assert guard_pos != -1, (
        "Null guard for $route not found after second $utopia->getRoute() call. "
        "Expected: `if ($route === null)` check in the shutdown action section."
    )

    # Verify the exception thrown is GENERAL_ROUTE_NOT_FOUND
    guard_section = content_after_second[guard_pos:guard_pos + 200]
    assert "GENERAL_ROUTE_NOT_FOUND" in guard_section, (
        "Guard exists but doesn't throw GENERAL_ROUTE_NOT_FOUND exception. "
        f"Got: {guard_section[:100]}"
    )


def test_no_direct_route_dereference_without_check():
    """
    P2P: Verify that $route is not directly dereferenced without null check.
    Check for patterns like $route->getLabel() or $route->getMatchedPath()
    that appear without a preceding null guard.
    """
    content = API_PHP.read_text()

    # Find all occurrences of $route dereferencing
    lines = content.split('\n')

    for i, line in enumerate(lines):
        # Skip comment lines
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('/*'):
            continue

        # Check for direct dereferencing
        if '$route->' in line and '$route = ' not in line:
            # Look backwards for a null guard in the previous 10 lines
            found_guard = False
            for j in range(max(0, i - 10), i):
                prev_line = lines[j].strip()
                if 'if ($route === null)' in prev_line or 'if ($route' in prev_line:
                    found_guard = True
                    break
                # Also check if this is inside a block that already has a guard
                if 'throw new AppwriteException' in prev_line and 'GENERAL_ROUTE_NOT_FOUND' in prev_line:
                    found_guard = True
                    break

            if not found_guard:
                # Check if this is inside the first action after the guard was added
                # by looking for the guard pattern somewhere before this line
                content_before = '\n'.join(lines[:i])
                if '$route = $utopia->getRoute()' in content_before:
                    # Find which getRoute this corresponds to
                    first_get = content_before.find("$route = $utopia->getRoute()")
                    second_get = content_before.find("$route = $utopia->getRoute()", first_get + 1)

                    current_pos = sum(len(l) + 1 for l in lines[:i])

                    if second_get != -1 and current_pos > second_get:
                        # We're after second getRoute, check for second guard
                        segment = content_before[second_get:current_pos]
                        if 'if ($route === null)' not in segment:
                            assert False, (
                                f"Line {i+1} dereferences $route without null guard: {line.strip()}. "
                                "Add `if ($route === null) { throw new AppwriteException(AppwriteException::GENERAL_ROUTE_NOT_FOUND); }` "
                                "before accessing $route methods."
                            )
                    elif first_get != -1 and current_pos > first_get:
                        # We're after first getRoute, check for first guard
                        segment = content_before[first_get:current_pos]
                        if 'if ($route === null)' not in segment:
                            assert False, (
                                f"Line {i+1} dereferences $route without null guard: {line.strip()}. "
                                "Add `if ($route === null) { throw new AppwriteException(AppwriteException::GENERAL_ROUTE_NOT_FOUND); }` "
                                "before accessing $route methods."
                            )


def test_php_syntax_valid():
    """
    P2P: Verify the PHP file has valid syntax after modifications.
    """
    result = subprocess.run(
        ["php", "-l", str(API_PHP)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, (
        f"PHP syntax error in api.php:\n{result.stderr}"
    )


def test_correct_exception_constant_used():
    """
    P2P: Verify that GENERAL_ROUTE_NOT_FOUND is used consistently in both guards.
    """
    content = API_PHP.read_text()

    # Count occurrences of the exception constant
    count = content.count("GENERAL_ROUTE_NOT_FOUND")

    # Should appear at least twice (once in each guard)
    assert count >= 2, (
        f"GENERAL_ROUTE_NOT_FOUND should appear at least twice (in both guards), "
        f"but found {count} occurrence(s)."
    )

    # Check that both guards use AppwriteException
    guards_with_exception = content.count("throw new AppwriteException(AppwriteException::GENERAL_ROUTE_NOT_FOUND)")
    assert guards_with_exception >= 2 or count >= 2, (
        "Both guards should throw `new AppwriteException(AppwriteException::GENERAL_ROUTE_NOT_FOUND)`. "
        f"Expected pattern count >= 2, but found {guards_with_exception}."
    )


def test_repo_composer_valid():
    """
    P2P: Verify composer.json is valid (pass_to_pass).
    Runs `composer validate` to ensure the composer.json and composer.lock
    files are syntactically correct and in sync.
    """
    result = subprocess.run(
        ["composer", "validate", "--no-check-publish", "--no-check-lock"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, (
        f"Composer validation failed:\n{result.stdout}\n{result.stderr}"
    )


def test_repo_php_syntax_all():
    """
    P2P: Verify key PHP files have valid syntax (pass_to_pass).
    Checks syntax on the modified file and other critical files.
    """
    php_files = [
        str(API_PHP),
        str(REPO / "app" / "init.php"),
    ]

    for php_file in php_files:
        result = subprocess.run(
            ["php", "-l", php_file],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"PHP syntax error in {php_file}:\n{result.stderr}"
        )


def test_repo_lint():
    """
    P2P: Verify the modified file passes PSR-12 linting (pass_to_pass).
    Runs Laravel Pint to check code formatting on the API controller.
    """
    result = subprocess.run(
        ["vendor/bin/pint", "--test", "--config", "pint.json", str(API_PHP)],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, (
        f"Linting failed on {API_PHP}:\n{result.stdout}\n{result.stderr}"
    )


def test_repo_static_analysis():
    """
    P2P: Verify key files pass PHPStan static analysis (pass_to_pass).
    Runs PHPStan on the modified controller file.
    """
    result = subprocess.run(
        ["./vendor/bin/phpstan", "analyse", str(API_PHP), "-c", "phpstan.neon", "--memory-limit=1G", "--no-progress"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, (
        f"Static analysis failed on {API_PHP}:\n{result.stdout}\n{result.stderr}"
    )


def test_repo_static_analysis_full():
    """
    P2P: Full PHPStan static analysis on the entire codebase (pass_to_pass).
    Runs PHPStan on all configured paths (src, app, bin, tests).
    """
    result = subprocess.run(
        ["./vendor/bin/phpstan", "analyse", "-c", "phpstan.neon", "--memory-limit=1G", "--no-progress"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, (
        f"Full static analysis failed:\n{result.stdout}\n{result.stderr}"
    )


def test_repo_unit_cors():
    """
    P2P: CORS unit tests pass (pass_to_pass).
    Tests the CORS handling logic used by API controllers.
    """
    result = subprocess.run(
        ["vendor/bin/phpunit", "tests/unit/Network/CorsTest.php", "--no-progress"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, (
        f"CORS unit tests failed:\n{result.stdout}\n{result.stderr}"
    )


def test_repo_unit_detector():
    """
    P2P: Detector unit tests pass (pass_to_pass).
    Tests the client/device detection used in API request handling.
    """
    result = subprocess.run(
        ["vendor/bin/phpunit", "tests/unit/Detector/DetectorTest.php", "--no-progress"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, (
        f"Detector unit tests failed:\n{result.stdout}\n{result.stderr}"
    )


def test_repo_unit_collections():
    """
    P2P: Collections validation unit tests pass (pass_to_pass).
    Tests collection validation logic used by the platform.
    """
    result = subprocess.run(
        ["vendor/bin/phpunit", "tests/unit/General/CollectionsTest.php", "--no-progress"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, (
        f"Collections unit tests failed:\n{result.stdout}\n{result.stderr}"
    )


def test_repo_unit_branch_domain():
    """
    P2P: Branch domain validation unit tests pass (pass_to_pass).
    Tests branch domain validation used in routing/platform logic.
    """
    result = subprocess.run(
        ["vendor/bin/phpunit", "tests/unit/Filter/BranchDomainTest.php", "--no-progress"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, (
        f"Branch domain unit tests failed:\n{result.stdout}\n{result.stderr}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
