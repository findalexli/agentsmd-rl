"""
Task: transformers-feat-added-cache-to-the
Repo: huggingface/transformers @ aa1c36f1a9f454e69c4eac83071ced235942c7ed
PR:   44790

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import subprocess
from pathlib import Path

REPO = "/workspace/transformers"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    for rel in ["utils/check_modeling_structure.py"]:
        path = Path(REPO) / rel
        source = path.read_text()
        ast.parse(source, filename=rel)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests: caching mechanism
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cache_functions_exist():
    """check_modeling_structure.py must define caching helpers."""
    source = Path(f"{REPO}/utils/check_modeling_structure.py").read_text()
    tree = ast.parse(source)
    func_names = {
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    }
    # Must have content hashing, cache load, and cache save functions
    assert "_content_hash" in func_names, \
        "Must define a _content_hash function for file-level caching"
    assert "_load_cache" in func_names, \
        "Must define a _load_cache function"
    assert "_save_cache" in func_names, \
        "Must define a _save_cache function"


# [pr_diff] fail_to_pass
def test_content_hash_uses_rules():
    """_content_hash must incorporate both file content and enabled rules."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "check_modeling_structure",
        f"{REPO}/utils/check_modeling_structure.py",
        submodule_search_locations=[]
    )
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        pass  # Module may fail to fully load due to missing deps

    _content_hash = getattr(mod, "_content_hash", None)
    assert _content_hash is not None, "_content_hash must be importable"

    # Same content + same rules => same hash
    h1 = _content_hash("hello", {"rule_a", "rule_b"})
    h2 = _content_hash("hello", {"rule_a", "rule_b"})
    assert h1 == h2, "Same inputs must produce same hash"

    # Different content => different hash
    h3 = _content_hash("world", {"rule_a", "rule_b"})
    assert h1 != h3, "Different content must produce different hash"

    # Different rules => different hash
    h4 = _content_hash("hello", {"rule_a"})
    assert h1 != h4, "Different enabled rules must produce different hash"


# [pr_diff] fail_to_pass
def test_no_cache_cli_flag():
    """check_modeling_structure.py must accept --no-cache flag."""
    result = subprocess.run(
        ["python3", "utils/check_modeling_structure.py", "--help"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert "--no-cache" in result.stdout, \
        "Script must accept a --no-cache CLI argument"


# [pr_diff] fail_to_pass
def test_cache_file_path():
    """Cache must be stored as .check_modeling_structure_cache.json in utils/."""
    source = Path(f"{REPO}/utils/check_modeling_structure.py").read_text()
    assert ".check_modeling_structure_cache.json" in source, \
        "Cache path must reference .check_modeling_structure_cache.json"


# [pr_diff] fail_to_pass
def test_makefile_typing_target():
    """Makefile must have a separate 'typing' target for type checking."""
    makefile = Path(f"{REPO}/Makefile").read_text()
    assert re.search(r'^typing:', makefile, re.MULTILINE), \
        "Makefile must have a 'typing:' target rule"


# [pr_diff] fail_to_pass
def test_style_target_no_type_checking():
    """The 'style' target must NOT run check_types.py (moved to 'typing')."""
    makefile = Path(f"{REPO}/Makefile").read_text()
    # Extract the style target block (from "style:" to next non-indented line)
    style_match = re.search(r'^style:.*?(?=^\S|\Z)', makefile, re.MULTILINE | re.DOTALL)
    assert style_match, "Makefile must have a 'style:' target"
    style_block = style_match.group()
    assert "check_types.py" not in style_block, \
        "style target must not run check_types.py (should be in typing target)"


# [pr_diff] fail_to_pass
def test_check_repo_runs_modeling_structure_hard():
    """check-repo target must run check_modeling_structure.py without soft-fail prefix."""
    makefile = Path(f"{REPO}/Makefile").read_text()
    check_repo_match = re.search(r'^check-repo:.*?(?=^[a-z]|\Z)', makefile, re.MULTILINE | re.DOTALL)
    assert check_repo_match, "Makefile must have a 'check-repo:' target"
    check_repo_block = check_repo_match.group()
    lines = check_repo_block.split('\n')
    modeling_lines = [l for l in lines if 'check_modeling_structure.py' in l]
    assert len(modeling_lines) > 0, \
        "check-repo must run check_modeling_structure.py"
    for line in modeling_lines:
        stripped = line.strip()
        assert not stripped.startswith('-'), \
            "check_modeling_structure.py in check-repo must not use soft-fail prefix (-)"


# ---------------------------------------------------------------------------
# Config edit tests — agent instructions must be updated
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cache_load_has_real_logic():
    """_load_cache must have real logic using JSON serialization."""
    source = Path(f"{REPO}/utils/check_modeling_structure.py").read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_load_cache":
            body_stmts = [s for s in node.body
                         if not isinstance(s, (ast.Pass, ast.Expr))]
            assert len(body_stmts) >= 1, "_load_cache must have real logic"
            func_source = ast.get_source_segment(source, node)
            assert "json" in func_source.lower(), \
                "_load_cache must use JSON for cache serialization"
            return
    raise AssertionError("_load_cache function not found")


# [static] pass_to_pass
def test_gitignore_has_cache_file():
    """.gitignore must exclude the modeling structure cache file."""
    gitignore = Path(f"{REPO}/.gitignore").read_text()
    assert ".check_modeling_structure_cache.json" in gitignore, \
        ".gitignore must exclude the cache file"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base AND after fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_check_modeling_structure_runs():
    """Repo's check_modeling_structure.py runs without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_modeling_structure.py", "--no-progress"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"check_modeling_structure.py failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_check_modeling_structure_help():
    """Repo's check_modeling_structure.py --help works (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_modeling_structure.py", "--help"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"check_modeling_structure.py --help failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_makefile_has_style_target():
    """Repo's Makefile must have a 'style' target (pass_to_pass)."""
    makefile = Path(f"{REPO}/Makefile").read_text()
    assert re.search(r'^style:', makefile, re.MULTILINE), \
        "Makefile must have a 'style:' target rule"


# [repo_tests] pass_to_pass
def test_repo_makefile_style_runs_ruff():
    """Repo's style target must run ruff check and ruff format (pass_to_pass)."""
    makefile = Path(f"{REPO}/Makefile").read_text()
    # Extract the style target block
    style_match = re.search(r'^style:.*?(?=^\S|\Z)', makefile, re.MULTILINE | re.DOTALL)
    assert style_match, "Makefile must have a 'style:' target"
    style_block = style_match.group()
    assert "ruff check" in style_block, "style target must run ruff check"
    assert "ruff format" in style_block, "style target must run ruff format"


# [repo_tests] pass_to_pass
def test_repo_check_modeling_structure_list_rules():
    """Repo's check_modeling_structure.py --list-rules works (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_modeling_structure.py", "--list-rules"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"--list-rules failed:\n{r.stderr}"
    assert "TRF001" in r.stdout, "Should list TRF001 rule"


# [repo_tests] pass_to_pass
def test_repo_check_modeling_structure_rule_doc():
    """Repo's check_modeling_structure.py --rule works (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_modeling_structure.py", "--rule", "TRF001"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"--rule failed:\n{r.stderr}"
    assert "TRF001" in r.stdout, "Should show TRF001 documentation"
    assert "config_class" in r.stdout, "Should mention config_class in documentation"


# [repo_tests] pass_to_pass
def test_repo_py_compile_check_modeling_structure():
    """Python syntax of check_modeling_structure.py is valid (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", "utils/check_modeling_structure.py"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr}"
