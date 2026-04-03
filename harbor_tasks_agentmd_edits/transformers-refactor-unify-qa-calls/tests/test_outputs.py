"""
Task: transformers-refactor-unify-qa-calls
Repo: huggingface/transformers @ 28af8184fb00a0e9bc778c3defdec39bbe7e8839
PR:   44879

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import sys
from pathlib import Path

REPO = "/workspace/transformers"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    files = [
        Path(REPO) / "utils" / "checkers.py",
        Path(REPO) / "setup.py",
        Path(REPO) / "src" / "transformers" / "dependency_versions_table.py",
    ]
    for f in files:
        if f.exists():
            source = f.read_text()
            ast.parse(source, filename=str(f))


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_checkers_module_exists_with_registry():
    """utils/checkers.py must exist and contain a CHECKERS registry dict."""
    checkers_path = Path(REPO) / "utils" / "checkers.py"
    assert checkers_path.exists(), "utils/checkers.py must exist"

    sys.path.insert(0, str(Path(REPO) / "utils"))
    try:
        source = checkers_path.read_text()
        tree = ast.parse(source)

        # Find CHECKERS assignment at module level
        has_checkers = False
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "CHECKERS":
                        has_checkers = True
        assert has_checkers, "utils/checkers.py must define a CHECKERS dict"
    finally:
        if str(Path(REPO) / "utils") in sys.path:
            sys.path.remove(str(Path(REPO) / "utils"))


# [pr_diff] fail_to_pass
def test_checkers_registry_has_expected_entries():
    """CHECKERS dict must include key checker names like ruff_check, copies, types."""
    checkers_path = Path(REPO) / "utils" / "checkers.py"
    assert checkers_path.exists(), "utils/checkers.py must exist"

    source = checkers_path.read_text()
    # Check that expected checker names are defined in the source
    expected = ["ruff_check", "ruff_format", "copies", "types", "deps_table", "imports"]
    for name in expected:
        assert f'"{name}"' in source or f"'{name}'" in source, \
            f"CHECKERS should contain entry for '{name}'"


# [pr_diff] fail_to_pass
def test_checkers_has_run_checker_function():
    """utils/checkers.py must define a run_checker() function."""
    checkers_path = Path(REPO) / "utils" / "checkers.py"
    assert checkers_path.exists(), "utils/checkers.py must exist"

    source = checkers_path.read_text()
    tree = ast.parse(source)

    func_names = [
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    ]
    assert "run_checker" in func_names, \
        "utils/checkers.py must define run_checker()"
    assert "main" in func_names, \
        "utils/checkers.py must define main()"


# [pr_diff] fail_to_pass
def test_makefile_has_check_code_quality_target():
    """Makefile must define a check-code-quality target that uses checkers.py."""
    makefile = Path(REPO) / "Makefile"
    content = makefile.read_text()
    assert "check-code-quality:" in content, \
        "Makefile must have a check-code-quality target"
    # The target should invoke checkers.py
    assert "checkers.py" in content or "checkers" in content, \
        "Makefile targets should use checkers.py"


# [pr_diff] fail_to_pass
def test_makefile_has_check_repository_consistency_target():
    """Makefile must define a check-repository-consistency target."""
    makefile = Path(REPO) / "Makefile"
    content = makefile.read_text()
    assert "check-repository-consistency:" in content, \
        "Makefile must have a check-repository-consistency target"


# [pr_diff] fail_to_pass
def test_tomli_in_quality_extras():
    """setup.py must include tomli in the quality extras."""
    setup_py = Path(REPO) / "setup.py"
    content = setup_py.read_text()
    # Find the quality extras line and check tomli is included
    quality_match = re.search(r'extras\["quality"\]\s*=\s*deps_list\(([^)]+)\)', content)
    assert quality_match is not None, "Could not find extras['quality'] definition"
    quality_deps = quality_match.group(1)
    assert "tomli" in quality_deps, "tomli must be in quality extras"


# [pr_diff] fail_to_pass
def test_tomli_in_dependency_versions_table():
    """dependency_versions_table.py must include a tomli entry."""
    deps_table = Path(REPO) / "src" / "transformers" / "dependency_versions_table.py"
    content = deps_table.read_text()
    assert '"tomli"' in content, \
        "dependency_versions_table.py must include tomli"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_makefile_retains_style_target():
    """Makefile must still have a style target."""
    makefile = Path(REPO) / "Makefile"
    content = makefile.read_text()
    assert "\nstyle:" in content or content.startswith("style:"), \
        "Makefile must retain the style target"


# [static] pass_to_pass
def test_makefile_retains_fix_repo_target():
    """Makefile must still have a fix-repo target."""
    makefile = Path(REPO) / "Makefile"
    content = makefile.read_text()
    assert "fix-repo:" in content, \
        "Makefile must retain the fix-repo target"


# ---------------------------------------------------------------------------
# Config edit (config_edit) — agent instruction file updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Anti-stub (static) — ensure checkers.py has real logic
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_checkers_not_stub():
    """utils/checkers.py must have substantial implementation, not just stubs."""
    checkers_path = Path(REPO) / "utils" / "checkers.py"
    if not checkers_path.exists():
        return  # other tests cover existence
    source = checkers_path.read_text()
    tree = ast.parse(source)

    func_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
    assert func_count >= 5, \
        f"utils/checkers.py should have substantial logic (found {func_count} functions, expected >= 5)"

    # Should have actual subprocess calls for running checks
    assert "subprocess" in source, \
        "checkers.py should use subprocess to run check scripts"
