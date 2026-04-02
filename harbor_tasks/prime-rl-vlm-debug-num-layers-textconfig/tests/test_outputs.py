"""
Task: prime-rl-vlm-debug-num-layers-textconfig
Repo: PrimeIntellect-ai/prime-rl @ c2dfc338c30d04286284b67cf87e73d534e43f3e
PR:   #2080

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import textwrap
from pathlib import Path

REPO = "/workspace"
MODEL_PY = Path(f"{REPO}/src/prime_rl/trainer/model.py")


def _extract_debug_num_layers_block():
    """AST-extract the `if config.debug.num_layers is not None:` block from model.py."""
    source = MODEL_PY.read_text()
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)

    def _refs_debug_num_layers(node):
        for child in ast.walk(node):
            if isinstance(child, ast.Attribute) and child.attr == "num_layers":
                inner = child.value
                if isinstance(inner, ast.Attribute) and inner.attr == "debug":
                    return True
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.If) and _refs_debug_num_layers(node.test):
            block_src = "".join(lines[node.lineno - 1 : node.end_lineno])
            return textwrap.dedent(block_src)

    # Also check inside nested functions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for child in ast.walk(node):
                if isinstance(child, ast.If) and _refs_debug_num_layers(child.test):
                    block_src = "".join(lines[child.lineno - 1 : child.end_lineno])
                    return textwrap.dedent(block_src)

    raise AssertionError("Could not find debug.num_layers if-block in model.py")


class _FakeLogger:
    def __init__(self):
        self.warnings = []

    def warning(self, msg, *a, **kw):
        self.warnings.append(msg)

    def debug(self, *a, **kw):
        pass

    def info(self, *a, **kw):
        pass


def _run_block(block_src, model_config, config):
    """Exec the extracted block with mocked globals, return the logger."""
    logger = _FakeLogger()
    exec(
        block_src,
        {
            "config": config,
            "model_config": model_config,
            "logger": logger,
            "min": min,
            "max": max,
            "__builtins__": __builtins__,
        },
    )
    return logger


def _make_config(num_layers):
    class DebugConfig:
        pass

    class Config:
        pass

    d = DebugConfig()
    d.num_layers = num_layers
    c = Config()
    c.debug = d
    return c


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """model.py must parse without syntax errors."""
    source = MODEL_PY.read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_vlm_no_toplevel():
    """VLM config with num_hidden_layers only under text_config must not crash."""
    block = _extract_debug_num_layers_block()

    class TextConfig:
        num_hidden_layers = 32

    class ModelConfig:
        text_config = TextConfig()

    model_config = ModelConfig()
    _run_block(block, model_config, _make_config(num_layers=4))
    assert model_config.text_config.num_hidden_layers == 4


# [pr_diff] fail_to_pass
def test_vlm_both_attrs():
    """When both levels have num_hidden_layers, text_config must be modified."""
    block = _extract_debug_num_layers_block()

    class TextConfig:
        num_hidden_layers = 24

    class ModelConfig:
        text_config = TextConfig()
        num_hidden_layers = 48

    model_config = ModelConfig()
    _run_block(block, model_config, _make_config(num_layers=6))
    assert model_config.text_config.num_hidden_layers == 6


# [pr_diff] fail_to_pass
def test_vlm_min_clamp():
    """debug.num_layers > actual layers should clamp via min()."""
    block = _extract_debug_num_layers_block()

    class TextConfig:
        num_hidden_layers = 8

    class ModelConfig:
        text_config = TextConfig()

    model_config = ModelConfig()
    _run_block(block, model_config, _make_config(num_layers=100))
    assert model_config.text_config.num_hidden_layers == 8


# [pr_diff] fail_to_pass
def test_vlm_warning_message():
    """Warning log must not crash for VLMs and report correct skipped layer count."""
    block = _extract_debug_num_layers_block()

    # Test with multiple layer counts to prevent hardcoding
    for total, requested, expected_skipped in [(32, 4, 28), (16, 4, 12), (24, 10, 14)]:

        class TextConfig:
            num_hidden_layers = total

        class ModelConfig:
            text_config = TextConfig()

        model_config = ModelConfig()
        logger = _run_block(block, model_config, _make_config(num_layers=requested))
        assert logger.warnings, f"No warning logged for {total} layers, requesting {requested}"
        assert str(expected_skipped) in str(logger.warnings[0]), (
            f"Warning should mention {expected_skipped} skipped layers (total={total}, "
            f"requested={requested}), got: {logger.warnings[0]}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — backward compatibility
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_non_vlm_backward_compat():
    """Standard LM config (no text_config) still works."""
    block = _extract_debug_num_layers_block()

    class ModelConfig:
        num_hidden_layers = 32

    model_config = ModelConfig()
    _run_block(block, model_config, _make_config(num_layers=4))
    assert model_config.num_hidden_layers == 4


# [pr_diff] pass_to_pass
def test_non_vlm_min_clamp():
    """Non-VLM: debug.num_layers > actual layers should clamp."""
    block = _extract_debug_num_layers_block()

    class ModelConfig:
        num_hidden_layers = 12

    model_config = ModelConfig()
    _run_block(block, model_config, _make_config(num_layers=999))
    assert model_config.num_hidden_layers == 12


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_not_stub():
    """get_model function must be substantive (not stubbed out)."""
    source = MODEL_PY.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_model":
            stmts = sum(1 for _ in ast.walk(node) if isinstance(_, ast.stmt))
            assert stmts > 20, f"get_model too short ({stmts} stmts) — likely stubbed"
            return
    # get_model may have been renamed — if behavioral tests pass, that's fine


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:5 @ c2dfc338
def test_no_unnecessary_try_except():
    """Fix must not wrap the debug.num_layers block in try/except (AGENTS.md:5)."""
    source = MODEL_PY.read_text()
    tree = ast.parse(source)

    def _refs_debug_num_layers(node):
        for child in ast.walk(node):
            if isinstance(child, ast.Attribute) and child.attr == "num_layers":
                inner = child.value
                if isinstance(inner, ast.Attribute) and inner.attr == "debug":
                    return True
        return False

    target_line = None
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and _refs_debug_num_layers(node.test):
            target_line = node.lineno
            break

    if target_line is None:
        return  # Can't find block — don't penalize

    for node in ast.walk(tree):
        if isinstance(node, ast.Try) and hasattr(node, "lineno"):
            assert abs(node.lineno - target_line) >= 8, (
                f"Unnecessary try/except near debug.num_layers at line {node.lineno}"
            )
