"""
Task: transformers-qwen2vl-tie-word-embeddings
Repo: huggingface/transformers @ 28e1cc59ecf479ea674f2cc4b443a2969aae3a69
PR:   44976

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/repo"

# Monkey-patch @auto_docstring to avoid PyTorch dependency at config import time.
# Config files do `from ...utils import auto_docstring` which calls modeling_auto
# (requires PyTorch). Replace with a no-op so config classes can be imported.
try:
    import transformers.utils as _tu
    _tu.auto_docstring = lambda **kwargs: lambda cls: cls
except ImportError:
    pass


def _find_class(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _find_method(cls_node, name):
    for item in cls_node.body:
        if isinstance(item, ast.FunctionDef) and item.name == name:
            return item
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) — actual CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ruff linter passes on modified files (pass_to_pass)."""
    files = [
        "src/transformers/models/qwen2_vl/configuration_qwen2_vl.py",
        "src/transformers/models/qwen2_5_vl/configuration_qwen2_5_vl.py",
        "src/transformers/models/colqwen2/configuration_colqwen2.py",
        "src/transformers/models/colmodernvbert/configuration_colmodernvbert.py",
        "src/transformers/models/modernvbert/modeling_modernvbert.py",
        "src/transformers/models/modernvbert/modular_modernvbert.py",
    ]
    r = subprocess.run(
        ["ruff", "check"] + [f"{REPO}/{f}" for f in files],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    files = [
        "src/transformers/models/qwen2_vl/configuration_qwen2_vl.py",
        "src/transformers/models/qwen2_5_vl/configuration_qwen2_5_vl.py",
        "src/transformers/models/colqwen2/configuration_colqwen2.py",
        "src/transformers/models/colmodernvbert/configuration_colmodernvbert.py",
        "src/transformers/models/modernvbert/modeling_modernvbert.py",
        "src/transformers/models/modernvbert/modular_modernvbert.py",
    ]
    r = subprocess.run(
        ["ruff", "format", "--check"] + [f"{REPO}/{f}" for f in files],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_copies():
    """Repo's copied code consistency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_copies.py"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"check_copies.py failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_inits():
    """Repo's init file consistency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_inits.py"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"check_inits.py failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_dummies():
    """Repo's dummy model files consistency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_dummies.py"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"check_dummies.py failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_modeling_structure():
    """Repo's modeling structure check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_modeling_structure.py"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"check_modeling_structure.py failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_doctest_list():
    """Repo's doctest list consistency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_doctest_list.py"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"check_doctest_list.py failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_pipeline_typing():
    """Repo's pipeline typing check passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_pipeline_typing.py"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"check_pipeline_typing.py failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified config/modeling files must parse without errors."""
    files = [
        "src/transformers/models/qwen2_vl/configuration_qwen2_vl.py",
        "src/transformers/models/qwen2_5_vl/configuration_qwen2_5_vl.py",
        "src/transformers/models/colqwen2/configuration_colqwen2.py",
        "src/transformers/models/colmodernvbert/configuration_colmodernvbert.py",
        "src/transformers/models/modernvbert/modeling_modernvbert.py",
        "src/transformers/models/modernvbert/modular_modernvbert.py",
    ]
    for f in files:
        source = (Path(REPO) / f).read_text()
        ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_qwen2vl_text_no_own_tie_field():
    """Qwen2VLTextConfig must not define tie_word_embeddings as its own class-level field.

    AST-only because: checking class annotation presence is inherently structural.
    """
    source = (Path(REPO) / "src/transformers/models/qwen2_vl/configuration_qwen2_vl.py").read_text()
    tree = ast.parse(source)
    cls = _find_class(tree, "Qwen2VLTextConfig")
    assert cls is not None, "Qwen2VLTextConfig class not found"

    for item in cls.body:
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            assert item.target.id != "tie_word_embeddings", (
                "tie_word_embeddings should be removed from Qwen2VLTextConfig class-level fields"
            )


# [pr_diff] fail_to_pass
def test_qwen2_5_vl_text_no_own_tie_field():
    """Qwen2_5_VLTextConfig must not define tie_word_embeddings as its own class-level field.

    AST-only because: checking class annotation presence is inherently structural.
    """
    source = (Path(REPO) / "src/transformers/models/qwen2_5_vl/configuration_qwen2_5_vl.py").read_text()
    tree = ast.parse(source)
    cls = _find_class(tree, "Qwen2_5_VLTextConfig")
    assert cls is not None, "Qwen2_5_VLTextConfig class not found"

    for item in cls.body:
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            assert item.target.id != "tie_word_embeddings", (
                "tie_word_embeddings should be removed from Qwen2_5_VLTextConfig class-level fields"
            )


# [pr_diff] fail_to_pass
def test_modernvbert_init_type_hint():
    """ModernVBertForMaskedLM.__init__ config param must have a type annotation.

    AST-only because: modeling file imports torch which is not installed.
    """
    source = (Path(REPO) / "src/transformers/models/modernvbert/modeling_modernvbert.py").read_text()
    tree = ast.parse(source)
    cls = _find_class(tree, "ModernVBertForMaskedLM")
    assert cls is not None, "ModernVBertForMaskedLM not found"
    init = _find_method(cls, "__init__")
    assert init is not None, "__init__ not found"
    config_args = [a for a in init.args.args if a.arg == "config"]
    assert config_args, "No 'config' parameter found"
    assert config_args[0].annotation is not None, (
        "config parameter missing type annotation"
    )


# [pr_diff] fail_to_pass
def test_modular_init_type_hint():
    """modular_modernvbert.py ModernVBertForMaskedLM.__init__ also needs the type hint.

    AST-only because: modular file imports torch-dependent modules.
    """
    source = (Path(REPO) / "src/transformers/models/modernvbert/modular_modernvbert.py").read_text()
    tree = ast.parse(source)
    cls = _find_class(tree, "ModernVBertForMaskedLM")
    assert cls is not None, "ModernVBertForMaskedLM not found in modular file"
    init = _find_method(cls, "__init__")
    assert init is not None, "__init__ not found in modular file"
    config_args = [a for a in init.args.args if a.arg == "config"]
    assert config_args, "No 'config' parameter found"
    assert config_args[0].annotation is not None, (
        "config parameter missing type annotation in modular file"
    )


# [pr_diff] fail_to_pass
def test_downstream_no_tie_propagation_hack():
    """ColQwen2Config and ColModernVBertConfig must not contain tie_word_embeddings propagation hack.

    Source text check because: hack removal is dead-code cleanup with no distinct
    behavioral effect once the text config's own tie_word_embeddings field is removed.
    """
    files = {
        "ColQwen2Config": "src/transformers/models/colqwen2/configuration_colqwen2.py",
        "ColModernVBertConfig": "src/transformers/models/colmodernvbert/configuration_colmodernvbert.py",
    }
    for name, path in files.items():
        source = (Path(REPO) / path).read_text()
        assert "text_config.tie_word_embeddings" not in source, (
            f"{name} still contains tie_word_embeddings propagation hack"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_text_configs_instantiate():
    """Text sub-configs can be instantiated and tie_word_embeddings is inherited."""
    from transformers.models.qwen2_vl.configuration_qwen2_vl import Qwen2VLTextConfig
    from transformers.models.qwen2_5_vl.configuration_qwen2_5_vl import Qwen2_5_VLTextConfig

    for ConfigCls in [Qwen2VLTextConfig, Qwen2_5_VLTextConfig]:
        cfg = ConfigCls()
        assert cfg.vocab_size == 152064, f"{ConfigCls.__name__}.vocab_size unexpected"
        d = cfg.to_dict()
        assert isinstance(d, dict)
        assert "vocab_size" in d
        assert d["model_type"] in ("qwen2_vl_text", "qwen2_5_vl_text")


# [pr_diff] pass_to_pass
def test_config_roundtrip():
    """Config instantiation and to_dict serialization works for text and composite configs."""
    from transformers.models.qwen2_vl.configuration_qwen2_vl import Qwen2VLTextConfig, Qwen2VLConfig
    from transformers.models.qwen2_5_vl.configuration_qwen2_5_vl import Qwen2_5_VLTextConfig, Qwen2_5_VLConfig

    for ConfigCls in [Qwen2VLTextConfig, Qwen2_5_VLTextConfig]:
        cfg = ConfigCls()
        d = cfg.to_dict()
        assert isinstance(d, dict), f"{ConfigCls.__name__}.to_dict() did not return dict"
        assert "model_type" in d, f"{ConfigCls.__name__}.to_dict() missing model_type"
        assert d["vocab_size"] == cfg.vocab_size, (
            f"{ConfigCls.__name__} vocab_size mismatch in round-trip"
        )

    for ConfigCls in [Qwen2VLConfig, Qwen2_5_VLConfig]:
        cfg = ConfigCls()
        d = cfg.to_dict()
        assert isinstance(d, dict), f"{ConfigCls.__name__}.to_dict() did not return dict"
        assert "model_type" in d, f"{ConfigCls.__name__}.to_dict() missing model_type"


# [static] pass_to_pass
def test_downstream_configs_structure():
    """ColQwen2Config and ColModernVBertConfig retain class structure after hack removal.

    AST-only because: downstream composite configs may fail to import without torch
    due to __init__.py import chains.
    """
    for cls_name, path in [
        ("ColQwen2Config", "src/transformers/models/colqwen2/configuration_colqwen2.py"),
        ("ColModernVBertConfig", "src/transformers/models/colmodernvbert/configuration_colmodernvbert.py"),
    ]:
        source = (Path(REPO) / path).read_text()
        tree = ast.parse(source)
        cls = _find_class(tree, cls_name)
        assert cls is not None, f"{cls_name} not found"
        post_init = _find_method(cls, "__post_init__")
        assert post_init is not None, f"{cls_name}.__post_init__ not found"
        # __post_init__ must still have real logic (super().__post_init__, vocab_size setup)
        body_stmts = [s for s in post_init.body
                       if not isinstance(s, (ast.Pass, ast.Expr))]
        assert len(body_stmts) >= 2, (
            f"{cls_name}.__post_init__ appears stubbed ({len(body_stmts)} statements)"
        )


# [static] pass_to_pass
def test_not_stub():
    """Modified config files must not be trivially emptied or stubbed."""
    files = [
        "src/transformers/models/qwen2_vl/configuration_qwen2_vl.py",
        "src/transformers/models/qwen2_5_vl/configuration_qwen2_5_vl.py",
        "src/transformers/models/colqwen2/configuration_colqwen2.py",
        "src/transformers/models/colmodernvbert/configuration_colmodernvbert.py",
    ]
    for f in files:
        lines = (Path(REPO) / f).read_text().splitlines()
        assert len(lines) >= 20, f"{f} has only {len(lines)} lines — appears stubbed"
