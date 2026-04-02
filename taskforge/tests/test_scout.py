"""Tests for taskforge.scout — patch splitting and PR filtering."""

from taskforge.scout import (
    extract_new_identifiers,
    split_patch,
)


class TestSplitPatch:
    def test_splits_code_and_test(self, sample_diff):
        code, test = split_patch(sample_diff)
        assert "lib/utils.py" in code
        assert "tests/test_utils.py" in test
        assert "test_check_resolution_inf_max" not in code
        assert "check_resolution" in code

    def test_code_only_diff(self, sample_code_only_diff):
        code, test = split_patch(sample_code_only_diff)
        assert code.strip()
        assert not test.strip()

    def test_test_only_diff(self, sample_test_only_diff):
        code, test = split_patch(sample_test_only_diff)
        assert not code.strip()
        assert test.strip()

    def test_empty_diff(self):
        code, test = split_patch("")
        assert code == ""
        assert test == ""

    def test_malformed_diff(self):
        code, test = split_patch("not a valid diff")
        assert code == ""
        assert test == ""


class TestExtractNewIdentifiers:
    def test_finds_added_identifiers(self, sample_diff):
        idents = extract_new_identifiers(sample_diff)
        assert "test_check_resolution_inf_max" in idents

    def test_excludes_removed_identifiers(self):
        diff = "+new_function_name\n-old_function_name\n+shared_name\n-shared_name"
        idents = extract_new_identifiers(diff)
        assert "new_function_name" in idents
        assert "shared_name" not in idents
        assert "old_function_name" not in idents

    def test_empty_diff(self):
        assert extract_new_identifiers("") == set()
