"""
Test outputs for airflow scheduler asset-triggered DAG bug fix.

This tests the fix where DagModel.dags_needing_dagruns() now properly skips
DAGs that have AssetDagRunQueue rows but no matching SerializedDagModel.
Without the fix, such DAGs would be included in triggered_date_by_dag,
potentially causing errors or premature DagRun creation.
"""

import logging
import os
import subprocess
import sys

import pytest

# Database test marker - requires SQLite/Postgres
pytestmark = [pytest.mark.db_test]

REPO = "/workspace/airflow"


def test_code_structure_fix_applied():
    """
    F2P: Verify the fix structure is present in the code.

    This checks that the code has been modified to include the fix for
    skipping DAGs without SerializedDagModel.
    """
    dag_file = os.path.join(REPO, "airflow-core/src/airflow/models/dag.py")

    with open(dag_file, "r") as f:
        content = f.read()

    # Check for the key fix components
    assert "missing_from_serialized := set(adrq_by_dag.keys()) - ser_dag_ids" in content, \
        "BUG: The fix for identifying missing serialized DAGs is not present"

    assert "Dags have queued asset events (ADRQ), but are not found in the serialized_dag table" in content, \
        "BUG: The log message for missing serialized DAGs is not present"

    # Verify the fix deletes from adrq_by_dag and dag_statuses
    assert "del adrq_by_dag[dag_id]" in content, \
        "BUG: The fix should remove missing DAGs from adrq_by_dag"

    assert "del dag_statuses[dag_id]" in content, \
        "BUG: The fix should remove missing DAGs from dag_statuses"


def test_docstring_added():
    """
    F2P: Verify the docstring update explaining the behavior is present.

    The fix adds documentation explaining that DAGs without SerializedDagModel
    are omitted from triggered_date_by_dag.
    """
    dag_file = os.path.join(REPO, "airflow-core/src/airflow/models/dag.py")

    with open(dag_file, "r") as f:
        content = f.read()

    # Check for the docstring update about the fix behavior
    assert "For asset-triggered scheduling, Dags that have ``AssetDagRunQueue`` rows but no matching" in content, \
        "BUG: Documentation about the fix is not present in the docstring"

    assert "are omitted from ``triggered_date_by_dag`` until serialization exists" in content, \
        "BUG: Documentation about omission behavior is not present"


def test_sorted_missing_dag_ids():
    """
    F2P: Verify that missing DAG IDs are logged in sorted order.

    The fix uses sorted(missing_from_serialized) in the log message.
    """
    dag_file = os.path.join(REPO, "airflow-core/src/airflow/models/dag.py")

    with open(dag_file, "r") as f:
        content = f.read()

    # Check for sorted() call in the log message
    assert "sorted(missing_from_serialized)" in content, \
        "BUG: The fix should sort the missing DAG IDs before logging"


def test_repo_unit_tests_exist():
    """
    P2P: Verify that the repo's unit tests for this feature exist.

    Checks that the test methods for the fix are present in test_dag.py.
    """
    test_file = os.path.join(REPO, "airflow-core/tests/unit/models/test_dag.py")

    with open(test_file, "r") as f:
        content = f.read()

    # Check for the new test methods added by the fix
    assert "test_dags_needing_dagruns_skips_adrq_when_serialized_dag_missing" in content, \
        "Missing test: test_dags_needing_dagruns_skips_adrq_when_serialized_dag_missing"

    assert "test_dags_needing_dagruns_missing_serialized_debug_lists_sorted_dag_ids" in content, \
        "Missing test: test_dags_needing_dagruns_missing_serialized_debug_lists_sorted_dag_ids"

    # Check that func is imported (used in the new tests for counting)
    assert "from sqlalchemy import delete, func, inspect, select, update" in content, \
        "BUG: func import missing from sqlalchemy imports (needed for new tests)"


def test_fix_does_not_delete_adrq_rows():
    """
    F2P: Verify the fix does NOT delete ADRQ rows.

    The fix should only delete from the in-memory dictionaries,
    not from the database.
    """
    dag_file = os.path.join(REPO, "airflow-core/src/airflow/models/dag.py")

    with open(dag_file, "r") as f:
        content = f.read()

    # Find the dags_needing_dagruns method
    method_start = content.find("def dags_needing_dagruns")
    if method_start == -1:
        pytest.skip("Method dags_needing_dagruns not found")

    # The key point: the fix should only do "del adrq_by_dag[dag_id]" (in-memory dict deletion)
    # and NOT "session.query(AssetDagRunQueue).delete()" or "session.delete(adrq)"
    # The patch adds the code between "ser_dags = SerializedDagModel.get_latest_serialized_dags"
    # and "for ser_dag in ser_dags:"

    # Look for the fix block - the code that handles missing_from_serialized
    # This block should only delete from dictionaries, not the database
    fix_block_start = content.find("missing_from_serialized := set(adrq_by_dag.keys()) - ser_dag_ids")

    if fix_block_start == -1:
        # Fix not applied - this is a fail case
        pytest.fail("BUG: The fix for missing serialized DAGs is not present")

    # Find the end of the fix block (the next line that starts a for loop with ser_dag)
    fix_block = content[fix_block_start:fix_block_start + 2000]

    # The fix block should delete from in-memory dictionaries
    assert "del adrq_by_dag[dag_id]" in fix_block, \
        "BUG: Fix should remove from in-memory adrq_by_dag dictionary"

    assert "del dag_statuses[dag_id]" in fix_block, \
        "BUG: Fix should remove from in-memory dag_statuses dictionary"

    # The fix block should NOT have database deletions
    # Check for patterns like session.delete(adrq... or session.query(...).delete()
    # We only care about deletions AFTER the fix block starts (not elsewhere in the method)
    lines_in_block = fix_block.split('\n')
    for line in lines_in_block:
        # Skip comments and strings
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'"):
            continue
        # Check for actual database deletion calls (not just dictionary deletion)
        if 'session.delete(' in stripped and 'adrq' in stripped.lower():
            pytest.fail(f"BUG: Fix should not delete ADRQ rows from database, found: {stripped}")
        if 'session.query(' in stripped and 'delete()' in stripped:
            pytest.fail(f"BUG: Fix should not delete from database, found: {stripped}")
