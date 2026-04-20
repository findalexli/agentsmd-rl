"""Tests for lancedb PR #3030 - graceful handling of empty result sets in hybrid search."""

import subprocess
import sys
import os
import tempfile
import shutil

# Constants
REPO = "/workspace/lancedb"
QUERY_FILE = f"{REPO}/python/python/lancedb/query.py"
SITE_PACKAGES = "/usr/local/lib/python3.12/site-packages"


def _apply_patch_to_site_packages():
    """Copy the repo's query.py to site-packages for testing."""
    src = f"{REPO}/python/python/lancedb/query.py"
    dst = f"{SITE_PACKAGES}/lancedb/query.py"
    if os.path.exists(src):
        shutil.copy2(src, dst)


def _get_query_file_content():
    """Read the query.py file content from the repo."""
    with open(QUERY_FILE, 'r') as f:
        return f.read()


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


def test_python_syntax_valid():
    """P2P: Python code should have valid syntax."""
    import ast
    content = _get_query_file_content()

    try:
        ast.parse(content)
    except SyntaxError as e:
        assert False, f"Syntax error in query.py: {e}"


def test_empty_results_no_crash():
    """F2P: Empty results should not crash with IndexError.

    The original bug was that _combine_hybrid_results crashed with IndexError
    when both vector_results and fts_results were empty. The fix should handle
    this case gracefully and return an empty table.
    """
    # Apply the repo's query.py to site-packages for testing
    _apply_patch_to_site_packages()

    # Now import and test
    import pyarrow as pa
    from lancedb.query import LanceHybridQueryBuilder

    # Create empty tables like the bug scenario
    vector_results = pa.table({
        "_rowid": pa.array([], type=pa.int64()),
        "_distance": pa.array([], type=pa.float32()),
    })
    fts_results = pa.table({
        "_rowid": pa.array([], type=pa.int64()),
        "_score": pa.array([], type=pa.float32()),
    })

    class MockReranker:
        def rerank_hybrid(self, query, vector_results, fts_results):
            return vector_results

    # This should not raise IndexError
    result = LanceHybridQueryBuilder._combine_hybrid_results(
        fts_results=fts_results,
        vector_results=vector_results,
        norm="score",
        fts_query="test",
        reranker=MockReranker(),
        limit=10,
        with_row_ids=False,
    )

    # Should return an empty table
    assert result.num_rows == 0, f"Expected 0 rows, got {result.num_rows}"


def test_empty_results_has_relevance_score():
    """F2P: Empty results table should have _relevance_score column.

    When handling empty results, the fix should return a table with the
    _relevance_score column (required by downstream code), even if empty.
    """
    _apply_patch_to_site_packages()

    import pyarrow as pa
    from lancedb.query import LanceHybridQueryBuilder

    vector_results = pa.table({
        "_rowid": pa.array([], type=pa.int64()),
        "_distance": pa.array([], type=pa.float32()),
    })
    fts_results = pa.table({
        "_rowid": pa.array([], type=pa.int64()),
        "_score": pa.array([], type=pa.float32()),
    })

    class MockReranker:
        def rerank_hybrid(self, query, vector_results, fts_results):
            return vector_results

    result = LanceHybridQueryBuilder._combine_hybrid_results(
        fts_results=fts_results,
        vector_results=vector_results,
        norm="score",
        fts_query="test",
        reranker=MockReranker(),
        limit=10,
        with_row_ids=False,
    )

    # Should have _relevance_score column
    assert "_relevance_score" in result.column_names, \
        f"Missing _relevance_score column. Got: {result.column_names}"

    # _relevance_score should be float type
    rel_score_field = result.schema.field("_relevance_score")
    assert pa.types.is_floating(rel_score_field.type), \
        f"_relevance_score should be float type, got {rel_score_field.type}"


def test_empty_results_respects_with_row_ids():
    """F2P: with_row_ids=False should drop _rowid column from empty results.

    When handling empty results with with_row_ids=False, the fix should
    drop the _rowid column from the returned table.
    """
    _apply_patch_to_site_packages()

    import pyarrow as pa
    from lancedb.query import LanceHybridQueryBuilder

    vector_results = pa.table({
        "_rowid": pa.array([], type=pa.int64()),
        "_distance": pa.array([], type=pa.float32()),
    })
    fts_results = pa.table({
        "_rowid": pa.array([], type=pa.int64()),
        "_score": pa.array([], type=pa.float32()),
    })

    class MockReranker:
        def rerank_hybrid(self, query, vector_results, fts_results):
            return vector_results

    # Test with with_row_ids=False
    result_no_rowid = LanceHybridQueryBuilder._combine_hybrid_results(
        fts_results=fts_results,
        vector_results=vector_results,
        norm="score",
        fts_query="test",
        reranker=MockReranker(),
        limit=10,
        with_row_ids=False,
    )

    # _rowid should be dropped when with_row_ids=False
    assert "_rowid" not in result_no_rowid.column_names, \
        f"_rowid should be dropped when with_row_ids=False. Got: {result_no_rowid.column_names}"

    # Test with with_row_ids=True
    result_with_rowid = LanceHybridQueryBuilder._combine_hybrid_results(
        fts_results=fts_results,
        vector_results=vector_results,
        norm="score",
        fts_query="test",
        reranker=MockReranker(),
        limit=10,
        with_row_ids=True,
    )

    # _rowid should be present when with_row_ids=True
    assert "_rowid" in result_with_rowid.column_names, \
        f"_rowid should be present when with_row_ids=True. Got: {result_with_rowid.column_names}"


def test_empty_results_merges_schemas():
    """F2P: Empty results table should have merged schema from both inputs.

    When handling empty results, the fix should merge schemas from both
    vector_results and fts_results to create a proper empty table.
    """
    _apply_patch_to_site_packages()

    import pyarrow as pa
    from lancedb.query import LanceHybridQueryBuilder

    # Create tables with distinct columns
    vector_results = pa.table({
        "_rowid": pa.array([], type=pa.int64()),
        "_distance": pa.array([], type=pa.float32()),
        "custom_vec_col": pa.array([], type=pa.float64()),
    })
    fts_results = pa.table({
        "_rowid": pa.array([], type=pa.int64()),
        "_score": pa.array([], type=pa.float32()),
        "custom_fts_col": pa.array([], type=pa.utf8()),
    })

    class MockReranker:
        def rerank_hybrid(self, query, vector_results, fts_results):
            return vector_results

    result = LanceHybridQueryBuilder._combine_hybrid_results(
        fts_results=fts_results,
        vector_results=vector_results,
        norm="score",
        fts_query="test",
        reranker=MockReranker(),
        limit=10,
        with_row_ids=False,
    )

    # Result should have columns from both schemas (minus _rowid if dropped)
    column_names = result.column_names

    # Should have _distance from vector_results
    assert "_distance" in column_names, f"Missing _distance. Got: {column_names}"

    # Should have _score from fts_results
    assert "_score" in column_names, f"Missing _score. Got: {column_names}"

    # Should have custom columns from both
    assert "custom_vec_col" in column_names, f"Missing custom_vec_col. Got: {column_names}"
    assert "custom_fts_col" in column_names, f"Missing custom_fts_col. Got: {column_names}"


def test_nonempty_results_still_work():
    """F2P: Non-empty results should still work correctly.

    The fix should not break the normal case where results are non-empty.
    """
    _apply_patch_to_site_packages()

    import pyarrow as pa
    from lancedb.query import LanceHybridQueryBuilder

    # Create non-empty tables
    vector_results = pa.table({
        "_rowid": pa.array([1, 2, 3], type=pa.int64()),
        "_distance": pa.array([0.1, 0.2, 0.3], type=pa.float32()),
    })
    fts_results = pa.table({
        "_rowid": pa.array([2, 3, 4], type=pa.int64()),
        "_score": pa.array([1.5, 2.0, 0.5], type=pa.float32()),
    })

    class MockReranker:
        def rerank_hybrid(self, query, vector_results, fts_results):
            # Return a simple combination
            return pa.table({
                "_rowid": pa.array([1, 2, 3], type=pa.int64()),
                "_distance": pa.array([0.1, 0.2, 0.3], type=pa.float32()),
                "_score": pa.array([0.0, 1.5, 2.0], type=pa.float32()),
                "_relevance_score": pa.array([0.5, 0.6, 0.7], type=pa.float32()),
            })

    result = LanceHybridQueryBuilder._combine_hybrid_results(
        fts_results=fts_results,
        vector_results=vector_results,
        norm="score",
        fts_query="test",
        reranker=MockReranker(),
        limit=10,
        with_row_ids=False,
    )

    # Should return results (not crash)
    assert result.num_rows > 0, f"Expected non-empty results, got {result.num_rows} rows"

    # Should have _relevance_score
    assert "_relevance_score" in result.column_names


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
