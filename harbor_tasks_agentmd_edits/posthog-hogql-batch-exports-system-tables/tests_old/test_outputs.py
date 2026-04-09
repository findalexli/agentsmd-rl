"""
Task: posthog-hogql-batch-exports-system-tables
Repo: PostHog/posthog @ 05600e36c426ef5128519dc60c7ec1d416da8bc0
PR:   53205

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/posthog"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files parse without errors."""
    system_py = Path(f"{REPO}/posthog/hogql/database/schema/system.py")
    src = system_py.read_text()
    ast.parse(src)


# [repo_tests] pass_to_pass - ruff lint check
def test_repo_ruff_check():
    """Repo's ruff lint check passes on modified file (pass_to_pass)."""
    # Install ruff if not present
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "ruff"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "posthog/hogql/database/schema/system.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass - ruff format check
def test_repo_ruff_format():
    """Repo's ruff format check passes on modified file (pass_to_pass)."""
    # Install ruff if not present
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "ruff"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", "posthog/hogql/database/schema/system.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass - Python compilation check
def test_repo_python_compile():
    """Modified Python files compile without errors (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", "posthog/hogql/database/schema/system.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Python compilation failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests (subprocess-based)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass - BEHAVIORAL (subprocess)
def test_batch_exports_table_defined():
    """batch_exports PostgresTable is defined with all required fields - verified by import."""
    code = """
import sys
sys.path.insert(0, '/workspace/posthog')

# Import the module - this will fail if the code has errors
from posthog.hogql.database.schema.system import batch_exports

# Verify it's the correct type and has required attributes
assert batch_exports.name == "batch_exports", f"Expected name 'batch_exports', got {batch_exports.name}"
assert batch_exports.postgres_table_name == "posthog_batchexport", f"Wrong postgres_table_name: {batch_exports.postgres_table_name}"
assert batch_exports.access_scope == "batch_export", f"Wrong access_scope: {batch_exports.access_scope}"

# Check required fields exist
required_fields = {
    "id", "team_id", "name", "model", "interval", "paused", "deleted",
    "destination_id", "timezone", "interval_offset", "created_at",
    "last_updated_at", "last_paused_at", "start_at", "end_at"
}
fields = set(batch_exports.fields.keys())
missing = required_fields - fields
assert not missing, f"Missing required fields: {missing}"

# Check special ExpressionField for paused/deleted (using hidden boolean fields)
from posthog.hogql.database.common import ExpressionField
assert "paused" in fields, "paused field must exist"
assert "deleted" in fields, "deleted field must exist"

print("PASS: batch_exports table defined correctly")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [pr_diff] fail_to_pass - BEHAVIORAL (subprocess)
def test_batch_export_backfills_table_defined():
    """batch_export_backfills PostgresTable is defined with all required fields - verified by import."""
    code = """
import sys
sys.path.insert(0, '/workspace/posthog')

# Import the module - this will fail if the code has errors
from posthog.hogql.database.schema.system import batch_export_backfills

# Verify it's the correct type and has required attributes
assert batch_export_backfills.name == "batch_export_backfills", f"Expected name 'batch_export_backfills', got {batch_export_backfills.name}"
assert batch_export_backfills.postgres_table_name == "posthog_batchexportbackfill", f"Wrong postgres_table_name: {batch_export_backfills.postgres_table_name}"
assert batch_export_backfills.access_scope == "batch_export", f"Wrong access_scope: {batch_export_backfills.access_scope}"

# Check required fields exist
required_fields = {
    "id", "team_id", "batch_export_id", "start_at", "end_at", "status",
    "created_at", "finished_at", "last_updated_at", "total_records_count"
}
fields = set(batch_export_backfills.fields.keys())
missing = required_fields - fields
assert not missing, f"Missing required fields: {missing}"

print("PASS: batch_export_backfills table defined correctly")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [pr_diff] fail_to_pass - BEHAVIORAL (subprocess)
def test_system_tables_registered():
    """Both tables are registered in SystemTables class dictionary - verified by runtime check."""
    code = """
import sys
sys.path.insert(0, '/workspace/posthog')

# Import the SystemTables class
from posthog.hogql.database.schema.system import SystemTables, batch_exports, batch_export_backfills

# Create an instance to check the tables dict
# Note: SystemTables inherits from TableNode and has a tables dict
instance = SystemTables()

# Check both tables are registered
assert "batch_exports" in instance.tables, "batch_exports not registered in SystemTables"
assert "batch_export_backfills" in instance.tables, "batch_export_backfills not registered in SystemTables"

# Verify they point to the correct table objects
assert instance.tables["batch_exports"].table == batch_exports, "batch_exports table reference mismatch"
assert instance.tables["batch_export_backfills"].table == batch_export_backfills, "batch_export_backfills table reference mismatch"

print("PASS: Both tables registered in SystemTables")
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [pr_diff] fail_to_pass
def test_skill_md_updated():
    """SKILL.md updated with link to batch exports reference doc."""
    skill_md = Path(f"{REPO}/products/posthog_ai/skills/query-examples/SKILL.md")
    assert skill_md.exists(), "SKILL.md must exist"

    content = skill_md.read_text()

    # Check for the batch exports link
    assert "models-batch-exports.md" in content, \
        "SKILL.md must contain a link to models-batch-exports.md"
    assert "Batch exports" in content or "batch exports" in content.lower(), \
        "SKILL.md must reference 'Batch exports' in the link text"


# [pr_diff] fail_to_pass
def test_batch_exports_reference_doc_created():
    """models-batch-exports.md reference documentation created with table schemas."""
    ref_doc = Path(f"{REPO}/products/posthog_ai/skills/query-examples/references/models-batch-exports.md")
    assert ref_doc.exists(), "models-batch-exports.md reference doc must be created"

    content = ref_doc.read_text()

    # Check for key sections and content
    assert "system.batch_exports" in content, \
        "Reference doc must document system.batch_exports"
    assert "system.batch_export_backfills" in content, \
        "Reference doc must document system.batch_export_backfills"

    # Check for BatchExport section
    assert "BatchExport" in content, \
        "Reference doc must have BatchExport section"

    # Check for BatchExportBackfill section
    assert "BatchExportBackfill" in content or "backfills" in content.lower(), \
        "Reference doc must document backfills"

    # Check for key columns mentioned
    assert "team_id" in content, "Must document team_id column"
    assert "destination_id" in content or "batch_export_id" in content, \
        "Must document relationship fields"
