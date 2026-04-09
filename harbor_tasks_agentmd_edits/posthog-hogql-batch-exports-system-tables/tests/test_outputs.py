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
# Fail-to-pass (pr_diff) — core behavioral tests (source inspection)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass - source inspection
def test_batch_exports_table_defined():
    """batch_exports PostgresTable is defined with all required fields."""
    system_py = Path(f"{REPO}/posthog/hogql/database/schema/system.py")
    src = system_py.read_text()

    # Check batch_exports table is defined
    assert "batch_exports: PostgresTable = PostgresTable(" in src, \
        "batch_exports PostgresTable must be defined"

    # Check required attributes
    assert 'name="batch_exports"' in src, "batch_exports must have name='batch_exports'"
    assert 'postgres_table_name="posthog_batchexport"' in src, \
        "batch_exports must have postgres_table_name='posthog_batchexport'"
    assert 'access_scope="batch_export"' in src, \
        "batch_exports must have access_scope='batch_export'"

    # Check required fields exist
    required_patterns = [
        'StringDatabaseField(name="id")',
        'IntegerDatabaseField(name="team_id")',
        'StringDatabaseField(name="name")',
        'StringDatabaseField(name="interval")',
        'StringDatabaseField(name="destination_id")',
        'DateTimeDatabaseField(name="created_at")',
        'DateTimeDatabaseField(name="last_updated_at")',
    ]
    for pattern in required_patterns:
        assert pattern in src, f"batch_exports must contain field pattern: {pattern}"


# [pr_diff] fail_to_pass - source inspection
def test_batch_export_backfills_table_defined():
    """batch_export_backfills PostgresTable is defined with all required fields."""
    system_py = Path(f"{REPO}/posthog/hogql/database/schema/system.py")
    src = system_py.read_text()

    # Check batch_export_backfills table is defined
    assert "batch_export_backfills: PostgresTable = PostgresTable(" in src, \
        "batch_export_backfills PostgresTable must be defined"

    # Check required attributes
    assert 'name="batch_export_backfills"' in src, \
        "batch_export_backfills must have name='batch_export_backfills'"
    assert 'postgres_table_name="posthog_batchexportbackfill"' in src, \
        "batch_export_backfills must have postgres_table_name='posthog_batchexportbackfill'"
    assert 'access_scope="batch_export"' in src, \
        "batch_export_backfills must have access_scope='batch_export'"

    # Check required fields exist
    required_patterns = [
        'StringDatabaseField(name="id")',
        'IntegerDatabaseField(name="team_id")',
        'StringDatabaseField(name="batch_export_id")',
        'StringDatabaseField(name="status")',
        'DateTimeDatabaseField(name="created_at")',
        'DateTimeDatabaseField(name="last_updated_at")',
    ]
    for pattern in required_patterns:
        assert pattern in src, f"batch_export_backfills must contain field pattern: {pattern}"


# [pr_diff] fail_to_pass - source inspection
def test_system_tables_registered():
    """Both tables are registered in SystemTables class dictionary."""
    system_py = Path(f"{REPO}/posthog/hogql/database/schema/system.py")
    src = system_py.read_text()

    # Check both tables are registered in SystemTables class
    assert '"batch_exports": TableNode(name="batch_exports"' in src, \
        "batch_exports must be registered in SystemTables"
    assert '"batch_export_backfills": TableNode(name="batch_export_backfills"' in src, \
        "batch_export_backfills must be registered in SystemTables"


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
