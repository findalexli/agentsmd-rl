"""Test module for verifying benchmark import path fixes.

This module tests that the benchmark file has correct import paths
by running vitest and checking for import resolution errors.
"""

import subprocess
import re
import os
import pytest

REPO = "/workspace/oxc"
NAPI_PARSER_DIR = os.path.join(REPO, "napi/parser")


def test_vitest_can_resolve_imports():
    """Verify vitest can resolve all imports in bench.bench.js.
    
    This is the key behavioral test. When import paths are wrong (NOP),
    vitest fails with 'Cannot find module ./generated/...'. When paths
    are correct (Gold), vitest can resolve imports but may fail on other
    issues (like missing fixture files).
    
    The test checks that imports from './generated/' are NOT present,
    which indicates the NOP bug where paths are missing the src-js/ prefix.
    """
    result = subprocess.run(
        ["pnpm", "vitest", "bench", "bench.bench.js"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=NAPI_PARSER_DIR
    )

    output = result.stdout + result.stderr

    # NOP bug: imports use ./generated/ instead of ./src-js/generated/
    # This causes "Cannot find module './generated/...'" errors
    has_nop_path_error = (
        "Cannot find module './generated/constants.js'" in output or
        "Cannot find module './generated/deserialize/js.js'" in output or
        "Cannot find module './generated/deserialize/ts.js'" in output or
        "Cannot find module './generated/lazy/walk.js'" in output
    )

    assert not has_nop_path_error, \
        f"NOP bug detected: imports use wrong path (./generated/ instead of ./src-js/generated/): {output[:800]}"


def test_target_files_exist():
    """Verify that the target import files actually exist (pass-to-pass).
    """
    required_files = [
        "napi/parser/src-js/generated/constants.js",
        "napi/parser/src-js/generated/deserialize/js.js",
        "napi/parser/src-js/generated/deserialize/ts.js",
        "napi/parser/src-js/generated/lazy/walk.js",
        "napi/parser/src-js/index.js",
    ]

    for rel_path in required_files:
        full_path = os.path.join(REPO, rel_path)
        assert os.path.exists(full_path), f"Required file should exist: {rel_path}"


def test_repo_unit_tests():
    """Repo's unit tests for napi/parser pass (pass_to_pass).
    """
    r = subprocess.run(
        ["pnpm", "run", "test-node"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=NAPI_PARSER_DIR,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_lint():
    """Repo's linter passes on napi/parser source files (pass_to_pass).
    """
    r = subprocess.run(
        ["pnpm", "exec", "oxlint", "--deny-warnings", "test/", "bench.bench.js"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=NAPI_PARSER_DIR,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"
