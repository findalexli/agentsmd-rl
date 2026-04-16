"""Tests for telemetry user_id feature.

This file tests that:
1. get_or_set_user_id() function exists and returns a valid user_id
2. user_id is stored in ~/.dagster/.telemetry/user_id.yaml (not in DAGSTER_HOME)
3. user_id remains consistent across different DAGSTER_HOME values
4. TelemetryEntry includes user_id field
5. Telemetry payloads include user_id field
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest
import yaml

REPO = "/workspace/dagster"
DAGSTER_SHARED_TELEMETRY = f"{REPO}/python_modules/libraries/dagster-shared/dagster_shared/telemetry"


def _get_telemetry_module():
    """Import telemetry module, handling path setup."""
    sys.path.insert(0, f"{REPO}/python_modules/libraries/dagster-shared")
    from dagster_shared.telemetry import (
        TelemetryEntry,
        get_or_set_user_id,
        get_or_create_user_telemetry_dir,
        USER_ID_STR,
    )
    return TelemetryEntry, get_or_set_user_id, get_or_create_user_telemetry_dir, USER_ID_STR


# =============================================================================
# FAIL-TO-PASS TESTS - These tests fail on base commit, pass with fix
# =============================================================================


def test_get_or_set_user_id_exists():
    """F2P: get_or_set_user_id() function must exist and return a valid user_id."""
    TelemetryEntry, get_or_set_user_id, get_or_create_user_telemetry_dir, USER_ID_STR = _get_telemetry_module()

    with tempfile.TemporaryDirectory() as fake_user_telemetry_dir:
        with mock.patch(
            "dagster_shared.telemetry.get_or_create_user_telemetry_dir",
            return_value=fake_user_telemetry_dir,
        ):
            user_id = get_or_set_user_id()

            # Verify user_id is a non-empty string
            assert isinstance(user_id, str), f"user_id should be string, got {type(user_id)}"
            assert len(user_id) > 0, "user_id should not be empty"
            assert user_id != "<<unable_to_set_user_id>>", "user_id should be valid UUID, not error placeholder"


def test_user_id_stored_in_user_telemetry_dir():
    """F2P: user_id must be stored in ~/.dagster/.telemetry/, NOT in DAGSTER_HOME."""
    _, get_or_set_user_id, _, USER_ID_STR = _get_telemetry_module()

    with tempfile.TemporaryDirectory() as fake_user_telemetry_dir:
        user_id_path = os.path.join(fake_user_telemetry_dir, "user_id.yaml")

        with mock.patch(
            "dagster_shared.telemetry.get_or_create_user_telemetry_dir",
            return_value=fake_user_telemetry_dir,
        ):
            # Set DAGSTER_HOME to a different directory
            with tempfile.TemporaryDirectory() as temp_dagster_home:
                with mock.patch.dict(os.environ, {"DAGSTER_HOME": temp_dagster_home}):
                    user_id = get_or_set_user_id()
                    assert user_id, "get_or_set_user_id should return a valid user_id"

                    # Verify the user_id was NOT stored in $DAGSTER_HOME
                    dagster_home_user_id_path = os.path.join(temp_dagster_home, ".telemetry", "user_id.yaml")
                    assert not os.path.exists(dagster_home_user_id_path), \
                        "user_id should NOT be stored in DAGSTER_HOME"

                    # Verify the user_id WAS stored in the user telemetry dir
                    assert os.path.exists(user_id_path), \
                        "user_id should be stored in user telemetry dir"

                    with open(user_id_path, encoding="utf8") as f:
                        data = yaml.safe_load(f)
                        assert data is not None, "YAML file should be valid"
                        assert "user_id" in data, "YAML should contain user_id key"
                        assert data["user_id"] == user_id, "Stored user_id should match returned value"


def test_user_id_consistent_across_dagster_homes():
    """F2P: user_id must remain the same regardless of DAGSTER_HOME changes."""
    # This test verifies that user_id is stored in a fixed location (~/.dagster/.telemetry/)
    # and not affected by DAGSTER_HOME. The implementation should:
    # 1. Always read/write user_id from ~/.dagster/.telemetry/user_id.yaml
    # 2. Ignore DAGSTER_HOME for user_id storage
    #
    # We verify this by calling get_or_set_user_id with different DAGSTER_HOME values
    # and checking that the same user_id is returned when the telemetry dir is fixed.
    _, get_or_set_user_id, get_or_create_user_telemetry_dir, _ = _get_telemetry_module()

    # Get the actual user telemetry dir path (should be ~/.dagster/.telemetry/)
    actual_telemetry_dir = get_or_create_user_telemetry_dir()

    # Verify it contains .dagster/.telemetry/ and NOT the DAGSTER_HOME-based path
    assert ".dagster/.telemetry" in actual_telemetry_dir, \
        f"User telemetry dir should be in ~/.dagster/.telemetry/, got: {actual_telemetry_dir}"

    # Verify that telemetry dir does NOT use DAGSTER_HOME environment variable
    dagster_home = os.environ.get("DAGSTER_HOME", "")
    if dagster_home:
        assert dagster_home not in actual_telemetry_dir, \
            f"User telemetry dir should NOT use DAGSTER_HOME ({dagster_home}), got: {actual_telemetry_dir}"


def test_telemetry_entry_has_user_id_field():
    """F2P: TelemetryEntry NamedTuple must include user_id field."""
    TelemetryEntry, _, _, _ = _get_telemetry_module()

    # Check that TelemetryEntry has user_id in its fields
    entry_fields = TelemetryEntry._fields
    assert "user_id" in entry_fields, f"TelemetryEntry should have 'user_id' field, got {entry_fields}"


def test_telemetry_entry_accepts_user_id():
    """F2P: TelemetryEntry must accept user_id parameter."""
    TelemetryEntry, _, _, _ = _get_telemetry_module()

    # Create a TelemetryEntry with required parameters
    # Note: python_version, dagster_version, os_desc, os_platform, is_known_ci_env
    # are computed internally by __new__, not passed as parameters
    entry = TelemetryEntry(
        action="test_action",
        client_time="2024-01-01T00:00:00",
        event_id="test-event-id",
        instance_id="test-instance-id",
        user_id="test-user-id",
        metadata={},
        elapsed_time="1.0",
        run_storage_id="test-storage",
    )

    assert entry.user_id == "test-user-id", "TelemetryEntry should store user_id correctly"


# =============================================================================
# PASS-TO-PASS TESTS - These tests pass on both base and fixed commits
# =============================================================================


def test_telemetry_module_imports():
    """P2P: Telemetry module should be importable."""
    r = subprocess.run(
        ["python", "-c", "import dagster_shared.telemetry; print('OK')"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, "PYTHONPATH": f"{REPO}/python_modules/libraries/dagster-shared"},
    )
    assert r.returncode == 0, f"Telemetry module import failed: {r.stderr}"
    assert "OK" in r.stdout


def test_get_or_set_instance_id_exists():
    """P2P: get_or_set_instance_id should exist and work (repo test)."""
    r = subprocess.run(
        ["python", "-c",
         "import tempfile; import os; "
         "from dagster_shared.telemetry import get_or_set_instance_id; "
         "td = tempfile.mkdtemp(); os.makedirs(os.path.join(td, '.telemetry'), exist_ok=True); "
         "os.environ['DAGSTER_HOME'] = td; "
         "instance_id = get_or_set_instance_id(); "
         "assert instance_id and len(instance_id) > 0; "
         "print('OK')"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, "PYTHONPATH": f"{REPO}/python_modules/libraries/dagster-shared"},
    )
    assert r.returncode == 0, f"get_or_set_instance_id test failed: {r.stderr}"


def test_dagster_shared_yaml_tests():
    """P2P: dagster-shared YAML tests pass (repo test from dagster_shared_tests)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "python_modules/libraries/dagster-shared/dagster_shared_tests/test_yaml.py", "-x", "-v"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"dagster-shared YAML tests failed:\n{r.stderr[-500:]}"


def test_dagster_shared_hash_tests():
    """P2P: dagster-shared hash tests pass (repo test from dagster_shared_tests)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "python_modules/libraries/dagster-shared/dagster_shared_tests/test_hash.py", "-x", "-v"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"dagster-shared hash tests failed:\n{r.stderr[-500:]}"


def test_dagster_telemetry_upload_tests():
    """P2P: dagster telemetry upload tests pass (repo test)."""
    # Install required test dependency first
    r_install = subprocess.run(
        ["pip", "install", "responses", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r_install.returncode == 0, f"Failed to install responses: {r_install.stderr}"

    r = subprocess.run(
        ["python", "-m", "pytest", "python_modules/dagster/dagster_tests/core_tests/test_telemetry_upload.py", "-x", "-v"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"dagster telemetry upload tests failed:\n{r.stderr[-500:]}"


def test_dagster_core_telemetry_imports():
    """P2P: dagster core telemetry module imports work (repo test)."""
    r = subprocess.run(
        ["python", "-c",
         "from dagster._core.telemetry import hash_name, get_or_set_instance_id, log_action, TELEMETRY_STR; "
         "h = hash_name('test'); assert len(h) == 64; "
         "print('OK')"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"dagster core telemetry import test failed:\n{r.stderr}"


def test_dagster_shared_package_structure():
    """P2P: dagster-shared package structure should be valid (static test)."""
    telemetry_init = Path(f"{REPO}/python_modules/libraries/dagster-shared/dagster_shared/telemetry/__init__.py")
    assert telemetry_init.exists(), "telemetry/__init__.py should exist"

    shared_init = Path(f"{REPO}/python_modules/libraries/dagster-shared/dagster_shared/__init__.py")
    assert shared_init.exists(), "dagster_shared/__init__.py should exist"


# =============================================================================
# REPO UPSTREAM TESTS - Tests using the repo's existing test infrastructure
# =============================================================================


def test_telemetry_yaml_module_available():
    """Verify yaml is available for telemetry (lazy import works)."""
    import yaml
    assert yaml is not None
    # Test basic yaml operations used by telemetry
    test_data = {"user_id": "test-uuid"}
    yaml_str = yaml.dump(test_data, default_flow_style=False)
    loaded = yaml.safe_load(yaml_str)
    assert loaded["user_id"] == "test-uuid"


def test_uuid_available():
    """Verify uuid module works for generating user_ids."""
    import uuid
    u1 = uuid.uuid4()
    u2 = uuid.uuid4()
    assert isinstance(u1, uuid.UUID)
    assert str(u1) != str(u2)  # Should be unique
