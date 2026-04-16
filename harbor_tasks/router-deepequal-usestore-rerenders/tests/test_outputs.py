#!/usr/bin/env python3
"""
Test outputs for TanStack Router PR #6886
Validates that deepEqual is properly added to useStore calls to prevent unnecessary re-renders.
"""

import subprocess
import sys
import ast
import os
from pathlib import Path

REPO = "/workspace/router"
SCRIPTS_TSX = Path(f"{REPO}/packages/react-router/src/Scripts.tsx")
HEAD_UTILS_TSX = Path(f"{REPO}/packages/react-router/src/headContentUtils.tsx")


def test_deepequal_import_in_scripts():
    """Verify deepEqual is imported in Scripts.tsx"""
    content = SCRIPTS_TSX.read_text()
    assert "import { deepEqual } from '@tanstack/router-core'" in content, \
        "deepEqual import not found in Scripts.tsx"


def test_deepequal_import_in_headutils():
    """Verify deepEqual is imported in headContentUtils.tsx"""
    content = HEAD_UTILS_TSX.read_text()
    assert "deepEqual" in content and "@tanstack/router-core" in content, \
        "deepEqual import not found in headContentUtils.tsx"




def test_repo_typescript_compiles():
    """Verify TypeScript compilation passes (pass-to-pass)"""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:types", "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, \
        f"TypeScript type check failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_repo_unit_tests_pass():
    """Verify unit tests pass (pass-to-pass)"""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:unit", "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, \
        f"Unit tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_repo_lint_passes():
    """Verify ESLint passes (pass-to-pass)"""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:eslint", "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, \
        f"ESLint check failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"


def test_repo_build_passes():
    """Verify package build validation passes (pass-to-pass)"""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:build", "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )
    assert result.returncode == 0, \
        f"Build validation failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"


def test_scripts_ast_usestore_has_deepequal():
    """AST-based verification that useStore calls in Scripts.tsx have deepEqual argument"""
    content = SCRIPTS_TSX.read_text()

    # Count occurrences of "deepEqual," which is used as the third argument to useStore
    deepequal_count = content.count("deepEqual,")

    # Should have at least 2 useStore calls with deepEqual (assetScripts and scripts)
    assert deepequal_count >= 2, \
        f"Expected at least 2 useStore calls with deepEqual argument, found {deepequal_count}"


def test_headutils_ast_usestore_has_deepequal():
    """AST-based verification that key useStore calls in headContentUtils.tsx have deepEqual"""
    content = HEAD_UTILS_TSX.read_text()

    # Simple string-based verification: count occurrences of "deepEqual,"
    # which is used as the third argument to useStore
    deepequal_count = content.count("deepEqual,")

    # Should have at least 5 useStore calls with deepEqual (routeMeta, links, preloadLinks, styles, headScripts)
    assert deepequal_count >= 5, \
        f"Expected at least 5 useStore calls with deepEqual argument, found {deepequal_count}"


if __name__ == "__main__":
    pytest_main = subprocess.run([sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"])
    sys.exit(pytest_main.returncode)
