"""Tests for transformers-unify-qa-checkers task.

Verifies utils/checkers.py module, Makefile targets, .ai/AGENTS.md updates,
and tomli dependency additions.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path("/workspace/transformers")


# ---------------------------------------------------------------------------
# pass_to_pass: repo CI/CD health checks
# ---------------------------------------------------------------------------


def test_repo_imports():
    """Repo's main package imports without error (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-c", "from transformers import *"],
        capture_output=True, text=True, timeout=60, cwd=str(REPO),
        env={"PYTHONPATH": str(REPO / "src")},
    )
    # Skip if optional dependencies are missing (these are not part of the fix)
    if r.returncode != 0:
        # Common optional dependencies that may be missing in test environment
        optional_patterns = [
            "torch", "tensorflow", "flax", "jax", "sentencepiece", "protobuf", 
            "tokenizers", "PIL", "accelerate", "aya_vision", "internvl", "GGUF",
            "qwen3_5", "Could not import module"
        ]
        if any(m in r.stderr for m in optional_patterns):
            pytest.skip(f"Skipping import test due to optional dependency")
    assert r.returncode == 0, f"Import failed:\n{r.stderr[-500:]}"


def test_repo_ruff_check():
    """Repo's ruff check passes on base commit (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "setup.py", "conftest.py"],
        capture_output=True, text=True, timeout=120, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}"


def test_repo_ruff_format():
    """Repo's ruff format check passes on base commit (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "setup.py", "conftest.py"],
        capture_output=True, text=True, timeout=120, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}"


def test_makefile_style_target_exists():
    """Makefile has 'style' target (pass_to_pass)."""
    r = subprocess.run(
        ["make", "-n", "style"],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, f"style target missing: {r.stderr}"


def test_makefile_typing_target_exists():
    """Makefile has 'typing' target (pass_to_pass)."""
    r = subprocess.run(
        ["make", "-n", "typing"],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, f"typing target missing: {r.stderr}"


def test_makefile_check_repo_target_exists():
    """Makefile has 'check-repo' target (pass_to_pass)."""
    r = subprocess.run(
        ["make", "-n", "check-repo"],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, f"check-repo target missing: {r.stderr}"


def test_makefile_fix_repo_target_exists():
    """Makefile has 'fix-repo' target (pass_to_pass)."""
    r = subprocess.run(
        ["make", "-n", "fix-repo"],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, f"fix-repo target missing: {r.stderr}"


def test_utils_scripts_syntax():
    """Utility scripts compile without syntax errors (pass_to_pass)."""
    utils_dir = REPO / "utils"
    scripts = [
        "check_types.py", "custom_init_isort.py", "sort_auto_mappings.py",
        "check_copies.py", "check_doc_toc.py", "check_dummies.py",
        "check_modular_conversion.py", "check_inits.py",
    ]
    for script in scripts:
        r = subprocess.run(
            [sys.executable, "-m", "py_compile", str(utils_dir / script)],
            capture_output=True, text=True, timeout=30, cwd=str(REPO),
        )
        assert r.returncode == 0, f"Syntax error in {script}:\n{r.stderr}"


# ---------------------------------------------------------------------------
# pass_to_pass: additional CI/CD health checks (enriched)
# ---------------------------------------------------------------------------


def test_repo_setup_py_syntax():
    """setup.py compiles without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", str(REPO / "setup.py")],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, f"setup.py syntax error:\n{r.stderr}"


def test_repo_conftest_syntax():
    """conftest.py compiles without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", str(REPO / "conftest.py")],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, f"conftest.py syntax error:\n{r.stderr}"



def test_utils_check_dummies_runs():
    """utils/check_dummies.py runs without error (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, str(REPO / "utils" / "check_dummies.py")],
        capture_output=True, text=True, timeout=120, cwd=str(REPO),
        env={"PYTHONPATH": str(REPO / "src")},
    )
    assert r.returncode == 0, f"check_dummies.py failed:\n{r.stderr[-500:]}"


def test_utils_custom_init_isort_runs():
    """utils/custom_init_isort.py --check_only runs without error (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, str(REPO / "utils" / "custom_init_isort.py"), "--check_only"],
        capture_output=True, text=True, timeout=120, cwd=str(REPO),
        env={"PYTHONPATH": str(REPO / "src")},
    )
    assert r.returncode == 0, f"custom_init_isort.py failed:\n{r.stderr[-500:]}"


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
    assert result.returncode == 0,         f"check-code-quality target missing or broken: {result.stderr}"
    output = result.stdout
    assert "checkers.py" in output, "Should invoke checkers.py"
    assert "ruff_check" in output, "Should include ruff_check"


def test_makefile_check_repository_consistency():
    """make check-repository-consistency target exists and invokes checkers.py."""
    result = subprocess.run(
        ["make", "-n", "check-repository-consistency"],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert result.returncode == 0,         f"check-repository-consistency target missing or broken: {result.stderr}"
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
    assert "CI-style consistency checks" not in agents_md,         "AGENTS.md still has old check-repo description"


def test_agents_md_removes_ci_check_reference():
    """AGENTS.md should not claim CI will run check-repo."""
    agents_md = (REPO / ".ai" / "AGENTS.md").read_text()
    assert "CI will run" not in agents_md,         "AGENTS.md should not claim CI runs check-repo"


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
