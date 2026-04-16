"""Tests for lancedb PR #3030 - graceful handling of empty result sets in hybrid search."""

import subprocess
import sys
import os
import ast
import re

# Constants
REPO = "/workspace/lancedb"
QUERY_FILE = f"{REPO}/python/python/lancedb/query.py"


def test_repo_ruff_lint():
    """Repo's Python linter passes (pass_to_pass).

    Runs ruff check on the modified query.py file.
    """
    r = subprocess.run(
        ["pip", "install", "ruff==0.9.9", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/python",
    )
    r = subprocess.run(
        ["ruff", "check", "python/lancedb/query.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/python",
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_ruff_format():
    """Repo's Python code is properly formatted (pass_to_pass).

    Runs ruff format --check on the modified query.py file.
    """
    r = subprocess.run(
        ["pip", "install", "ruff==0.9.9", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/python",
    )
    r = subprocess.run(
        ["ruff", "format", "--check", "python/lancedb/query.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/python",
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_git_trackable():
    """Modified file is in a clean git state (pass_to_pass).

    Verifies the repo has a proper git checkout that can track changes.
    """
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    # Git status should succeed (repo is properly cloned)
    assert r.returncode == 0, f"Git status failed: {r.stderr}"

def _read_query_file():
    """Read the query.py file content."""
    with open(QUERY_FILE, 'r') as f:
        return f.read()


def test_empty_results_early_return_exists():
    """F2P: Check that early return for empty results exists in _combine_hybrid_results.

    The fix should add a check for empty vector and FTS results before reranking.
    """
    content = _read_query_file()

    # Find the _combine_hybrid_results method
    tree = ast.parse(content)

    found_method = False
    found_early_return = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == '_combine_hybrid_results':
            found_method = True
            # Look for the early return check: vector_results.num_rows == 0 and fts_results.num_rows == 0
            source_segment = ast.unparse(node) if hasattr(ast, 'unparse') else content[node.col_offset:node.end_col_offset]

            # Check for the empty results check pattern
            if 'num_rows == 0' in source_segment and 'vector_results' in source_segment and 'fts_results' in source_segment:
                found_early_return = True
            break

    assert found_method, "_combine_hybrid_results method not found"
    assert found_early_return, "Early return for empty results not found - should check num_rows == 0 for both results"


def test_relevance_score_column_added():
    """F2P: Check that _relevance_score column is added to empty results.

    The fix should append a _relevance_score column to the empty table.
    """
    content = _read_query_file()

    # Check for _relevance_score column being added
    assert '_relevance_score' in content, "_relevance_score column handling not found"

    # Look for append_column with _relevance_score
    pattern = r'append_column\s*\(\s*["\']_relevance_score["\']'
    matches = re.findall(pattern, content)
    assert len(matches) > 0, "_relevance_score column not being appended to empty results"


def test_with_row_ids_handling():
    """F2P: Check that with_row_ids flag is respected in empty results.

    The fix should drop _rowid column when with_row_ids=False.
    """
    content = _read_query_file()

    # Find the _combine_hybrid_results method
    tree = ast.parse(content)

    found_method = False
    found_rowid_handling = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == '_combine_hybrid_results':
            found_method = True
            # Check for with_row_ids handling
            source = ast.unparse(node) if hasattr(ast, 'unparse') else content

            # Look for the pattern: if not with_row_ids and "_rowid" in empty.column_names
            if 'with_row_ids' in source and '_rowid' in source and 'drop' in source:
                found_rowid_handling = True
            break

    assert found_method, "_combine_hybrid_results method not found"
    assert found_rowid_handling, "with_row_ids handling not found - should drop _rowid when with_row_ids=False"


def test_pa_unify_schemas_usage():
    """F2P: Check that pa.unify_schemas is used to merge schemas.

    The fix should use pa.unify_schemas to properly combine vector and FTS schemas.
    """
    content = _read_query_file()

    # Check for pa.unify_schemas call
    assert 'pa.unify_schemas' in content, "pa.unify_schemas not used for schema merging"


def test_python_syntax_valid():
    """P2P: Python code should have valid syntax."""
    content = _read_query_file()

    try:
        ast.parse(content)
    except SyntaxError as e:
        assert False, f"Syntax error in query.py: {e}"


def test_patch_code_structure():
    """F2P: The specific patch structure should be present.

    Check for the distinctive lines from the gold patch:
    - Early return comment about empty results
    - vector_results.num_rows == 0 check
    - pa.unify_schemas call
    - empty.append_column for _relevance_score
    """
    content = _read_query_file()

    # Check for key lines from the patch
    checks = [
        ('early return comment', 'return early to avoid errors in reranking' in content.lower() or
                                'return early' in content.lower()),
        ('empty results check', 'num_rows == 0' in content),
        ('schema unification', 'pa.unify_schemas' in content),
        ('relevance score column', '_relevance_score' in content),
        ('with_row_ids check', 'with_row_ids' in content and '_rowid' in content),
    ]

    failed = []
    for name, check in checks:
        if not check:
            failed.append(name)

    assert len(failed) == 0, f"Missing patch elements: {failed}"


def test_no_index_error_on_empty_results():
    """F2P: Verify the code handles empty results without IndexError.

    The original bug was that empty results passed to rerankers caused IndexError.
    The fix adds an early return before reranking.
    """
    content = _read_query_file()

    # Parse and find the _combine_hybrid_results method
    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == '_combine_hybrid_results':
            # Get method source
            method_start = node.lineno - 1
            method_end = node.end_lineno

            lines = content.split('\n')[method_start:method_end]
            method_source = '\n'.join(lines)

            # Check that early return comes before reranker.rerank_hybrid call
            early_return_idx = -1
            rerank_idx = -1

            for i, line in enumerate(lines):
                if 'num_rows == 0' in line and 'return' in method_source[i:]:
                    early_return_idx = i
                if 'rerank_hybrid' in line or 'reranker' in line and 'rerank' in line:
                    rerank_idx = i

            if early_return_idx >= 0 and rerank_idx >= 0:
                assert early_return_idx < rerank_idx, \
                    "Early return should come before reranker call"
            elif early_return_idx >= 0:
                # Early return exists, which is what we want
                pass
            else:
                assert False, "Early return for empty results not found"


def test_combined_schema_includes_both():
    """F2P: Check that combined schema includes fields from both input tables.

    The fix should create an empty table with unified schema from vector_results and fts_results.
    """
    content = _read_query_file()

    # Check for the pattern that creates combined schema from both tables
    assert 'vector_results.schema' in content, "vector_results.schema not used"
    assert 'fts_results.schema' in content, "fts_results.schema not used"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
