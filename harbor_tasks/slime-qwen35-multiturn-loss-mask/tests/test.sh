#!/usr/bin/env bash
set -euo pipefail

REPO=/workspace/slime
LOG_DIR=/logs/verifier
mkdir -p "$LOG_DIR"
SCORE=0

# === Shared fake tokenizer for behavioral tests ===
# A char-level tokenizer that renders Qwen-style <|im_start|>/<|im_end|> templates.
# This lets us call the actual MultiTurnLossMaskGenerator code without heavy deps.
FAKE_TOK=$(cat <<'PYTOK'
import sys, os
sys.path.insert(0, "/workspace/slime")

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

from slime.utils.mask_utils import MultiTurnLossMaskGenerator
PYTOK
)

# === GATE (0): Syntax check — abort on failure ===
echo "=== GATE: Syntax check ==="
if ! python3 -c "
import py_compile
py_compile.compile('$REPO/slime/utils/mask_utils.py', doraise=True)
py_compile.compile('$REPO/slime/utils/arguments.py', doraise=True)
py_compile.compile('$REPO/slime/rollout/sft_rollout.py', doraise=True)
print('PASS: syntax OK')
"; then
    echo "FAIL: syntax error — aborting"
    echo "0.00" > "$LOG_DIR/reward.txt"
    exit 0
fi

# [pr_diff] (0.15): qwen3_5 generator accepts single-turn messages and returns valid masks
echo ""
echo "=== Test 1: qwen3_5 single-turn loss mask ==="
T1=$(python3 -c "
$FAKE_TOK
tok = FakeTokenizer()
gen = MultiTurnLossMaskGenerator(tok, 'qwen3_5')
messages = [
    {'role': 'system', 'content': 'You are helpful.'},
    {'role': 'user', 'content': 'Hello'},
    {'role': 'assistant', 'content': 'Hi there!'},
]
token_ids, loss_mask = gen.get_loss_mask(messages)
# Basic validity
assert len(token_ids) == len(loss_mask), f'Length mismatch: {len(token_ids)} vs {len(loss_mask)}'
assert len(token_ids) > 0, 'Empty output'
# Assistant content should be supervised (some 1s in mask)
assert 1 in loss_mask, 'No supervised tokens found'
# System/user content should NOT all be supervised
assert 0 in loss_mask, 'Everything is supervised — system/user should be masked out'
print('PASS')
" 2>&1 | tail -1)
echo "$T1"
if [ "$T1" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.15)"); fi

# [pr_diff] (0.20): qwen3_5 generator handles multi-turn correctly
echo ""
echo "=== Test 2: qwen3_5 multi-turn loss mask ==="
T2=$(python3 -c "
$FAKE_TOK
tok = FakeTokenizer()
gen = MultiTurnLossMaskGenerator(tok, 'qwen3_5')
messages = [
    {'role': 'system', 'content': 'SYS'},
    {'role': 'user', 'content': 'Q1'},
    {'role': 'assistant', 'content': 'A1'},
    {'role': 'user', 'content': 'Q2'},
    {'role': 'assistant', 'content': '<think>\nR2\n</think>\n\nA2'},
]
token_ids, loss_mask = gen.get_loss_mask(messages)
assert len(token_ids) == len(loss_mask), f'Length mismatch: {len(token_ids)} vs {len(loss_mask)}'
# Decode supervised tokens to verify correctness
supervised = gen.get_text_from_loss_mask(token_ids, loss_mask)
# First assistant turn: 'A1' should be supervised (content + end marker)
assert any('A1' in s for s in supervised), f'A1 not supervised: {supervised}'
# Second assistant turn: reasoning 'R2' and answer 'A2' should be supervised
assert any('A2' in s for s in supervised), f'A2 not supervised: {supervised}'
assert any('R2' in s for s in supervised), f'R2 not supervised: {supervised}'
print('PASS')
" 2>&1 | tail -1)
echo "$T2"
if [ "$T2" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

# [pr_diff] (0.15): qwen3_5 skips <think>\n prefix from supervision
echo ""
echo "=== Test 3: qwen3_5 think prefix handling ==="
T3=$(python3 -c "
$FAKE_TOK
tok = FakeTokenizer()
gen = MultiTurnLossMaskGenerator(tok, 'qwen3_5')
messages = [
    {'role': 'user', 'content': 'Q'},
    {'role': 'assistant', 'content': '<think>\nREASON\n</think>\n\nANSWER'},
]
token_ids, loss_mask = gen.get_loss_mask(messages)
rendered = tok.apply_chat_template(messages, tokenize=False)
# The <think>\n prefix (8 chars) after assistant header should NOT be supervised
header = '<|im_start|>assistant\n'
header_pos = rendered.find(header)
content_start = header_pos + len(header)
# Characters at content_start..content_start+8 are '<think>\n' — should be 0 in mask
think_prefix_mask = loss_mask[content_start:content_start + len('<think>\n')]
assert all(m == 0 for m in think_prefix_mask), f'<think> prefix should not be supervised: {think_prefix_mask}'
# But content after <think>\n should be supervised
after_think = loss_mask[content_start + len('<think>\n')]
assert after_think == 1, f'Content after <think> prefix should be supervised, got {after_think}'
print('PASS')
" 2>&1 | tail -1)
echo "$T3"
if [ "$T3" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.15)"); fi

# [pr_diff] (0.15): token_ids and loss_mask always same length across message configs
echo ""
echo "=== Test 4: Length consistency across configurations ==="
T4=$(python3 -c "
$FAKE_TOK
tok = FakeTokenizer()
gen = MultiTurnLossMaskGenerator(tok, 'qwen3_5')

configs = [
    # single system+user+assistant
    [{'role': 'system', 'content': 'S'}, {'role': 'user', 'content': 'U'}, {'role': 'assistant', 'content': 'A'}],
    # multi-turn
    [{'role': 'user', 'content': 'U1'}, {'role': 'assistant', 'content': 'A1'},
     {'role': 'user', 'content': 'U2'}, {'role': 'assistant', 'content': 'A2'}],
    # with think block
    [{'role': 'user', 'content': 'U'}, {'role': 'assistant', 'content': '<think>\nR\n</think>\n\nA'}],
    # with step_loss_mask=0
    [{'role': 'user', 'content': 'U'}, {'role': 'assistant', 'content': 'A', 'step_loss_mask': 0}],
]

for i, msgs in enumerate(configs):
    tids, lm = gen.get_loss_mask(msgs)
    assert len(tids) == len(lm), f'Config {i}: length mismatch {len(tids)} vs {len(lm)}'
    # All mask values must be 0 or 1
    assert all(v in (0, 1) for v in lm), f'Config {i}: mask values not in {{0,1}}'
print('PASS')
" 2>&1 | tail -1)
echo "$T4"
if [ "$T4" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.15)"); fi

# [pr_diff] (0.05): P2P — qwen mask type still works
echo ""
echo "=== Test 5: P2P — qwen mask type still works ==="
T5=$(python3 -c "
$FAKE_TOK
tok = FakeTokenizer()
gen = MultiTurnLossMaskGenerator(tok, 'qwen')
messages = [
    {'role': 'system', 'content': 'SYS'},
    {'role': 'user', 'content': 'Q'},
    {'role': 'assistant', 'content': 'A'},
]
tids, lm = gen.get_loss_mask(messages)
assert len(tids) == len(lm), f'Length mismatch: {len(tids)} vs {len(lm)}'
assert 1 in lm, 'No supervised tokens'
print('PASS')
" 2>&1 | tail -1)
echo "$T5"
if [ "$T5" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi

# [pr_diff] (0.05): P2P — qwen3 mask type still works
echo ""
echo "=== Test 6: P2P — qwen3 mask type still works ==="
T6=$(python3 -c "
$FAKE_TOK
tok = FakeTokenizer()
gen = MultiTurnLossMaskGenerator(tok, 'qwen3')
messages = [
    {'role': 'system', 'content': 'SYS'},
    {'role': 'user', 'content': 'Q'},
    {'role': 'assistant', 'content': 'A'},
]
tids, lm = gen.get_loss_mask(messages)
assert len(tids) == len(lm), f'Length mismatch: {len(tids)} vs {len(lm)}'
assert 1 in lm, 'No supervised tokens'
print('PASS')
" 2>&1 | tail -1)
echo "$T6"
if [ "$T6" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi

# [pr_diff] (0.10): sft_rollout validates token_ids/loss_mask length
# WHY structural: generate_rollout() requires torch, ray, sglang — cannot call without GPU stack
echo ""
echo "=== Test 7: sft_rollout length validation ==="
if grep -q 'len(token_ids).*!=.*len(loss_mask)\|len(loss_mask).*!=.*len(token_ids)' "$REPO/slime/rollout/sft_rollout.py"; then
    echo "PASS"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL: sft_rollout.py missing length mismatch validation"
fi

# [pr_diff] (0.05): qwen3_5 is a valid argument choice
# WHY structural: arguments.py imports megatron internals — cannot parse without full stack
echo ""
echo "=== Test 8: qwen3_5 in argument choices ==="
if grep -q "qwen3_5" "$REPO/slime/utils/arguments.py"; then
    echo "PASS"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL: qwen3_5 not found in arguments.py choices"
fi

# [agent_config] (0.05): loss_mask values are 0 or 1 only — .claude/skills/add-rollout-function/SKILL.md:79
echo ""
echo "=== Test 9: loss_mask values consistent (0/1 only) ==="
T9=$(python3 -c "
$FAKE_TOK
tok = FakeTokenizer()
gen = MultiTurnLossMaskGenerator(tok, 'qwen3_5')
messages = [
    {'role': 'user', 'content': 'Q1'}, {'role': 'assistant', 'content': 'A1'},
    {'role': 'user', 'content': 'Q2'}, {'role': 'assistant', 'content': '<think>\nR\n</think>\n\nA2'},
]
_, lm = gen.get_loss_mask(messages)
bad = [v for v in lm if v not in (0, 1)]
assert not bad, f'Non-binary mask values: {set(bad)}'
print('PASS')
" 2>&1 | tail -1)
echo "$T9"
if [ "$T9" = "PASS" ]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi

# [agent_config] (0.05): explicit ValueError for validation failures — .claude/skills/add-reward-function/SKILL.md:51
echo ""
echo "=== Test 10: explicit ValueError on validation failure ==="
if grep -q 'raise ValueError' "$REPO/slime/rollout/sft_rollout.py" && \
   grep -q 'raise ValueError' "$REPO/slime/utils/mask_utils.py"; then
    echo "PASS"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL: missing explicit ValueError in modified files"
fi

# --- Final score ---
echo ""
echo "=== Final Score ==="
SCORE=$(python3 -c "print(f'{min(1.0, $SCORE):.2f}')")
echo "Deterministic score: $SCORE"
echo "$SCORE" > "$LOG_DIR/reward.txt"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
