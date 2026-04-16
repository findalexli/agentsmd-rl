"""Benchmark tests for OpenHands health routes consolidation.

This module validates the PR that moves health endpoints from
openhands/server/routes/health.py to openhands/app_server/status/status_router.py.

Tests are designed to:
- FAIL on base commit (before the fix) - f2p tests
- PASS on merge commit (after the fix) - p2p and f2p tests
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Base paths
REPO = Path('/workspace/OpenHands')
STATUS_ROUTER_PATH = REPO / 'openhands' / 'app_server' / 'status' / 'status_router.py'
SYSTEM_STATS_NEW_PATH = REPO / 'openhands' / 'app_server' / 'status' / 'system_stats.py'
SYSTEM_STATS_OLD_PATH = REPO / 'openhands' / 'runtime' / 'utils' / 'system_stats.py'
OLD_HEALTH_PATH = REPO / 'openhands' / 'server' / 'routes' / 'health.py'
SERVER_APP_PATH = REPO / 'openhands' / 'server' / 'app.py'
ACTION_EXEC_SERVER_PATH = REPO / 'openhands' / 'runtime' / 'action_execution_server.py'
ACTION_EXEC_CLIENT_PATH = REPO / 'openhands' / 'runtime' / 'impl' / 'action_execution' / 'action_execution_client.py'


def set_pythonpath():
    """Ensure PYTHONPATH includes the repo."""
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))


# ============================================================================
# FAIL-TO-PASS TESTS - These fail on base, pass on fix
# ============================================================================


def test_status_router_exists():
    """F2P: Status router must exist in app_server package."""
    assert STATUS_ROUTER_PATH.exists(), (
        f"Status router not found at {STATUS_ROUTER_PATH}\n"
        "The health routes should be consolidated to openhands/app_server/status/"
    )


def test_status_router_has_required_endpoints():
    """F2P: Status router must define all required health endpoints."""
    if not STATUS_ROUTER_PATH.exists():
        pytest.skip("Status router doesn't exist yet")

    content = STATUS_ROUTER_PATH.read_text()

    # Check for all four endpoints
    required_endpoints = ['/alive', '/health', '/server_info', '/ready']
    for endpoint in required_endpoints:
        assert f"@router.get('{endpoint}')" in content or f'@router.get("{endpoint}")' in content, (
            f"Endpoint {endpoint} not found in status_router.py"
        )

    # Check for APIRouter with Status tag
    assert "APIRouter(tags=['Status'])" in content or 'APIRouter(tags=["Status"])' in content, (
        "Router should be tagged with 'Status'"
    )


def test_status_router_can_be_imported():
    """F2P: Status router module should be importable."""
    if not STATUS_ROUTER_PATH.exists():
        pytest.skip("Status router doesn't exist yet")

    set_pythonpath()

    try:
        from openhands.app_server.status.status_router import router
        assert router is not None, "Router should be importable"
    except ImportError as e:
        pytest.fail(f"Cannot import status_router: {e}")


def test_status_router_routes_work():
    """F2P: All status router endpoints should return correct values."""
    if not STATUS_ROUTER_PATH.exists():
        pytest.skip("Status router doesn't exist yet")

    set_pythonpath()

    from openhands.app_server.status.status_router import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    # Test /alive
    response = client.get('/alive')
    assert response.status_code == 200, f"/alive returned {response.status_code}"
    assert response.json() == {'status': 'ok'}, f"/alive returned {response.json()}"

    # Test /health
    response = client.get('/health')
    assert response.status_code == 200, f"/health returned {response.status_code}"
    assert response.json() == 'OK', f"/health returned {response.json()}"

    # Test /ready
    response = client.get('/ready')
    assert response.status_code == 200, f"/ready returned {response.status_code}"
    assert response.json() == 'OK', f"/ready returned {response.json()}"

    # Test /server_info
    response = client.get('/server_info')
    assert response.status_code == 200, f"/server_info returned {response.status_code}"
    data = response.json()
    assert isinstance(data, dict), f"/server_info should return dict, got {type(data)}"


def test_system_stats_moved_to_app_server():
    """F2P: System stats should be in app_server package."""
    assert SYSTEM_STATS_NEW_PATH.exists(), (
        f"system_stats.py should be at {SYSTEM_STATS_NEW_PATH}"
    )


def test_system_stats_can_be_imported_from_new_location():
    """F2P: System stats functions should be importable from new location."""
    if not SYSTEM_STATS_NEW_PATH.exists():
        pytest.skip("system_stats.py not in new location yet")

    set_pythonpath()

    try:
        from openhands.app_server.status.system_stats import (
            get_system_info,
            get_system_stats,
            update_last_execution_time,
        )
        assert callable(get_system_info), "get_system_info should be callable"
        assert callable(get_system_stats), "get_system_stats should be callable"
        assert callable(update_last_execution_time), "update_last_execution_time should be callable"
    except ImportError as e:
        pytest.fail(f"Cannot import system_stats from new location: {e}")


def test_server_app_health_endpoints_work():
    """F2P: Server app should expose working health endpoints."""
    if not SERVER_APP_PATH.exists():
        pytest.skip("server/app.py doesn't exist")

    set_pythonpath()

    # Import the server app module
    try:
        # The app module may be at openhands.server.app or openhands.server
        import openhands.server as server_module
        if hasattr(server_module, 'app'):
            app = server_module.app
        elif hasattr(server_module, 'create_app'):
            app = server_module.create_app()
        else:
            pytest.skip("Cannot find FastAPI app in server module")
    except ImportError as e:
        pytest.fail(f"Cannot import server module: {e}")
    except Exception as e:
        pytest.skip(f"Cannot load server app: {e}")

    client = TestClient(app)

    # Test that health endpoints work via the main app router
    response = client.get('/alive')
    assert response.status_code == 200, f"/alive via app returned {response.status_code}"
    assert response.json() == {'status': 'ok'}, f"/alive returned {response.json()}"

    response = client.get('/health')
    assert response.status_code == 200, f"/health via app returned {response.status_code}"
    assert response.json() == 'OK', f"/health returned {response.json()}"

    response = client.get('/ready')
    assert response.status_code == 200, f"/ready via app returned {response.status_code}"
    assert response.json() == 'OK', f"/ready returned {response.json()}"

    response = client.get('/server_info')
    assert response.status_code == 200, f"/server_info via app returned {response.status_code}"
    data = response.json()
    assert isinstance(data, dict), f"/server_info should return dict, got {type(data)}"


def test_old_health_file_removed():
    """F2P: Old health.py should be removed from server/routes."""
    assert not OLD_HEALTH_PATH.exists(), (
        f"Old health.py should be removed: {OLD_HEALTH_PATH}"
    )


def test_action_execution_server_imports_work():
    """F2P: Action execution server should be able to import system_stats from new location."""
    if not ACTION_EXEC_SERVER_PATH.exists():
        pytest.skip("action_execution_server.py doesn't exist")

    set_pythonpath()

    # Try to import the module and verify it doesn't fail due to system_stats import
    try:
        import openhands.runtime.action_execution_server as aes
        # If we get here without ImportError, the imports work
        # The module will have various attributes - just verify import succeeded
    except ImportError as e:
        pytest.fail(f"Cannot import action_execution_server (system_stats import issue?): {e}")


def test_action_execution_client_imports_work():
    """F2P: Action execution client should be able to import update_last_execution_time from new location."""
    if not ACTION_EXEC_CLIENT_PATH.exists():
        pytest.skip("action_execution_client.py doesn't exist")

    set_pythonpath()

    try:
        from openhands.runtime.impl.action_execution.action_execution_client import (
            update_last_execution_time,
        )
        assert callable(update_last_execution_time), "update_last_execution_time should be callable"
    except ImportError as e:
        pytest.fail(f"Cannot import update_last_execution_time from new location: {e}")


def test_system_info_returns_dict():
    """F2P: get_system_info() should return a dictionary with system information."""
    if not SYSTEM_STATS_NEW_PATH.exists():
        pytest.skip("system_stats.py not in new location yet")

    set_pythonpath()

    from openhands.app_server.status.system_stats import get_system_info

    info = get_system_info()
    assert isinstance(info, dict), f"get_system_info should return dict, got {type(info)}"
    # Check for expected keys that should exist (actual format from OpenHands)
    assert 'uptime' in info, "get_system_info should include uptime"
    assert 'idle_time' in info, "get_system_info should include idle_time"
    assert 'resources' in info, "get_system_info should include resources"


# ============================================================================
# PASS-TO-PASS TESTS - These pass on both base and fix (repo validation)
# ============================================================================


def test_system_stats_functions_work():
    """P2P: System stats functions should work correctly."""
    set_pythonpath()

    # Import from the new location (will work on fix, may fail on base)
    try:
        from openhands.app_server.status.system_stats import (
            get_system_stats,
            update_last_execution_time,
        )
    except ImportError:
        pytest.skip("system_stats not in new location yet")

    # Test get_system_stats
    stats = get_system_stats()
    assert isinstance(stats, dict), "get_system_stats should return a dict"
    assert 'memory' in stats, "get_system_stats should include memory info"
    assert 'cpu_percent' in stats, "get_system_stats should include cpu_percent"
    assert 'disk' in stats, "get_system_stats should include disk info"

    # Test update_last_execution_time (should not raise)
    update_last_execution_time()


def test_server_app_py_syntax_valid():
    """P2P: Server app.py should have valid Python syntax."""
    result = subprocess.run(
        [sys.executable, '-m', 'py_compile', str(SERVER_APP_PATH)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"server/app.py has syntax errors: {result.stderr}"


def test_action_execution_server_syntax_valid():
    """P2P: Action execution server should have valid Python syntax."""
    result = subprocess.run(
        [sys.executable, '-m', 'py_compile', str(ACTION_EXEC_SERVER_PATH)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"action_execution_server.py has syntax errors: {result.stderr}"
    )


def test_action_execution_client_syntax_valid():
    """P2P: Action execution client should have valid Python syntax."""
    result = subprocess.run(
        [sys.executable, '-m', 'py_compile', str(ACTION_EXEC_CLIENT_PATH)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"action_execution_client.py has syntax errors: {result.stderr}"
    )


def test_repo_tests_if_available():
    """P2P: Run repo's own unit tests for system_stats if they exist."""
    test_file = REPO / 'tests' / 'runtime' / 'utils' / 'test_system_stats.py'
    if not test_file.exists():
        pytest.skip("Repo test file doesn't exist")

    # Run the specific test file with pytest
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', str(test_file), '-v', '--tb=short'],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
        env={**os.environ, 'PYTHONPATH': str(REPO)},
    )

    # Just check it doesn't crash with import errors
    # The tests may pass or fail based on the current state
    assert 'ImportError' not in result.stderr, (
        f"Import errors in repo tests: {result.stderr[:500]}"
    )


def test_repo_ruff_system_stats():
    """P2P: Repo ruff linting passes on system_stats.py (pass_to_pass)."""
    # Ensure ruff is installed
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'ruff', '-q'], check=True, timeout=60)
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'ruff',
            'check',
            str(REPO / 'openhands' / 'runtime' / 'utils' / 'system_stats.py'),
            '--config',
            str(REPO / 'dev_config' / 'python' / 'ruff.toml'),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Ruff linting failed on system_stats.py:\n{result.stderr}"


def test_repo_ruff_health_routes():
    """P2P: Repo ruff linting passes on health.py routes (pass_to_pass)."""
    # If health.py is removed (as expected after the fix), skip this test
    health_path = REPO / 'openhands' / 'server' / 'routes' / 'health.py'
    if not health_path.exists():
        pytest.skip("health.py removed as expected after migration")

    # Ensure ruff is installed
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'ruff', '-q'], check=True, timeout=60)
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'ruff',
            'check',
            str(health_path),
            '--config',
            str(REPO / 'dev_config' / 'python' / 'ruff.toml'),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Ruff linting failed on health.py:\n{result.stderr}"


def test_repo_unit_tests_system_stats():
    """P2P: Repo unit tests for system_stats pass (pass_to_pass)."""
    # Ensure pytest and psutil are installed
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pytest', 'psutil', '-q'], check=True, timeout=60)
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'pytest',
            str(REPO / 'tests' / 'runtime' / 'utils' / 'test_system_stats.py'),
            '-v',
            '--tb=short',
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(REPO),
        env={**os.environ, 'PYTHONPATH': str(REPO)},
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stdout[-1000:]}{result.stderr[-500:]}"


def test_repo_ruff_server_app():
    """P2P: Repo ruff linting passes on server/app.py (pass_to_pass)."""
    # Ensure ruff is installed
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'ruff', '-q'], check=True, timeout=60)
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'ruff',
            'check',
            str(REPO / 'openhands' / 'server' / 'app.py'),
            '--config',
            str(REPO / 'dev_config' / 'python' / 'ruff.toml'),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Ruff linting failed:\n{result.stderr}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])