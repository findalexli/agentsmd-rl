"""Behavioral tests for the packageManager monorepo fix in shadcn templates.

These tests verify actual behavior by running the scaffold tests, not by
inspecting source code strings.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO = "/workspace/ui"


def run_test(cmd, cwd=REPO, timeout=120):
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=isinstance(cmd, str)
    )
    return result


# FAIL-TO-PASS TESTS

def test_monorepo_with_bun_sets_packagemanager_version():
    result = run_test(
        [
            "pnpm", "--filter=shadcn", "test", "--",
            "src/utils/scaffold.test.ts",
            "-t", "should convert pnpm-workspace.yaml to workspaces field for non-pnpm monorepo"
        ],
        cwd=REPO,
        timeout=120
    )
    assert result.returncode == 0, (
        f"Scaffold test for bun monorepo failed. "
        f"stderr: {result.stderr[-500:]}"
    )


def test_non_monorepo_strips_packagemanager():
    result = run_test(
        [
            "pnpm", "--filter=shadcn", "test", "--",
            "src/utils/scaffold.test.ts",
            "-t", "should strip packageManager field from package.json for non-pnpm"
        ],
        cwd=REPO,
        timeout=120
    )
    assert result.returncode == 0, (
        f"Scaffold test for non-monorepo failed. "
        f"stderr: {result.stderr[-500:]}"
    )


def test_npm_monorepo_sets_packagemanager():
    result = run_test(
        [
            "pnpm", "--filter=shadcn", "test", "--",
            "src/utils/scaffold.test.ts",
            "-t", "should rewrite workspace: protocol refs to * for npm monorepo"
        ],
        cwd=REPO,
        timeout=120
    )
    assert result.returncode == 0, (
        f"Scaffold test for npm monorepo failed. "
        f"stderr: {result.stderr[-500:]}"
    )


def test_all_scaffold_tests_pass():
    result = run_test(
        ["pnpm", "--filter=shadcn", "test", "--", "src/utils/scaffold.test.ts"],
        cwd=REPO,
        timeout=180
    )
    assert result.returncode == 0, (
        f"All scaffold tests failed. "
        f"stderr: {result.stderr[-800:]}"
    )


# PASS-TO-PASS TESTS

def test_repo_typescript_compiles():
    result = run_test(
        ["npx", "tsc", "--noEmit"],
        cwd=str(Path(REPO) / "packages/shadcn"),
        timeout=120
    )
    assert result.returncode == 0, (
        f"TypeScript compilation failed. stderr: {result.stderr[-1000:]}"
    )


def test_repo_shadcn_typecheck():
    result = run_test(
        ["pnpm", "--filter=shadcn", "typecheck"],
        cwd=REPO,
        timeout=120
    )
    assert result.returncode == 0, (
        f"pnpm typecheck failed. stderr: {result.stderr[-500:]}"
    )


def test_repo_shadcn_build():
    result = run_test(
        ["pnpm", "--filter=shadcn", "build"],
        cwd=REPO,
        timeout=180
    )
    assert result.returncode == 0, (
        f"pnpm build failed. stderr: {result.stderr[-500:]}"
    )


def test_repo_shadcn_tests():
    result = run_test(
        ["pnpm", "--filter=shadcn", "test"],
        cwd=REPO,
        timeout=300
    )
    assert result.returncode == 0, (
        f"pnpm test failed. stderr: {result.stderr[-500:]}"
    )


def test_repo_lint():
    result = run_test(
        ["pnpm", "lint"],
        cwd=REPO,
        timeout=300
    )
    assert result.returncode == 0, (
        f"pnpm lint failed. stderr: {result.stderr[-500:]}"
    )