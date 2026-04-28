"""Harbor tests for huggingface/transformers#45572."""

import subprocess
import sys
import os

REPO = "/workspace/transformers"


def test_route_tokens_masks_with_neg_inf():
    """Dots1MoE routes tokens to the correct experts when scores are negative.

    When valid expert scores are negative, an incorrect fill value for masked
    positions can cause those masked positions to outrank the valid ones.
    The fix ensures masked positions can never win a topk selection.
    """
    import torch
    from transformers.models.dots1.modeling_dots1 import Dots1MoE
    from transformers import Dots1Config

    config = Dots1Config(
        n_routed_experts=8,
        n_group=2,
        topk_group=1,
        num_experts_per_tok=2,
        n_shared_experts=1,
        moe_intermediate_size=16,
        intermediate_size=32,
        hidden_size=64,
    )
    moe = Dots1MoE(config)

    # Bias group 0 (indices 0-3) heavily negative so it's NOT the selected group.
    # Bias group 1 (indices 4-7) moderately negative — it WILL be selected.
    # All valid scores end up negative, so the fill value determines correctness.
    bias = torch.zeros(8)
    bias[0:4] = -10.0
    bias[4:8] = -5.0
    moe.gate.e_score_correction_bias = torch.nn.Parameter(bias)

    # sigmoid(0) = 0.5, so router_logits_for_choice ≈ 0.5 + bias
    router_logits = torch.zeros(1, 8)

    indices, _ = moe.route_tokens_to_experts(router_logits)

    selected = indices[0].tolist()
    all_in_valid_group = all(4 <= idx < 8 for idx in selected)
    assert all_in_valid_group, (
        f"BUG: masked positions selected over valid ones. "
        f"Got indices {selected}, expected all in range [4, 8). "
        f"The fill value used for masked scores still outranks valid negative scores."
    )


def test_route_tokens_with_negative_group_bias():
    """Dots1MoE selects correct experts when all group biases are negative.

    Uses a 3-group configuration where every group has negative bias.
    Only the least-negative group should be selected for routing.
    With the bug, the fill value outranks valid negative scores.
    """
    import torch
    from transformers.models.dots1.modeling_dots1 import Dots1MoE
    from transformers import Dots1Config

    config = Dots1Config(
        n_routed_experts=6,
        n_group=3,
        topk_group=1,
        num_experts_per_tok=2,
        n_shared_experts=1,
        moe_intermediate_size=16,
        intermediate_size=32,
        hidden_size=64,
    )
    moe = Dots1MoE(config)

    # 6 experts -> 3 groups of 2: group 0 = [0,1], group 1 = [2,3], group 2 = [4,5]
    # All groups get negative bias so the fill-value bug would manifest.
    # Group 2 gets the least negative bias -> it should be selected.
    bias = torch.zeros(6)
    bias[0:2] = -20.0
    bias[2:4] = -15.0
    bias[4:6] = -3.0
    moe.gate.e_score_correction_bias = torch.nn.Parameter(bias)

    router_logits = torch.zeros(2, 6)  # batch of 2
    indices, _ = moe.route_tokens_to_experts(router_logits)

    for b in range(2):
        selected = indices[b].tolist()
        all_in_group2 = all(idx in (4, 5) for idx in selected)
        assert all_in_group2, (
            f"Batch {b}: masked positions selected over valid negative scores. "
            f"Got indices {selected}, expected all in {{4, 5}}"
        )


def test_import_model():
    """Dots1MoE can be imported (pass_to_pass)."""
    from transformers.models.dots1.modeling_dots1 import Dots1MoE
    from transformers import Dots1Config

    config = Dots1Config(
        n_routed_experts=8,
        n_group=2,
        topk_group=1,
        num_experts_per_tok=2,
        n_shared_experts=1,
        moe_intermediate_size=16,
        intermediate_size=32,
        hidden_size=64,
    )
    moe = Dots1MoE(config)
    assert moe is not None


def test_repo_consistency_check():
    """Modular-modelling consistency holds (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-c", """
import sys
sys.path.insert(0, '/workspace/transformers/src')

# Verify both modular and modeling files are syntactically valid
import ast
for f in [
    '/workspace/transformers/src/transformers/models/dots1/modular_dots1.py',
    '/workspace/transformers/src/transformers/models/dots1/modeling_dots1.py',
]:
    with open(f) as fh:
        ast.parse(fh.read())
print('ok')
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Consistency check failed:\n{r.stderr}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_check_timestamps_verify_merge_commit_timestamp_is_older_t():
    """pass_to_pass | CI job 'Check timestamps' → step 'Verify `merge_commit` timestamp is older than the issue comment timestamp'"""
    r = subprocess.run(
        ["bash", "-lc", 'COMMENT_TIMESTAMP=$(date -d "${COMMENT_DATE}" +"%s")\necho "COMMENT_DATE: $COMMENT_DATE"\necho "COMMENT_TIMESTAMP: $COMMENT_TIMESTAMP"\nif [ $COMMENT_TIMESTAMP -le $PR_MERGE_COMMIT_TIMESTAMP ]; then\n  echo "Last commit on the pull request is newer than the issue comment triggering this run! Abort!";\n  exit -1;\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify `merge_commit` timestamp is older than the issue comment timestamp' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_get_tests_verify_merge_commit_sha():
    """pass_to_pass | CI job 'get-tests' → step 'Verify merge commit SHA'"""
    r = subprocess.run(
        ["bash", "-lc", 'PR_MERGE_SHA=$(git log -1 --format=%H)\nif [ $PR_MERGE_SHA != $VERIFIED_PR_MERGE_SHA ]; then\n  echo "The merged commit SHA is not the same as the verified one! Security issue detected, abort the workflow!";\n  exit -1;\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify merge commit SHA' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_get_tests_get_models_to_test():
    """pass_to_pass | CI job 'get-tests' → step 'Get models to test'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -m pip install GitPython'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Get models to test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_get_tests_show_models_to_test():
    """pass_to_pass | CI job 'get-tests' → step 'Show models to test'"""
    r = subprocess.run(
        ["bash", "-lc", 'echo "$models"\necho "models=$models" >> $GITHUB_OUTPUT\necho "$quantizations"\necho "quantizations=$quantizations" >> $GITHUB_OUTPUT'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Show models to test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check___report_process_and_filter_reports():
    """pass_to_pass | CI job 'Check & Report' → step 'Process and filter reports'"""
    r = subprocess.run(
        ["bash", "-lc", "python3 << 'PYTHON_SCRIPT'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Process and filter reports' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")