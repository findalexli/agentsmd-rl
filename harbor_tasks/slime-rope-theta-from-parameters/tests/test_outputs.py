"""
Task: slime-rope-theta-from-parameters
Repo: THUDM/slime @ 73a1f4d935baf1619bf764eadd199a77cecf55cf
PR:   1734

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import textwrap
import pytest
from pathlib import Path

REPO = "/workspace/slime"
TARGET = Path(f"{REPO}/slime_plugins/mbridge/deepseek_v32.py")


class _MockDeepseekV3Bridge:
    """Stand-in for the parent class DeepseekV3Bridge."""

    def __init__(self, hf_config, **kwargs):
        self.hf_config = hf_config


def _load_bridge_init_class():
    """Extract only __init__ from DeepseekV32Bridge and exec with mock parent.

    AST-only extraction because: the full class references torch.Tensor in
    annotations and DeepseekV3Bridge._ATTENTION_MAPPING at class-body level,
    neither of which is available without GPU deps.
    """
    source = TARGET.read_text()
    tree = ast.parse(source)

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef) and node.name == "DeepseekV32Bridge":
            # Look for __init__
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    lines = source.splitlines()
                    init_source = "\n".join(lines[item.lineno - 1 : item.end_lineno])
                    init_dedented = textwrap.dedent(init_source)
                    class_code = (
                        "class DeepseekV32Bridge(DeepseekV3Bridge):\n"
                        + textwrap.indent(init_dedented, "    ")
                    )
                    ns = {"DeepseekV3Bridge": _MockDeepseekV3Bridge}
                    exec(class_code, ns)
                    return ns["DeepseekV32Bridge"]

            # No __init__ found — return bare subclass (will fail f2p tests)
            class _Bare(_MockDeepseekV3Bridge):
                pass

            return _Bare

    pytest.fail("DeepseekV32Bridge class not found in source")


def _get_class_ast():
    """Return the AST ClassDef node for DeepseekV32Bridge."""
    source = TARGET.read_text()
    tree = ast.parse(source)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef) and node.name == "DeepseekV32Bridge":
            return node
    pytest.fail("DeepseekV32Bridge class not found in source")


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_valid():
    """Target file parses without syntax errors."""
    source = TARGET.read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_rope_theta_from_parameters():
    """rope_theta resolved from rope_parameters dict when top-level absent (transformers 5.x)."""
    Bridge = _load_bridge_init_class()

    for expected_theta in [500000, 10000, 1234567]:

        class Config:
            rope_parameters = {"rope_theta": expected_theta}

        cfg = Config()
        assert not hasattr(cfg, "rope_theta"), "setup: rope_theta should not exist yet"
        Bridge(cfg)
        assert hasattr(cfg, "rope_theta"), "rope_theta not set on config"
        assert cfg.rope_theta == expected_theta, f"Expected {expected_theta}, got {cfg.rope_theta}"


# [pr_diff] fail_to_pass
def test_rope_theta_default_when_missing():
    """rope_theta defaults to 1000000 when neither rope_theta nor rope_parameters exists."""
    Bridge = _load_bridge_init_class()

    class Config:
        pass

    cfg = Config()
    Bridge(cfg)
    assert hasattr(cfg, "rope_theta"), "rope_theta not set on config"
    assert cfg.rope_theta == 1000000, f"Expected default 1000000, got {cfg.rope_theta}"


# [pr_diff] fail_to_pass
def test_rope_theta_empty_rope_parameters():
    """rope_theta defaults to 1000000 when rope_parameters is an empty dict."""
    Bridge = _load_bridge_init_class()

    class Config:
        rope_parameters = {}

    cfg = Config()
    Bridge(cfg)
    assert hasattr(cfg, "rope_theta"), "rope_theta not set on config"
    assert cfg.rope_theta == 1000000, f"Expected default 1000000, got {cfg.rope_theta}"


# [pr_diff] fail_to_pass
def test_rope_theta_none_rope_parameters():
    """rope_theta defaults to 1000000 when rope_parameters is None."""
    Bridge = _load_bridge_init_class()

    class Config:
        rope_parameters = None

    cfg = Config()
    Bridge(cfg)
    assert hasattr(cfg, "rope_theta"), "rope_theta not set on config"
    assert cfg.rope_theta == 1000000, f"Expected default 1000000, got {cfg.rope_theta}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + backward compat
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_rope_theta_preserved_when_present():
    """Existing rope_theta not overwritten (transformers 4.x backward compat)."""
    Bridge = _load_bridge_init_class()

    for original_value in [10000, 250000, 1000000]:

        class Config:
            rope_theta = original_value

        cfg = Config()
        Bridge(cfg)
        assert cfg.rope_theta == original_value, (
            f"rope_theta changed from {original_value} to {cfg.rope_theta}"
        )


# [pr_diff] pass_to_pass
def test_super_init_called():
    """super().__init__ is called, preserving parent initialization."""
    Bridge = _load_bridge_init_class()

    class Config:
        rope_theta = 10000

    cfg = Config()
    bridge = Bridge(cfg)
    assert bridge.hf_config is cfg, "super().__init__ not called (hf_config not stored)"


# [static] pass_to_pass — AST-only because: full class can't be exec'd without torch
def test_class_members_preserved():
    """Original class attributes (_DSA_ATTENTION_MAPPING) and methods not removed."""
    cls_node = _get_class_ast()

    member_names = set()
    for item in cls_node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    member_names.add(target.id)
        elif isinstance(item, ast.FunctionDef):
            member_names.add(item.name)

    assert "_DSA_ATTENTION_MAPPING" in member_names, "_DSA_ATTENTION_MAPPING removed"
    assert "_weight_to_hf_format" in member_names, "_weight_to_hf_format removed"
    assert "_weight_to_mcore_format" in member_names, "_weight_to_mcore_format removed"
