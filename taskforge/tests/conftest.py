"""Shared fixtures for taskforge tests."""

from __future__ import annotations

import pytest

from taskforge.models import PRCandidate


# Valid unified diffs with correct hunk headers.
# Hunk header: @@ -old_start,old_count +new_start,new_count @@
# old_count = context lines + removed lines
# new_count = context lines + added lines
SAMPLE_DIFF = (
    "diff --git a/lib/utils.py b/lib/utils.py\n"
    "--- a/lib/utils.py\n"
    "+++ b/lib/utils.py\n"
    "@@ -10,4 +10,5 @@\n"       # old=4 (3 ctx + 1 del), new=5 (3 ctx + 2 add)
    " def check_resolution(width, height):\n"
    "     if width < 0:\n"
    "-        return False\n"
    "+        if width > 100:\n"
    "+            return False\n"
    "     return True\n"
    "diff --git a/tests/test_utils.py b/tests/test_utils.py\n"
    "--- a/tests/test_utils.py\n"
    "+++ b/tests/test_utils.py\n"
    "@@ -1,2 +1,5 @@\n"       # old=2 (2 ctx), new=5 (2 ctx + 3 add)
    " def test_basic():\n"
    "     assert True\n"
    "+\n"
    "+def test_check_resolution_inf_max():\n"
    "+    assert check_resolution(1024, 768) == True\n"
)

SAMPLE_CODE_ONLY_DIFF = (
    "diff --git a/lib/utils.py b/lib/utils.py\n"
    "--- a/lib/utils.py\n"
    "+++ b/lib/utils.py\n"
    "@@ -10,4 +10,6 @@\n"       # old=4 (4 ctx), new=6 (4 ctx + 2 add)
    " def check_resolution(width, height):\n"
    "     if width < 0:\n"
    "         return False\n"
    "+    if height < 0:\n"
    "+        return False\n"
    "     return True\n"
)

SAMPLE_TEST_ONLY_DIFF = (
    "diff --git a/tests/test_utils.py b/tests/test_utils.py\n"
    "--- a/tests/test_utils.py\n"
    "+++ b/tests/test_utils.py\n"
    "@@ -1,2 +1,5 @@\n"       # old=2 (2 ctx), new=5 (2 ctx + 3 add)
    " def test_basic():\n"
    "     assert True\n"
    "+\n"
    "+def test_new():\n"
    "+    assert 1 + 1 == 2\n"
)


@pytest.fixture
def sample_diff():
    return SAMPLE_DIFF


@pytest.fixture
def sample_code_only_diff():
    return SAMPLE_CODE_ONLY_DIFF


@pytest.fixture
def sample_test_only_diff():
    return SAMPLE_TEST_ONLY_DIFF


@pytest.fixture
def sample_pr():
    return PRCandidate(
        repo="example/repo",
        pr_number=42,
        title="Fix resolution check with infinite max",
        changed_files=2,
        additions=5,
        deletions=2,
        merged_at="2026-03-15T10:00:00Z",
        merge_sha="abc123def456",
        file_paths=["lib/utils.py", "tests/test_utils.py"],
    )


@pytest.fixture
def large_pr():
    return PRCandidate(
        repo="example/repo",
        pr_number=99,
        title="Major refactor",
        changed_files=12,
        additions=500,
        deletions=300,
        file_paths=[f"src/file{i}.py" for i in range(12)],
    )


@pytest.fixture
def docs_only_pr():
    return PRCandidate(
        repo="example/repo",
        pr_number=50,
        title="Update docs",
        changed_files=3,
        additions=20,
        deletions=5,
        file_paths=["docs/guide.md", "README.md", "CHANGELOG.rst"],
    )
