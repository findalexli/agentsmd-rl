"""
Task: sglang-ngram-external-sam-benchmark
Repo: sgl-project/sglang @ 73fc87a74f5e6e2974403d95292dca9bb387b288
PR:   22199

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This PR refactors the ngram speculative decoding tests:
1. Removes redundant TestNgramExternalSamSmoke class
2. Adds test_output_as_corpus_boosts_accept_length to TestNgramSpeculativeDecodingFlashinfer
3. Updates get_server_args to include --speculative-ngram-external-sam-budget 8
4. Cleans up unused imports and helpers
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/sglang"
TEST_FILE = f"{REPO}/test/registered/spec/test_ngram_speculative_decoding.py"


def _get_test_file_content():
    """Helper to read and cache test file content."""
    return Path(TEST_FILE).read_text()


def _parse_test_file():
    """Helper to parse test file AST."""
    return ast.parse(_get_test_file_content())


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

def test_syntax_check():
    """Modified test file must parse without errors."""
    src = Path(TEST_FILE).read_text()
    try:
        ast.parse(src)
    except SyntaxError as e:
        raise AssertionError(f"Syntax error in test file: {e}")


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core structural tests
# -----------------------------------------------------------------------------

def test_new_test_method_added():
    """
    TestNgramSpeculativeDecodingFlashinfer must have the new
    test_output_as_corpus_boosts_accept_length method.
    """
    tree = _parse_test_file()

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name == "TestNgramSpeculativeDecodingFlashinfer":
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                assert "test_output_as_corpus_boosts_accept_length" in methods, \
                    "Missing test_output_as_corpus_boosts_accept_length method"
                return

    raise AssertionError("TestNgramSpeculativeDecodingFlashinfer class not found")


def test_sam_budget_flag_added():
    """
    TestNgramSpeculativeDecodingFlashinfer.get_server_args must include
    --speculative-ngram-external-sam-budget 8
    """
    tree = _parse_test_file()

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestNgramSpeculativeDecodingFlashinfer":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "get_server_args":
                    src = ast.unparse(item)
                    assert "speculative-ngram-external-sam-budget" in src, \
                        "Missing --speculative-ngram-external-sam-budget flag"
                    assert '"8"' in src or "'8'" in src, \
                        "SAM budget should be set to 8"
                    return
            raise AssertionError("get_server_args method not found in TestNgramSpeculativeDecodingFlashinfer")

    raise AssertionError("TestNgramSpeculativeDecodingFlashinfer class not found")


def test_old_smoke_class_removed():
    """TestNgramExternalSamSmoke class must be removed."""
    tree = _parse_test_file()

    class_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    assert "TestNgramExternalSamSmoke" not in class_names, \
        "TestNgramExternalSamSmoke class should have been removed"


def test_unused_imports_removed():
    """Unused imports (json, os, tempfile) should be removed from imports."""
    tree = _parse_test_file()

    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for alias in node.names:
                    imported_names.add(alias.name)

    # These were removed in the PR
    assert "json" not in imported_names, "json import should be removed"
    assert "os" not in imported_names, "os import should be removed"
    assert "tempfile" not in imported_names, "tempfile import should be removed"


def test_unused_helpers_removed():
    """
    Helper functions _safe_remove, _safe_kill_process, and constant
    EXTERNAL_SAM_CORPUS_RECORDS should be removed.
    """
    tree = _parse_test_file()

    # Check for function definitions
    func_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    assert "_safe_remove" not in func_names, "_safe_remove function should be removed"
    assert "_safe_kill_process" not in func_names, "_safe_kill_process function should be removed"

    # Check for the constant (assignments at module level)
    src = _get_test_file_content()
    assert "EXTERNAL_SAM_CORPUS_RECORDS" not in src, \
        "EXTERNAL_SAM_CORPUS_RECORDS constant should be removed"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# -----------------------------------------------------------------------------

def test_file_imports_cleanly():
    """Test file must import without errors."""
    # Add repo to path for import
    sys.path.insert(0, f"{REPO}/test/registered/spec")
    sys.path.insert(0, f"{REPO}/python")

    # Just verify the file can be parsed and basic structure is valid
    tree = _parse_test_file()

    # Check that expected imports are present (unittest, requests)
    has_unittest = False
    has_requests = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "unittest":
                    has_unittest = True
        elif isinstance(node, ast.ImportFrom):
            if node.module and "requests" in str(node.module):
                has_requests = True

    assert has_unittest, "unittest import should be present"


def test_base_classes_still_present():
    """Core test base classes should still exist."""
    tree = _parse_test_file()

    class_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    assert "TestNgramSpeculativeDecodingBase" in class_names, \
        "TestNgramSpeculativeDecodingBase should be preserved"
    assert "TestNgramSpeculativeDecodingFlashinfer" in class_names, \
        "TestNgramSpeculativeDecodingFlashinfer should be preserved"
    assert "TestNgramSpeculativeDecodingPaged" in class_names, \
        "TestNgramSpeculativeDecodingPaged should be preserved"
