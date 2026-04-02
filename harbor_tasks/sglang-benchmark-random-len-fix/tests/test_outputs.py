"""
Task: sglang-benchmark-random-len-fix
Repo: sgl-project/sglang @ a93065679b6395c07fd03249e2e99ccca293ac15
PR:   21492

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import sys
from pathlib import Path

import numpy as np

REPO = "/workspace/sglang"
TARGET = f"{REPO}/python/sglang/benchmark/datasets/random.py"

sys.path.insert(0, f"{REPO}/python")


class _MockTokenizer:
    """Configurable mock tokenizer for testing sample_random_requests."""

    def __init__(self, num_special=1, vocab_size=1000):
        self.vocab_size = vocab_size
        self._num_special = num_special

    def num_special_tokens_to_add(self, pair=False):
        return self._num_special

    def decode(self, ids):
        return "x" * len(ids) if ids else ""

    def encode(self, text):
        return list(range(len(text)))

    def get_vocab(self):
        return {str(i): i for i in range(self.vocab_size)}


def _call_sample(input_len, output_len, num_prompts, range_ratio, num_special=1, seed=42):
    from sglang.benchmark.datasets.random import sample_random_requests

    tok = _MockTokenizer(num_special=num_special)
    np.random.seed(seed)
    return sample_random_requests(
        input_len=input_len,
        output_len=output_len,
        num_prompts=num_prompts,
        range_ratio=range_ratio,
        tokenizer=tok,
        dataset_path="",
        random_sample=False,
        return_text=True,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse without errors."""
    import ast

    source = Path(TARGET).read_text()
    ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_small_input_len_produces_nonempty_prompts():
    """input_len equal to num_special_tokens must still produce non-empty prompts.

    Bug: max(0, 1-1)=0 -> empty prompt -> server rejects.
    Fix: max(1, 1-1)=1 -> 1-token prompt -> works.
    """
    results = _call_sample(input_len=1, output_len=10, num_prompts=20, range_ratio=0.0,
                           num_special=1, seed=42)
    for r in results:
        assert r.prompt, "Got empty prompt string"
        assert r.prompt_len >= 1, f"prompt_len={r.prompt_len}, expected >= 1"


# [pr_diff] fail_to_pass
def test_input_len_less_than_special_tokens():
    """input_len < num_special_tokens must clamp adjusted length to >= 1.

    With 3 special tokens and input_len=2: max(0, 2-3)=max(0,-1)=0 (bug).
    Fix: max(1, 2-3)=1.
    """
    results = _call_sample(input_len=2, output_len=5, num_prompts=15, range_ratio=0.0,
                           num_special=3, seed=77)
    for r in results:
        assert r.prompt, "Got empty prompt string"
        assert r.prompt_len >= 1, f"prompt_len={r.prompt_len}, expected >= 1"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_normal_subtraction_correct():
    """Normal input_len >> special_tokens subtracts correctly (regression).

    Uses range_ratio=1.0 so compute_random_lens always returns exactly full_len
    (randint(N, N+1, size=k) == [N]*k), making prompt_len predictable.

    input_len=100, special=1, range_ratio=1.0 -> prompt_len=99
    input_len=200, special=3, range_ratio=1.0 -> prompt_len=197
    input_len=50, special=1, range_ratio=1.0 -> prompt_len=49
    """
    # 1 special token cases
    for input_len, expected in [(100, 99), (50, 49)]:
        results = _call_sample(input_len=input_len, output_len=20, num_prompts=10,
                               range_ratio=1.0, num_special=1, seed=42)
        for r in results:
            assert r.prompt_len == expected, (
                f"input_len={input_len}, special=1: expected prompt_len={expected}, got {r.prompt_len}"
            )

    # 3 special tokens
    results = _call_sample(input_len=200, output_len=50, num_prompts=10,
                           range_ratio=1.0, num_special=3, seed=77)
    for r in results:
        assert r.prompt_len == 197, f"expected prompt_len=197, got {r.prompt_len}"


# [pr_diff] pass_to_pass
def test_range_ratio_produces_valid_lengths():
    """range_ratio > 0 still produces valid, varied lengths."""
    results = _call_sample(input_len=100, output_len=50, num_prompts=50,
                           range_ratio=0.5, num_special=1, seed=55)
    for r in results:
        assert r.prompt_len >= 1, f"prompt_len={r.prompt_len} < 1"
        assert 49 <= r.prompt_len <= 99, f"prompt_len={r.prompt_len} outside [49,99]"

    unique_lens = set(r.prompt_len for r in results)
    assert len(unique_lens) >= 5, (
        f"Expected varied lengths with range_ratio=0.5, got only {len(unique_lens)} unique"
    )


# [static] pass_to_pass
def test_not_stub():
    """sample_random_requests has real logic, not a stub."""
    import ast

    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "sample_random_requests":
            func = node
            break

    assert func is not None, "sample_random_requests function not found"

    stmts = sum(
        1
        for s in ast.walk(func)
        if isinstance(s, (ast.Assign, ast.AugAssign, ast.For, ast.If, ast.Return, ast.With))
    )
    assert stmts >= 10, f"Function has only {stmts} non-trivial statements, expected >= 10"
