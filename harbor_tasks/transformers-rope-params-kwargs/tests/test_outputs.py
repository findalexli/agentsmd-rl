"""
Task: transformers-rope-params-kwargs
Repo: huggingface/transformers @ d65c2b138a3d27a3321f7bbced0efc9bfb5a9688
PR:   45049

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/transformers"
TARGET = f"{REPO}/src/transformers/configuration_utils.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """configuration_utils.py must parse without syntax errors."""
    import py_compile

    py_compile.compile(TARGET, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_legacy_rope_kwargs_converted():
    """Config without rope_parameters attribute but with rope_scaling+rope_theta in
    kwargs should still have rope_parameters set after init (conversion happened)."""
    sys.path.insert(0, REPO)
    from dataclasses import dataclass

    from transformers.configuration_utils import PreTrainedConfig

    @dataclass
    class NoRopeAttrConfig(PreTrainedConfig):
        model_type = "test_no_rope_attr"
        hidden_size: int = 128
        num_attention_heads: int = 4
        num_hidden_layers: int = 2
        vocab_size: int = 1000

    # Test with multiple different RoPE parameter values
    for theta, scaling_type, factor in [
        (10000.0, "linear", 2.0),
        (50000.0, "dynamic", 4.0),
    ]:
        config = NoRopeAttrConfig(
            rope_scaling={"type": scaling_type, "factor": factor},
            rope_theta=theta,
        )
        assert hasattr(config, "rope_parameters"), (
            f"rope_parameters not set for theta={theta}"
        )
        assert config.rope_parameters is not None, (
            f"rope_parameters is None for theta={theta}"
        )
        assert config.rope_parameters.get("rope_theta") == theta, (
            f"Expected rope_theta={theta}, got {config.rope_parameters.get('rope_theta')}"
        )


# [pr_diff] fail_to_pass
def test_warning_emitted_for_legacy_rope():
    """A warning/log message should be emitted when legacy RoPE kwargs are used
    on a config that doesn't define rope_parameters."""
    import io
    import logging

    sys.path.insert(0, REPO)
    from dataclasses import dataclass

    import transformers.configuration_utils
    from transformers.configuration_utils import PreTrainedConfig

    @dataclass
    class WarnTestConfig(PreTrainedConfig):
        model_type = "test_warn"
        hidden_size: int = 128
        num_attention_heads: int = 4
        num_hidden_layers: int = 2
        vocab_size: int = 1000

    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.WARNING)
    transformers.configuration_utils.logger.addHandler(handler)
    transformers.configuration_utils.logger.setLevel(logging.WARNING)

    try:
        WarnTestConfig(
            rope_scaling={"type": "linear", "factor": 2.0},
            rope_theta=10000.0,
        )
        log_output = log_capture.getvalue().lower()
        assert "rope_scaling" in log_output or "rope_parameters" in log_output, (
            f"No warning about rope params emitted. Log was: {log_capture.getvalue()}"
        )
    finally:
        transformers.configuration_utils.logger.removeHandler(handler)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_config_with_rope_parameters_attr():
    """Config class that defines rope_parameters should still work as before."""
    sys.path.insert(0, REPO)
    from dataclasses import dataclass

    from transformers.configuration_utils import PreTrainedConfig

    @dataclass
    class WithRopeConfig(PreTrainedConfig):
        model_type = "test_with_rope"
        hidden_size: int = 128
        num_attention_heads: int = 4
        num_hidden_layers: int = 2
        vocab_size: int = 1000
        rope_parameters: dict = None

    config = WithRopeConfig(
        rope_scaling={"type": "linear", "factor": 2.0},
        rope_theta=10000.0,
    )
    assert hasattr(config, "rope_parameters"), "rope_parameters attr should be set"
    assert config.rope_parameters is not None


# [repo_tests] pass_to_pass
def test_config_without_rope_kwargs():
    """Config without any RoPE kwargs should initialize normally."""
    sys.path.insert(0, REPO)
    from dataclasses import dataclass

    from transformers.configuration_utils import PreTrainedConfig

    @dataclass
    class PlainConfig(PreTrainedConfig):
        model_type = "test_plain"
        hidden_size: int = 256
        num_attention_heads: int = 8
        num_hidden_layers: int = 4
        vocab_size: int = 2000

    config = PlainConfig()
    assert config.hidden_size == 256
    assert config.num_attention_heads == 8


# [static] pass_to_pass
def test_not_stub():
    """The __post_init__ method must have real logic handling the elif branch."""
    import ast

    src = Path(TARGET).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "__post_init__":
            body_stmts = [
                s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))
            ]
            assert len(body_stmts) >= 5, (
                f"__post_init__ body too short ({len(body_stmts)} statements) — looks like a stub"
            )
            return
    raise AssertionError("__post_init__ method not found")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:2 @ d65c2b138a3d27a3321f7bbced0efc9bfb5a9688
def test_ruff_check():
    """Changed file passes ruff linting (CLAUDE.md: `make style` runs ruff)."""
    r = subprocess.run(
        ["ruff", "check", TARGET],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"ruff check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [agent_config] pass_to_pass — CLAUDE.md:2 @ d65c2b138a3d27a3321f7bbced0efc9bfb5a9688
def test_ruff_format():
    """Changed file passes ruff format check (CLAUDE.md: `make style` runs ruff format)."""
    r = subprocess.run(
        ["ruff", "format", "--check", TARGET],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"ruff format failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual repo CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — Repo CI: ruff check
def test_repo_ruff_check():
    """Repo's ruff check passes on the target file (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", TARGET],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Repo CI: Python syntax check via py_compile
def test_repo_python_syntax():
    """Target file compiles without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", TARGET],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Repo tests: ConfigTestUtils
def test_repo_config_common_kwargs():
    """Repo's config_common_kwargs test passes (pass_to_pass)."""
    r = subprocess.run(
        [
            "python",
            "-c",
            "import sys; sys.path.insert(0, '/workspace/transformers'); "
            "import unittest; from tests.utils.test_configuration_utils import ConfigTestUtils; "
            "suite = unittest.TestSuite(); "
            "suite.addTest(ConfigTestUtils('test_config_common_kwargs_is_complete')); "
            "runner = unittest.TextTestRunner(verbosity=0); "
            "result = runner.run(suite); "
            "sys.exit(0 if result.wasSuccessful() else 1)",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"config_common_kwargs test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Repo tests: ConfigTestUtils
def test_repo_config_from_string():
    """Repo's config_from_string test passes (pass_to_pass)."""
    r = subprocess.run(
        [
            "python",
            "-c",
            "import sys; sys.path.insert(0, '/workspace/transformers'); "
            "import unittest; from tests.utils.test_configuration_utils import ConfigTestUtils; "
            "suite = unittest.TestSuite(); "
            "suite.addTest(ConfigTestUtils('test_config_from_string')); "
            "runner = unittest.TextTestRunner(verbosity=0); "
            "result = runner.run(suite); "
            "sys.exit(0 if result.wasSuccessful() else 1)",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"config_from_string test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Repo CI: check_config_attributes.py
def test_repo_check_config_attributes():
    """Repo's check_config_attributes script passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", f"{REPO}/utils/check_config_attributes.py"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"check_config_attributes failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Repo CI: check_config_docstrings.py
def test_repo_check_config_docstrings():
    """Repo's check_config_docstrings script passes (pass_to_pass)."""
    r = subprocess.run(
        ["python", f"{REPO}/utils/check_config_docstrings.py"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"check_config_docstrings failed:\n{r.stderr[-500:]}"
