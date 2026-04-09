"""Tests for transformers-unify-qa-checkers task.

Verifies utils/checkers.py module, Makefile targets, .ai/AGENTS.md updates,
and tomli dependency additions.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/transformers")


# ---------------------------------------------------------------------------
# fail_to_pass: behavioral tests (subprocess)
# ---------------------------------------------------------------------------


def test_checkers_module_imports():
    """utils/checkers.py must import with CHECKERS dict containing all expected names."""
    result = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, '/workspace/transformers'); "
         "from utils.checkers import CHECKERS; print(sorted(CHECKERS.keys()))"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"
    keys = eval(result.stdout.strip())
    expected = [
        "add_dates", "auto_mappings", "config_attributes", "config_docstrings",
        "copies", "deps_table", "doc_toc", "docstrings", "doctest_list",
        "dummies", "imports", "init_isort", "inits", "modeling_structure",
        "modular_conversion", "pipeline_typing", "repo", "ruff_check",
        "ruff_format", "types", "update_metadata",
    ]
    for name in expected:
        assert name in keys, f"Missing checker: {name}"


def test_checkers_cli_lists_all():
    """Running checkers.py --list must output checker names."""
    result = subprocess.run(
        [sys.executable, str(REPO / "utils" / "checkers.py"), "--list"],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert result.returncode == 0, f"--list failed: {result.stderr}"
    output = result.stdout
    for name in ["copies", "types", "ruff_check", "deps_table", "imports", "modeling_structure"]:
        assert name in output, f"Checker '{name}' not listed"


def test_checkers_rejects_unknown():
    """checkers.py rejects unknown checker names with 'Unknown' message."""
    result = subprocess.run(
        [sys.executable, str(REPO / "utils" / "checkers.py"), "nonexistent_checker"],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert result.returncode != 0, "Should reject unknown checker"
    combined = result.stdout + result.stderr
    assert "nknown" in combined, f"Expected 'unknown' mention, got: {combined}"


def test_makefile_check_code_quality():
    """make check-code-quality target exists and invokes checkers.py with ruff_check."""
    result = subprocess.run(
        ["make", "-n", "check-code-quality"],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert result.returncode == 0, \
        f"check-code-quality target missing or broken: {result.stderr}"
    output = result.stdout
    assert "checkers.py" in output, "Should invoke checkers.py"
    assert "ruff_check" in output, "Should include ruff_check"


def test_makefile_check_repository_consistency():
    """make check-repository-consistency target exists and invokes checkers.py."""
    result = subprocess.run(
        ["make", "-n", "check-repository-consistency"],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert result.returncode == 0, \
        f"check-repository-consistency target missing or broken: {result.stderr}"
    output = result.stdout
    assert "checkers.py" in output, "Should invoke checkers.py"
    assert "copies" in output, "Should include copies checker"
    assert "deps_table" in output, "Should include deps_table checker"


def test_makefile_check_repo_keep_going():
    """make check-repo invokes checkers.py with --keep-going."""
    result = subprocess.run(
        ["make", "-n", "check-repo"],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert result.returncode == 0, f"check-repo target failed: {result.stderr}"
    output = result.stdout
    assert "checkers.py" in output, "check-repo should invoke checkers.py"
    assert "--keep-going" in output, "check-repo should use --keep-going"


def test_makefile_fix_repo_fix():
    """make fix-repo invokes checkers.py with --fix."""
    result = subprocess.run(
        ["make", "-n", "fix-repo"],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert result.returncode == 0, f"fix-repo target failed: {result.stderr}"
    output = result.stdout
    assert "checkers.py" in output, "fix-repo should invoke checkers.py"
    assert "--fix" in output, "fix-repo should use --fix"


# ---------------------------------------------------------------------------
# fail_to_pass: config update checks
# ---------------------------------------------------------------------------


def test_agents_md_check_repo_updated():
    """AGENTS.md must not describe check-repo as 'CI-style consistency checks'."""
    agents_md = (REPO / ".ai" / "AGENTS.md").read_text()
    assert "CI-style consistency checks" not in agents_md, \
        "AGENTS.md still has old check-repo description"


def test_agents_md_removes_ci_check_reference():
    """AGENTS.md should not claim CI will run check-repo."""
    agents_md = (REPO / ".ai" / "AGENTS.md").read_text()
    assert "CI will run" not in agents_md, \
        "AGENTS.md should not claim CI runs check-repo"


# ---------------------------------------------------------------------------
# fail_to_pass: dependency checks
# ---------------------------------------------------------------------------


def test_setup_py_includes_tomli():
    """setup.py must include tomli in quality extras."""
    setup_py = (REPO / "setup.py").read_text()
    assert '"tomli"' in setup_py, "setup.py must include tomli dependency"


def test_dependency_versions_table_has_tomli():
    """dependency_versions_table.py exports deps dict with a tomli entry."""
    result = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, '/workspace/transformers/src'); "
         "from transformers.dependency_versions_table import deps; "
         "assert 'tomli' in deps, 'tomli missing from deps table'"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"Failed: {result.stderr}"
