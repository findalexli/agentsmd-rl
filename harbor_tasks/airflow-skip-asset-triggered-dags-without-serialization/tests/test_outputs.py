"""
Behavioral tests for airflow scheduler asset-triggered DAG bug fix.

These tests execute actual Airflow code to verify that DagModel.dags_needing_dagruns()
properly skips DAGs that have AssetDagRunQueue rows but no matching SerializedDagModel.
"""

import subprocess
import sys

REPO = "/workspace/airflow"
DAG_PY = "airflow-core/src/airflow/models/dag.py"
TEST_DAG_PY = "airflow-core/tests/unit/models/test_dag.py"


def test_skips_dag_without_serialized_model():
    """
    F2P: DAG with AssetDagRunQueue but no SerializedDagModel is excluded from triggered_date_by_dag.

    This test creates a real database scenario where:
    - A DAG exists in DagModel with an asset expression
    - AssetDagRunQueue rows exist for that DAG
    - But NO SerializedDagModel exists for the DAG

    The fix should exclude such DAGs from the returned triggered_date_by_dag dict.
    """
    code = '''
import logging
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
from airflow.models.dag import DagModel
from airflow.models.assets import AssetModel, AssetDagRunQueue
from airflow.utils import timezone

# Configure logging to capture the log message
logging.basicConfig(level=logging.DEBUG)

# Create in-memory SQLite database
engine = create_engine("sqlite:///:memory:")
Session = sessionmaker(bind=engine)

# Create tables
from airflow.models.base import Base
Base.metadata.create_all(engine)

session = Session()

# Create an orphan DAG scenario: ADRQ exists but no SerializedDagModel
orphan_dag_id = "adrq_no_serialized_dag"
orphan_uri = "test://asset_for_orphan_adrq"

# Add asset
asset = AssetModel(uri=orphan_uri)
session.add(asset)
session.flush()
asset_id = session.scalar(select(AssetModel.id).where(AssetModel.uri == orphan_uri))

# Add DagModel (but NOT SerializedDagModel)
dag_model = DagModel(
    dag_id=orphan_dag_id,
    bundle_name="testing",
    max_active_tasks=1,
    has_task_concurrency_limits=False,
    max_consecutive_failed_dag_runs=0,
    next_dagrun=timezone.datetime(2038, 1, 1),
    next_dagrun_create_after=timezone.datetime(2038, 1, 2),
    is_stale=False,
    has_import_errors=False,
    is_paused=False,
    asset_expression={"any": [{"uri": orphan_uri}]},
)
session.add(dag_model)
session.flush()

# Add AssetDagRunQueue row
session.add(AssetDagRunQueue(asset_id=asset_id, target_dag_id=orphan_dag_id))
session.flush()

# Call the method under test
_query, triggered_date_by_dag = DagModel.dags_needing_dagruns(session)

# Verify the orphan DAG is NOT in the result
if orphan_dag_id in triggered_date_by_dag:
    print(f"FAIL: {orphan_dag_id} should not be in triggered_date_by_dag")
    sys.exit(1)

# Verify ADRQ row still exists in database
adrq_count = session.scalar(
    select(func.count())
    .select_from(AssetDagRunQueue)
    .where(AssetDagRunQueue.target_dag_id == orphan_dag_id)
)
if adrq_count != 1:
    print(f"FAIL: ADRQ row should still exist, found count={adrq_count}")
    sys.exit(1)

print("PASS: DAG without SerializedDagModel was correctly skipped")
'''

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
        env={"PYTHONPATH": f"{REPO}/airflow-core/src:{REPO}/devel-common/src:{REPO}/task-sdk/src:{REPO}/shared"},
    )

    if result.returncode != 0:
        raise AssertionError(f"Test failed: {result.stderr}")
    assert "PASS:" in result.stdout, f"Expected PASS in output, got: {result.stdout}"


def test_log_message_includes_sorted_dag_ids():
    """
    F2P: Log message shows sorted DAG IDs when multiple DAGs lack SerializedDagModel.

    When multiple DAGs have ADRQ rows but no SerializedDagModel,
    the log message should list them in alphabetical order.
    """
    code = '''
import logging
import sys
from io import StringIO
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
from airflow.models.dag import DagModel
from airflow.models.assets import AssetModel, AssetDagRunQueue
from airflow.utils import timezone

# Create in-memory SQLite database
engine = create_engine("sqlite:///:memory:")
Session = sessionmaker(bind=engine)

# Create tables
from airflow.models.base import Base
Base.metadata.create_all(engine)

session = Session()

# Create two orphan DAGs: ghost_z and ghost_a (should be sorted as ghost_a, ghost_z)
session.add_all([
    AssetModel(uri="test://ds_ghost_z"),
    AssetModel(uri="test://ds_ghost_a"),
])
session.flush()

id_z = session.scalar(select(AssetModel.id).where(AssetModel.uri == "test://ds_ghost_z"))
id_a = session.scalar(select(AssetModel.id).where(AssetModel.uri == "test://ds_ghost_a"))

far = timezone.datetime(2038, 1, 1)
far_after = timezone.datetime(2038, 1, 2)

session.add_all([
    DagModel(
        dag_id="ghost_z",
        bundle_name="testing",
        max_active_tasks=1,
        has_task_concurrency_limits=False,
        max_consecutive_failed_dag_runs=0,
        next_dagrun=far,
        next_dagrun_create_after=far_after,
        is_stale=False,
        has_import_errors=False,
        is_paused=False,
        asset_expression={"any": [{"uri": "test://ds_ghost_z"}]},
    ),
    DagModel(
        dag_id="ghost_a",
        bundle_name="testing",
        max_active_tasks=1,
        has_task_concurrency_limits=False,
        max_consecutive_failed_dag_runs=0,
        next_dagrun=far,
        next_dagrun_create_after=far_after,
        is_stale=False,
        has_import_errors=False,
        is_paused=False,
        asset_expression={"any": [{"uri": "test://ds_ghost_a"}]},
    ),
])
session.flush()

session.add_all([
    AssetDagRunQueue(asset_id=id_z, target_dag_id="ghost_z"),
    AssetDagRunQueue(asset_id=id_a, target_dag_id="ghost_a"),
])
session.flush()

# Set up log capture
log_capture = StringIO()
handler = logging.StreamHandler(log_capture)
handler.setLevel(logging.INFO)
logger = logging.getLogger("airflow.models.dag")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Call the method under test
_query, triggered_date_by_dag = DagModel.dags_needing_dagruns(session)

# Check results
if "ghost_a" in triggered_date_by_dag or "ghost_z" in triggered_date_by_dag:
    print("FAIL: Orphan DAGs should not be in triggered_date_by_dag")
    sys.exit(1)

# Check log message contains sorted order
log_output = log_capture.getvalue()
expected_msg = "Dags have queued asset events (ADRQ), but are not found in the serialized_dag table"
if expected_msg not in log_output:
    print(f"FAIL: Expected log message not found. Log output: {log_output}")
    sys.exit(1)

# Check alphabetical ordering in the log
if log_output.index("ghost_a") > log_output.index("ghost_z"):
    print(f"FAIL: DAG IDs not in sorted order in log message: {log_output}")
    sys.exit(1)

# Verify ADRQ rows still exist
adrq_count = session.scalar(
    select(func.count())
    .select_from(AssetDagRunQueue)
    .where(AssetDagRunQueue.target_dag_id.in_(["ghost_a", "ghost_z"]))
)
if adrq_count != 2:
    print(f"FAIL: Both ADRQ rows should exist, found count={adrq_count}")
    sys.exit(1)

print("PASS: Multiple orphan DAGs logged in sorted order")
'''

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
        env={"PYTHONPATH": f"{REPO}/airflow-core/src:{REPO}/devel-common/src:{REPO}/task-sdk/src:{REPO}/shared"},
    )

    if result.returncode != 0:
        raise AssertionError(f"Test failed: {result.stderr}")
    assert "PASS:" in result.stdout, f"Expected PASS in output, got: {result.stdout}"


def test_adrq_rows_not_deleted():
    """
    F2P: AssetDagRunQueue rows are preserved (not deleted from database).

    The fix only removes DAGs from in-memory dictionaries (adrq_by_dag and dag_statuses),
    it does NOT delete rows from the asset_dag_run_queue table.
    """
    code = '''
import logging
import sys
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
from airflow.models.dag import DagModel
from airflow.models.assets import AssetModel, AssetDagRunQueue
from airflow.utils import timezone

# Create in-memory SQLite database
engine = create_engine("sqlite:///:memory:")
Session = sessionmaker(bind=engine)

# Create tables
from airflow.models.base import Base
Base.metadata.create_all(engine)

session = Session()

# Create orphan DAG
orphan_dag_id = "adrq_preserved_test"
orphan_uri = "test://asset_preserved"

asset = AssetModel(uri=orphan_uri)
session.add(asset)
session.flush()
asset_id = session.scalar(select(AssetModel.id).where(AssetModel.uri == orphan_uri))

dag_model = DagModel(
    dag_id=orphan_dag_id,
    bundle_name="testing",
    max_active_tasks=1,
    has_task_concurrency_limits=False,
    max_consecutive_failed_dag_runs=0,
    next_dagrun=timezone.datetime(2038, 1, 1),
    next_dagrun_create_after=timezone.datetime(2038, 1, 2),
    is_stale=False,
    has_import_errors=False,
    is_paused=False,
    asset_expression={"any": [{"uri": orphan_uri}]},
)
session.add(dag_model)
session.flush()

session.add(AssetDagRunQueue(asset_id=asset_id, target_dag_id=orphan_dag_id))
session.flush()

# Count ADRQ rows before calling dags_needing_dagruns
adrq_before = session.scalar(select(func.count()).select_from(AssetDagRunQueue))

# Call the method under test
_query, triggered_date_by_dag = DagModel.dags_needing_dagruns(session)

# Count ADRQ rows after calling dags_needing_dagruns
adrq_after = session.scalar(select(func.count()).select_from(AssetDagRunQueue))

# Verify ADRQ rows were NOT deleted
if adrq_before != adrq_after:
    print(f"FAIL: ADRQ rows were deleted! Before: {adrq_before}, After: {adrq_after}")
    sys.exit(1)

# Verify the specific row still exists
adrq_exists = session.scalar(
    select(func.count())
    .select_from(AssetDagRunQueue)
    .where(AssetDagRunQueue.target_dag_id == orphan_dag_id)
)
if adrq_exists != 1:
    print(f"FAIL: ADRQ row for {orphan_dag_id} should still exist")
    sys.exit(1)

print("PASS: ADRQ rows were preserved (not deleted)")
'''

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
        env={"PYTHONPATH": f"{REPO}/airflow-core/src:{REPO}/devel-common/src:{REPO}/task-sdk/src:{REPO}/shared"},
    )

    if result.returncode != 0:
        raise AssertionError(f"Test failed: {result.stderr}")
    assert "PASS:" in result.stdout, f"Expected PASS in output, got: {result.stdout}"


def test_repo_unit_tests_exist():
    """
    P2P: Verify that the repository's unit tests for this feature exist.

    The fix should include unit tests that verify the behavioral changes.
    These tests should exist in airflow-core/tests/unit/models/test_dag.py.
    """
    test_file = f"{REPO}/airflow-core/tests/unit/models/test_dag.py"

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


def test_repo_unit_tests_pass():
    """
    P2P: The repository's own unit tests for the fix should pass.

    This runs the specific unit tests that were added as part of the fix
    to ensure they work correctly with the patched code.
    """
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/unit/models/test_dag.py::TestDagModel::test_dags_needing_dagruns_skips_adrq_when_serialized_dag_missing",
            "tests/unit/models/test_dag.py::TestDagModel::test_dags_needing_dagruns_missing_serialized_debug_lists_sorted_dag_ids",
            "-v",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env={"PYTHONPATH": f"{REPO}/airflow-core/src:{REPO}/devel-common/src:{REPO}/task-sdk/src:{REPO}/shared"},
    )

    if result.returncode != 0:
        # Show the last 1000 characters of output for debugging
        output = result.stdout + result.stderr
        raise AssertionError(f"Repo unit tests failed:\n{output[-1000:]}")


def test_no_session_commit_in_dags_needing_dagruns():
    """
    P2P: The dags_needing_dagruns method must not call session.commit().

    Per Airflow conventions, methods with a session parameter should not
    call session.commit() - the caller manages the transaction.
    """
    dag_file = f"{REPO}/airflow-core/src/airflow/models/dag.py"

    with open(dag_file, "r") as f:
        content = f.read()

    # Find the dags_needing_dagruns method
    method_start = content.find("def dags_needing_dagruns")
    if method_start == -1:
        raise AssertionError("Method dags_needing_dagruns not found")

    # Find the end of the method (next method at same indentation level or class end)
    method_content = content[method_start:]

    # Find the next method definition at the same indentation level (4 spaces for class method)
    next_method = method_content.find("\n    def ", 1)
    if next_method == -1:
        method_end = len(content)
    else:
        method_end = method_start + next_method

    method_body = content[method_start:method_end]

    # Check that session.commit() is NOT called in the method
    if "session.commit()" in method_body:
        raise AssertionError("BUG: dags_needing_dagruns should not call session.commit()")


# =============================================================================
# Pass-to-Pass Tests: Repo CI/CD checks
# These ensure the fix doesn't break existing repository quality checks.
# =============================================================================


def test_repo_ruff_check():
    """P2P: Ruff linting passes on the modified dag.py file."""
    result = subprocess.run(
        [
            "bash", "-c",
            f". {REPO}/.venv/bin/activate && uv run --project {REPO}/airflow-core "
            f"ruff check {DAG_PY}"
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff check failed:\n{result.stderr}\n{result.stdout}"


def test_repo_ruff_format():
    """P2P: Ruff formatting check passes on the modified dag.py file."""
    result = subprocess.run(
        [
            "bash", "-c",
            f". {REPO}/.venv/bin/activate && uv run --project {REPO}/airflow-core "
            f"ruff format --check {DAG_PY}"
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff format check failed:\n{result.stderr}\n{result.stdout}"


def test_repo_mypy():
    """P2P: Mypy type checking passes on the modified dag.py file."""
    result = subprocess.run(
        [
            "bash", "-c",
            f". {REPO}/.venv/bin/activate && uv run --project {REPO}/airflow-core "
            f"mypy {DAG_PY}"
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Mypy check failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_repo_dags_needing_dagruns_tests():
    """P2P: Existing dags_needing_dagruns tests in the repo still pass.

    This runs the existing tests for dags_needing_dagruns to ensure the fix
    doesn't break any existing functionality.
    """
    result = subprocess.run(
        [
            "bash", "-c",
            f". {REPO}/.venv/bin/activate && uv run --project {REPO}/airflow-core "
            f"pytest {TEST_DAG_PY} -k 'dags_needing_dagruns' --tb=short -q"
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    if result.returncode != 0:
        output = result.stdout + result.stderr
        raise AssertionError(f"Repo dags_needing_dagruns tests failed:\n{output[-1000:]}")
