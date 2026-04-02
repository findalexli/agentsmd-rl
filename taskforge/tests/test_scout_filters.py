"""Tests for taskforge.filters — PR filtering heuristics."""

from taskforge.scout import is_good_candidate
from taskforge.models import PRCandidate


class TestIsGoodCandidate:
    def test_good_pr_passes(self, sample_pr, sample_diff):
        passed, reason = is_good_candidate(sample_pr, diff=sample_diff)
        assert passed, reason

    def test_too_large_rejected(self):
        huge = PRCandidate(repo="a/b", pr_number=1, changed_files=200,
                           additions=10000, deletions=5000,
                           file_paths=[f"src/f{i}.py" for i in range(200)])
        passed, reason = is_good_candidate(huge)
        assert not passed

    def test_too_small_rejected(self):
        tiny = PRCandidate(repo="a/b", pr_number=1, changed_files=1,
                           additions=2, deletions=1, file_paths=["src/main.py"])
        passed, reason = is_good_candidate(tiny)
        assert not passed
        assert "too small" in reason

    def test_docs_only_rejected(self, docs_only_pr):
        passed, reason = is_good_candidate(docs_only_pr)
        assert not passed
        assert "docs" in reason.lower()

    def test_deps_only_rejected(self):
        pr = PRCandidate(repo="a/b", pr_number=1, changed_files=2,
                         additions=10, deletions=5,
                         file_paths=["requirements.txt", "package-lock.json"])
        passed, reason = is_good_candidate(pr)
        assert not passed
        assert "deps" in reason

    def test_test_only_rejected(self, sample_pr, sample_test_only_diff):
        passed, reason = is_good_candidate(sample_pr, diff=sample_test_only_diff)
        assert not passed
        assert "test-only" in reason.lower()

    def test_commit_hash_in_title_rejected(self):
        pr = PRCandidate(repo="a/b", pr_number=1, changed_files=2,
                         additions=10, deletions=5,
                         title="revert " + "a" * 40,
                         file_paths=["src/main.py"])
        passed, reason = is_good_candidate(pr)
        assert not passed
        assert "commit hash" in reason

    def test_zero_files_rejected(self):
        pr = PRCandidate(repo="a/b", pr_number=1, changed_files=0,
                         additions=10, deletions=5)
        passed, _ = is_good_candidate(pr)
        assert not passed
