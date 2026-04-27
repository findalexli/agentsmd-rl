"""Tests for remix-run/remix#11019 — href benchmark uses git branch + short commit as bench name."""

import json
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/remix")
BENCH_FILE = REPO / "packages/route-pattern/bench/href.bench.ts"
EXTRACTOR = Path("/workspace/extractor")


def _extract_bench_names(cwd: Path = REPO) -> list[str]:
    """Module-load the bench file with vitest stubbed and return the captured bench names."""
    r = subprocess.run(
        [
            "node",
            "--import",
            "tsx",
            str(EXTRACTOR / "extract.mjs"),
            str(BENCH_FILE),
            str(cwd),
        ],
        cwd=EXTRACTOR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"extract.mjs failed (exit {r.returncode})\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    last = r.stdout.strip().splitlines()[-1]
    return json.loads(last)


def _git(*args: str, cwd: Path = REPO) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


# -----------------------------------------------------------------------------
# Behavioral fail-to-pass tests
# -----------------------------------------------------------------------------

def test_bench_file_loads():
    """The bench file must still be loadable as an ES module."""
    names = _extract_bench_names()
    assert isinstance(names, list)
    assert len(names) >= 1, "expected at least one bench() call to be registered"


def test_bench_name_uses_git_branch_and_short_commit():
    """Each bench() call name must be '<branch> (<short-commit>)' from the current git state.

    On the base commit, every bench is named the literal 'bench', which fails this test.
    """
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    short_commit = _git("rev-parse", "--short", "HEAD")
    expected = f"{branch} ({short_commit})"

    names = _extract_bench_names()
    assert names, "no bench names captured"
    for n in names:
        assert n == expected, (
            f"bench name {n!r} != expected {expected!r}; "
            f"the bench name must be derived from git via 'git rev-parse --abbrev-ref HEAD' "
            f"and 'git rev-parse --short HEAD'"
        )


def test_bench_name_is_not_literal_bench():
    """At base, every name is the string 'bench'. After the fix, none of them should be."""
    names = _extract_bench_names()
    assert names, "no bench names captured"
    assert all(n != "bench" for n in names), (
        f"bench names should be derived from git, not the literal string 'bench'; got {names}"
    )


def test_bench_name_matches_branch_and_short_sha_pattern():
    """Names must match '<some-branch> (<7+ hex chars>)'.

    Tests with the actual current branch and a freshly created branch to ensure the
    name truly reflects git state rather than being hardcoded.
    """
    pattern = re.compile(r"^\S.*\s\([0-9a-f]{7,}\)$")

    names = _extract_bench_names()
    for n in names:
        assert pattern.match(n), (
            f"bench name {n!r} does not match '<branch> (<short-sha>)' pattern"
        )

    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    short_commit = _git("rev-parse", "--short", "HEAD")
    for n in names:
        assert branch in n and short_commit in n, (
            f"bench name {n!r} must contain branch {branch!r} and short commit {short_commit!r}"
        )


def test_bench_name_changes_with_new_commit(tmp_path):
    """The bench name must reflect the *current* git state.

    A test that hardcodes a constant string (e.g. always returns 'main (abc1234)') would
    pass test_bench_name_is_not_literal_bench but fail this one — after creating a new
    commit, the short-commit segment of the bench name must change.
    """
    before_names = _extract_bench_names()
    before_short = _git("rev-parse", "--short", "HEAD")
    assert all(before_short in n for n in before_names)

    subprocess.check_call(
        [
            "git",
            "-c",
            "user.email=test@local",
            "-c",
            "user.name=test",
            "commit",
            "--allow-empty",
            "-m",
            "extra commit for f2p check",
        ],
        cwd=REPO,
    )

    try:
        after_short = _git("rev-parse", "--short", "HEAD")
        assert after_short != before_short, "expected a new commit SHA"

        after_names = _extract_bench_names()
        assert after_names, "no bench names captured after new commit"
        assert all(after_short in n for n in after_names), (
            f"after a new commit, every bench name should contain {after_short!r}; got {after_names}"
        )
        assert all(before_short not in n for n in after_names), (
            f"after a new commit, no bench name should still contain old short SHA "
            f"{before_short!r}; got {after_names}"
        )
    finally:
        subprocess.check_call(["git", "reset", "--hard", "HEAD~1"], cwd=REPO)


def test_bench_name_falls_back_when_git_unavailable(tmp_path):
    """When the working dir is not a git repo, getBenchName must fall back to 'bench'.

    This validates the try/catch fallback path explicitly.
    """
    non_git = tmp_path / "no-git"
    non_git.mkdir()
    names = _extract_bench_names(cwd=non_git)
    assert names, "no bench names captured when running outside a git repo"
    assert all(n == "bench" for n in names), (
        f"when git is unavailable, bench names should fall back to the literal 'bench'; got {names}"
    )
