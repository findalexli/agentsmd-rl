"""Verifier tests for transformers Dots1 MoE routing fix."""
from __future__ import annotations

import subprocess
import sys
import types
from pathlib import Path

import pytest
import torch

REPO = Path("/workspace/transformers")


def _mock_self(
    *,
    n_group: int,
    n_routed_experts: int,
    topk_group: int,
    top_k: int,
    bias_value: float,
    norm_topk_prob: bool = True,
    routed_scaling_factor: float = 1.0,
):
    """Build a minimal stand-in object that satisfies Dots1MoE.route_tokens_to_experts."""
    obj = types.SimpleNamespace()
    obj.gate = types.SimpleNamespace(
        e_score_correction_bias=torch.full((n_routed_experts,), bias_value, dtype=torch.float32)
    )
    obj.n_group = n_group
    obj.n_routed_experts = n_routed_experts
    obj.topk_group = topk_group
    obj.top_k = top_k
    obj.norm_topk_prob = norm_topk_prob
    obj.routed_scaling_factor = routed_scaling_factor
    return obj


def _import_dots1_moe():
    from transformers.models.dots1.modeling_dots1 import Dots1MoE
    return Dots1MoE


def _import_dsv3_moe():
    from transformers.models.deepseek_v3.modeling_deepseek_v3 import DeepseekV3MoE
    return DeepseekV3MoE


@pytest.mark.parametrize("seed", [0, 7, 123])
def test_dots1_moe_picks_only_in_group_experts(seed):
    """When negative bias makes in-group scores < 0, routing must still pick in-group experts.

    Bug: masking out-of-group with 0.0 means the topk over (in-group<0, out-of-group=0)
    selects the out-of-group experts because 0 > negative.
    """
    Dots1MoE = _import_dots1_moe()

    n_group = 4
    n_routed_experts = 16  # 4 experts per group
    topk_group = 2
    top_k = 4
    experts_per_group = n_routed_experts // n_group  # 4

    self_obj = _mock_self(
        n_group=n_group,
        n_routed_experts=n_routed_experts,
        topk_group=topk_group,
        top_k=top_k,
        bias_value=-2.0,  # sigmoid is in [0,1], so router_logits_for_choice in [-2, -1] (all negative)
    )

    torch.manual_seed(seed)
    batch_size = 8
    router_logits = torch.randn(batch_size, n_routed_experts) * 0.05
    # Boost groups 0 and 1 (experts 0..7) so they will be selected as the top-2 groups.
    router_logits[:, : 2 * experts_per_group] += 4.0

    indices, weights = Dots1MoE.route_tokens_to_experts(self_obj, router_logits)

    assert indices.shape == (batch_size, top_k)
    assert weights.shape == (batch_size, top_k)

    in_group_experts = set(range(2 * experts_per_group))
    flat = indices.flatten().tolist()
    out_of_group = [i for i in flat if i not in in_group_experts]
    assert not out_of_group, (
        f"route_tokens_to_experts selected out-of-group experts {sorted(set(out_of_group))} "
        f"despite their group not being in the top-{topk_group} groups. The mask value used to "
        f"zero out non-selected groups is too small in magnitude — when in-group scores go "
        f"negative (because of e_score_correction_bias), the masked sentinel can outrank them "
        f"in topk."
    )


def test_dots1_moe_matches_deepseek_v3_routing():
    """Dots1 routing must produce the same indices/weights as DeepseekV3 for the same inputs.

    Both models share the exact same routing math; the comment 'main diff with deepseekv3' was
    a remnant. Once the masking sentinel is fixed, the two functions are equivalent.
    """
    Dots1MoE = _import_dots1_moe()
    DeepseekV3MoE = _import_dsv3_moe()

    n_group = 8
    n_routed_experts = 64
    topk_group = 4
    top_k = 6

    torch.manual_seed(42)
    bias = -1.5
    self_dots = _mock_self(
        n_group=n_group, n_routed_experts=n_routed_experts,
        topk_group=topk_group, top_k=top_k, bias_value=bias,
    )
    self_dsv3 = _mock_self(
        n_group=n_group, n_routed_experts=n_routed_experts,
        topk_group=topk_group, top_k=top_k, bias_value=bias,
    )

    batch_size = 12
    router_logits = torch.randn(batch_size, n_routed_experts)

    d1_indices, d1_weights = Dots1MoE.route_tokens_to_experts(self_dots, router_logits.clone())
    dsv3_indices, dsv3_weights = DeepseekV3MoE.route_tokens_to_experts(self_dsv3, router_logits.clone())

    # Sort within each row so we don't depend on topk's ordering of equal scores.
    d1_sorted, _ = torch.sort(d1_indices, dim=-1)
    dsv3_sorted, _ = torch.sort(dsv3_indices, dim=-1)
    assert torch.equal(d1_sorted, dsv3_sorted), (
        "Dots1 routing produces different expert selection than DeepseekV3 for the same input. "
        "After the fix they should be equivalent.\n"
        f"Dots1 row 0:  {d1_sorted[0].tolist()}\n"
        f"DSV3  row 0:  {dsv3_sorted[0].tolist()}"
    )
    assert torch.allclose(d1_weights.sort(dim=-1).values, dsv3_weights.sort(dim=-1).values, atol=1e-5)


def test_dots1_module_imports_cleanly():
    """The dots1 modeling module imports without ImportError (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-c", "import transformers.models.dots1.modeling_dots1 as m; print(m.Dots1MoE.__name__)"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Import failed:\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    assert "Dots1MoE" in r.stdout


def test_modular_dots1_in_sync_with_modeling_dots1():
    """Running the modular converter on modular_dots1.py must reproduce modeling_dots1.py.

    This is the repo convention enforced in CI: modeling_*.py is auto-generated from
    modular_*.py and the two must remain consistent.
    """
    r = subprocess.run(
        [
            sys.executable, "utils/check_modular_conversion.py",
            "--files", "src/transformers/models/dots1/modular_dots1.py",
            "--check_all",
        ],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    if r.returncode != 0:
        msg = (
            "Modular consistency check failed. modular_dots1.py and modeling_dots1.py "
            "are out of sync — running `make fix-repo` would change one of them.\n"
            f"--- stdout (tail) ---\n{r.stdout[-2000:]}\n"
            f"--- stderr (tail) ---\n{r.stderr[-2000:]}"
        )
        raise AssertionError(msg)

# === CI-mined tests (ruff lint + format checks sourced from repo CI) ===
def test_ci_ruff_check_on_dots1():
    """pass_to_pass | ruff lint check passes on dots1 modular + modeling files."""
    mod_file = "src/transformers/models/dots1/modular_dots1.py"
    gen_file = "src/transformers/models/dots1/modeling_dots1.py"
    r = subprocess.run(
        ["ruff", "check", mod_file, gen_file],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"ruff check failed on dots1 files (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_ruff_format_check_on_dots1():
    """pass_to_pass | ruff format --check passes on dots1 modular + modeling files."""
    mod_file = "src/transformers/models/dots1/modular_dots1.py"
    gen_file = "src/transformers/models/dots1/modeling_dots1.py"
    r = subprocess.run(
        ["ruff", "format", "--check", mod_file, gen_file],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"ruff format --check failed on dots1 files (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")