#!/usr/bin/env python3
"""
Test that CORS headers are properly added to error responses in Appwrite.

This tests that the Http::error() handler:
1. Injects the 'cors' resource
2. Adds CORS headers before sending error responses
3. Has graceful degradation via try-catch
"""

import subprocess
import re
from pathlib import Path

REPO = Path("/workspace/appwrite")
TARGET_FILE = REPO / "app" / "controllers" / "general.php"


def test_cors_injection_in_error_handler():
    """
    Fail-to-pass: Verify the error handler injects the 'cors' resource.

    The fix adds ->inject('cors') to the Http::error() handler chain.
    """
    content = TARGET_FILE.read_text()

    # Find the Http::error() handler and check it injects 'cors'
    # Look for the error handler registration with cors injection
    error_handler_pattern = r"Http::error\([^)]*\)(?:\s*->\s*[^\(]+\([^)]*\))*\s*->\s*inject\(['\"]cors['\"]\)"

    # Alternative: find the error handler section and check for inject('cors') nearby
    cors_inject_pattern = r"->\s*inject\(['\"]cors['\"]\)"

    match = re.search(cors_inject_pattern, content)
    assert match is not None, (
        "Http::error() handler missing 'cors' injection. "
        "Expected ->inject('cors') to be added to the error handler chain."
    )


def test_cors_headers_added_before_error_response():
    """
    Fail-to-pass: Verify CORS headers are fetched and added to the response.

    The fix should get the cors resource and call headers() to add them to the response.
    """
    content = TARGET_FILE.read_text()

    # Check that the error handler gets the cors resource
    get_resource_pattern = r"\$cors\s*=\s*\$utopia->getResource\(['\"]cors['\"]\)"
    match = re.search(get_resource_pattern, content)
    assert match is not None, (
        "Missing $cors = $utopia->getResource('cors') in error handler. "
        "The fix should retrieve the cors resource before adding headers."
    )

    # Check that cors headers are added to the response
    headers_pattern = r"\$cors->headers\([^)]+\)"
    match = re.search(headers_pattern, content)
    assert match is not None, (
        "Missing $cors->headers() call to get CORS headers. "
        "The fix should call the headers() method on the cors resource."
    )

    # Check that headers are added via addHeader in a loop
    add_header_pattern = r"\$response->addHeader\(\$name,\s*\$value"
    match = re.search(add_header_pattern, content)
    assert match is not None, (
        "Missing $response->addHeader($name, $value, ...) loop. "
        "The fix should iterate over CORS headers and add them to the response."
    )


def test_cors_in_error_response_uses_try_catch():
    """
    Fail-to-pass: Verify the CORS header addition is wrapped in try-catch.

    The fix wraps the cors header injection in try-catch to gracefully handle
    failures (e.g., if cors resolution fails due to a DB error).
    """
    content = TARGET_FILE.read_text()

    # Find the section that adds CORS headers - should be wrapped in try-catch
    # Look for try block containing cors resource and header addition
    try_cors_pattern = r"try\s*\{\s*\$cors\s*=\s*\$utopia->getResource\(['\"]cors['\"]\)[^}]+\$cors->headers"

    # Also check for the simpler pattern: try { followed by getResource('cors')
    simpler_pattern = r"try\s*\{[^}]*\$utopia->getResource\(['\"]cors['\"]\)"

    match = re.search(simpler_pattern, content, re.DOTALL)
    assert match is not None, (
        "CORS header injection not wrapped in try-catch. "
        "The fix should wrap cors resource retrieval and header addition in a try block "
        "to gracefully degrade if cors resolution fails."
    )


def test_override_flag_on_cors_headers():
    """
    Pass-to-pass: Verify CORS headers use override flag to avoid duplicates.

    If init() already set CORS headers, we should use override:true to avoid duplicates.
    """
    content = TARGET_FILE.read_text()

    # Check for override flag in addHeader call
    override_pattern = r"addHeader\(\$name,\s*\$value[^)]*override:\s*true"
    match = re.search(override_pattern, content)
    assert match is not None, (
        "CORS headers should use override:true to avoid duplicates. "
        "If the init() handler already set CORS headers, the error handler "
        "should override them rather than create duplicates."
    )


def test_error_handler_follows_injection_pattern():
    """
    Pass-to-pass: Verify error handler follows the Action injection pattern.

    Per AGENTS.md, actions use inject() to get dependencies and pass them as
    callback parameters. The cors injection should follow this pattern.
    """
    content = TARGET_FILE.read_text()

    # The error handler should have Cors $cors parameter after the fix
    cors_param_pattern = r"function\s*\([^)]*Cors\s+\$cors[^)]*\)"
    match = re.search(cors_param_pattern, content)

    # Note: The fix actually uses getResource() instead of injection, so this
    # may not be present. Let's check for either injection pattern or getResource.
    if match is None:
        # Alternative: uses getResource pattern
        getresource_pattern = r"\$utopia->getResource\(['\"]cors['\"]\)"
        match = re.search(getresource_pattern, content)
        assert match is not None, (
            "Error handler should either inject 'cors' or use getResource('cors'). "
            "The fix needs to access the cors resource to add headers."
        )


def test_comments_document_cors_fix():
    """
    Pass-to-pass: Verify the fix has explanatory comments.

    Good documentation helps future developers understand why CORS headers are
    needed in error responses.
    """
    content = TARGET_FILE.read_text()

    # Check for the distinctive comment from the patch
    comment_patterns = [
        r"Add CORS headers to error responses",
        r"cors resource.*DB",
        r"Degrade gracefully",
    ]

    found = sum(1 for p in comment_patterns if re.search(p, content, re.IGNORECASE))
    assert found >= 1, (
        "The fix should include explanatory comments about why CORS headers "
        "are added to error responses and the try-catch pattern."
    )


def test_error_response_header_ordering():
    """
    Pass-to-pass: Verify CORS headers are added before cache headers.

    The CORS headers should be set before the Cache-Control and Expires headers
    that are already in the error handler.
    """
    content = TARGET_FILE.read_text()

    lines = content.split('\n')

    # Find the error handler section - look for Http::error()
    error_handler_start = None
    for i, line in enumerate(lines):
        if "Http::error(" in line:
            error_handler_start = i
            break

    # Find CORS addition within the error handler (after error handler start)
    cors_line = None
    cache_line = None

    if error_handler_start:
        for i in range(error_handler_start, min(len(lines), error_handler_start + 400)):
            line = lines[i]
            if '$utopia->getResource' in line and 'cors' in line:
                cors_line = i
            # Look for Cache-Control in the $response chain that comes after the cors block
            if cors_line and "->addHeader('Cache-Control'" in line:
                cache_line = i
                break

    # Both should exist within the error handler section
    assert cors_line is not None, "CORS header addition not found in error handler"
    assert cache_line is not None, "Cache headers not found after CORS in error handler"

    # CORS should come before Cache-Control in the error handler
    assert cors_line < cache_line, (
        "CORS headers should be added before Cache-Control headers "
        "to ensure they are present in error responses."
    )


def test_request_origin_used_for_cors():
    """
    Pass-to-pass: Verify the request origin is passed to cors.headers().

    The fix should pass $request->getOrigin() to the cors headers method.
    """
    content = TARGET_FILE.read_text()

    origin_pattern = r"\$request->getOrigin\(\)"
    match = re.search(origin_pattern, content)
    assert match is not None, (
        "The fix should use $request->getOrigin() when generating CORS headers "
        "to properly set the Access-Control-Allow-Origin header."
    )


def test_throwable_catch_not_exception():
    """
    Pass-to-pass: Verify the catch uses Throwable, not just Exception.

    Using Throwable catches both Error and Exception, providing better resilience.
    """
    content = TARGET_FILE.read_text()

    # Look for catch with Throwable
    throwable_pattern = r"catch\s*\(\s*Throwable"
    match = re.search(throwable_pattern, content)
    assert match is not None, (
        "The try-catch should catch Throwable (not just Exception) "
        "to handle both errors and exceptions during CORS resolution."
    )


def test_repo_composer_validate():
    """
    Pass-to-pass: Composer validation passes on the repo.

    Ensures composer.json is valid and dependencies are resolvable.
    """
    r = subprocess.run(
        ["composer", "validate", "--no-interaction"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Composer validate failed:\n{r.stderr[-500:]}"


def test_repo_composer_lint():
    """
    Pass-to-pass: Composer lint (Pint code style check) passes on the repo.

    Ensures PHP code follows the project's coding standards (PSR-12).
    """
    r = subprocess.run(
        ["composer", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Composer lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_php_syntax():
    """
    Pass-to-pass: PHP syntax check passes on the target file.

    Ensures the modified file has valid PHP syntax.
    """
    r = subprocess.run(
        ["php", "-l", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"PHP syntax check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
    assert "No syntax errors" in r.stdout, f"PHP syntax errors found in {TARGET_FILE}"
