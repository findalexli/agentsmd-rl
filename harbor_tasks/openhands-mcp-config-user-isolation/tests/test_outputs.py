"""Test MCP config user-specific isolation fix.

This test verifies that MCP settings are properly isolated per user:
1. mcp_config is stored on org_member (not org)
2. SaasSettingsStore.load() reads from org_member.mcp_config
3. SaasSettingsStore.store() skips org.mcp_config, only saves to org_member
4. OrgUpdate model no longer includes mcp_config field
"""

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path("/workspace/OpenHands")
ENTERPRISE = REPO / "enterprise"


# =============================================================================
# PASS-TO-PASS TESTS (Repo CI/CD checks - must pass on both base and fixed)
# =============================================================================


def test_repo_python_syntax_valid():
    """All Python files in the repo should have valid syntax (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c", f"cd {REPO} && find enterprise -name '*.py' -exec python -m py_compile {} +"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Python syntax errors found:\n{result.stderr}"


def test_repo_migration_102_exists():
    """Migration 102 (down_revision for 103) should exist (pass_to_pass)."""
    migration_102 = ENTERPRISE / "migrations" / "versions" / "102_add_org_member_profile.py"
    # Check common naming patterns for migration 102
    migrations_dir = ENTERPRISE / "migrations" / "versions"
    if migrations_dir.exists():
        migration_files = list(migrations_dir.glob("102_*.py"))
        assert len(migration_files) > 0, "Migration 102 should exist as down_revision for 103"


def test_repo_storage_modules_syntax():
    """All storage module files should have valid syntax (pass_to_pass)."""
    storage_dir = ENTERPRISE / "storage"
    if not storage_dir.exists():
        pytest.skip("Storage directory not found")

    py_files = list(storage_dir.glob("*.py"))
    assert len(py_files) > 0, "Storage directory should contain Python files"

    for py_file in py_files:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(py_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Syntax error in {py_file}: {result.stderr}"


def test_repo_routes_modules_syntax():
    """All routes module files should have valid syntax (pass_to_pass)."""
    routes_dir = ENTERPRISE / "server" / "routes"
    if not routes_dir.exists():
        pytest.skip("Routes directory not found")

    py_files = list(routes_dir.glob("*.py"))
    assert len(py_files) > 0, "Routes directory should contain Python files"

    for py_file in py_files:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(py_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Syntax error in {py_file}: {result.stderr}"


def test_repo_migrations_dir_structure():
    """Migrations directory should have expected structure (pass_to_pass)."""
    migrations_dir = ENTERPRISE / "migrations" / "versions"
    assert migrations_dir.exists(), "Migrations versions directory should exist"

    migration_files = list(migrations_dir.glob("*.py"))
    assert len(migration_files) > 0, "Should have migration files"

    # Check that migrations have valid Python syntax
    for migration_file in migration_files[:10]:  # Check first 10
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(migration_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Migration {migration_file.name} has syntax errors"


def test_repo_modified_files_syntax():
    """Files modified by PR have valid Python syntax (pass_to_pass).\n    
    This test runs py_compile on the specific files that the PR modifies:
    - saas_settings_store.py
    - org_member.py  
    - org_models.py
    """
    modified_files = [
        ENTERPRISE / "storage" / "saas_settings_store.py",
        ENTERPRISE / "storage" / "org_member.py",
        ENTERPRISE / "server" / "routes" / "org_models.py",
    ]
    
    for py_file in modified_files:
        if py_file.exists():
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(py_file)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, f"Syntax error in {py_file}: {result.stderr}"


def test_repo_alembic_ini_exists():
    """Alembic configuration file should exist for migrations (pass_to_pass)."""
    alembic_ini = ENTERPRISE / "alembic.ini"
    alembic_env = ENTERPRISE / "migrations" / "env.py"
    
    assert alembic_ini.exists() or (ENTERPRISE / "pyproject.toml").exists(), "Alembic config should exist"
    assert alembic_env.exists(), "Alembic env.py should exist"
    
    # Check env.py has valid syntax
    if alembic_env.exists():
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(alembic_env)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Syntax error in alembic env.py: {result.stderr}"


def test_repo_storage_init_syntax():
    """Storage package init file should have valid syntax (pass_to_pass)."""
    init_file = ENTERPRISE / "storage" / "__init__.py"
    if init_file.exists():
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(init_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Syntax error in storage/__init__.py: {result.stderr}"


def test_repo_org_store_syntax():
    """Org storage module should have valid Python syntax (pass_to_pass)."""
    org_store = ENTERPRISE / "storage" / "org.py"
    if org_store.exists():
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(org_store)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Syntax error in org.py: {result.stderr}"


def test_migration_file_exists():
    """Migration 103 should add mcp_config column to org_member table."""
    migration_file = (
        ENTERPRISE
        / "migrations"
        / "versions"
        / "103_add_mcp_config_to_org_member.py"
    )
    assert migration_file.exists(), "Migration file 103_add_mcp_config_to_org_member.py must exist"

    content = migration_file.read_text()

    # Should add mcp_config column to org_member
    assert "op.add_column('org_member'" in content, "Migration must add column to org_member"
    assert "mcp_config" in content, "Migration must add mcp_config column"
    assert "sa.JSON()" in content or "JSON" in content, "mcp_config should be JSON type"

    # Should handle migration of existing org-level configs
    assert "UPDATE org_member" in content, "Migration should migrate existing configs to members"
    assert "org WHERE mcp_config IS NOT NULL" in content, "Migration should find orgs with existing configs"


def test_migration_has_downgrade():
    """Migration should include downgrade to drop the column."""
    migration_file = (
        ENTERPRISE
        / "migrations"
        / "versions"
        / "103_add_mcp_config_to_org_member.py"
    )
    assert migration_file.exists(), "Migration file must exist"

    content = migration_file.read_text()
    assert "def downgrade()" in content, "Migration must have downgrade function"
    assert "op.drop_column('org_member', 'mcp_config')" in content, "Downgrade must drop mcp_config column"


def test_org_member_model_has_mcp_config():
    """OrgMember model should have mcp_config column defined."""
    org_member_file = ENTERPRISE / "storage" / "org_member.py"
    assert org_member_file.exists(), "org_member.py must exist"

    content = org_member_file.read_text()

    # Should import JSON from sqlalchemy
    assert "from sqlalchemy import JSON" in content or "JSON" in content, "Must import JSON type"

    # Should have mcp_config column
    assert "mcp_config = Column(JSON" in content or "mcp_config = Column" in content, "Must have mcp_config column"


def test_saas_settings_store_load_reads_from_org_member():
    """SaasSettingsStore.load() should read mcp_config from org_member, not org."""
    store_file = ENTERPRISE / "storage" / "saas_settings_store.py"
    assert store_file.exists(), "saas_settings_store.py must exist"

    content = store_file.read_text()

    # Should check org_member.mcp_config in load()
    assert "org_member.mcp_config" in content, "load() must check org_member.mcp_config"

    # Should set kwargs['mcp_config'] from org_member
    pattern = r"if org_member\.mcp_config is not None:\s*kwargs\['mcp_config'\] = org_member\.mcp_config"
    assert re.search(pattern, content), "load() must set mcp_config from org_member when not None"

    # Should have comment about user-specific storage
    assert "user-specific" in content.lower() or "org_member" in content, "Should document user-specific storage"


def test_saas_settings_store_store_skips_org_mcp_config():
    """SaasSettingsStore.store() should skip mcp_config when storing to org."""
    store_file = ENTERPRISE / "storage" / "saas_settings_store.py"
    assert store_file.exists(), "saas_settings_store.py must exist"

    content = store_file.read_text()

    # Should skip mcp_config for org
    assert "if key == 'mcp_config' and model is org:" in content, "store() must skip mcp_config for org"
    assert "continue" in content, "store() must continue to skip org.mcp_config"

    # Should have comment explaining why
    assert "user-specific" in content.lower() or "org_member" in content.lower(), "Should document user-specific behavior"


def test_org_update_model_no_mcp_config():
    """OrgUpdate model should NOT have mcp_config field."""
    org_models_file = ENTERPRISE / "server" / "routes" / "org_models.py"
    assert org_models_file.exists(), "org_models.py must exist"

    content = org_models_file.read_text()

    # Parse the file to find OrgUpdate class
    tree = ast.parse(content)

    org_update_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "OrgUpdate":
            org_update_class = node
            break

    assert org_update_class is not None, "Must find OrgUpdate class"

    # Check that mcp_config is NOT in the class annotations
    for stmt in org_update_class.body:
        if isinstance(stmt, ast.AnnAssign):
            target = stmt.target
            if isinstance(target, ast.Name) and target.id == "mcp_config":
                pytest.fail("OrgUpdate should NOT have mcp_config field - it was removed")


def test_store_method_preserves_other_fields():
    """store() should still save other fields to org - only skip mcp_config."""
    store_file = ENTERPRISE / "storage" / "saas_settings_store.py"
    assert store_file.exists(), "saas_settings_store.py must exist"

    content = store_file.read_text()

    # The fix should only skip mcp_config for org, not all fields
    # Find the loop that iterates over models
    assert "for model in (user, org, org_member):" in content, "store() should iterate over all models"
    assert "for key, value in kwargs.items():" in content, "store() should iterate over kwargs"

    # The skip condition should be specific to mcp_config and org
    assert "if key == 'mcp_config' and model is org:" in content, "Must specifically skip mcp_config for org only"


def test_load_method_checks_for_none():
    """load() should check if org_member.mcp_config is not None before using it."""
    store_file = ENTERPRISE / "storage" / "saas_settings_store.py"
    assert store_file.exists(), "saas_settings_store.py must exist"

    content = store_file.read_text()

    # Should check for None before assigning
    assert "if org_member.mcp_config is not None:" in content, "load() must check for None before using mcp_config"


@pytest.mark.skipif(
    not (ENTERPRISE / "tests" / "unit" / "test_saas_settings_store.py").exists(),
    reason="Unit test file not available"
)
def test_unit_tests_exist_for_mcp_config_isolation():
    """Unit tests should exist for MCP config user-specific behavior."""
    test_file = ENTERPRISE / "tests" / "unit" / "test_saas_settings_store.py"
    assert test_file.exists(), "Unit test file must exist"

    content = test_file.read_text()

    # Should have tests for user-specific behavior
    assert "test_store_saves_mcp_config_to_user_org_member_only" in content or \
           "test_store_saves_mcp_config" in content, "Must have test for saving to org_member only"

    assert "test_store_does_not_update_org_mcp_config" in content or \
           "test_store_does_not_update_org" in content, "Must have test for not updating org.mcp_config"

    assert "test_load_returns_user_specific_mcp_config" in content or \
           "test_load_returns_user" in content, "Must have test for loading user-specific config"


def test_migration_has_correct_revision():
    """Migration should have correct revision ID and down_revision."""
    migration_file = (
        ENTERPRISE
        / "migrations"
        / "versions"
        / "103_add_mcp_config_to_org_member.py"
    )
    assert migration_file.exists(), "Migration file must exist"

    content = migration_file.read_text()

    # Should have revision 103
    assert "revision: str = '103'" in content or "revision = '103'" in content, "Must have correct revision ID"

    # Should depend on revision 102
    assert "down_revision" in content and "'102'" in content, "Must have correct down_revision to 102"
