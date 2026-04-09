"""
Task: transformers-mxfp4-dependency-checks
Repo: huggingface/transformers @ a8732d5546d84bfb4519b6dbf461c947a5de45f6
PR:   44930

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import logging
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import torch

REPO = "/workspace/transformers"
TARGET = f"{REPO}/src/transformers/quantizers/quantizer_mxfp4.py"
MODULE = "transformers.quantizers.quantizer_mxfp4"

sys.path.insert(0, REPO)

# In CPU-only Docker, torch.accelerator.current_accelerator() raises RuntimeError.
# Patch it to return torch.device("cpu") so validate_environment() reaches the
# is_triton_available / is_kernels_available checks (which we also mock per-test).
_CPU_DEVICE = torch.device("cpu")
_ACCEL_PATCH = patch("torch.accelerator.current_accelerator", return_value=_CPU_DEVICE)


class _WarningCollector(logging.Handler):
    """Collects WARNING+ log messages from the transformers logger."""

    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


def _clear_warning_cache():
    try:
        from transformers.utils.logging import warning_once

        warning_once.cache_clear()
    except (ImportError, AttributeError):
        pass


def _make_quantizer(pre_quantized):
    from transformers.utils.quantization_config import Mxfp4Config
    from transformers.quantizers.quantizer_mxfp4 import Mxfp4HfQuantizer

    config = Mxfp4Config()
    q = Mxfp4HfQuantizer(config)
    q.pre_quantized = pre_quantized
    return q


def _collect_warnings(quantizer):
    """Call validate_environment and return lowercased warning text."""
    _clear_warning_cache()
    collector = _WarningCollector()
    logger = logging.getLogger("transformers")
    logger.addHandler(collector)
    try:
        quantizer.validate_environment()
    finally:
        logger.removeHandler(collector)
    return " ".join(collector.messages).lower()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    src = Path(TARGET).read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_warning_triton_missing_mentions_triton():
    """pre_quantized + triton missing + kernels present: warning mentions triton, not combined."""
    q = _make_quantizer(pre_quantized=True)
    with (
        _ACCEL_PATCH,
        patch(f"{MODULE}.is_triton_available", return_value=False),
        patch(f"{MODULE}.is_kernels_available", return_value=True),
    ):
        warnings = _collect_warnings(q)

    assert "triton" in warnings, f"Warning should mention triton, got: {warnings}"
    assert "triton and kernels" not in warnings, f"Should not use combined message: {warnings}"
    assert q.quantization_config.dequantize is True


# [pr_diff] fail_to_pass
def test_warning_kernels_missing_mentions_kernels():
    """pre_quantized + triton present + kernels missing: warning mentions kernels, not combined."""
    q = _make_quantizer(pre_quantized=True)
    with (
        _ACCEL_PATCH,
        patch(f"{MODULE}.is_triton_available", return_value=True),
        patch(f"{MODULE}.is_kernels_available", return_value=False),
    ):
        warnings = _collect_warnings(q)

    assert "kernel" in warnings, f"Warning should mention kernels, got: {warnings}"
    assert "triton and kernels" not in warnings, f"Should not use combined message: {warnings}"
    assert q.quantization_config.dequantize is True


# [pr_diff] fail_to_pass
def test_error_triton_missing_raises_for_triton():
    """Not pre_quantized + triton missing + kernels present: ValueError mentions triton."""
    q = _make_quantizer(pre_quantized=False)
    with (
        _ACCEL_PATCH,
        patch(f"{MODULE}.is_triton_available", return_value=False),
        patch(f"{MODULE}.is_kernels_available", return_value=True),
    ):
        with pytest.raises(ValueError) as exc_info:
            q.validate_environment()

    msg = str(exc_info.value).lower()
    assert "triton" in msg, f"Error should mention triton, got: {msg}"
    assert "triton and kernels" not in msg, f"Should not use combined message: {msg}"


# [pr_diff] fail_to_pass
def test_error_kernels_missing_raises_for_kernels():
    """Not pre_quantized + triton present + kernels missing: ValueError mentions kernels."""
    q = _make_quantizer(pre_quantized=False)
    with (
        _ACCEL_PATCH,
        patch(f"{MODULE}.is_triton_available", return_value=True),
        patch(f"{MODULE}.is_kernels_available", return_value=False),
    ):
        with pytest.raises(ValueError) as exc_info:
            q.validate_environment()

    msg = str(exc_info.value).lower()
    assert "kernel" in msg, f"Error should mention kernels, got: {msg}"
    assert "triton and kernels" not in msg, f"Should not use combined message: {msg}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structure + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_validate_environment_not_stub():
    """validate_environment has substantial implementation with essential references."""
    src = Path(TARGET).read_text()
    tree = ast.parse(src)

    func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and "Mxfp4" in node.name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "validate_environment":
                    func = item
                    break

    assert func is not None, "validate_environment method not found in Mxfp4HfQuantizer"

    for ref in ("is_triton_available", "is_kernels_available", "pre_quantized"):
        assert ref in src, f"Missing essential reference: {ref}"

    node_count = len(list(ast.walk(func)))
    assert node_count >= 80, f"Function too small ({node_count} AST nodes), looks stubbed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from agent config files
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .ai/AGENTS.md:2 @ a8732d5546d84bfb4519b6dbf461c947a5de45f6
def test_ruff_lint():
    """Modified file must pass ruff linting (code style enforced by CI)."""
    r = subprocess.run(
        ["ruff", "check", "--select=E,W,F,I", "--ignore=E501", TARGET],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"ruff violations:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates (p2p_enrichment)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_mxfp4_config_unittest():
    """Repo's MXFP4 config tests pass via unittest (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "unittest", "tests.quantization.mxfp4.test_mxfp4.Mxfp4ConfigTest", "-v"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"MXFP4 config unittest failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Modified file passes ruff check with repo's lint rules (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "--select=E,W,F,I", "--ignore=E501", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_imports():
    """Key module imports work without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c",
         "import sys; sys.path.insert(0, '/workspace/transformers/src'); "
         "from transformers.quantizers.quantizer_mxfp4 import Mxfp4HfQuantizer, is_triton_available, is_kernels_available; "
         "print('OK')"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Import test failed:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, f"Import test did not complete successfully: {r.stdout}"
