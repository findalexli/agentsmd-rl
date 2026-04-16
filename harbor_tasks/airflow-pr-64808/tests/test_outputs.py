#!/usr/bin/env python3
"""
Tests for apache/airflow#64808 - Fix group/extra bug in initialize_virtualenv

The bug: initialize_virtualenv.py was using --group for all extras instead of
distinguishing between dependency groups (--group) and package extras (--extra).

The fix should correctly categorize extras: dependency groups use --group,
optional extras use --extra.

These tests verify BEHAVIOR by patching subprocess.run in the script's namespace,
calling uv_install_requirements with appropriate args, and asserting on the
captured uv sync command.
"""
import subprocess
import sys
import tempfile
import os
from pathlib import Path

REPO = Path("/workspace/airflow")
SCRIPT_PATH = REPO / "scripts" / "tools" / "initialize_virtualenv.py"


def load_script_module():
    source = SCRIPT_PATH.read_text()
    source = source.replace(
        'if __name__ not in ("__main__", "__mp_main__"):',
        'if False:'
    )
    source = source.replace(
        'if __name__ == "__main__":\n    main()',
        '# main() call disabled for testing'
    )
    namespace = {"__name__": "__test__", "__file__": str(SCRIPT_PATH)}
    exec(compile(source, str(SCRIPT_PATH), "exec"), namespace)
    return namespace


def create_test_pyproject_toml(dependency_groups=None, optional_extras=None):
    """Create a temp pyproject.toml and return the Path. Caller must unlink."""
    groups_lines = ""
    if dependency_groups:
        groups_lines = "\n[dependency-groups]\n" + "\n".join(f"{g} = []" for g in dependency_groups)

    extras_lines = ""
    if optional_extras:
        extras_lines = "\n[project.optional-dependencies]\n" + "\n".join(f"{e} = []" for e in optional_extras)

    content = f"""
[project]
name = "test-project"
version = "1.0.0"
{groups_lines}
{extras_lines}
"""
    fd, path = tempfile.mkstemp(suffix='.toml')
    os.write(fd, content.encode())
    os.close(fd)
    return Path(path)


def capture_uv_command(temp_pyproject_path: Path, extras_arg: str):
    """
    Load the script, mock subprocess.run, call uv_install_requirements,
    and return the captured uv sync command list.
    
    Handles both NOP (0-arg) and fixed (1-arg with pyproject_path) calling conventions.
    """
    captured = [None]
    
    # Inject mock into subprocess module before loading script
    original_run = subprocess.run
    def mock_run(cmd, check=True, capture_output=False, text=False, cwd=None, env=None):
        captured[0] = list(cmd)
        r = type('R', (), {'returncode': 0})()
        return r
    
    # Patch at module level
    import subprocess as sp_module
    saved_run = sp_module.run
    sp_module.run = mock_run
    
    try:
        ns = load_script_module()
        uv_func = ns['uv_install_requirements']
        
        # Set sys.argv to simulate the extras argument
        sys.argv = ['initialize_virtualenv.py', extras_arg]
        
        argcount = uv_func.__code__.co_argcount
        if argcount == 0:
            # NOP version: no args
            uv_func()
        else:
            # Fixed version: takes pyproject_path as argument
            uv_func(temp_pyproject_path)
        
        if captured[0] is None:
            raise RuntimeError("subprocess.run was never called")
        return captured[0]
    finally:
        sp_module.run = saved_run


# =============================================================================
# FAIL-TO-PASS TESTS - These should FAIL on base commit, PASS after fix
# =============================================================================

def test_groups_vs_extras_produces_correct_flags():
    """
    The fix should produce --group for dependency groups and --extra for optional extras.
    Test: dev (group) + graphviz (extra) should produce --group dev --extra graphviz
    (fail_to_pass)
    """
    temp_path = create_test_pyproject_toml(
        dependency_groups=["dev", "docs"],
        optional_extras=["graphviz", "otel"]
    )
    try:
        uv_cmd = capture_uv_command(temp_path, "dev,graphviz")
        
        # dev should use --group
        assert "--group" in uv_cmd and "dev" in uv_cmd, \
            f"dev should use --group flag. Got: {uv_cmd}"
        
        # graphviz should use --extra
        assert "--extra" in uv_cmd and "graphviz" in uv_cmd, \
            f"graphviz should use --extra flag. Got: {uv_cmd}"
        
        # graphviz should NOT be preceded by --group
        gi = uv_cmd.index("graphviz")
        assert uv_cmd[gi - 1] != "--group", \
            f"graphviz should use --extra, not --group. Got: {uv_cmd}"
    finally:
        temp_path.unlink()


def test_all_groups_use_group_flag():
    """
    When all extras are dependency groups (dev,docs), all should use --group.
    (fail_to_pass)
    """
    temp_path = create_test_pyproject_toml(
        dependency_groups=["dev", "docs"],
        optional_extras=["graphviz"]
    )
    try:
        uv_cmd = capture_uv_command(temp_path, "dev,docs")
        
        assert uv_cmd.count("--group") == 2, \
            f"Expected 2 --group flags for dev,docs. Got: {uv_cmd}"
        assert "dev" in uv_cmd and "docs" in uv_cmd
    finally:
        temp_path.unlink()


def test_all_extras_use_extra_flag():
    """
    When all extras are optional extras (graphviz,otel), all should use --extra.
    (fail_to_pass)
    """
    temp_path = create_test_pyproject_toml(
        dependency_groups=["dev"],
        optional_extras=["graphviz", "otel"]
    )
    try:
        uv_cmd = capture_uv_command(temp_path, "graphviz,otel")
        
        assert "--group" not in uv_cmd, \
            f"Optional extras should not use --group. Got: {uv_cmd}"
        assert uv_cmd.count("--extra") == 2, \
            f"Expected 2 --extra flags. Got: {uv_cmd}"
        assert "graphviz" in uv_cmd and "otel" in uv_cmd
    finally:
        temp_path.unlink()


def test_mixed_groups_and_extras():
    """
    Mixed extras: dev (group) + graphviz (extra) should get respective flags.
    (fail_to_pass)
    """
    temp_path = create_test_pyproject_toml(
        dependency_groups=["dev"],
        optional_extras=["graphviz"]
    )
    try:
        uv_cmd = capture_uv_command(temp_path, "dev,graphviz")
        
        expected = ["uv", "sync", "--group", "dev", "--extra", "graphviz"]
        assert uv_cmd == expected, f"Expected {expected}. Got: {uv_cmd}"
    finally:
        temp_path.unlink()


def test_three_way_mixed():
    """
    Three extras: dev,docs (groups) + graphviz (extra).
    (fail_to_pass)
    """
    temp_path = create_test_pyproject_toml(
        dependency_groups=["dev", "docs"],
        optional_extras=["graphviz"]
    )
    try:
        uv_cmd = capture_uv_command(temp_path, "dev,docs,graphviz")
        
        expected = ["uv", "sync", "--group", "dev", "--group", "docs", "--extra", "graphviz"]
        assert uv_cmd == expected, f"Expected {expected}. Got: {uv_cmd}"
    finally:
        temp_path.unlink()


def test_real_airflow_pyproject_classifies_correctly():
    """
    Against real airflow pyproject.toml, known groups (dev) use --group
    and known optional extras (graphviz) use --extra.
    (fail_to_pass)
    """
    real_pyproject = REPO / "pyproject.toml"
    
    uv_cmd = capture_uv_command(real_pyproject, "dev,graphviz")
    
    dev_idx = uv_cmd.index("dev")
    graphviz_idx = uv_cmd.index("graphviz")
    
    assert uv_cmd[dev_idx - 1] == "--group", \
        f"dev should be preceded by --group. Got: {uv_cmd}"
    assert uv_cmd[graphviz_idx - 1] == "--extra", \
        f"graphviz should be preceded by --extra. Got: {uv_cmd}"


# =============================================================================
# PASS-TO-PASS TESTS - These should PASS on both base commit and after fix
# =============================================================================

def test_script_syntax_valid():
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"Syntax error: {result.stderr}"


def test_script_can_be_loaded():
    ns = load_script_module()
    assert ns is not None


def test_repo_ruff_check():
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True,
        timeout=120
    )
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"ruff check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_format():
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True,
        timeout=120
    )
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"ruff format check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_mypy_typecheck():
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "mypy", "-q"],
        capture_output=True,
        timeout=120
    )
    result = subprocess.run(
        [sys.executable, "-m", "mypy", "--disable-error-code=no-redef", str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, f"mypy failed:\n{result.stdout}\n{result.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
