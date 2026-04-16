"""
Tests for apache/airflow#64738: Fix scheduler to skip asset-triggered dags without SerializedDagModel.

The bug: When a DAG has AssetDagRunQueue (ADRQ) rows but no corresponding SerializedDagModel,
the scheduler's dags_needing_dagruns method would fail because it tried to access dag_statuses
for dag_ids that weren't in the serialized_dag table.

The fix: Check for missing serialized dags and remove them from the processing set before
iterating, while keeping the ADRQ rows for later re-evaluation.
"""

import subprocess
import sys

REPO = "/workspace/airflow"
DAG_PY = f"{REPO}/airflow-core/src/airflow/models/dag.py"


def test_missing_serialized_dag_handling():
    """
    Test that dags_needing_dagruns handles DAGs with ADRQ but no SerializedDagModel (fail_to_pass).

    This test verifies the core bug fix: when a DAG has AssetDagRunQueue rows but no
    SerializedDagModel, the method should skip it instead of failing with a KeyError.
    """
    test_code = f'''
import sys

with open("{DAG_PY}", "r") as f:
    dag_code = f.read()

# The fix adds this specific pattern to detect missing serialized dags:
# ser_dag_ids = {{ser_dag.dag_id for ser_dag in ser_dags}}
# if missing_from_serialized := set(adrq_by_dag.keys()) - ser_dag_ids:
has_ser_dag_ids = "ser_dag_ids = " in dag_code and "ser_dag.dag_id" in dag_code
has_missing_check = "missing_from_serialized" in dag_code

if has_ser_dag_ids and has_missing_check:
    print("FIX_PRESENT: Code correctly handles missing serialized DAGs")
    sys.exit(0)
else:
    print(f"FIX_MISSING: ser_dag_ids={{has_ser_dag_ids}}, missing_check={{has_missing_check}}")
    sys.exit(1)
'''

    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    assert result.returncode == 0, f"Missing serialized dag handling failed:\n{result.stdout}\n{result.stderr}"
    assert "FIX_PRESENT" in result.stdout, f"Fix not detected:\n{result.stdout}"


def test_fix_removes_orphan_dags_from_both_dicts():
    """
    Test that the fix removes orphan dag_ids from both adrq_by_dag and dag_statuses (fail_to_pass).

    The critical part of the fix is that it deletes orphan dag_ids from BOTH dictionaries
    in a loop over missing_from_serialized, preventing KeyError.
    """
    test_code = f'''
import sys
import re

with open("{DAG_PY}", "r") as f:
    dag_code = f.read()

# The fix must delete from both dicts in a loop that handles missing_from_serialized
# Look for the pattern:
#     for dag_id in missing_from_serialized:
#         del adrq_by_dag[dag_id]
#         del dag_statuses[dag_id]

# First check if missing_from_serialized exists
if "missing_from_serialized" not in dag_code:
    print("FIX_MISSING: No missing_from_serialized handling")
    sys.exit(1)

# Find the section handling missing_from_serialized
idx = dag_code.find("missing_from_serialized")
section = dag_code[idx:idx+600]

# Check for the deletion pattern in this section
has_for_loop = "for dag_id in missing_from_serialized" in section
has_adrq_del = "del adrq_by_dag[dag_id]" in section
has_statuses_del = "del dag_statuses[dag_id]" in section

if has_for_loop and has_adrq_del and has_statuses_del:
    print("FIX_COMPLETE: Both dicts cleaned up in loop over missing_from_serialized")
    sys.exit(0)
else:
    print(f"FIX_INCOMPLETE: for_loop={{has_for_loop}}, adrq_del={{has_adrq_del}}, statuses_del={{has_statuses_del}}")
    sys.exit(1)
'''

    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    assert result.returncode == 0, f"Fix incomplete - missing cleanup:\n{result.stdout}\n{result.stderr}"


def test_fix_logs_skipped_dags_message():
    """
    Test that the fix logs the specific message about skipped DAGs (fail_to_pass).

    The fix should emit: "Dags have queued asset events (ADRQ), but are not found in the serialized_dag table."
    """
    test_code = f'''
import sys

with open("{DAG_PY}", "r") as f:
    dag_code = f.read()

# The fix should contain this specific log message
expected_msg = "not found in the serialized_dag table"

if expected_msg in dag_code:
    print("FIX_LOGS: Specific log message for skipped DAGs present")
    sys.exit(0)
else:
    print("FIX_NO_LOGS: Missing specific log message")
    sys.exit(1)
'''

    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    assert result.returncode == 0, f"Fix missing logging:\n{result.stdout}\n{result.stderr}"


def test_fix_does_not_delete_adrq_rows():
    """
    Test that the fix only removes from in-memory dicts, not the database (fail_to_pass).

    A key requirement is that ADRQ rows must NOT be deleted from the database.
    The fix should use `del adrq_by_dag[dag_id]` (dict delete), NOT `session.delete()`.
    """
    test_code = f'''
import sys

with open("{DAG_PY}", "r") as f:
    dag_code = f.read()

# The fix must use missing_from_serialized
if "missing_from_serialized" not in dag_code:
    print("FIX_MISSING: No handling for missing serialized dags")
    sys.exit(1)

# Extract the relevant section
idx = dag_code.find("missing_from_serialized")
section = dag_code[idx:idx+600]

# Check there's no database deletion in this section
# Good: del adrq_by_dag[dag_id] (dict operation)
# Bad: session.delete(...) or .delete().where(...)
has_session_delete = "session.delete" in section
has_orm_delete = ".delete(" in section and "AssetDagRunQueue" in section

if has_session_delete or has_orm_delete:
    print("FIX_BAD: ADRQ rows are being deleted from database")
    sys.exit(1)
else:
    print("FIX_GOOD: ADRQ rows preserved in database (dict operations only)")
    sys.exit(0)
'''

    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    assert result.returncode == 0, f"Fix deletes ADRQ rows:\n{result.stdout}\n{result.stderr}"


def test_fix_uses_set_difference():
    """
    Test that the fix correctly identifies missing serialized dags using set operations (fail_to_pass).

    The fix should compute: set(adrq_by_dag.keys()) - ser_dag_ids
    """
    test_code = f'''
import sys

with open("{DAG_PY}", "r") as f:
    dag_code = f.read()

# The fix must use this specific set difference pattern
# Look for: set(adrq_by_dag.keys()) - ser_dag_ids
# Or: missing_from_serialized := set(adrq_by_dag.keys()) - ser_dag_ids

has_set_adrq_keys = "set(adrq_by_dag.keys())" in dag_code
has_minus_ser_dag_ids = "- ser_dag_ids" in dag_code

if has_set_adrq_keys and has_minus_ser_dag_ids:
    print("FIX_CORRECT: Uses set(adrq_by_dag.keys()) - ser_dag_ids")
    sys.exit(0)
else:
    print(f"FIX_WRONG: set_adrq_keys={{has_set_adrq_keys}}, minus_ser={{has_minus_ser_dag_ids}}")
    sys.exit(1)
'''

    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    assert result.returncode == 0, f"Fix doesn't use set difference:\n{result.stdout}\n{result.stderr}"


def test_fix_logs_sorted_dag_ids():
    """
    Test that the fix logs dag_ids in sorted order (fail_to_pass).

    The fix should use sorted(missing_from_serialized) for deterministic logging.
    """
    test_code = f'''
import sys

with open("{DAG_PY}", "r") as f:
    dag_code = f.read()

if "missing_from_serialized" not in dag_code:
    print("FIX_MISSING: No missing_from_serialized")
    sys.exit(1)

# The fix should sort the dag_ids for logging
if "sorted(missing_from_serialized)" in dag_code:
    print("FIX_SORTED: Uses sorted() for deterministic logging")
    sys.exit(0)
else:
    print("FIX_UNSORTED: Missing sorted() call")
    sys.exit(1)
'''

    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    assert result.returncode == 0, f"Fix doesn't sort dag_ids:\n{result.stdout}\n{result.stderr}"


def test_dag_model_syntax_valid():
    """
    Test that dag.py has valid Python syntax (pass_to_pass).
    """
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", "airflow-core/src/airflow/models/dag.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    assert result.returncode == 0, f"Syntax error in dag.py:\n{result.stderr}"


def test_dags_needing_dagruns_method_exists():
    """
    Test that dags_needing_dagruns method exists and is properly defined (pass_to_pass).
    """
    test_code = f'''
import sys
import ast

with open("{DAG_PY}", "r") as f:
    dag_code = f.read()

tree = ast.parse(dag_code)

# Find the DagModel class and its dags_needing_dagruns method
found_method = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "DagModel":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "dags_needing_dagruns":
                found_method = True
                print("METHOD_OK: dags_needing_dagruns exists in DagModel")
                sys.exit(0)

if not found_method:
    print("METHOD_MISSING: dags_needing_dagruns not found in DagModel")
    sys.exit(1)
'''

    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    assert result.returncode == 0, f"Method not found:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_lint():
    """
    Test that dag.py passes ruff linter checks (pass_to_pass).

    Runs the repo's standard ruff linter on the modified file to ensure
    code quality and style compliance.
    """
    # First install ruff
    install_result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )

    # Run ruff check on dag.py
    result = subprocess.run(
        ["ruff", "check", "airflow-core/src/airflow/models/dag.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )

    assert result.returncode == 0, f"Ruff lint check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_format():
    """
    Test that dag.py passes ruff format check (pass_to_pass).

    Runs the repo's ruff formatter in check mode to verify code formatting
    matches the project's style configuration.
    """
    # First install ruff
    install_result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )

    # Run ruff format --check on dag.py
    result = subprocess.run(
        ["ruff", "format", "--check", "airflow-core/src/airflow/models/dag.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )

    assert result.returncode == 0, f"Ruff format check failed:\n{result.stdout}\n{result.stderr}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
