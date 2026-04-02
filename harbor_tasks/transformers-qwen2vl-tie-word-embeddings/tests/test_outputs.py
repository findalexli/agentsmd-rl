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
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_qwen2vl_text_no_own_tie_field():
    """Qwen2VLTextConfig must not define tie_word_embeddings as its own dataclass field."""
    from transformers.models.qwen2_vl.configuration_qwen2_vl import Qwen2VLTextConfig

    own_annotations = vars(Qwen2VLTextConfig).get("__annotations__", {})
    assert "tie_word_embeddings" not in own_annotations, (
        "tie_word_embeddings should be removed from Qwen2VLTextConfig class-level fields"
    )
    # Must still be accessible via inheritance from PreTrainedConfig
    cfg = Qwen2VLTextConfig()
    assert hasattr(cfg, "tie_word_embeddings")


# [pr_diff] fail_to_pass
def test_qwen2_5_vl_text_no_own_tie_field():
    """Qwen2_5_VLTextConfig must not define tie_word_embeddings as its own dataclass field."""
    from transformers.models.qwen2_5_vl.configuration_qwen2_5_vl import Qwen2_5_VLTextConfig

    own_annotations = vars(Qwen2_5_VLTextConfig).get("__annotations__", {})
    assert "tie_word_embeddings" not in own_annotations, (
        "tie_word_embeddings should be removed from Qwen2_5_VLTextConfig class-level fields"
    )
    cfg = Qwen2_5_VLTextConfig()
    assert hasattr(cfg, "tie_word_embeddings")


# [pr_diff] pass_to_pass
def test_text_configs_instantiate():
    """Text sub-configs can be instantiated with no args and have expected fields."""
    from transformers.models.qwen2_vl.configuration_qwen2_vl import Qwen2VLTextConfig
    from transformers.models.qwen2_5_vl.configuration_qwen2_5_vl import Qwen2_5_VLTextConfig

    for ConfigCls in [Qwen2VLTextConfig, Qwen2_5_VLTextConfig]:
        cfg = ConfigCls()
        assert cfg.vocab_size == 152064, f"{ConfigCls.__name__}.vocab_size unexpected"
        d = cfg.to_dict()
        assert isinstance(d, dict)
        assert "vocab_size" in d
        assert d["model_type"] in ("qwen2_vl_text", "qwen2_5_vl_text")


# [pr_diff] fail_to_pass
def test_modernvbert_init_type_hint():
    """ModernVBertForMaskedLM.__init__ config param must have a type annotation.

    AST check justified: modeling file imports torch which is not installed.
    """
    source = (Path(REPO) / "src/transformers/models/modernvbert/modeling_modernvbert.py").read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ModernVBertForMaskedLM":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    config_args = [a for a in item.args.args if a.arg == "config"]
                    assert config_args, "No 'config' parameter found"
                    assert config_args[0].annotation is not None, (
                        "config parameter missing type annotation"
                    )
                    return
    assert False, "ModernVBertForMaskedLM class or __init__ not found"


# [pr_diff] fail_to_pass
def test_modular_init_type_hint():
    """modular_modernvbert.py ModernVBertForMaskedLM.__init__ also needs the type hint.

    AST check justified: modular file imports torch-dependent modules.
    """
    source = (Path(REPO) / "src/transformers/models/modernvbert/modular_modernvbert.py").read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ModernVBertForMaskedLM":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    config_args = [a for a in item.args.args if a.arg == "config"]
                    assert config_args, "No 'config' parameter found"
                    assert config_args[0].annotation is not None, (
                        "config parameter missing type annotation in modular file"
                    )
                    return
    assert False, "ModernVBertForMaskedLM class or __init__ not found in modular file"


# [pr_diff] fail_to_pass
def test_downstream_no_tie_propagation_hack():
    """ColQwen2Config and ColModernVBertConfig must not contain tie_word_embeddings propagation hack.

    Source inspection because: hack removal is dead-code cleanup with no distinct behavioral
    effect once the text config's own tie_word_embeddings field is removed.
    """
    import inspect
    from transformers.models.colqwen2.configuration_colqwen2 import ColQwen2Config
    from transformers.models.colmodernvbert.configuration_colmodernvbert import ColModernVBertConfig

    for ConfigCls in [ColQwen2Config, ColModernVBertConfig]:
        source = inspect.getsource(ConfigCls)
        assert "vlm_config.text_config.tie_word_embeddings" not in source, (
            f"{ConfigCls.__name__} still contains tie_word_embeddings propagation hack"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_config_roundtrip():
    """Config instantiation and to_dict serialization must work for all affected configs."""
    from transformers.models.qwen2_vl.configuration_qwen2_vl import Qwen2VLTextConfig, Qwen2VLConfig
    from transformers.models.qwen2_5_vl.configuration_qwen2_5_vl import Qwen2_5_VLTextConfig, Qwen2_5_VLConfig

    # Text configs declare vocab_size directly
    for ConfigCls in [Qwen2VLTextConfig, Qwen2_5_VLTextConfig]:
        cfg = ConfigCls()
        d = cfg.to_dict()
        assert isinstance(d, dict), f"{ConfigCls.__name__}.to_dict() did not return dict"
        assert "model_type" in d, f"{ConfigCls.__name__}.to_dict() missing model_type"
        assert d["vocab_size"] == cfg.vocab_size, (
            f"{ConfigCls.__name__} vocab_size mismatch in round-trip"
        )

    # Composite configs don't declare vocab_size at the top level
    for ConfigCls in [Qwen2VLConfig, Qwen2_5_VLConfig]:
        cfg = ConfigCls()
        d = cfg.to_dict()
        assert isinstance(d, dict), f"{ConfigCls.__name__}.to_dict() did not return dict"
        assert "model_type" in d, f"{ConfigCls.__name__}.to_dict() missing model_type"


# [pr_diff] pass_to_pass
def test_downstream_configs_instantiate():
    """ColQwen2Config and ColModernVBertConfig must instantiate and serialize."""
    from transformers.models.colqwen2.configuration_colqwen2 import ColQwen2Config
    from transformers.models.colmodernvbert.configuration_colmodernvbert import ColModernVBertConfig

    for ConfigCls in [ColQwen2Config, ColModernVBertConfig]:
        cfg = ConfigCls()
        d = cfg.to_dict()
        assert isinstance(d, dict), f"{ConfigCls.__name__}.to_dict() failed"


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


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:2 @ 28e1cc59ecf479ea674f2cc4b443a2969aae3a69
def test_ruff_lint():
    """ruff linter must pass on all changed files (CLAUDE.md: 'make style: runs formatters and linters')."""
    files = [
        f"{REPO}/src/transformers/models/qwen2_vl/configuration_qwen2_vl.py",
        f"{REPO}/src/transformers/models/qwen2_5_vl/configuration_qwen2_5_vl.py",
        f"{REPO}/src/transformers/models/colqwen2/configuration_colqwen2.py",
        f"{REPO}/src/transformers/models/colmodernvbert/configuration_colmodernvbert.py",
        f"{REPO}/src/transformers/models/modernvbert/modeling_modernvbert.py",
        f"{REPO}/src/transformers/models/modernvbert/modular_modernvbert.py",
    ]
    r = subprocess.run(
        ["ruff", "check", "--select", "E,W", "--quiet"] + files,
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
