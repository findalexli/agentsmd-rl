"""
Tests for the --library-push flag addition to containers registries credentials command.

This test suite validates that the PR correctly:
1. Adds LIBRARY_PUSH to the ImageRegistryPermissions enum
2. Adds the --library-push CLI argument with correct type and description
3. Updates the validation logic to require at least one of --pull, --push, or --library-push
4. Passes the library_push permission to the API when the flag is used
5. Runs the existing wrangler test suite for containers registries
"""

import subprocess
import os
import re

REPO = "/workspace/workers-sdk"
WRANGLER_SRC = f"{REPO}/packages/wrangler/src"
CONTAINERS_SHARED = f"{REPO}/packages/containers-shared/src"


def test_library_push_enum_exists():
    """
    Fail-to-pass: ImageRegistryPermissions enum must include LIBRARY_PUSH.

    This test checks that the enum value was added to represent the library_push
    permission that will be sent to the API.
    """
    enum_file = f"{CONTAINERS_SHARED}/client/models/ImageRegistryPermissions.ts"
    with open(enum_file, "r") as f:
        content = f.read()

    # Check for the new enum member
    assert "LIBRARY_PUSH" in content, "LIBRARY_PUSH enum value not found"
    assert 'library_push' in content, "library_push string value not found"


def test_cli_argument_definition():
    """
    Fail-to-pass: CLI must define the --library-push argument.

    Verifies the argument is defined with correct type, description, and hidden flag.
    """
    registries_file = f"{WRANGLER_SRC}/containers/registries.ts"
    with open(registries_file, "r") as f:
        content = f.read()

    # Check for the argument definition
    assert '"library-push"' in content, "library-push argument not defined"
    assert "type: \"boolean\"" in content or 'type: "boolean"' in content, "Argument type not boolean"

    # Check for description mentioning library namespace
    assert "library namespace" in content.lower(), "Description should mention library namespace"


def test_function_parameter():
    """
    Fail-to-pass: registryCredentialsCommand must accept libraryPush parameter.

    The function signature needs to be updated to receive the libraryPush option.
    """
    registries_file = f"{WRANGLER_SRC}/containers/registries.ts"
    with open(registries_file, "r") as f:
        content = f.read()

    # Check for libraryPush parameter in function signature
    assert "libraryPush?:" in content or "libraryPush?: boolean" in content, \
        "libraryPush parameter not in function signature"


def test_validation_logic():
    """
    Fail-to-pass: Validation must accept --library-push as a valid option.

    The error message should only mention --push and --pull, and the validation
    must check all three flags.
    """
    registries_file = f"{WRANGLER_SRC}/containers/registries.ts"
    with open(registries_file, "r") as f:
        content = f.read()

    # Find the validation section - it should check all three flags
    # The condition should be: if (!pull && !push && !libraryPush)
    validation_pattern = r"if\s*\(\s*![^}]+pull\s*&&\s*![^}]+push\s*&&\s*![^}]+libraryPush"
    assert re.search(validation_pattern, content, re.DOTALL), \
        "Validation logic must check all three flags (pull, push, libraryPush)"


def test_permission_passed_to_api():
    """
    Fail-to-pass: library_push must be included in permissions array when flag is set.

    When libraryPush is true, the string "library_push" should be added to the
    permissions array sent to the API.
    """
    registries_file = f"{WRANGLER_SRC}/containers/registries.ts"
    with open(registries_file, "r") as f:
        content = f.read()

    # Check that library_push is conditionally added to permissions
    assert '...(credentialsArgs.libraryPush ? ["library_push"] : [])' in content, \
        "library_push permission not conditionally added to API call"


def test_wrangler_unit_tests():
    """
    Pass-to-pass: The wrangler containers registries tests should pass.

    Runs the existing unit test suite for the containers registries command.
    This ensures the change doesn't break existing functionality.
    """
    result = subprocess.run(
        ["pnpm", "run", "test:ci", "--filter", "wrangler", "--", "containers/registries"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )

    # Check test output
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-2000:]}"


def test_enum_matches_api_values():
    """
    Additional check: Verify enum values are lowercase strings as expected.

    The enum values should match what the API expects (library_push, not LIBRARY_PUSH).
    """
    enum_file = f"{CONTAINERS_SHARED}/client/models/ImageRegistryPermissions.ts"
    with open(enum_file, "r") as f:
        content = f.read()

    # Extract enum members and their values
    assert 'LIBRARY_PUSH = "library_push"' in content, \
        "LIBRARY_PUSH must equal 'library_push' string value"


def test_typescript_compiles():
    """
    Pass-to-pass: TypeScript should compile without errors.

    Ensures the code changes are syntactically valid TypeScript.
    """
    # Check wrangler package compiles
    result = subprocess.run(
        ["pnpm", "run", "check:type", "--filter", "wrangler"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stderr[-1000:]}"


def test_modified_files_format():
    """
    Pass-to-pass: Modified files must follow the repo's formatting standards.

    Runs oxfmt (the repo's formatter) on the files modified by the PR.
    """
    result = subprocess.run(
        [
            "pnpm", "exec", "oxfmt", "--check",
            "packages/wrangler/src/containers/registries.ts",
            "packages/containers-shared/src/client/models/ImageRegistryPermissions.ts",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, f"Format check failed:\n{result.stderr[-500:]}"


def test_modified_files_lint():
    """
    Pass-to-pass: Modified files must pass the repo's linter.

    Runs oxlint (the repo's linter) on the files modified by the PR.
    """
    result = subprocess.run(
        [
            "pnpm", "exec", "oxlint", "--deny-warnings", "--type-aware",
            "packages/wrangler/src/containers/registries.ts",
            "packages/containers-shared/src/client/models/ImageRegistryPermissions.ts",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, f"Lint check failed:\n{result.stderr[-500:]}"
