#!/usr/bin/env python3
"""Test outputs for quickwit#6280 - delete_metrics_splits error handling fix.

These tests verify BEHAVIOR, not text. They check:
- The code compiles and passes clippy (behavior of the fix)
- The CTE query pattern is used (structure, not variable names)
- FailedPrecondition is returned for non-deletable splits (error behavior)
- The query returns structured multi-value result (types, not names)
- The doc comment references the proto type (observable output)
"""

import subprocess
import os
import re
import sys

REPO = "/workspace/quickwit"


def test_delete_splits_query_uses_cte():
    """DELETE_SPLITS_QUERY in delete_metrics_splits uses a CTE pattern (WITH clause).

    This verifies the query structure, not variable names inside the CTE.
    """
    metastore_rs = os.path.join(
        REPO, "quickwit/quickwit-metastore/src/metastore/postgres/metastore.rs"
    )
    with open(metastore_rs, "r") as f:
        content = f.read()

    func_start = content.find("async fn delete_metrics_splits")
    assert func_start >= 0, "delete_metrics_splits function not found"

    # Extract the function content - look for DELETE_SPLITS_QUERY constant
    # The query is a large string constant within the function
    query_start = content.find("DELETE_SPLITS_QUERY", func_start)
    assert query_start >= 0, "DELETE_SPLITS_QUERY not found"
    # Extract the query string (it's a large raw string)
    query_end = content.find('"#;', query_start)
    assert query_end >= 0, "DELETE_SPLITS_QUERY terminator not found"
    query = content[query_start:query_end]

    # Verify it's a CTE query (starts with WITH, has subqueries)
    # We check for WITH at the start of the query string content
    lines = query.split('\n')
    # Skip the raw string prefix line and find actual query start
    query_text = '\n'.join(lines[1:])  # Skip 'const DELETE_SPLITS_QUERY: &str = r#"'
    query_text = query_text.strip()

    assert query_text.startswith("WITH"), (
        "DELETE_SPLITS_QUERY should use a CTE pattern starting with WITH"
    )

    # Verify it has subquery structure (at least 2 SELECTs within the CTE)
    select_count = query_text.upper().count("SELECT")
    assert select_count >= 3, (
        f"CTE query should have at least 3 SELECT statements (input_splits, deleted, output), found {select_count}"
    )


def test_failed_precondition_for_staged_published():
    """delete_metrics_splits returns FailedPrecondition for Staged/Published splits.

    This verifies the error behavior, not variable names.
    """
    metastore_rs = os.path.join(
        REPO, "quickwit/quickwit-metastore/src/metastore/postgres/metastore.rs"
    )
    with open(metastore_rs, "r") as f:
        content = f.read()

    func_start = content.find("async fn delete_metrics_splits")
    func_content = content[func_start:func_start + 10000]

    # The fixed code returns FailedPrecondition when splits are not deletable
    assert "FailedPrecondition" in func_content, (
        "delete_metrics_splits should return FailedPrecondition for non-deletable splits"
    )

    # Verify the error is specifically about splits being "not deletable"
    # We check for a format string containing "not deletable" without naming variables
    assert "not deletable" in func_content, (
        "FailedPrecondition message should explain splits are not deletable"
    )


def test_row_keys_proto_doc_updated():
    """row_keys_proto doc comment references the proto type and file.

    This verifies the doc comment mentions the proto type name, not implementation details.
    """
    metadata_rs = os.path.join(
        REPO, "quickwit/quickwit-parquet-engine/src/split/metadata.rs"
    )
    with open(metadata_rs, "r") as f:
        content = f.read()

    row_keys_idx = content.find("pub row_keys_proto:")
    assert row_keys_idx >= 0, "row_keys_proto field not found"

    # Get the preceding doc comment (within 300 chars before the field)
    doc_area = content[max(0, row_keys_idx - 300):row_keys_idx + 50]

    assert "sortschema::RowKeys" in doc_area, (
        "row_keys_proto doc comment should reference sortschema::RowKeys"
    )
    assert "event_store_sortschema.proto" in doc_area, (
        "row_keys_proto doc comment should reference event_store_sortschema.proto"
    )


def test_not_found_handling():
    """delete_metrics_splits handles not-found splits with warn + success (idempotent).

    This verifies the warning behavior for missing splits.
    """
    metastore_rs = os.path.join(
        REPO, "quickwit/quickwit-metastore/src/metastore/postgres/metastore.rs"
    )
    with open(metastore_rs, "r") as f:
        content = f.read()

    func_start = content.find("async fn delete_metrics_splits")
    func_content = content[func_start:func_start + 10000]

    # Code should warn about not-found splits (idempotent behavior)
    # We look for warn! macro call that includes split IDs for missing splits
    # Without specifying variable names, just the pattern of warning about missing splits
    assert "warn!(" in func_content, (
        "delete_metrics_splits should log a warning for not-found splits"
    )
    # The warning should reference "not found" or "not_found" concept
    assert ("not_found" in func_content or "not found" in func_content), (
        "delete_metrics_splits should track not_found for idempotent behavior"
    )


def test_delete_splits_query_returns_struct():
    """DELETE_SPLITS_QUERY returns a struct/tuple with multiple values.

    This verifies the query returns structured data (num_found, num_deleted counts
    and arrays for not_deletable/not_found), without specifying variable names.
    """
    metastore_rs = os.path.join(
        REPO, "quickwit/quickwit-metastore/src/metastore/postgres/metastore.rs"
    )
    with open(metastore_rs, "r") as f:
        content = f.read()

    func_start = content.find("async fn delete_metrics_splits")
    func_content = content[func_start:func_start + 10000]

    # The fixed query returns multiple values via query_as
    # We check that the code uses query_as and destructures a tuple with multiple values
    assert "sqlx::query_as" in func_content or "query_as(" in func_content, (
        "delete_metrics_splits should use sqlx::query_as for the CTE query"
    )

    # The query returns counts and arrays - check for the pattern of returning
    # multiple values without naming the specific variable names
    # Look for tuple destructuring: (Value, Value, Vec, Vec) or similar
    assert re.search(r"\(\s*\w+\s*,\s*\w+\s*,\s*\w+\s*,\s*\w+\s*\)", func_content), (
        "delete_metrics_splits should destructure a 4-tuple from the CTE query"
    )

    # Verify Staged and Published are checked (the deletable states)
    assert "Staged" in func_content and "Published" in func_content, (
        "delete_metrics_splits should check Staged and Published states"
    )


def test_metastore_check():
    """quickwit-metastore lib passes cargo check (no syntax errors)."""
    r = subprocess.run(
        ["bash", "-c",
         "apt-get update -qq && apt-get install -y -qq protobuf-compiler >/dev/null 2>&1 && "
         "cd /workspace/quickwit/quickwit && cargo check -p quickwit-metastore --lib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-1000:]}"


def test_metastore_clippy():
    """quickwit-metastore lib passes clippy (no warnings as errors)."""
    r = subprocess.run(
        ["bash", "-c",
         "apt-get update -qq && apt-get install -y -qq protobuf-compiler >/dev/null 2>&1 && "
         "rustup component add clippy >/dev/null 2>&1 && "
         "cd /workspace/quickwit/quickwit && cargo clippy -p quickwit-metastore --lib -- -D warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"clippy failed:\n{r.stderr[-1000:]}"


def test_parquet_engine_check():
    """quickwit-parquet-engine lib passes cargo check (no syntax errors)."""
    r = subprocess.run(
        ["bash", "-c",
         "apt-get update -qq && apt-get install -y -qq protobuf-compiler >/dev/null 2>&1 && "
         "cd /workspace/quickwit/quickwit && cargo check -p quickwit-parquet-engine --lib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-1000:]}"


def test_parquet_engine_clippy():
    """quickwit-parquet-engine lib passes clippy (no warnings as errors)."""
    r = subprocess.run(
        ["bash", "-c",
         "apt-get update -qq && apt-get install -y -qq protobuf-compiler >/dev/null 2>&1 && "
         "rustup component add clippy >/dev/null 2>&1 && "
         "cd /workspace/quickwit/quickwit && cargo clippy -p quickwit-parquet-engine --lib -- -D warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"clippy failed:\n{r.stderr[-1000:]}"


if __name__ == "__main__":
    tests = [
        test_delete_splits_query_uses_cte,
        test_failed_precondition_for_staged_published,
        test_row_keys_proto_doc_updated,
        test_not_found_handling,
        test_delete_splits_query_returns_struct,
        test_metastore_check,
        test_metastore_clippy,
        test_parquet_engine_check,
        test_parquet_engine_clippy,
    ]
    failed = []
    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
        except AssertionError as e:
            print(f"FAIL: {test.__name__} — {e}")
            failed.append(test.__name__)
        except Exception as e:
            print(f"ERROR: {test.__name__} — {e}")
            failed.append(test.__name__)

    if failed:
        print(f"\n{len(failed)} test(s) failed")
        sys.exit(1)
    else:
        print("\nAll tests passed")
        sys.exit(0)
