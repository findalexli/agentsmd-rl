"""
Task: transformers-checkrepo-nested-class-kwargs
Repo: huggingface/transformers @ 9a9997fd73c5eb29fb3677d3c489f5d3cd0765f6

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
import os
import tempfile
from pathlib import Path

REPO = "/workspace/transformers"
CHECK_REPO = f"{REPO}/utils/check_repo.py"

# Ensure utils is importable
sys.path.insert(0, f"{REPO}/utils")
sys.path.insert(0, f"{REPO}/src")


def _make_model_dir(tmpdir, name, code):
    """Create a fake modeling file in a temp model directory."""
    model_dir = os.path.join(tmpdir, "models", name)
    os.makedirs(model_dir)
    filepath = os.path.join(model_dir, f"modeling_{name}.py")
    with open(filepath, "w") as f:
        f.write(code.lstrip())
    return model_dir


def _run_check_with_models(model_code_map):
    """Set up a temp directory with model files and run check_models_have_kwargs.

    model_code_map: dict of {model_name: source_code}
    Returns (exception_or_none, error_message_str).
    """
    import check_repo

    tmpdir = tempfile.mkdtemp()
    for name, code in model_code_map.items():
        _make_model_dir(tmpdir, name, code)

    old_path = check_repo.PATH_TO_TRANSFORMERS
    # Clear get_model_modules cache if present
    if hasattr(check_repo.get_model_modules, "cache_clear"):
        check_repo.get_model_modules.cache_clear()

    check_repo.PATH_TO_TRANSFORMERS = tmpdir
    try:
        check_repo.check_models_have_kwargs()
        return None, ""
    except Exception as e:
        return e, str(e)
    finally:
        check_repo.PATH_TO_TRANSFORMERS = old_path


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """utils/check_repo.py must parse without syntax errors."""
    import ast

    src = Path(CHECK_REPO).read_text()
    ast.parse(src)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_nested_class_in_container_ignored():
    """Nested class inside another class should NOT be flagged for missing **kwargs."""
    exc, msg = _run_check_with_models({
        "mixedmodel": """
class PreTrainedModel:
    pass

class TopLevelBadModel(PreTrainedModel):
    def forward(self, hidden_states):
        return hidden_states

class ContainerHelper:
    class NestedBadModel(PreTrainedModel):
        def forward(self, hidden_states):
            return hidden_states
"""
    })
    # TopLevelBadModel should be flagged (it's top-level and missing **kwargs)
    assert exc is not None, "Expected exception for TopLevelBadModel"
    assert "TopLevelBadModel" in msg, f"Expected TopLevelBadModel in error: {msg}"
    # NestedBadModel should NOT be flagged
    assert "NestedBadModel" not in msg, f"NestedBadModel should not be flagged: {msg}"


# [pr_diff] fail_to_pass
def test_nested_class_in_function_ignored():
    """Nested class inside a function should NOT be flagged for missing **kwargs."""
    exc, msg = _run_check_with_models({
        "funcmodel": """
class PreTrainedModel:
    pass

class TopLevelNoKwargs(PreTrainedModel):
    def forward(self, hidden_states):
        return hidden_states

def make_helper():
    class FuncNestedModel(PreTrainedModel):
        def forward(self, hidden_states):
            return hidden_states
    return FuncNestedModel
"""
    })
    assert exc is not None, "Expected exception for TopLevelNoKwargs"
    assert "TopLevelNoKwargs" in msg, f"Expected TopLevelNoKwargs in error: {msg}"
    assert "FuncNestedModel" not in msg, f"FuncNestedModel should not be flagged: {msg}"


# [pr_diff] fail_to_pass
def test_nested_only_file_no_error():
    """File with ONLY nested classes (no top-level models) should produce no error."""
    exc, msg = _run_check_with_models({
        "nestedonly": """
class PreTrainedModel:
    pass

class Wrapper:
    class InnerModel(PreTrainedModel):
        def forward(self, hidden_states):
            return hidden_states

def factory():
    class LocalModel(PreTrainedModel):
        def forward(self, x):
            return x
    return LocalModel
"""
    })
    assert exc is None, f"Nested-only file should not raise, got: {msg}"


# [pr_diff] fail_to_pass
def test_get_model_modules_cached():
    """get_model_modules() should return the same cached object on repeated calls."""
    from types import SimpleNamespace
    from unittest.mock import patch
    import check_repo

    if hasattr(check_repo.get_model_modules, "cache_clear"):
        check_repo.get_model_modules.cache_clear()

    class FakeNamespace:
        def __init__(self, mapping):
            self._mapping = mapping

        def __dir__(self):
            return list(self._mapping.keys())

        def __getattr__(self, name):
            try:
                return self._mapping[name]
            except KeyError as e:
                raise AttributeError(name) from e

    alpha_modeling = object()
    alpha_module = FakeNamespace({"modeling_alpha": alpha_modeling})
    beta_modeling = object()
    beta_module = FakeNamespace({"modeling_beta": beta_modeling})
    fake_models = FakeNamespace({"alpha": alpha_module, "beta": beta_module})
    fake_transformers = SimpleNamespace(models=fake_models)

    with patch.object(check_repo, "transformers", fake_transformers):
        first = check_repo.get_model_modules()
        second = check_repo.get_model_modules()

    assert first is second, "get_model_modules() should return cached (identical) object"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_toplevel_missing_kwargs_caught():
    """Top-level PreTrainedModel subclass without **kwargs must still be flagged."""
    exc, msg = _run_check_with_models({
        "badmodel": """
class PreTrainedModel:
    pass

class BadModel(PreTrainedModel):
    def forward(self, hidden_states):
        return hidden_states
"""
    })
    assert exc is not None, "Expected exception for top-level class missing **kwargs"
    assert "BadModel" in msg, f"Expected BadModel in error: {msg}"


# [pr_diff] pass_to_pass
def test_toplevel_with_kwargs_passes():
    """Top-level PreTrainedModel subclass WITH **kwargs should pass."""
    exc, msg = _run_check_with_models({
        "goodmodel": """
class PreTrainedModel:
    pass

class GoodModel(PreTrainedModel):
    def forward(self, hidden_states, **kwargs):
        return hidden_states
"""
    })
    assert exc is None, f"Top-level class with **kwargs should pass, got: {msg}"


# ---------------------------------------------------------------------------
# Repo CI/CD (pass_to_pass) — ensure repo checks pass on base commit
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — CI: python -m py_compile
def test_repo_py_compile():
    """Repo's check_repo.py compiles without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", CHECK_REPO],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass — CI: module import check
def test_repo_module_importable():
    """Repo's check_repo module can be imported (pass_to_pass)."""
    r = subprocess.run(
        [
            "python",
            "-c",
            f"import sys; sys.path.insert(0, '{REPO}/utils'); sys.path.insert(0, '{REPO}/src'); import check_repo; print('OK')",
        ],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Module import failed:\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass — CI: check_model_list
def test_repo_check_model_list():
    """Repo's check_model_list() passes (pass_to_pass)."""
    r = subprocess.run(
        [
            "python",
            "-c",
            f"import sys; sys.path.insert(0, '{REPO}/utils'); sys.path.insert(0, '{REPO}/src'); from check_repo import check_model_list; check_model_list(); print('OK')",
        ],
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_model_list failed:\n{r.stderr.decode()[-500:]}"


# [repo_tests] pass_to_pass — CI: check_models_have_kwargs (modified function)
def test_repo_check_models_have_kwargs():
    """Repo's check_models_have_kwargs() passes (pass_to_pass) — tests the fixed function."""
    r = subprocess.run(
        [
            "python",
            "-c",
            f"import sys; sys.path.insert(0, '{REPO}/utils'); sys.path.insert(0, '{REPO}/src'); from check_repo import check_models_have_kwargs; check_models_have_kwargs(); print('OK')",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"check_models_have_kwargs failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI: ast.parse check on modified file
def test_repo_ast_parse():
    """Modified file utils/check_repo.py parses as valid Python AST (pass_to_pass)."""
    r = subprocess.run(
        [
            "python",
            "-c",
            f"import ast; ast.parse(open('{CHECK_REPO}').read()); print('OK')",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"AST parse failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI: ruff format check on modified file
def test_repo_ruff_format():
    """Modified file utils/check_repo.py follows ruff formatting (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", CHECK_REPO, "--config", f"{REPO}/pyproject.toml"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI: check_models_are_in_init
def test_repo_check_models_are_in_init():
    """Repo's check_models_are_in_init() passes (pass_to_pass)."""
    r = subprocess.run(
        [
            "python",
            "-c",
            f"import sys; sys.path.insert(0, '{REPO}/utils'); sys.path.insert(0, '{REPO}/src'); from check_repo import check_models_are_in_init; check_models_are_in_init(); print('OK')",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_models_are_in_init failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI: check_all_auto_mappings_importable
def test_repo_check_all_auto_mappings_importable():
    """Repo's check_all_auto_mappings_importable() passes (pass_to_pass)."""
    r = subprocess.run(
        [
            "python",
            "-c",
            f"import sys; sys.path.insert(0, '{REPO}/utils'); sys.path.insert(0, '{REPO}/src'); from check_repo import check_all_auto_mappings_importable; check_all_auto_mappings_importable(); print('OK')",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_all_auto_mappings_importable failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI: check_all_models_are_tested
def test_repo_check_all_models_are_tested():
    """Repo's check_all_models_are_tested() passes (pass_to_pass)."""
    r = subprocess.run(
        [
            "python",
            "-c",
            f"import sys; sys.path.insert(0, '{REPO}/utils'); sys.path.insert(0, '{REPO}/src'); from check_repo import check_all_models_are_tested; check_all_models_are_tested(); print('OK')",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"check_all_models_are_tested failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI: custom_init_isort check
def test_repo_init_isort():
    """Repo's init file isort check passes (pass_to_pass)."""
    r = subprocess.run(
        [
            "python",
            f"{REPO}/utils/custom_init_isort.py",
            "--check_only",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"custom_init_isort failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI: sort_auto_mappings check
def test_repo_sort_auto_mappings():
    """Repo's auto mappings sort check passes (pass_to_pass)."""
    r = subprocess.run(
        [
            "python",
            f"{REPO}/utils/sort_auto_mappings.py",
            "--check_only",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"sort_auto_mappings failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:2 @ 9a9997fd73c5eb29fb3677d3c489f5d3cd0765f6
def test_ruff_lint():
    """Modified file passes ruff linting (CLAUDE.md: 'make style: runs formatters and linters (ruff)')."""
    r = subprocess.run(
        ["ruff", "check", CHECK_REPO, "--config", f"{REPO}/pyproject.toml", "--quiet"],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Anti-stub (static) — pass_to_pass
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """check_repo.py must not be stubbed out (should have >1000 lines of real code)."""
    lines = Path(CHECK_REPO).read_text().splitlines()
    assert len(lines) >= 1000, f"check_repo.py only has {len(lines)} lines (expected >= 1000)"
