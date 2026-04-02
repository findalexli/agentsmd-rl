"""Tests for taskforge.models."""

from taskforge.models import PRCandidate


class TestPRCandidate:
    def test_total_changes(self):
        pr = PRCandidate(repo="a/b", pr_number=1, additions=10, deletions=5)
        assert pr.total_changes == 15

    def test_repo_short(self):
        pr = PRCandidate(repo="sgl-project/sglang", pr_number=1)
        assert pr.repo_short == "sglang"

    def test_from_dict(self):
        data = {
            "repo": "owner/repo",
            "pr_number": 42,
            "title": "Fix bug",
            "changed_files": 2,
            "additions": 10,
            "deletions": 5,
            "file_paths": ["src/main.py"],
        }
        pr = PRCandidate(**data)
        assert pr.pr_number == 42
        assert pr.total_changes == 15
