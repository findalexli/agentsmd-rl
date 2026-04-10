"""
Task: transformers-ci-testshub-empty-skip
Repo: huggingface/transformers @ c9faacd7d57459157656bdffe049dabb6293f011
PR:   #45014

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "/workspace/transformers"
FETCHER = f"{REPO}/utils/tests_fetcher.py"

_fetcher_mod = None


def _load_fetcher():
    """Load tests_fetcher module dynamically (cached)."""
    global _fetcher_mod
    if _fetcher_mod is not None:
        return _fetcher_mod
    spec = importlib.util.spec_from_file_location("tests_fetcher", FETCHER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["tests_fetcher"] = mod
    spec.loader.exec_module(mod)
    _fetcher_mod = mod
    return mod


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """tests_fetcher.py must parse without errors."""
    import ast

    src = Path(FETCHER).read_text()
    ast.parse(src)


# [repo_ci] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff check passes on tests_fetcher.py (pass_to_pass)."""
    # Use repo's pyproject.toml config which ignores E501 and E741
    r = subprocess.run(
        ["ruff", "check", "utils/tests_fetcher.py"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_ci] pass_to_pass
def test_repo_ruff_format_check():
    """Repo's ruff format check passes on tests_fetcher.py (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "utils/tests_fetcher.py"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_ci] pass_to_pass
def test_repo_tests_fetcher_import():
    """Repo's tests_fetcher module can be imported without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c", "from utils import tests_fetcher; print('OK')"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"Import failed:\n{r.stderr}"


# [repo_ci] pass_to_pass
def test_repo_tests_fetcher_help():
    """Repo's tests_fetcher.py --help works (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/tests_fetcher.py", "--help"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"Help command failed:\n{r.stderr}"
    assert "usage:" in r.stdout, "Expected usage message in help output"


# [repo_ci] pass_to_pass
def test_repo_syntax_all():
    """All repo Python files must have valid syntax (pass_to_pass)."""
    import ast

    errors = []
    for py_file in Path(REPO).rglob("*.py"):
        # Skip hidden dirs and build artifacts
        if any(part.startswith(".") for part in py_file.parts):
            continue
        if "__pycache__" in str(py_file):
            continue
        try:
            ast.parse(py_file.read_text())
        except SyntaxError as e:
            errors.append(f"{py_file}: {e}")
    assert not errors, f"Syntax errors found:\n{chr(10).join(errors)}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_empty_list_skips_hub():
    """Empty test list must not produce a tests_hub file."""
    mod = _load_fetcher()
    tmpdir = tempfile.mkdtemp()
    try:
        mod.create_test_list_from_filter([], tmpdir)
        hub_file = os.path.join(tmpdir, "tests_hub_test_list.txt")
        assert not os.path.exists(hub_file), (
            "tests_hub_test_list.txt was written despite empty test list"
        )
    finally:
        shutil.rmtree(tmpdir)


# [pr_diff] fail_to_pass
def test_unmatched_files_skip_hub():
    """Files matching no job filter must not produce a tests_hub file."""
    mod = _load_fetcher()
    # Try several non-test paths to avoid gaming with specific filenames
    for unmatched in [
        ["README.md", "setup.py"],
        ["src/transformers/__init__.py"],
        ["docs/source/en/index.md", "Makefile"],
    ]:
        tmpdir = tempfile.mkdtemp()
        try:
            mod.create_test_list_from_filter(unmatched, tmpdir)
            hub_file = os.path.join(tmpdir, "tests_hub_test_list.txt")
            assert not os.path.exists(hub_file), (
                f"tests_hub_test_list.txt was written for input {unmatched}"
            )
        finally:
            shutil.rmtree(tmpdir)


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_matching_files_include_hub():
    """When real test files match jobs, tests_hub must also be written."""
    mod = _load_fetcher()
    # Multiple sets of matching files
    test_inputs = [
        ["tests/models/bert/test_modeling_bert.py"],
        ["tests/models/bert/test_modeling_bert.py", "tests/repo_utils/test_check_config_docstrings.py"],
        ["tests/models/gpt2/test_modeling_gpt2.py", "tests/models/t5/test_modeling_t5.py"],
    ]
    for test_files in test_inputs:
        tmpdir = tempfile.mkdtemp()
        try:
            mod.create_test_list_from_filter(test_files, tmpdir)
            hub_file = os.path.join(tmpdir, "tests_hub_test_list.txt")
            assert os.path.exists(hub_file), (
                f"tests_hub_test_list.txt not written for input {test_files}"
            )
        finally:
            shutil.rmtree(tmpdir)


# [pr_diff] pass_to_pass
def test_hub_content_is_tests():
    """When tests_hub is written, its content must be 'tests'."""
    mod = _load_fetcher()
    for test_files in [
        ["tests/models/bert/test_modeling_bert.py"],
        ["tests/models/gpt2/test_modeling_gpt2.py", "tests/generation/test_utils.py"],
    ]:
        tmpdir = tempfile.mkdtemp()
        try:
            mod.create_test_list_from_filter(test_files, tmpdir)
            hub_file = os.path.join(tmpdir, "tests_hub_test_list.txt")
            assert os.path.exists(hub_file), "tests_hub_test_list.txt not written"
            content = Path(hub_file).read_text().strip()
            assert content == "tests", f"Expected 'tests', got '{content}'"
        finally:
            shutil.rmtree(tmpdir)


# [pr_diff] pass_to_pass
def test_other_jobs_correct():
    """Non-hub job test lists are unaffected by the fix."""
    mod = _load_fetcher()
    tmpdir = tempfile.mkdtemp()
    try:
        test_files = [
            "tests/models/bert/test_modeling_bert.py",
            "tests/repo_utils/test_check_config_docstrings.py",
        ]
        mod.create_test_list_from_filter(test_files, tmpdir)
        # tests_torch should have bert modeling test
        torch_file = os.path.join(tmpdir, "tests_torch_test_list.txt")
        assert os.path.exists(torch_file), "tests_torch_test_list.txt not written"
        content = Path(torch_file).read_text()
        assert "tests/models/bert/test_modeling_bert.py" in content
        # tests_repo_utils should have the repo utils test
        repo_file = os.path.join(tmpdir, "tests_repo_utils_test_list.txt")
        assert os.path.exists(repo_file), "tests_repo_utils_test_list.txt not written"
        repo_content = Path(repo_file).read_text()
        assert "tests/repo_utils/test_check_config_docstrings.py" in repo_content
    finally:
        shutil.rmtree(tmpdir)


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """tests_fetcher.py must not be stubbed out (>= 800 lines)."""
    lines = Path(FETCHER).read_text().splitlines()
    assert len(lines) >= 800, (
        f"tests_fetcher.py has {len(lines)} lines, expected >= 800"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:15 @ c9faacd
def test_minimal_diff():
    """Fix should be concise — no more than 30 lines added."""
    # Diff working tree against base commit
    result = subprocess.run(
        ["git", "diff", "c9faacd7d57459157656bdffe049dabb6293f011",
         "--numstat", "--", "utils/tests_fetcher.py"],
        capture_output=True, text=True, cwd=REPO,
    )
    numstat = result.stdout.strip()
    if not numstat:
        # No changes at all — base commit, pass vacuously
        return
    added = int(numstat.split()[0])
    assert added <= 30, f"Too many lines added ({added}), expected <= 30"


# [agent_config] pass_to_pass — CLAUDE.md:2 @ c9faacd
def test_style_ruff():
    """Agent's changes must not introduce new ruff violations."""
    import json as _json
    import tempfile as _tf

    BASE = "c9faacd7d57459157656bdffe049dabb6293f011"

    # Get base version without touching the working tree
    base_src = subprocess.run(
        ["git", "show", f"{BASE}:utils/tests_fetcher.py"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert base_src.returncode == 0, "Could not read base commit version"

    with _tf.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(base_src.stdout)
        base_tmp = f.name
    try:
        base_ruff = subprocess.run(
            ["ruff", "check", base_tmp, "--select=E,W,F,I", "--output-format=json"],
            capture_output=True, text=True,
        )
        base_count = len(_json.loads(base_ruff.stdout)) if base_ruff.stdout.strip() else 0
    finally:
        os.unlink(base_tmp)

    cur_ruff = subprocess.run(
        ["ruff", "check", "utils/tests_fetcher.py", "--select=E,W,F,I", "--output-format=json"],
        capture_output=True, text=True, cwd=REPO,
    )
    cur_count = len(_json.loads(cur_ruff.stdout)) if cur_ruff.stdout.strip() else 0

    assert cur_count <= base_count, (
        f"Agent introduced {cur_count - base_count} new ruff violation(s) "
        f"(base: {base_count}, current: {cur_count})"
    )
