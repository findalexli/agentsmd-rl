"""
Task: slime-qwen35-multiturn-loss-mask
Repo: THUDM/slime @ e8e4b64872a469e1c0b85653650a3f76154c88dd
PR:   1742

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import sys
from pathlib import Path

sys.path.insert(0, "/workspace/slime")

REPO = "/workspace/slime"


# ---------------------------------------------------------------------------
# Shared fake tokenizer — char-level with Qwen-style chat template rendering
# ---------------------------------------------------------------------------

class FakeTokenizer:
    """Char-level tokenizer with Qwen-style chat template rendering."""

    def __call__(self, text, add_special_tokens=False, return_offsets_mapping=False):
        result = {"input_ids": [ord(c) for c in text]}
        if return_offsets_mapping:
            result["offset_mapping"] = [(i, i + 1) for i in range(len(text))]
        return result

    def decode(self, ids):
        return "".join(chr(i) for i in ids)

    def get_added_vocab(self):
        return {}

    def apply_chat_template(self, messages, tokenize=True, tools=None,
                            return_dict=False, add_generation_prompt=False,
                            add_special_tokens=False, **kwargs):
        parts = []
        for msg in messages:
            role = msg["role"]
            content = msg.get("content", "")
            parts.append(f"<|im_start|>{role}\n{content}<|im_end|>\n")
        if add_generation_prompt:
            parts.append("<|im_start|>assistant\n")
        text = "".join(parts)
        if tokenize:
            return [ord(c) for c in text]
        return text


def _supervised_text(token_ids, loss_mask):
    """Extract the supervised characters as a string (char-level tokenizer)."""
    return "".join(chr(tid) for tid, m in zip(token_ids, loss_mask) if m == 1)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile
    py_compile.compile(f"{REPO}/slime/utils/mask_utils.py", doraise=True)
    py_compile.compile(f"{REPO}/slime/utils/arguments.py", doraise=True)
    py_compile.compile(f"{REPO}/slime/rollout/sft_rollout.py", doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_qwen35_single_turn():
    """qwen3_5 generator accepts single-turn messages and returns valid masks."""
    from slime.utils.mask_utils import MultiTurnLossMaskGenerator

    tok = FakeTokenizer()
    gen = MultiTurnLossMaskGenerator(tok, "qwen3_5")

    configs = [
        (
            [{"role": "system", "content": "You are helpful."},
             {"role": "user", "content": "Hello"},
             {"role": "assistant", "content": "Hi there!"}],
            "Hi there!",
        ),
        (
            [{"role": "user", "content": "What is 2+2?"},
             {"role": "assistant", "content": "4"}],
            "4",
        ),
        (
            [{"role": "system", "content": "Be concise."},
             {"role": "user", "content": "Name a color"},
             {"role": "assistant", "content": "Blue is a color."}],
            "Blue is a color.",
        ),
    ]
    for messages, expected_supervised in configs:
        token_ids, loss_mask = gen.get_loss_mask(messages)
        assert len(token_ids) == len(loss_mask), f"Length mismatch: {len(token_ids)} vs {len(loss_mask)}"
        assert len(token_ids) > 0, "Empty output"
        assert 1 in loss_mask, "No supervised tokens found"
        assert 0 in loss_mask, "Everything is supervised — system/user should be masked out"
        supervised = _supervised_text(token_ids, loss_mask)
        assert expected_supervised in supervised, (
            f"Assistant content not supervised: {supervised!r}"
        )


# [pr_diff] fail_to_pass
def test_qwen35_multiturn_supervision():
    """qwen3_5 multi-turn: assistant turns are supervised, system/user excluded."""
    from slime.utils.mask_utils import MultiTurnLossMaskGenerator

    tok = FakeTokenizer()
    gen = MultiTurnLossMaskGenerator(tok, "qwen3_5")

    # 2-turn conversation
    messages_2turn = [
        {"role": "system", "content": "SYS"},
        {"role": "user", "content": "Q1"},
        {"role": "assistant", "content": "A1"},
        {"role": "user", "content": "Q2"},
        {"role": "assistant", "content": "<think>\nR2\n</think>\n\nA2"},
    ]
    token_ids, loss_mask = gen.get_loss_mask(messages_2turn)
    assert len(token_ids) == len(loss_mask)
    supervised = _supervised_text(token_ids, loss_mask)
    assert "A1" in supervised, f"A1 not supervised: {supervised}"
    assert "A2" in supervised, f"A2 not supervised: {supervised}"
    assert "R2" in supervised, f"R2 (reasoning) not supervised: {supervised}"
    assert "SYS" not in supervised, f"System content should not be supervised: {supervised}"
    assert "Q1" not in supervised, f"User content should not be supervised: {supervised}"

    # 3-turn conversation
    messages_3turn = [
        {"role": "user", "content": "FIRST_Q"},
        {"role": "assistant", "content": "FIRST_A"},
        {"role": "user", "content": "SECOND_Q"},
        {"role": "assistant", "content": "SECOND_A"},
        {"role": "user", "content": "THIRD_Q"},
        {"role": "assistant", "content": "THIRD_A"},
    ]
    token_ids, loss_mask = gen.get_loss_mask(messages_3turn)
    assert len(token_ids) == len(loss_mask)
    supervised = _supervised_text(token_ids, loss_mask)
    for label in ("FIRST_A", "SECOND_A", "THIRD_A"):
        assert label in supervised, f"{label} not supervised: {supervised}"
    for label in ("FIRST_Q", "SECOND_Q", "THIRD_Q"):
        assert label not in supervised, f"{label} should not be supervised: {supervised}"


# [pr_diff] fail_to_pass
def test_qwen35_think_prefix_excluded():
    """qwen3_5 skips <think>\\n prefix from supervision."""
    from slime.utils.mask_utils import MultiTurnLossMaskGenerator

    tok = FakeTokenizer()
    gen = MultiTurnLossMaskGenerator(tok, "qwen3_5")

    messages = [
        {"role": "user", "content": "Q"},
        {"role": "assistant", "content": "<think>\nREASON\n</think>\n\nANSWER"},
    ]
    token_ids, loss_mask = gen.get_loss_mask(messages)
    rendered = tok.apply_chat_template(messages, tokenize=False)
    header = "<|im_start|>assistant\n"
    header_pos = rendered.find(header)
    content_start = header_pos + len(header)
    think_prefix = "<think>\n"
    # Characters at content_start..content_start+len(think_prefix) are '<think>\n' — should be 0
    think_prefix_mask = loss_mask[content_start:content_start + len(think_prefix)]
    assert all(m == 0 for m in think_prefix_mask), (
        f"<think> prefix should not be supervised: {think_prefix_mask}"
    )
    # Content after <think>\n should be supervised
    assert loss_mask[content_start + len(think_prefix)] == 1, (
        "Content after <think> prefix should be supervised"
    )

    # Also test with a different think block to verify it's not hardcoded
    messages2 = [
        {"role": "user", "content": "Explain X"},
        {"role": "assistant", "content": "<think>\nDEEP_THOUGHT\n</think>\n\nFINAL"},
    ]
    _, lm2 = gen.get_loss_mask(messages2)
    sup2 = _supervised_text(_, lm2)
    assert "DEEP_THOUGHT" in sup2, f"Think body should be supervised: {sup2}"
    assert "FINAL" in sup2, f"Answer should be supervised: {sup2}"


# [pr_diff] fail_to_pass
def test_qwen35_step_loss_mask_suppression():
    """step_loss_mask=0 suppresses supervision for that assistant turn."""
    from slime.utils.mask_utils import MultiTurnLossMaskGenerator

    tok = FakeTokenizer()
    gen = MultiTurnLossMaskGenerator(tok, "qwen3_5")

    # Case 1: first turn suppressed
    messages = [
        {"role": "user", "content": "Q1"},
        {"role": "assistant", "content": "SUPPRESSED_ANSWER", "step_loss_mask": 0},
        {"role": "user", "content": "Q2"},
        {"role": "assistant", "content": "VISIBLE_ANSWER"},
    ]
    token_ids, loss_mask = gen.get_loss_mask(messages)
    assert len(token_ids) == len(loss_mask)
    supervised = _supervised_text(token_ids, loss_mask)
    assert "SUPPRESSED_ANSWER" not in supervised, (
        f"step_loss_mask=0 turn should not be supervised: {supervised}"
    )
    assert "VISIBLE_ANSWER" in supervised, (
        f"Default step_loss_mask=1 turn should be supervised: {supervised}"
    )

    # Case 2: second turn suppressed instead
    messages2 = [
        {"role": "user", "content": "X1"},
        {"role": "assistant", "content": "KEEP_THIS"},
        {"role": "user", "content": "X2"},
        {"role": "assistant", "content": "DROP_THIS", "step_loss_mask": 0},
    ]
    _, lm2 = gen.get_loss_mask(messages2)
    sup2 = _supervised_text(_, lm2)
    assert "KEEP_THIS" in sup2, f"Non-suppressed turn should be supervised: {sup2}"
    assert "DROP_THIS" not in sup2, f"Suppressed turn should not appear: {sup2}"

    # Case 3: all turns suppressed → no supervision
    messages3 = [
        {"role": "user", "content": "Y"},
        {"role": "assistant", "content": "GONE", "step_loss_mask": 0},
    ]
    _, lm3 = gen.get_loss_mask(messages3)
    assert all(m == 0 for m in lm3), "All-suppressed conversation should have no supervision"


# [pr_diff] fail_to_pass
def test_qwen35_conditional_init():
    """qwen3_5 type does not call get_system_message_length() during init."""
    from slime.utils.mask_utils import MultiTurnLossMaskGenerator

    tok = FakeTokenizer()
    gen = MultiTurnLossMaskGenerator(tok, "qwen3_5")
    # On the fix, system_message_length and gen_token_length are 0 for qwen3_5
    # On base, they would be set by get_system_message_length()
    assert gen.system_message_length == 0, (
        f"qwen3_5 should not init system_message_length, got {gen.system_message_length}"
    )
    assert gen.gen_token_length == 0, (
        f"qwen3_5 should not init gen_token_length, got {gen.gen_token_length}"
    )


# [pr_diff] fail_to_pass
# AST-only because: arguments.py imports megatron (not installed in test image)
def test_qwen35_argument_choice():
    """qwen3_5 is a valid argument choice in arguments.py."""
    src = Path(f"{REPO}/slime/utils/arguments.py").read_text()
    lines = src.splitlines(True)
    stripped = [re.sub(r"#.*$", "", l) for l in lines]
    code = "".join(stripped)
    tree = ast.parse(code)
    found = any(
        isinstance(node, ast.Constant) and node.value == "qwen3_5"
        for node in ast.walk(tree)
    )
    assert found, "qwen3_5 not found as string literal in arguments.py"


# [pr_diff] fail_to_pass
# AST-only because: sft_rollout.py imports megatron training pipeline (not installed)
def test_sft_rollout_length_validation():
    """sft_rollout.py validates token_ids/loss_mask length match."""
    src = Path(f"{REPO}/slime/rollout/sft_rollout.py").read_text()
    lines = src.splitlines(True)
    stripped = [re.sub(r"#.*$", "", l) for l in lines]
    code = "".join(stripped)
    tree = ast.parse(code)
    found = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.Compare, ast.If)):
            s = ast.dump(node if isinstance(node, ast.Compare) else node.test)
            if "token_ids" in s and "loss_mask" in s and "len" in s.lower():
                found = True
                break
    assert found, "sft_rollout.py missing length mismatch validation for token_ids vs loss_mask"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_qwen_type_regression():
    """Existing 'qwen' mask type still works after changes."""
    from slime.utils.mask_utils import MultiTurnLossMaskGenerator

    tok = FakeTokenizer()
    gen = MultiTurnLossMaskGenerator(tok, "qwen")
    for messages in [
        [{"role": "system", "content": "SYS"},
         {"role": "user", "content": "Q"},
         {"role": "assistant", "content": "A"}],
        [{"role": "user", "content": "Hello"},
         {"role": "assistant", "content": "World"}],
    ]:
        tids, lm = gen.get_loss_mask(messages)
        assert len(tids) == len(lm), f"Length mismatch: {len(tids)} vs {len(lm)}"
        assert 1 in lm, "No supervised tokens"


# [repo_tests] pass_to_pass
def test_qwen3_type_regression():
    """Existing 'qwen3' mask type still works after changes."""
    from slime.utils.mask_utils import MultiTurnLossMaskGenerator

    tok = FakeTokenizer()
    gen = MultiTurnLossMaskGenerator(tok, "qwen3")
    for messages in [
        [{"role": "system", "content": "SYS"},
         {"role": "user", "content": "Q"},
         {"role": "assistant", "content": "A"}],
        [{"role": "user", "content": "X"},
         {"role": "assistant", "content": "Y"}],
    ]:
        tids, lm = gen.get_loss_mask(messages)
        assert len(tids) == len(lm), f"Length mismatch: {len(tids)} vs {len(lm)}"
        assert 1 in lm, "No supervised tokens"


# [repo_tests] pass_to_pass
def test_get_loss_mask_dispatch_rejects_unknown():
    """get_loss_mask raises ValueError for unrecognized tokenizer_type."""
    from slime.utils.mask_utils import MultiTurnLossMaskGenerator
    import pytest

    tok = FakeTokenizer()
    gen = MultiTurnLossMaskGenerator(tok, "nonexistent_type")
    with pytest.raises((ValueError, KeyError)):
        gen.get_loss_mask([{"role": "user", "content": "Q"},
                          {"role": "assistant", "content": "A"}])


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .claude/skills/
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/add-rollout-function/SKILL.md:79 @ e8e4b64
def test_loss_mask_binary_values():
    """loss_mask values must be 0 or 1 only (consistent semantics)."""
    from slime.utils.mask_utils import MultiTurnLossMaskGenerator

    tok = FakeTokenizer()
    gen = MultiTurnLossMaskGenerator(tok, "qwen3_5")
    configs = [
        [{"role": "user", "content": "U"}, {"role": "assistant", "content": "A"}],
        [
            {"role": "user", "content": "U1"},
            {"role": "assistant", "content": "A1"},
            {"role": "user", "content": "U2"},
            {"role": "assistant", "content": "<think>\nR\n</think>\n\nA2"},
        ],
        [
            {"role": "user", "content": "U"},
            {"role": "assistant", "content": "A", "step_loss_mask": 0},
        ],
    ]
    for i, msgs in enumerate(configs):
        _, lm = gen.get_loss_mask(msgs)
        bad = [v for v in lm if v not in (0, 1)]
        assert not bad, f"Config {i}: non-binary mask values: {set(bad)}"
