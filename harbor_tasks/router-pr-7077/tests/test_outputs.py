"""
Tests for TanStack Router notFound() error preservation fix.

The fix ensures that notFound() errors thrown from route components preserve
the routeId through framework error boundaries, so the correct route-specific
notFoundComponent is rendered.
"""
import subprocess
import os
import sys

REPO = "/workspace/router"


class TestReactRouterNotFoundFix:
    """Tests for the React router notFound preservation fix."""

    def test_react_match_preserves_routeid_on_notfound_error(self):
        """
        Verify that the React Match component assigns routeId to notFound errors.
        (fail_to_pass)

        The fix adds: error.routeId ??= matchState.routeId as any
        This ensures component-thrown notFound() errors get the current route's ID.
        """
        match_file = os.path.join(REPO, "packages/react-router/src/Match.tsx")
        with open(match_file, "r") as f:
            content = f.read()

        # The fix should contain the routeId assignment pattern
        # Check for the specific fix pattern in onCatch handler
        assert "error.routeId ??= matchState.routeId" in content, (
            "React Match.tsx must assign routeId to notFound errors in onCatch handler"
        )

    def test_react_notfound_error_handling_structure(self):
        """
        Verify the React Match component has proper notFound error handling structure.
        (fail_to_pass)

        The fix changes from simple rethrow to routeId-annotated rethrow.
        """
        match_file = os.path.join(REPO, "packages/react-router/src/Match.tsx")
        with open(match_file, "r") as f:
            content = f.read()

        # The OLD broken code had: if (isNotFound(error)) throw error
        # The NEW fixed code has a block that assigns routeId before throwing

        # Should NOT have the simple one-liner that doesn't preserve routeId
        lines = content.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Check for the broken pattern (single line throw without routeId assignment)
            if stripped == "if (isNotFound(error)) throw error":
                raise AssertionError(
                    f"Found unpatched notFound handling at line {i+1}: "
                    "should assign routeId before throwing"
                )


class TestSolidRouterNotFoundFix:
    """Tests for the Solid router notFound preservation fix."""

    def test_solid_has_getnotfound_helper(self):
        """
        Verify Solid router exports getNotFound helper function.
        (fail_to_pass)

        Solid wraps thrown values in Error objects with the original on 'cause'.
        getNotFound() unwraps these to get the actual notFound error.
        """
        not_found_file = os.path.join(REPO, "packages/solid-router/src/not-found.tsx")
        with open(not_found_file, "r") as f:
            content = f.read()

        # The fix adds a getNotFound function that handles Solid's error wrapping
        assert "export function getNotFound(" in content, (
            "Solid not-found.tsx must export getNotFound helper function"
        )

        # Verify it handles the .cause unwrapping
        assert ".cause" in content, (
            "getNotFound must handle Solid's error wrapping via .cause property"
        )

    def test_solid_match_uses_getnotfound(self):
        """
        Verify Solid Match component uses getNotFound for proper error unwrapping.
        (fail_to_pass)
        """
        match_file = os.path.join(REPO, "packages/solid-router/src/Match.tsx")
        with open(match_file, "r") as f:
            content = f.read()

        # Should import getNotFound from not-found module
        assert "getNotFound" in content, (
            "Solid Match.tsx must use getNotFound for error unwrapping"
        )

        # Should use it for notFound error handling
        assert "const notFoundError = getNotFound(error)" in content, (
            "Solid Match.tsx must call getNotFound to unwrap notFound errors"
        )


class TestVueRouterNotFoundFix:
    """Tests for the Vue router notFound preservation fix."""

    def test_vue_match_preserves_routeid_on_notfound_error(self):
        """
        Verify that the Vue Match component assigns routeId to notFound errors.
        (fail_to_pass)
        """
        match_file = os.path.join(REPO, "packages/vue-router/src/Match.tsx")
        with open(match_file, "r") as f:
            content = f.read()

        # The fix should contain the routeId assignment pattern
        # Vue uses matchData.value?.routeId due to Vue's reactivity
        assert "routeId ??=" in content and "matchData.value" in content, (
            "Vue Match.tsx must assign routeId to notFound errors"
        )

    def test_vue_notfound_error_handling_structure(self):
        """
        Verify the Vue Match component has proper notFound error handling structure.
        (fail_to_pass)
        """
        match_file = os.path.join(REPO, "packages/vue-router/src/Match.tsx")
        with open(match_file, "r") as f:
            content = f.read()

        # Should NOT have the simple one-liner
        lines = content.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == "if (isNotFound(error)) throw error":
                raise AssertionError(
                    f"Found unpatched notFound handling at line {i+1}: "
                    "should assign routeId before throwing"
                )


class TestPassToPass:
    """Pass-to-pass tests to ensure the fix doesn't break existing functionality."""

    def test_typescript_compilation(self):
        """
        Verify TypeScript compilation passes.
        (pass_to_pass)
        """
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/react-router:test:types"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
        )
        assert result.returncode == 0, (
            f"TypeScript compilation failed:\n{result.stderr[-2000:]}"
        )

    def test_eslint_passes(self):
        """
        Verify ESLint passes for react-router.
        (pass_to_pass)
        """
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/react-router:test:eslint"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
        )
        assert result.returncode == 0, (
            f"ESLint failed:\n{result.stderr[-2000:]}"
        )

    def test_react_router_unit_tests(self):
        """
        Verify React router unit tests pass.
        (pass_to_pass)
        """
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/react-router:test:unit"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=600,
            env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
        )
        assert result.returncode == 0, (
            f"React router unit tests failed:\n{result.stderr[-2000:]}"
        )

    def test_solid_router_eslint_passes(self):
        """
        Verify ESLint passes for solid-router.
        (pass_to_pass)
        """
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/solid-router:test:eslint"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
        )
        assert result.returncode == 0, (
            f"Solid router ESLint failed:\n{result.stderr[-2000:]}"
        )

    def test_solid_router_typescript_compilation(self):
        """
        Verify TypeScript compilation passes for solid-router.
        (pass_to_pass)
        """
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/solid-router:test:types"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
        )
        assert result.returncode == 0, (
            f"Solid router TypeScript compilation failed:\n{result.stderr[-2000:]}"
        )

    def test_solid_router_unit_tests(self):
        """
        Verify Solid router unit tests pass.
        (pass_to_pass)
        """
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/solid-router:test:unit"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=600,
            env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
        )
        assert result.returncode == 0, (
            f"Solid router unit tests failed:\n{result.stderr[-2000:]}"
        )

    def test_vue_router_eslint_passes(self):
        """
        Verify ESLint passes for vue-router.
        (pass_to_pass)
        """
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/vue-router:test:eslint"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
        )
        assert result.returncode == 0, (
            f"Vue router ESLint failed:\n{result.stderr[-2000:]}"
        )

    def test_vue_router_typescript_compilation(self):
        """
        Verify TypeScript compilation passes for vue-router.
        (pass_to_pass)
        """
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/vue-router:test:types"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
        )
        assert result.returncode == 0, (
            f"Vue router TypeScript compilation failed:\n{result.stderr[-2000:]}"
        )

    def test_vue_router_unit_tests(self):
        """
        Verify Vue router unit tests pass.
        (pass_to_pass)
        """
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/vue-router:test:unit"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=600,
            env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
        )
        assert result.returncode == 0, (
            f"Vue router unit tests failed:\n{result.stderr[-2000:]}"
        )


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
