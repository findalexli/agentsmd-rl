"""
Task: slime-rope-theta-parameters-dict
Repo: THUDM/slime @ 600624625219566f742540189dd18399d310d923
PR:   1720

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import sys
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO = "/workspace/slime"
TARGET = f"{REPO}/slime/backends/megatron_utils/arguments.py"


def _get_validate_fn():
    """Get _hf_validate_args by import or source extraction."""
    # Try direct import first
    try:
        sys.path.insert(0, REPO)
        import importlib
        mod = importlib.import_module("slime.backends.megatron_utils.arguments")
        for name in dir(mod):
            if "hf_validate_args" in name and callable(getattr(mod, name)):
                return getattr(mod, name)
    except Exception:
        pass

    # Fallback: extract from source and exec
    src = Path(TARGET).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and "hf_validate_args" in node.name:
            lines = src.splitlines(keepends=True)
            func_src = textwrap.dedent(
                "".join(lines[node.lineno - 1 : node.end_lineno])
            )
            ns = {}
            exec(compile(func_src, TARGET, "exec"), ns)
            return ns[node.name]

    raise RuntimeError("hf_validate_args function not found in source")


def _make_args(**overrides):
    """Create a mock args namespace matching Megatron config names."""
    defaults = dict(
        hidden_size=1024,
        num_attention_heads=16,
        num_layers=24,
        ffn_hidden_size=4096,
        untie_embeddings_and_output_weights=False,
        norm_epsilon=1e-6,
        rotary_base=10000,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_config(**overrides):
    """Create a mock HF config namespace matching HF config names."""
    defaults = dict(
        hidden_size=1024,
        num_attention_heads=16,
        num_hidden_layers=24,
        intermediate_size=4096,
        tie_word_embeddings=True,
        rms_norm_eps=1e-6,
        rope_theta=10000,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """arguments.py must parse without errors."""
    src = Path(TARGET).read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rope_theta_from_parameters_dict():
    """rope_theta=500000 in rope_parameters dict used instead of stale default 10000."""
    validate = _get_validate_fn()
    config = _make_config(
        rope_theta=10000,  # stale class default
        rope_parameters={"rope_theta": 500000},  # actual value from model
    )
    args = _make_args(rotary_base=500000)
    # Should NOT raise — dict value 500000 matches rotary_base
    validate(args, config)


# [pr_diff] fail_to_pass
def test_rope_theta_from_parameters_dict_varied():
    """Same fix with different theta value (200000)."""
    validate = _get_validate_fn()
    config = _make_config(
        rope_theta=10000,
        rope_parameters={"rope_theta": 200000},
    )
    args = _make_args(rotary_base=200000)
    validate(args, config)


# [pr_diff] fail_to_pass
def test_mismatch_detected_with_dict_override():
    """Dict rope_theta overrides stale default; mismatch with args is caught."""
    validate = _get_validate_fn()
    config = _make_config(
        rope_theta=10000,  # stale, matches args
        rope_parameters={"rope_theta": 999},  # actual, doesn't match
    )
    args = _make_args(rotary_base=10000)
    with pytest.raises(AssertionError, match=r"rope_theta|rotary_base"):
        validate(args, config)


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression / fallback path
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_fallback_to_direct_attribute():
    """Without rope_parameters dict, direct rope_theta attribute still validates."""
    validate = _get_validate_fn()
    config = _make_config(rope_theta=10000)  # no rope_parameters
    args = _make_args(rotary_base=10000)
    validate(args, config)


# [pr_diff] pass_to_pass
def test_fallback_mismatch_detected():
    """Without rope_parameters, mismatch via direct attribute still raises."""
    validate = _get_validate_fn()
    config = _make_config(rope_theta=500000)  # no rope_parameters
    args = _make_args(rotary_base=10000)
    with pytest.raises(AssertionError, match=r"rope_theta|rotary_base"):
        validate(args, config)


# ---------------------------------------------------------------------------
# Anti-stub (static, pass_to_pass)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """_hf_validate_args has real validation logic, not a stub."""
    src = Path(TARGET).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and "hf_validate_args" in node.name:
            stmts = [
                s for s in node.body
                if not isinstance(s, ast.Pass)
                and not (
                    isinstance(s, ast.Expr)
                    and isinstance(getattr(s, "value", None), ast.Constant)
                )
            ]
            assert len(stmts) >= 5, f"Function body too shallow ({len(stmts)} stmts)"
            return
    raise AssertionError("hf_validate_args function not found")
