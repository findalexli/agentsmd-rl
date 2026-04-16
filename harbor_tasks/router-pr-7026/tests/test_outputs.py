"""
Tests for TanStack/router#7026: Remove global file route helpers

This PR removes the global pollution that was setting createFileRoute and
createLazyFileRoute on globalThis when importing the router module.

Fail-to-pass tests verify that global pollution is removed.
Pass-to-pass tests verify the packages still build and work correctly.
"""

import subprocess
import os

REPO = "/workspace/router"


def run_node_script(script: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a Node.js script and return the result."""
    return subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


class TestGlobalPollutionRemoved:
    """Fail-to-pass tests: verify global pollution is removed from router modules."""

    def test_react_router_no_global_createFileRoute(self):
        """React router should not pollute globalThis with createFileRoute (fail_to_pass).

        On the base commit, importing @tanstack/react-router sets globalThis.createFileRoute.
        After the fix, globalThis.createFileRoute should be undefined.
        """
        script = """
import './packages/react-router/dist/esm/index.js';
const result = typeof globalThis.createFileRoute;
console.log(JSON.stringify({ createFileRoute: result }));
process.exit(result === 'undefined' ? 0 : 1);
"""
        result = run_node_script(script)
        assert result.returncode == 0, (
            f"globalThis.createFileRoute should be undefined but was defined.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_react_router_no_global_createLazyFileRoute(self):
        """React router should not pollute globalThis with createLazyFileRoute (fail_to_pass).

        On the base commit, importing @tanstack/react-router sets globalThis.createLazyFileRoute.
        After the fix, globalThis.createLazyFileRoute should be undefined.
        """
        script = """
import './packages/react-router/dist/esm/index.js';
const result = typeof globalThis.createLazyFileRoute;
console.log(JSON.stringify({ createLazyFileRoute: result }));
process.exit(result === 'undefined' ? 0 : 1);
"""
        result = run_node_script(script)
        assert result.returncode == 0, (
            f"globalThis.createLazyFileRoute should be undefined but was defined.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


class TestSourceCodeChanges:
    """Fail-to-pass: Verify the source code changes are correct."""

    def test_react_router_source_no_global_assignment(self):
        """React router source should not have global assignment code (fail_to_pass)."""
        source_file = os.path.join(REPO, "packages/react-router/src/router.ts")
        with open(source_file, "r") as f:
            content = f.read()

        # The base commit has these patterns, the fix removes them
        has_global_pollution = "(globalThis as any).createFileRoute" in content
        assert not has_global_pollution, (
            "Source file should not contain global assignment for createFileRoute"
        )

    def test_solid_router_source_no_global_assignment(self):
        """Solid router source should not have global assignment code (fail_to_pass)."""
        source_file = os.path.join(REPO, "packages/solid-router/src/router.ts")
        with open(source_file, "r") as f:
            content = f.read()

        # The base commit has these patterns, the fix removes them
        has_global_pollution = "(globalThis as any).createFileRoute" in content
        assert not has_global_pollution, (
            "Source file should not contain global assignment for createFileRoute"
        )

    def test_react_router_source_no_fileRoute_import_in_router(self):
        """React router.ts should not import createFileRoute from fileRoute (fail_to_pass)."""
        source_file = os.path.join(REPO, "packages/react-router/src/router.ts")
        with open(source_file, "r") as f:
            content = f.read()

        # The fix removes the import of createFileRoute from ./fileRoute
        has_import = "import { createFileRoute, createLazyFileRoute } from './fileRoute'" in content
        assert not has_import, (
            "router.ts should not import createFileRoute from fileRoute"
        )

    def test_solid_router_source_no_fileRoute_import_in_router(self):
        """Solid router.ts should not import createFileRoute from fileRoute (fail_to_pass)."""
        source_file = os.path.join(REPO, "packages/solid-router/src/router.ts")
        with open(source_file, "r") as f:
            content = f.read()

        # The fix removes the import of createFileRoute from ./fileRoute
        has_import = "import { createFileRoute, createLazyFileRoute } from './fileRoute'" in content
        assert not has_import, (
            "router.ts should not import createFileRoute from fileRoute"
        )

    def test_react_router_no_window_assignment(self):
        """React router should not have window global assignment code (fail_to_pass)."""
        source_file = os.path.join(REPO, "packages/react-router/src/router.ts")
        with open(source_file, "r") as f:
            content = f.read()

        has_window_pollution = "(window as any).createFileRoute" in content
        assert not has_window_pollution, (
            "Source file should not contain window assignment for createFileRoute"
        )

    def test_solid_router_no_window_assignment(self):
        """Solid router should not have window global assignment code (fail_to_pass)."""
        source_file = os.path.join(REPO, "packages/solid-router/src/router.ts")
        with open(source_file, "r") as f:
            content = f.read()

        has_window_pollution = "(window as any).createFileRoute" in content
        assert not has_window_pollution, (
            "Source file should not contain window assignment for createFileRoute"
        )


class TestRouterFunctionality:
    """Pass-to-pass tests: verify router packages still work correctly."""

    def test_react_router_exports_router_class(self):
        """React router should export the Router class (pass_to_pass)."""
        script = """
import { Router } from './packages/react-router/dist/esm/index.js';
if (typeof Router !== 'function') {
    console.error('Router is not a function');
    process.exit(1);
}
console.log('Router class exported correctly');
process.exit(0);
"""
        result = run_node_script(script)
        assert result.returncode == 0, (
            f"Router class should be exported.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_react_router_createFileRoute_still_importable(self):
        """createFileRoute should still be importable from fileRoute module (pass_to_pass)."""
        script = """
import { createFileRoute } from './packages/react-router/dist/esm/fileRoute.js';
if (typeof createFileRoute !== 'function') {
    console.error('createFileRoute is not a function');
    process.exit(1);
}
console.log('createFileRoute importable from fileRoute module');
process.exit(0);
"""
        result = run_node_script(script)
        assert result.returncode == 0, (
            f"createFileRoute should be importable from fileRoute module.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_react_router_createLazyFileRoute_still_importable(self):
        """createLazyFileRoute should still be importable from fileRoute module (pass_to_pass)."""
        script = """
import { createLazyFileRoute } from './packages/react-router/dist/esm/fileRoute.js';
if (typeof createLazyFileRoute !== 'function') {
    console.error('createLazyFileRoute is not a function');
    process.exit(1);
}
console.log('createLazyFileRoute importable from fileRoute module');
process.exit(0);
"""
        result = run_node_script(script)
        assert result.returncode == 0, (
            f"createLazyFileRoute should be importable from fileRoute module.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_react_router_still_exports_core_components(self):
        """React router should still export core router components (pass_to_pass)."""
        script = """
import {
    Router,
    RouterProvider,
    useRouter,
    useNavigate
} from './packages/react-router/dist/esm/index.js';

// Check that essential exports are present and are functions
const exports = { Router, RouterProvider, useRouter, useNavigate };
const missing = Object.entries(exports)
    .filter(([name, val]) => typeof val !== 'function')
    .map(([name]) => name);

if (missing.length > 0) {
    console.error('Missing exports:', missing.join(', '));
    process.exit(1);
}
console.log('All core exports present');
process.exit(0);
"""
        result = run_node_script(script)
        assert result.returncode == 0, (
            f"Core exports should be present.\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


class TestRepoCICommands:
    """Pass-to-pass tests: run actual repo CI commands (pass_to_pass)."""

    def test_repo_react_router_eslint(self):
        """React router ESLint passes (pass_to_pass)."""
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/react-router:test:eslint"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO,
        )
        # ESLint may have warnings but should not have errors (exit 0)
        assert result.returncode == 0, (
            f"React router ESLint failed:\n{result.stderr[-2000:]}"
        )

    def test_repo_solid_router_eslint(self):
        """Solid router ESLint passes (pass_to_pass)."""
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/solid-router:test:eslint"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO,
        )
        assert result.returncode == 0, (
            f"Solid router ESLint failed:\n{result.stderr[-2000:]}"
        )

    def test_repo_react_router_fileRoute_unit(self):
        """React router fileRoute unit tests pass (pass_to_pass)."""
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/react-router:test:unit", "--run",
             "tests/fileRoute.test.ts"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO,
        )
        assert result.returncode == 0, (
            f"React router fileRoute unit tests failed:\n{result.stderr[-2000:]}"
        )

    def test_repo_react_router_build_verification(self):
        """React router build verification passes (pass_to_pass)."""
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/react-router:test:build"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO,
        )
        assert result.returncode == 0, (
            f"React router build verification failed:\n{result.stderr[-2000:]}"
        )

    def test_repo_react_router_typecheck(self):
        """React router TypeScript type check passes (pass_to_pass)."""
        result = subprocess.run(
            ["pnpm", "nx", "run", "@tanstack/react-router:test:types:ts60"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO,
        )
        assert result.returncode == 0, (
            f"React router type check failed:\n{result.stderr[-2000:]}"
        )
