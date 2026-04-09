"""
Task: transformers-unified-qa-checkers
Repo: transformers @ 28af8184fb00a0e9bc778c3defdec39bbe7e8839
PR:   44879

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/transformers"


# ---------------------------------------------------------------------------
# Code behaviour: fail_to_pass
# ---------------------------------------------------------------------------


def test_checkers_list():
    """utils/checkers.py --list outputs all expected checker names."""
    r = subprocess.run(
        ["python3", "utils/checkers.py", "all", "--list"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"checkers.py --list failed:\n{r.stderr}"
    output = r.stdout
    for name in [
        "ruff_check", "ruff_format", "copies", "modular_conversion",
        "doc_toc", "types", "modeling_structure", "deps_table", "imports",
        "init_isort", "auto_mappings", "docstrings", "dummies",
    ]:
        assert name in output, f"Checker '{name}' not listed in output"


def test_checkers_unknown_checker():
    """Unknown checker name produces a clear error."""
    r = subprocess.run(
        ["python3", "utils/checkers.py", "nonexistent_xyz_checker"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode != 0, "Should fail for unknown checker"
    combined = r.stdout + r.stderr
    assert "unknown" in combined.lower(), \
        f"Should mention 'unknown' in output:\n{combined}"


def test_checkers_help():
    """checkers.py --help shows usage with --fix and --keep-going flags."""
    r = subprocess.run(
        ["python3", "utils/checkers.py", "--help"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"--help failed:\n{r.stderr}"
    assert "--fix" in r.stdout, "Help should mention --fix flag"
    assert "--keep-going" in r.stdout, "Help should mention --keep-going flag"


def test_makefile_has_new_targets():
    """Makefile defines check-code-quality and check-repository-consistency."""
    makefile = (Path(REPO) / "Makefile").read_text()
    assert "check-code-quality" in makefile, \
        "Makefile missing check-code-quality target"
    assert "check-repository-consistency" in makefile, \
        "Makefile missing check-repository-consistency target"


def test_makefile_delegates_to_checkers():
    """Makefile targets use the unified checkers module instead of raw commands."""
    makefile = (Path(REPO) / "Makefile").read_text()
    assert "utils/checkers.py" in makefile or "checkers.py" in makefile, \
        "Makefile should delegate to the unified checkers module"
    # Old scattered pattern should be removed
    assert "ruff check $(check_dirs)" not in makefile, \
        "Makefile should not directly call ruff with $(check_dirs) anymore"


def test_circleci_uses_make_targets():
    """CircleCI config uses make check-code-quality and make check-repository-consistency."""
    ci = (Path(REPO) / ".circleci" / "config.yml").read_text()
    assert "make check-code-quality" in ci, \
        "CircleCI should use make check-code-quality"
    assert "make check-repository-consistency" in ci, \
        "CircleCI should use make check-repository-consistency"
    # Old inline script calls should be gone
    assert "python utils/custom_init_isort.py" not in ci, \
        "CircleCI should not call individual check scripts directly"
    assert "python utils/check_copies.py" not in ci, \
        "CircleCI should not call check_copies.py directly"


def test_tomli_in_quality_deps():
    """tomli is listed in both setup.py quality extras and dependency_versions_table."""
    setup = (Path(REPO) / "setup.py").read_text()
    assert "tomli" in setup, "setup.py should include tomli in dependencies"

    deps = (Path(REPO) / "src" / "transformers" / "dependency_versions_table.py").read_text()
    assert "tomli" in deps, "dependency_versions_table.py should include tomli"


# ---------------------------------------------------------------------------
# Config update: fail_to_pass
# ---------------------------------------------------------------------------


def test_agents_md_updated_check_repo():
    """.ai/AGENTS.md should reflect the updated make check-repo description."""
    agents = (Path(REPO) / ".ai" / "AGENTS.md").read_text()
    # Old wording should be replaced
    assert "CI-style consistency checks" not in agents, \
        ".ai/AGENTS.md still has old 'CI-style consistency checks' description"


def test_agents_md_no_stale_ci_statement():
    """.ai/AGENTS.md should not claim CI runs make check-repo."""
    agents = (Path(REPO) / ".ai" / "AGENTS.md").read_text()
    assert "The CI will run `make check-repo`" not in agents, \
        ".ai/AGENTS.md still claims 'The CI will run make check-repo'"


# ---------------------------------------------------------------------------
# Pass-to-pass: must hold before AND after the fix
# ---------------------------------------------------------------------------


def test_makefile_core_targets_exist():
    """Core make targets (style, typing, check-repo, fix-repo) must always exist."""
    makefile = (Path(REPO) / "Makefile").read_text()
    for target in ["style:", "typing:", "check-repo:", "fix-repo:"]:
        assert target in makefile, f"Makefile missing core target {target}"


def test_agents_md_has_make_commands():
    """.ai/AGENTS.md should document make style, typing, fix-repo, check-repo."""
    agents = (Path(REPO) / ".ai" / "AGENTS.md").read_text()
    for cmd in ["make style", "make typing", "make fix-repo", "make check-repo"]:
        assert cmd in agents, f".ai/AGENTS.md should document '{cmd}'"
