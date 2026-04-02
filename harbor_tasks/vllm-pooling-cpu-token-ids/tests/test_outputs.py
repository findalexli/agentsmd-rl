"""
Task: vllm-pooling-cpu-token-ids
Repo: vllm-project/vllm @ 8c0b6267d7fa5c8a07e318809180fc021a0afbf2
PR:   38139

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import inspect
from pathlib import Path

import torch

REPO = "/workspace/vllm"

MODIFIED_FILES = [
    "vllm/v1/pool/metadata.py",
    "vllm/v1/worker/gpu_input_batch.py",
    "vllm/v1/worker/gpu_model_runner.py",
    "vllm/model_executor/layers/pooler/special.py",
    "vllm/model_executor/models/bert.py",
    "vllm/model_executor/models/gritlm.py",
]


def _make_pooling_metadata(**overrides):
    """Construct a PoolingMetadata, adapting to whatever fields the dataclass expects."""
    from vllm.v1.pool.metadata import PoolingMetadata

    sig = inspect.signature(PoolingMetadata)
    defaults = dict(
        prompt_lens=torch.tensor([0]),
        prompt_token_ids=None,
        pooling_params=[],
        pooling_states=[],
    )
    if "prompt_token_ids_cpu" in sig.parameters:
        defaults["prompt_token_ids_cpu"] = None
    defaults.update(overrides)
    return PoolingMetadata(**defaults)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for rel in MODIFIED_FILES:
        src = Path(f"{REPO}/{rel}").read_text()
        ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_get_prompt_token_ids_cpu():
    """get_prompt_token_ids_cpu slices token IDs per-sequence on CPU."""
    # Case 1: multiple sequences with varying lengths
    m = _make_pooling_metadata(
        prompt_lens=torch.tensor([3, 2, 1]),
        prompt_token_ids_cpu=torch.tensor([
            [10, 20, 30, 0],
            [40, 50,  0, 0],
            [99,  0,  0, 0],
        ]),
    )
    result = m.get_prompt_token_ids_cpu()
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert len(result) == 3
    assert result[0].tolist() == [10, 20, 30]
    assert result[1].tolist() == [40, 50]
    assert result[2].tolist() == [99]
    for t in result:
        assert t.device.type == "cpu", f"Expected CPU tensor, got {t.device}"

    # Case 2: single sequence
    m2 = _make_pooling_metadata(
        prompt_lens=torch.tensor([5]),
        prompt_token_ids_cpu=torch.tensor([[1, 2, 3, 4, 5, 0, 0]]),
    )
    result2 = m2.get_prompt_token_ids_cpu()
    assert len(result2) == 1
    assert result2[0].tolist() == [1, 2, 3, 4, 5]

    # Case 3: all same length, no padding
    m3 = _make_pooling_metadata(
        prompt_lens=torch.tensor([2, 2]),
        prompt_token_ids_cpu=torch.tensor([[100, 200], [300, 400]]),
    )
    result3 = m3.get_prompt_token_ids_cpu()
    assert result3[0].tolist() == [100, 200]
    assert result3[1].tolist() == [300, 400]


# [pr_diff] fail_to_pass
def test_get_prompt_token_ids_cpu_full_length():
    """CPU method works when sequences fill the entire tensor width."""
    # Single sequence filling full width
    m = _make_pooling_metadata(
        prompt_lens=torch.tensor([4]),
        prompt_token_ids_cpu=torch.tensor([[7, 8, 9, 11]]),
    )
    result = m.get_prompt_token_ids_cpu()
    assert result[0].tolist() == [7, 8, 9, 11]

    # Multiple sequences all filling full width
    m2 = _make_pooling_metadata(
        prompt_lens=torch.tensor([3, 3]),
        prompt_token_ids_cpu=torch.tensor([[10, 20, 30], [40, 50, 60]]),
    )
    result2 = m2.get_prompt_token_ids_cpu()
    assert result2[0].tolist() == [10, 20, 30]
    assert result2[1].tolist() == [40, 50, 60]


# [pr_diff] fail_to_pass
def test_pooling_metadata_has_cpu_field():
    """PoolingMetadata accepts prompt_token_ids_cpu and stores it."""
    cpu_tensor = torch.tensor([[1, 2], [3, 4]])
    m = _make_pooling_metadata(
        prompt_lens=torch.tensor([2, 2]),
        prompt_token_ids_cpu=cpu_tensor,
    )
    assert hasattr(m, "prompt_token_ids_cpu"), "Missing prompt_token_ids_cpu field"
    assert m.prompt_token_ids_cpu is not None
    assert torch.equal(m.prompt_token_ids_cpu, cpu_tensor)

    # Larger tensor
    big = torch.arange(15).reshape(3, 5)
    m2 = _make_pooling_metadata(
        prompt_lens=torch.tensor([3, 5, 2]),
        prompt_token_ids_cpu=big,
    )
    assert torch.equal(m2.prompt_token_ids_cpu, big)


# [pr_diff] fail_to_pass
def test_getitem_preserves_cpu_field():
    """__getitem__ slicing on PoolingMetadata preserves prompt_token_ids_cpu."""
    from vllm.pooling_params import PoolingParams

    m = _make_pooling_metadata(
        prompt_lens=torch.tensor([2, 3, 1]),
        prompt_token_ids=torch.tensor([[10, 20, 0], [30, 40, 50], [60, 0, 0]]),
        prompt_token_ids_cpu=torch.tensor([[10, 20, 0], [30, 40, 50], [60, 0, 0]]),
        pooling_params=[PoolingParams(), PoolingParams(), PoolingParams()],
        pooling_states=[{}, {}, {}],
    )

    # Slice last two
    sliced = m[1:]
    assert sliced.prompt_token_ids_cpu is not None
    assert sliced.prompt_token_ids_cpu.tolist() == [[30, 40, 50], [60, 0, 0]]

    # Slice first one
    sliced0 = m[:1]
    assert sliced0.prompt_token_ids_cpu is not None
    assert sliced0.prompt_token_ids_cpu.tolist() == [[10, 20, 0]]

    # Slice middle
    sliced1 = m[1:2]
    assert sliced1.prompt_token_ids_cpu is not None
    assert sliced1.prompt_token_ids_cpu.tolist() == [[30, 40, 50]]


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_get_prompt_token_ids_device_preserved():
    """Original device-side get_prompt_token_ids() still works correctly."""
    m = _make_pooling_metadata(
        prompt_lens=torch.tensor([2, 1]),
        prompt_token_ids=torch.tensor([[100, 200, 0], [300, 0, 0]]),
    )
    result = m.get_prompt_token_ids()
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].tolist() == [100, 200]
    assert result[1].tolist() == [300]

    # Verify with different shape
    m2 = _make_pooling_metadata(
        prompt_lens=torch.tensor([4]),
        prompt_token_ids=torch.tensor([[10, 20, 30, 40]]),
    )
    result2 = m2.get_prompt_token_ids()
    assert result2[0].tolist() == [10, 20, 30, 40]


# ---------------------------------------------------------------------------
# Structural (pr_diff) — consumer files use CPU accessor
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: consumer models import heavy GPU deps (torch.cuda, triton,
# custom CUDA kernels) that are unavailable in the CPU-only test environment
def test_consumers_call_cpu_accessor():
    """Consumer models (special.py, bert.py, gritlm.py) call get_prompt_token_ids_cpu()."""
    consumer_files = [
        "vllm/model_executor/layers/pooler/special.py",
        "vllm/model_executor/models/bert.py",
        "vllm/model_executor/models/gritlm.py",
    ]
    missing = []
    for rel in consumer_files:
        src = Path(f"{REPO}/{rel}").read_text()
        tree = ast.parse(src)
        found = any(
            isinstance(node, ast.Attribute) and node.attr == "get_prompt_token_ids_cpu"
            for node in ast.walk(tree)
        )
        if not found:
            missing.append(rel)

    assert not missing, (
        f"These files do not call .get_prompt_token_ids_cpu(): {missing}"
    )
