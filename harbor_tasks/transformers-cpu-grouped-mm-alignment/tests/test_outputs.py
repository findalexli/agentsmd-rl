"""
Task: transformers-cpu-grouped-mm-alignment
Repo: huggingface/transformers @ b3d7942fbaedda791668d7fe42eaaa323ed7a089
PR:   #44970

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
import unittest.mock
from pathlib import Path

import torch

REPO = "/repo"


def _ensure_grouped_mm():
    """Return context-manager patches that make grouped_mm appear available."""
    patches = []
    if not hasattr(torch.nn.functional, "grouped_mm"):
        patches.append(
            unittest.mock.patch.object(
                torch.nn.functional, "grouped_mm", create=True, new=lambda *a, **kw: None
            )
        )
    if not hasattr(torch, "_grouped_mm"):
        patches.append(
            unittest.mock.patch.object(
                torch, "_grouped_mm", create=True, new=lambda *a, **kw: None
            )
        )
    return patches


def _mock_old_torch():
    """Mock is_torch_less_or_equal to return True, simulating torch <= 2.10.

    The fix only adds the alignment check for torch <= 2.10. If a newer torch
    is installed in the test image, the check is skipped (PyTorch fixed it
    upstream). We mock the version gate so the alignment logic is always exercised.
    """
    return unittest.mock.patch(
        "transformers.integrations.moe.is_torch_less_or_equal",
        return_value=True,
        create=True,
    )


def _make_misaligned(shape, dtype=torch.bfloat16):
    """Create a tensor whose data_ptr is NOT 16-byte aligned."""
    numel = 1
    for s in shape:
        numel *= s
    buf = torch.zeros(numel + 10, dtype=dtype)
    t = buf[1 : 1 + numel].reshape(shape)
    assert t.data_ptr() % 16 != 0, "Failed to create misaligned tensor"
    return t


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile

    for f in [
        "src/transformers/integrations/moe.py",
        "src/transformers/conversion_mapping.py",
        "src/transformers/core_model_loading.py",
    ]:
        py_compile.compile(f"{REPO}/{f}", doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_misaligned_weight_returns_false():
    """_can_use_grouped_mm returns False when weight tensor is misaligned."""
    patches = _ensure_grouped_mm()
    for p in patches:
        p.start()
    try:
        with _mock_old_torch():
            from transformers.integrations.moe import _can_use_grouped_mm

            test_cases = [
                ((2, 8), (16, 8)),
                ((4, 16), (32, 16)),
                ((1, 4), (8, 4)),
            ]
            for inp_shape, w_shape in test_cases:
                aligned_i = torch.randn(*inp_shape, dtype=torch.bfloat16)
                misaligned_w = _make_misaligned(w_shape)
                offs = torch.tensor([inp_shape[0]], dtype=torch.int32)

                assert aligned_i.data_ptr() % 16 == 0
                result = _can_use_grouped_mm(aligned_i, misaligned_w, offs)
                assert result is False, (
                    f"Misaligned weight {w_shape} should return False, got {result}"
                )
    finally:
        for p in patches:
            p.stop()


# [pr_diff] fail_to_pass
def test_misaligned_input_returns_false():
    """_can_use_grouped_mm returns False when input tensor is misaligned."""
    patches = _ensure_grouped_mm()
    for p in patches:
        p.start()
    try:
        with _mock_old_torch():
            from transformers.integrations.moe import _can_use_grouped_mm

            test_cases = [
                ((2, 8), (16, 8)),
                ((4, 16), (32, 16)),
                ((1, 4), (8, 4)),
            ]
            for inp_shape, w_shape in test_cases:
                misaligned_i = _make_misaligned(inp_shape)
                aligned_w = torch.randn(*w_shape, dtype=torch.bfloat16)
                offs = torch.tensor([inp_shape[0]], dtype=torch.int32)

                assert aligned_w.data_ptr() % 16 == 0
                result = _can_use_grouped_mm(misaligned_i, aligned_w, offs)
                assert result is False, (
                    f"Misaligned input {inp_shape} should return False, got {result}"
                )
    finally:
        for p in patches:
            p.stop()


# [pr_diff] fail_to_pass
def test_force16bytes_removed_from_mappings():
    """Force16BytesAlignment no longer used in conversion_mapping."""
    from transformers.conversion_mapping import _build_checkpoint_conversion_mapping
    from transformers.core_model_loading import WeightConverter

    mappings = _build_checkpoint_conversion_mapping()
    found = []
    for model_name, converters in mappings.items():
        if isinstance(converters, list):
            for conv in converters:
                if isinstance(conv, WeightConverter) and conv.operations:
                    for op in conv.operations:
                        if type(op).__name__ == "Force16BytesAlignment":
                            found.append(model_name)
    assert len(found) == 0, f"Force16BytesAlignment still used in: {found}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_aligned_tensors_return_true():
    """_can_use_grouped_mm returns True for properly aligned tensors of various sizes."""
    patches = _ensure_grouped_mm()
    for p in patches:
        p.start()
    try:
        with _mock_old_torch():
            from transformers.integrations.moe import _can_use_grouped_mm

            shapes = [(1, 8, 8, 8), (4, 16, 32, 16), (8, 32, 64, 32)]
            for bi, ki, ko, ki2 in shapes:
                inp = torch.randn(bi, ki, dtype=torch.bfloat16)
                w = torch.randn(ko, ki2, dtype=torch.bfloat16)
                offs = torch.tensor([bi], dtype=torch.int32)
                assert inp.data_ptr() % 16 == 0
                assert w.data_ptr() % 16 == 0
                r = _can_use_grouped_mm(inp, w, offs)
                assert r is True, f"Aligned {inp.shape},{w.shape} should return True, got {r}"
    finally:
        for p in patches:
            p.stop()


# [pr_diff] pass_to_pass
def test_no_grouped_mm_returns_false():
    """Returns False when grouped_mm API is entirely unavailable."""
    import importlib

    saved = {}
    if hasattr(torch.nn.functional, "grouped_mm"):
        saved["nnf"] = torch.nn.functional.grouped_mm
        delattr(torch.nn.functional, "grouped_mm")
    if hasattr(torch, "_grouped_mm"):
        saved["torch"] = torch._grouped_mm
        delattr(torch, "_grouped_mm")

    try:
        import transformers.integrations.moe as moe_mod

        importlib.reload(moe_mod)
    except Exception:
        pass

    try:
        from transformers.integrations.moe import _can_use_grouped_mm

        inp = torch.randn(2, 8, dtype=torch.bfloat16)
        w = torch.randn(16, 8, dtype=torch.bfloat16)
        offs = torch.tensor([2], dtype=torch.int32)
        result = _can_use_grouped_mm(inp, w, offs)
        assert result is False, f"Without grouped_mm, should return False, got {result}"
    finally:
        if "nnf" in saved:
            torch.nn.functional.grouped_mm = saved["nnf"]
        if "torch" in saved:
            torch._grouped_mm = saved["torch"]


# [pr_diff] pass_to_pass
def test_conversion_mapping_builds():
    """Weight conversion mapping loads cleanly with known MoE models."""
    from transformers.conversion_mapping import _build_checkpoint_conversion_mapping

    mappings = _build_checkpoint_conversion_mapping()
    assert len(mappings) > 0, "Empty mappings"
    for model in ["mixtral", "qwen3_moe"]:
        assert model in mappings, f"{model} missing from mappings"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — CLAUDE.md:2 @ b3d7942
def test_ruff_check():
    """Changed files pass ruff linter (CLAUDE.md line 2: 'make style: runs formatters and linters')."""
    r = subprocess.run(
        [
            sys.executable, "-m", "ruff", "check",
            "src/transformers/integrations/moe.py",
            "src/transformers/conversion_mapping.py",
            "src/transformers/core_model_loading.py",
            "--quiet",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
