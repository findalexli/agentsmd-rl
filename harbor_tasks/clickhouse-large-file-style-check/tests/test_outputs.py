"""Tests for the ClickHouse large-file style check.

The PR adds a check to ci/jobs/scripts/check_style/various_checks.sh that
flags any git-tracked file larger than 5 MB unless its path matches one of
several whitelist patterns. The same change also deletes an unused 14 MB
test fixture (tests/stress/keeper/workloads/zookeeper_log.parquet).

These tests execute the modified script — they do not grep for source
strings. Each fixture is its own isolated git repo so tests don't share
state.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO = Path("/workspace/clickhouse")
SCRIPT = REPO / "ci/jobs/scripts/check_style/various_checks.sh"
PARQUET = REPO / "tests/stress/keeper/workloads/zookeeper_log.parquet"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_script_in(repo_dir: Path) -> subprocess.CompletedProcess[str]:
    """Run the agent's modified various_checks.sh against *repo_dir*."""
    return subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=str(repo_dir),
        capture_output=True,
        text=True,
        timeout=120,
    )


def _make_git_repo(tmp_path: Path, files: dict[str, bytes]) -> Path:
    """Initialise a fresh git repo inside *tmp_path* with the given files.

    *files* maps relative path → file content (bytes). All files are added
    and committed so `git ls-files` returns them.
    """
    root = tmp_path / "repo"
    root.mkdir()
    for rel, data in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    subprocess.run(["git", "init", "-q", "-b", "master"], cwd=root, check=True, env=env)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, env=env)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=root, check=True, env=env)
    return root


def _zeros(n_bytes: int) -> bytes:
    return b"\x00" * n_bytes


# ---------------------------------------------------------------------------
# fail_to_pass tests — these MUST fail on the base script and pass on a fix.
# ---------------------------------------------------------------------------

def test_oversized_file_is_flagged(tmp_path):
    """A 6 MB non-whitelisted tracked file produces a warning naming it."""
    repo = _make_git_repo(tmp_path, {
        "data/big_blob.bin": _zeros(6 * 1024 * 1024),
        "src/main.py": b"print('hi')\n",
    })
    res = _run_script_in(repo)
    out = res.stdout + res.stderr
    assert "big_blob.bin" in out, (
        f"Expected the warning to name the oversized file. Output:\n{out!r}"
    )
    assert "is larger than 5 MB" in out, (
        f"Expected substring 'is larger than 5 MB'. Output:\n{out!r}"
    )


def test_undersized_file_is_not_flagged(tmp_path):
    """A 4 MB tracked file (under threshold) does NOT trigger the size warning."""
    repo = _make_git_repo(tmp_path, {
        "data/small_blob.bin": _zeros(4 * 1024 * 1024),
        "src/main.py": b"print('hi')\n",
    })
    res = _run_script_in(repo)
    out = res.stdout + res.stderr
    assert "small_blob.bin" not in out or "larger than 5 MB" not in out, (
        f"4 MB file should NOT produce the size warning. Output:\n{out!r}"
    )
    # Stronger: no "larger than 5 MB" warning at all.
    assert "is larger than 5 MB" not in out, (
        f"No file should trigger the size warning. Output:\n{out!r}"
    )


def test_remediation_advice_present(tmp_path):
    """The warning must include remediation guidance about not committing large files."""
    repo = _make_git_repo(tmp_path, {
        "junk/build_artifact.bin": _zeros(7 * 1024 * 1024),
    })
    res = _run_script_in(repo)
    out = res.stdout + res.stderr
    assert "Large files should not be committed to git" in out, (
        f"Warning must mention 'Large files should not be committed to git'. Output:\n{out!r}"
    )


def test_whitelisted_file_is_not_flagged(tmp_path):
    """A 6 MB file whose name matches a whitelist entry is NOT flagged."""
    repo = _make_git_repo(tmp_path, {
        # multi_column_bf.gz.parquet is whitelisted (see PR description).
        "tests/data/multi_column_bf.gz.parquet": _zeros(6 * 1024 * 1024),
        "src/main.py": b"print('hi')\n",
    })
    res = _run_script_in(repo)
    out = res.stdout + res.stderr
    assert "multi_column_bf.gz.parquet" not in out, (
        f"Whitelisted file must NOT appear in size warning. Output:\n{out!r}"
    )
    assert "is larger than 5 MB" not in out, (
        f"No size warning should be produced when the only oversized file is whitelisted. Output:\n{out!r}"
    )


def test_whitelist_includes_libcatboostmodel(tmp_path):
    """libcatboostmodel.so_x86_64 / _aarch64 are explicitly whitelisted."""
    repo = _make_git_repo(tmp_path, {
        "contrib/libcatboost/libcatboostmodel.so_x86_64": _zeros(6 * 1024 * 1024),
        "contrib/libcatboost/libcatboostmodel.so_aarch64": _zeros(7 * 1024 * 1024),
    })
    res = _run_script_in(repo)
    out = res.stdout + res.stderr
    assert "libcatboostmodel.so_x86_64" not in out
    assert "libcatboostmodel.so_aarch64" not in out
    assert "is larger than 5 MB" not in out, out


def test_multiple_oversized_files_all_reported(tmp_path):
    """When several non-whitelisted files exceed the limit, each gets a warning."""
    repo = _make_git_repo(tmp_path, {
        "a/blob1.bin": _zeros(6 * 1024 * 1024),
        "b/blob2.bin": _zeros(8 * 1024 * 1024),
        "c/blob3.bin": _zeros(7 * 1024 * 1024),
    })
    res = _run_script_in(repo)
    out = res.stdout + res.stderr
    assert "blob1.bin" in out, out
    assert "blob2.bin" in out, out
    assert "blob3.bin" in out, out
    # Three separate "larger than 5 MB" lines.
    assert out.count("is larger than 5 MB") >= 3, out


def test_threshold_is_5mb_not_smaller(tmp_path):
    """Files between 1 MB and 5 MB must not trigger the warning.

    Verifies the threshold is 5 MB (not e.g. 1 MB or 2 MB).
    """
    repo = _make_git_repo(tmp_path, {
        "size_1mb.bin": _zeros(1 * 1024 * 1024),
        "size_2mb.bin": _zeros(2 * 1024 * 1024),
        "size_4mb.bin": _zeros(4 * 1024 * 1024 + 1024),  # 4 MB + 1 KB
    })
    res = _run_script_in(repo)
    out = res.stdout + res.stderr
    assert "is larger than 5 MB" not in out, (
        f"None of these files should trigger the warning. Output:\n{out!r}"
    )


def test_check_runs_against_base_repo_and_finds_unused_parquet(tmp_path):
    """Within the workspace repo as shipped, the new check should either:
       a) flag the unused 14 MB zookeeper_log.parquet, OR
       b) the parquet has been removed from the working tree AND from git.

    Both outcomes are valid solutions to the PR's problem statement.
    """
    # Run the modified script in the actual workspace clickhouse repo.
    res = _run_script_in(REPO)
    out = res.stdout + res.stderr

    parquet_tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch",
         "tests/stress/keeper/workloads/zookeeper_log.parquet"],
        cwd=str(REPO), capture_output=True,
    ).returncode == 0

    if parquet_tracked:
        # If still tracked, the script must flag it (and call out 5 MB).
        assert "zookeeper_log.parquet" in out, (
            f"Parquet still tracked but script did not flag it. Output:\n{out!r}"
        )
        assert "is larger than 5 MB" in out, out
    else:
        # If removed: ensure no other oversized non-whitelisted file is
        # tracked, so the check passes silently.
        assert "is larger than 5 MB" not in out, (
            f"Parquet was removed but some other large file is still tracked: {out!r}"
        )


def test_warning_phrase_exact(tmp_path):
    """The exact warning string from the PR is produced verbatim, including
    the remediation tail. Tests both the size phrase AND the advice tail
    appear together for a single file."""
    repo = _make_git_repo(tmp_path, {
        "big/oversize.bin": _zeros(6 * 1024 * 1024),
    })
    res = _run_script_in(repo)
    out = res.stdout + res.stderr
    # The full sentence the PR specifies must appear.
    assert "is larger than 5 MB. Large files should not be committed to git" in out, (
        f"Expected the full sentence from the spec. Output:\n{out!r}"
    )


# ---------------------------------------------------------------------------
# pass_to_pass tests — invariants that hold both before and after the fix.
# ---------------------------------------------------------------------------

def test_script_bash_syntax_valid():
    """The modified script must still parse as bash (no syntax errors)."""
    res = subprocess.run(
        ["bash", "-n", str(SCRIPT)], capture_output=True, text=True, timeout=30,
    )
    assert res.returncode == 0, f"bash -n failed:\n{res.stderr}"


def test_existing_clickhouse_url_check_preserved():
    """The pre-existing CLICKHOUSE_URL check must not be removed by the patch.

    The line that emits 'CLICKHOUSE_URL already includes ...' is part of the
    original script and must remain after editing.
    """
    text = SCRIPT.read_text()
    assert "CLICKHOUSE_URL already includes" in text, (
        "Existing CLICKHOUSE_URL check appears to have been removed."
    )


def test_existing_query_log_check_preserved():
    """The pre-existing system.query_log/query_thread_log check must remain."""
    text = SCRIPT.read_text()
    assert "system.query_log/system.query_thread_log" in text, (
        "Pre-existing query_log check appears to have been removed."
    )


def test_script_executable(tmp_path):
    """The script file must remain runnable via bash without a syntax error."""
    assert SCRIPT.exists(), f"{SCRIPT} missing"
    # Smoke run inside a tiny fresh git repo — should not crash.
    repo = _make_git_repo(tmp_path, {"x.txt": b"hi\n"})
    res = subprocess.run(
        ["bash", str(SCRIPT)],
        cwd=str(repo), capture_output=True, text=True, timeout=120,
    )
    # Non-zero exit is fine (the script emits warnings, not errors).
    # We only care that it didn't blow up with a fatal interpreter error.
    assert "syntax error" not in (res.stderr or "").lower(), res.stderr
