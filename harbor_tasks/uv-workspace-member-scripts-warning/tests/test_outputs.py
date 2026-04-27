"""Behavioral tests for astral-sh/uv PR #18389.

The PR makes `uv sync` warn for *every* workspace member that declares
`[project.scripts]` without a `[build-system]` (or `tool.uv.package = true`),
and includes the package name in the warning. Before the fix, the check only
inspected the workspace root, so non-root members were skipped silently.
"""
from __future__ import annotations

import os
import subprocess
import textwrap
from pathlib import Path

import pytest


REPO = Path("/workspace/uv")
UV_BIN = REPO / "target" / "debug" / "uv"

WARNING_PREFIX = "Skipping installation of entry points (`project.scripts`)"


def _build_uv() -> None:
    """Compile the uv binary (incremental — Docker pre-warmed the cache)."""
    r = subprocess.run(
        ["cargo", "build", "-p", "uv", "--bin", "uv"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900,
    )
    if r.returncode != 0:
        raise AssertionError(
            f"cargo build failed (exit {r.returncode}):\n"
            f"--- stderr (last 2000 chars) ---\n{r.stderr[-2000:]}"
        )
    assert UV_BIN.is_file() and os.access(UV_BIN, os.X_OK), (
        f"expected built binary at {UV_BIN}"
    )


@pytest.fixture(scope="session", autouse=True)
def build_uv():
    _build_uv()


def _run_sync(workdir: Path, *extra_args: str) -> subprocess.CompletedProcess:
    """Invoke the freshly built uv binary in `workdir`. Returns CompletedProcess."""
    env = os.environ.copy()
    env["UV_NO_TELEMETRY"] = "1"
    env["UV_NO_PROGRESS"] = "1"
    env["NO_COLOR"] = "1"
    return subprocess.run(
        [str(UV_BIN), "sync", "--offline", *extra_args],
        cwd=workdir,
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )


def _write(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(content).lstrip())


# --------- Fixture builders ---------

def _workspace_member_unpackaged(root: Path) -> None:
    """Workspace root with no scripts; a single member with [project.scripts]
    and no [build-system]."""
    _write(root / "pyproject.toml", """\
        [project]
        name = "root"
        version = "0.1.0"
        requires-python = ">=3.11"
        dependencies = []

        [tool.uv.workspace]
        members = ["member"]
    """)
    _write(root / "member" / "pyproject.toml", """\
        [project]
        name = "member"
        version = "0.1.0"
        requires-python = ">=3.11"
        dependencies = []

        [project.scripts]
        member = "main:main"
    """)


def _single_project_unpackaged(root: Path) -> None:
    _write(root / "pyproject.toml", """\
        [project]
        name = "foo"
        version = "0.1.0"
        requires-python = ">=3.11"
        dependencies = []

        [project.scripts]
        foo = "main:main"
    """)


def _workspace_member_packaged(root: Path) -> None:
    """Workspace member with scripts AND tool.uv.package=true (no warning expected)."""
    _write(root / "pyproject.toml", """\
        [project]
        name = "root"
        version = "0.1.0"
        requires-python = ">=3.11"
        dependencies = []

        [tool.uv.workspace]
        members = ["member"]
    """)
    _write(root / "member" / "pyproject.toml", """\
        [project]
        name = "member"
        version = "0.1.0"
        requires-python = ">=3.11"
        dependencies = []

        [project.scripts]
        member = "main:main"

        [tool.uv]
        package = true
    """)


# ───────────────────────── fail-to-pass behavioral tests ─────────────────────────

def test_warning_fires_for_workspace_member(tmp_path: Path):
    """When a workspace member has scripts but isn't packaged, a warning must fire."""
    _workspace_member_unpackaged(tmp_path)
    r = _run_sync(tmp_path, "--all-packages")
    assert r.returncode == 0, (
        f"sync failed (exit {r.returncode}):\nstderr:\n{r.stderr}\nstdout:\n{r.stdout}"
    )
    assert WARNING_PREFIX in r.stderr, (
        "Expected the entry-points-skipped warning in stderr.\n"
        f"--- stderr ---\n{r.stderr}"
    )


def test_warning_names_workspace_member_package(tmp_path: Path):
    """Warning for a workspace member must identify the member by name."""
    _workspace_member_unpackaged(tmp_path)
    r = _run_sync(tmp_path, "--all-packages")
    assert r.returncode == 0, f"sync failed:\n{r.stderr}"
    assert "for package `member`" in r.stderr, (
        "Expected warning to identify the offending package by name "
        "(format: ``for package `<name>` ``).\n"
        f"--- stderr ---\n{r.stderr}"
    )


def test_warning_names_single_project(tmp_path: Path):
    """Even for a non-workspace project, the warning must include the package name."""
    _single_project_unpackaged(tmp_path)
    r = _run_sync(tmp_path)
    assert r.returncode == 0, f"sync failed:\n{r.stderr}"
    assert WARNING_PREFIX in r.stderr, (
        f"Expected the warning prefix in stderr.\n--- stderr ---\n{r.stderr}"
    )
    assert "for package `foo`" in r.stderr, (
        "Expected warning to identify the package by name.\n"
        f"--- stderr ---\n{r.stderr}"
    )


# ───────────────────────── pass-to-pass regression / over-fire guards ─────────────────────────

def test_no_warning_for_packaged_member(tmp_path: Path):
    """If `tool.uv.package = true` is set, no warning should fire.

    `--no-install-workspace` skips the actual build step (which would need
    network in the offline test environment), but the warning logic runs
    regardless of installation, so this still exercises the warning gate.
    """
    _workspace_member_packaged(tmp_path)
    r = _run_sync(tmp_path, "--all-packages", "--no-install-workspace")
    assert r.returncode == 0, f"sync failed:\n{r.stderr}"
    assert WARNING_PREFIX not in r.stderr, (
        "No warning should fire when the member is explicitly packaged "
        "(`tool.uv.package = true`).\n"
        f"--- stderr ---\n{r.stderr}"
    )


def test_no_warning_for_unsynced_member(tmp_path: Path):
    """A workspace member that's NOT in the sync target must not trigger a warning."""
    _workspace_member_unpackaged(tmp_path)
    # Default sync (no --all-packages, no --package): only the root is synced;
    # the member is not in the sync target, so no warning should fire for it.
    r = _run_sync(tmp_path)
    assert r.returncode == 0, f"sync failed:\n{r.stderr}"
    assert "for package `member`" not in r.stderr, (
        "Warning should not fire for a member that is not part of the sync target.\n"
        f"--- stderr ---\n{r.stderr}"
    )


def test_uv_compiles(tmp_path: Path):
    """Repo lint: cargo check must pass after the fix (compilation regression guard)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv", "--bin", "uv"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"cargo check failed (exit {r.returncode}):\n"
        f"--- stderr (last 2000 chars) ---\n{r.stderr[-2000:]}"
    )
