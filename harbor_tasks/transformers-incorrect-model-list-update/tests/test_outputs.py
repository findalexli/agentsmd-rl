"""
Task: transformers-incorrect-model-list-update
Repo: huggingface/transformers @ a48a63c27d1cdb7845d2c3acc4f11f580917b69b

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
import typing
from pathlib import Path

REPO = "/workspace/transformers"

sys.path.insert(0, f"{REPO}/src")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without syntax errors."""
    import py_compile

    for f in [
        "src/transformers/models/auto/tokenization_auto.py",
        "src/transformers/models/llama4/configuration_llama4.py",
    ]:
        py_compile.compile(f"{REPO}/{f}", doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_key_missing_models_present():
    """Key model types added by the PR must be in MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS."""
    from transformers.models.auto.tokenization_auto import (
        MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS,
    )

    key_models = {"h2ovl_chat", "internvl_chat", "molmo", "phi3_v", "openvla", "kimi_k25"}
    missing = key_models - MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS
    assert not missing, f"Missing key models: {missing}"


# [pr_diff] fail_to_pass
def test_remaining_missing_models_present():
    """All remaining model types added by the PR must be in the set."""
    from transformers.models.auto.tokenization_auto import (
        MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS,
    )

    remaining = {"chatlm", "minimax_m2", "molmo2", "nemotron", "nvfp4", "phimoe", "minicpmv"}
    missing = remaining - MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS
    assert not missing, f"Missing remaining models: {missing}"


# [pr_diff] pass_to_pass
def test_layer_types_accepts_strings():
    """Llama4TextConfig.layer_types must accept and store string values."""
    from transformers.models.llama4.configuration_llama4 import Llama4TextConfig

    config = Llama4TextConfig(layer_types=["dense", "moe", "dense"])
    assert config.layer_types is not None, "layer_types is None after setting"
    assert all(isinstance(t, str) for t in config.layer_types), "layer_types contains non-string values"
    assert config.layer_types == ["dense", "moe", "dense"], f"Unexpected value: {config.layer_types}"

    # Also test with different string values to vary inputs
    config2 = Llama4TextConfig(layer_types=["attention", "ffn", "attention", "moe"])
    assert config2.layer_types == ["attention", "ffn", "attention", "moe"]


# [pr_diff] fail_to_pass
def test_layer_types_type_annotation():
    """The type annotation for layer_types must declare str, not int."""
    from transformers.models.llama4.configuration_llama4 import Llama4TextConfig

    hints = typing.get_type_hints(Llama4TextConfig)
    layer_hint = hints.get("layer_types")
    assert layer_hint is not None, "layer_types has no type hint"
    hint_str = str(layer_hint)
    assert "str" in hint_str, f"Type hint missing str: {hint_str}"
    assert "int" not in hint_str, f"Type hint still declares int: {hint_str}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_preexisting_models_retained():
    """Pre-existing entries must not be removed from the set."""
    from transformers.models.auto.tokenization_auto import (
        MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS,
    )

    existing = {
        "arctic", "chameleon", "deepseek_v2", "deepseek_v3", "deepseek_vl",
        "deepseek_vl_v2", "deepseek_vl_hybrid", "fuyu", "hyperclovax_vlm",
        "internlm2", "jamba", "janus", "llava", "llava_next", "modernbert",
        "opencua", "phi3", "step3p5", "vipllava",
    }
    missing = existing - MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS
    assert not missing, f"Removed pre-existing models: {missing}"


# [pr_diff] pass_to_pass
def test_llama4_config_attributes_intact():
    """Other Llama4TextConfig attributes must remain intact."""
    from transformers.models.llama4.configuration_llama4 import Llama4TextConfig

    config = Llama4TextConfig()
    assert isinstance(config.attention_chunk_size, int), "attention_chunk_size wrong type"
    assert isinstance(config.attn_temperature_tuning, bool), "attn_temperature_tuning wrong type"
    assert isinstance(config.floor_scale, int), "floor_scale wrong type"
    assert isinstance(config.attn_scale, float), "attn_scale wrong type"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:5 @ a48a63c27d1cdb7845d2c3acc4f11f580917b69b
def test_set_entries_sorted():
    """Set entries in source file must be sorted alphabetically (make check-repo consistency)."""
    import ast

    src = Path(f"{REPO}/src/transformers/models/auto/tokenization_auto.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and hasattr(node.target, "id"):
            if node.target.id == "MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS":
                assert hasattr(node.value, "elts"), "Set is not a literal — cannot verify order"
                source_order = [
                    elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)
                ]
                assert source_order == sorted(source_order), (
                    f"Entries not sorted: got {source_order}"
                )
                return

    raise AssertionError("MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS not found in source")


# [agent_config] pass_to_pass — CLAUDE.md:2 @ a48a63c27d1cdb7845d2c3acc4f11f580917b69b
def test_ruff_lint_clean():
    """Changed files must pass ruff lint (make style)."""
    r = subprocess.run(
        [
            "python3", "-m", "ruff", "check",
            "src/transformers/models/auto/tokenization_auto.py",
            "src/transformers/models/llama4/configuration_llama4.py",
            "--select", "E,W", "--quiet",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff lint issues:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Anti-stub (static) — set cardinality check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_set_has_sufficient_entries():
    """Set must contain all expected models (>= 25 entries), not be gutted."""
    from transformers.models.auto.tokenization_auto import (
        MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS,
    )

    count = len(MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS)
    assert count >= 25, f"Only {count} entries, expected >= 25"
