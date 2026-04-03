"""
Task: transformers-detr-loss-amp-dtype-crash
Repo: huggingface/transformers @ b94fee049373eb2e140d4866847559c4c42b3d7e
PR:   44886

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import sys
from contextlib import contextmanager
from pathlib import Path

import torch

REPO = "/repo"
sys.path.insert(0, f"{REPO}/src")

LW_FILE = f"{REPO}/src/transformers/loss/loss_lw_detr.py"
RT_FILE = f"{REPO}/src/transformers/loss/loss_rt_detr.py"


@contextmanager
def pow_promotes_to_float32():
    """Simulate CUDA autocast: torch.pow returns float32 even on float16 inputs."""
    orig_pow = torch.Tensor.pow
    orig_rpow = torch.Tensor.__pow__

    def _promoted_pow(self, exponent):
        return orig_pow(self.float(), exponent)

    def _promoted_rpow(self, exponent):
        return orig_rpow(self.float(), exponent)

    torch.Tensor.pow = _promoted_pow
    torch.Tensor.__pow__ = _promoted_rpow
    try:
        yield
    finally:
        torch.Tensor.pow = orig_pow
        torch.Tensor.__pow__ = orig_rpow


def _lwdetr_inputs(B, Q, C, n_targets, dtype=torch.float32):
    logits = torch.randn(B, Q, C, dtype=dtype)
    pred_boxes = torch.rand(B, Q, 4, dtype=dtype)
    pred_boxes[..., 2:] = pred_boxes[..., 2:].abs().clamp(min=0.05)
    targets = []
    src_idx, tgt_idx = [], []
    for _ in range(B):
        n = min(n_targets, Q)
        targets.append({
            "class_labels": torch.randint(0, C, (n,)),
            "boxes": torch.rand(n, 4, dtype=dtype).clamp(min=0.05, max=0.95),
        })
        src_idx.append(torch.arange(n))
        tgt_idx.append(torch.arange(n))
    indices = list(zip(src_idx, tgt_idx))
    return logits, pred_boxes, targets, indices


def _make_lwdetr(C, indices):
    from transformers.loss.loss_lw_detr import LwDetrImageLoss

    captured = indices  # avoid late-binding in lambda
    matcher = type("M", (), {"__call__": lambda s, o, t, g: captured})()
    return LwDetrImageLoss(
        matcher=matcher, num_classes=C, focal_alpha=0.25,
        losses=["labels"], group_detr=1,
    )


class FakeRTDetrConfig:
    matcher_class_cost = 2.0
    matcher_bbox_cost = 5.0
    matcher_giou_cost = 2.0
    use_focal_loss = True
    matcher_alpha = 0.25
    matcher_gamma = 2.0
    num_labels = 3
    weight_loss_vfl = 1.0
    weight_loss_bbox = 5.0
    weight_loss_giou = 2.0
    eos_coefficient = 0.1
    focal_loss_alpha = 0.75
    focal_loss_gamma = 2.0


def _rtdetr_inputs(B, Q, C, n_targets, dtype=torch.float32):
    logits = torch.randn(B, Q, C, dtype=dtype)
    pred_boxes = torch.rand(B, Q, 4, dtype=dtype)
    pred_boxes[..., 2:] = pred_boxes[..., 2:].abs().clamp(min=0.05)
    targets = []
    src_idx, tgt_idx = [], []
    for _ in range(B):
        n = min(n_targets, Q)
        targets.append({
            "class_labels": torch.randint(0, C, (n,)),
            "boxes": torch.rand(n, 4, dtype=dtype).clamp(min=0.05, max=0.95),
        })
        src_idx.append(torch.arange(n))
        tgt_idx.append(torch.arange(n))
    indices = list(zip(src_idx, tgt_idx))
    return logits, pred_boxes, targets, indices


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both modified loss files must parse without errors."""
    import py_compile

    for f in [LW_FILE, RT_FILE]:
        py_compile.compile(f, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_lwdetr_loss_labels_float16_pow_promotion():
    """LwDetrImageLoss.loss_labels must not crash when pow promotes to float32."""
    from transformers.loss.loss_lw_detr import LwDetrImageLoss

    for B, Q, C, n_tgt in [(1, 4, 3, 2), (2, 6, 5, 3), (3, 10, 7, 4)]:
        logits, pred_boxes, targets, indices = _lwdetr_inputs(B, Q, C, n_tgt, dtype=torch.float16)
        loss_fn = _make_lwdetr(C, indices)
        loss_fn.eval()

        with pow_promotes_to_float32():
            losses = loss_fn.loss_labels(
                {"logits": logits, "pred_boxes": pred_boxes},
                targets, indices,
                num_boxes=float(sum(len(t["class_labels"]) for t in targets)),
            )

        val = losses["loss_ce"]
        assert not torch.isnan(val), f"loss_ce is NaN (B={B}, Q={Q})"
        assert not torch.isinf(val), f"loss_ce is Inf (B={B}, Q={Q})"
        assert val.item() >= 0, f"loss_ce is negative: {val.item()}"


# [pr_diff] fail_to_pass
def test_rtdetr_loss_labels_vfl_float16_pow_promotion():
    """RTDetrLoss.loss_labels_vfl must not crash when pow promotes to float32."""
    from transformers.loss.loss_rt_detr import RTDetrLoss

    for B, Q, C, n_tgt in [(1, 4, 3, 2), (2, 8, 5, 4), (3, 12, 7, 5)]:
        logits, pred_boxes, targets, indices = _rtdetr_inputs(B, Q, C, n_tgt, dtype=torch.float16)
        config = FakeRTDetrConfig()
        config.num_labels = C
        loss_module = RTDetrLoss(config)

        with pow_promotes_to_float32():
            losses = loss_module.loss_labels_vfl(
                {"logits": logits, "pred_boxes": pred_boxes},
                targets, indices,
                num_boxes=float(sum(len(t["class_labels"]) for t in targets)),
            )

        val = losses["loss_vfl"]
        assert not torch.isnan(val), f"loss_vfl is NaN (B={B}, Q={Q})"
        assert not torch.isinf(val), f"loss_vfl is Inf (B={B}, Q={Q})"
        assert val.item() >= 0, f"loss_vfl is negative: {val.item()}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_lwdetr_loss_labels_float32():
    """LwDetrImageLoss.loss_labels still works with default float32 inputs."""
    from transformers.loss.loss_lw_detr import LwDetrImageLoss

    for B, Q, C, n_tgt in [(1, 4, 3, 2), (2, 6, 5, 3)]:
        logits, pred_boxes, targets, indices = _lwdetr_inputs(B, Q, C, n_tgt)
        loss_fn = _make_lwdetr(C, indices)
        losses = loss_fn.loss_labels(
            {"logits": logits, "pred_boxes": pred_boxes},
            targets, indices,
            num_boxes=float(sum(len(t["class_labels"]) for t in targets)),
        )
        assert "loss_ce" in losses
        assert not torch.isnan(losses["loss_ce"])


# [pr_diff] pass_to_pass
def test_rtdetr_loss_labels_vfl_float32():
    """RTDetrLoss.loss_labels_vfl still works with default float32 inputs."""
    from transformers.loss.loss_rt_detr import RTDetrLoss

    for B, Q, C, n_tgt in [(1, 4, 3, 2), (2, 8, 5, 4)]:
        logits, pred_boxes, targets, indices = _rtdetr_inputs(B, Q, C, n_tgt)
        config = FakeRTDetrConfig()
        config.num_labels = C
        loss_module = RTDetrLoss(config)
        losses = loss_module.loss_labels_vfl(
            {"logits": logits, "pred_boxes": pred_boxes},
            targets, indices,
            num_boxes=float(sum(len(t["class_labels"]) for t in targets)),
        )
        assert "loss_vfl" in losses
        assert not torch.isnan(losses["loss_vfl"])


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .ai/skills/add-or-fix-type-checking/SKILL.md:185-186 @ b94fee049373eb2e140d4866847559c4c42b3d7e
def test_no_bare_type_ignore():
    """type: ignore comments must include specific error codes, not bare."""
    import re

    bare_pattern = re.compile(r"#\s*type:\s*ignore\s*(?!\[)")
    for fpath in [LW_FILE, RT_FILE]:
        src = Path(fpath).read_text()
        for i, line in enumerate(src.splitlines(), 1):
            assert not bare_pattern.search(line), (
                f"{fpath}:{i} has bare '# type: ignore' without error code"
            )
