#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="${REPO_ROOT:-/workspace}"
DATA_FILE="$REPO_ROOT/src/prime_rl/trainer/sft/data.py"
SCORE=0

echo "=== GATE: Syntax check ==="
# [pr_diff] (0.00): data.py must be valid Python
if ! python3 -c "import ast; ast.parse(open('$DATA_FILE').read())"; then
    echo "GATE FAILED: syntax error"
    echo "0.0" > "/logs/verifier/reward.txt"
    exit 0
fi
echo "GATE PASSED"

add() { SCORE=$(python3 -c "print($SCORE + $1)"); }

echo ""
echo "=== Behavioral: messages column produces valid tokenized output ==="
# [pr_diff] (0.30): SFTDataset must accept a dataset with 'messages' column and tokenize it
RESULT=$(cd "$REPO_ROOT" && python3 << 'PYEOF'
import sys
try:
    from datasets import Dataset
    from transformers import AutoTokenizer
    from prime_rl.trainer.sft.data import SFTDataset

    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]
    ds = Dataset.from_list([{"messages": messages}])
    sft_ds = SFTDataset(ds, tokenizer=tokenizer, max_examples=1)
    sample = next(iter(sft_ds))

    assert "input_ids" in sample and len(sample["input_ids"]) > 0
    assert "loss_mask" in sample and len(sample["loss_mask"]) > 0
    assert "target_ids" in sample and len(sample["target_ids"]) > 0
    assert "position_ids" in sample and len(sample["position_ids"]) > 0
    assert len(sample["input_ids"]) == len(sample["loss_mask"])
    assert any(sample["loss_mask"]), "Some tokens should be trainable"
    print("1")
except Exception as e:
    print(f"FAIL: {e}", file=sys.stderr)
    print("0")
PYEOF
)
RESULT=$(echo "$RESULT" | tail -1)
if [ "$RESULT" = "1" ]; then
    echo "PASS: messages column produces valid tokenized output"
    add 0.30
else
    echo "FAIL: messages column not accepted or output invalid"
fi

echo ""
echo "=== Behavioral: messages takes precedence over prompt/completion ==="
# [pr_diff] (0.20): When both 'messages' and 'prompt'/'completion' present, messages wins
RESULT=$(cd "$REPO_ROOT" && python3 << 'PYEOF'
import sys
try:
    from datasets import Dataset
    from transformers import AutoTokenizer
    from prime_rl.trainer.sft.data import SFTDataset

    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")

    row_both = {
        "messages": [
            {"role": "user", "content": "From messages"},
            {"role": "assistant", "content": "Response from messages"},
        ],
        "prompt": [{"role": "user", "content": "Ignored prompt"}],
        "completion": [{"role": "assistant", "content": "Ignored completion"}],
    }
    row_messages_only = {
        "messages": [
            {"role": "user", "content": "From messages"},
            {"role": "assistant", "content": "Response from messages"},
        ],
    }

    ds_both = SFTDataset(Dataset.from_list([row_both]), tokenizer=tokenizer, max_examples=1)
    ds_only = SFTDataset(Dataset.from_list([row_messages_only]), tokenizer=tokenizer, max_examples=1)

    sample_both = next(iter(ds_both))
    sample_only = next(iter(ds_only))

    assert sample_both["input_ids"] == sample_only["input_ids"], \
        "messages should take precedence over prompt/completion"
    print("1")
except Exception as e:
    print(f"FAIL: {e}", file=sys.stderr)
    print("0")
PYEOF
)
RESULT=$(echo "$RESULT" | tail -1)
if [ "$RESULT" = "1" ]; then
    echo "PASS: messages takes precedence"
    add 0.20
else
    echo "FAIL: messages does not take precedence"
fi

echo ""
echo "=== Behavioral: error message mentions messages format ==="
# [pr_diff] (0.10): ValueError should inform users about the messages column option
RESULT=$(cd "$REPO_ROOT" && python3 << 'PYEOF'
import sys
try:
    from datasets import Dataset
    from transformers import AutoTokenizer
    from prime_rl.trainer.sft.data import SFTDataset

    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    ds = Dataset.from_list([{"text": "irrelevant"}])
    sft_ds = SFTDataset(ds, tokenizer=tokenizer, max_examples=1)

    try:
        next(iter(sft_ds))
        print("0")
    except ValueError as e:
        msg = str(e).lower()
        if "messages" in msg:
            print("1")
        else:
            print("0")
            print(f"Error doesn't mention 'messages': {e}", file=sys.stderr)
except Exception as e:
    print(f"FAIL: {e}", file=sys.stderr)
    print("0")
PYEOF
)
RESULT=$(echo "$RESULT" | tail -1)
if [ "$RESULT" = "1" ]; then
    echo "PASS: error message mentions messages format"
    add 0.10
else
    echo "FAIL: error message does not mention messages format"
fi

echo ""
echo "=== Pass-to-pass: prompt+completion format still works ==="
# [pr_diff] (0.15): Existing prompt+completion format must continue working
RESULT=$(cd "$REPO_ROOT" && python3 << 'PYEOF'
import sys
try:
    from datasets import Dataset
    from transformers import AutoTokenizer
    from prime_rl.trainer.sft.data import SFTDataset

    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    ds = Dataset.from_list([{
        "prompt": [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
        ],
        "completion": [{"role": "assistant", "content": "Hi there!"}],
    }])
    sft_ds = SFTDataset(ds, tokenizer=tokenizer, max_examples=1)
    sample = next(iter(sft_ds))

    assert "input_ids" in sample and len(sample["input_ids"]) > 0
    assert any(sample["loss_mask"]), "Some tokens should be trainable"
    print("1")
except Exception as e:
    print(f"FAIL: {e}", file=sys.stderr)
    print("0")
PYEOF
)
RESULT=$(echo "$RESULT" | tail -1)
if [ "$RESULT" = "1" ]; then
    echo "PASS: prompt+completion format still works"
    add 0.15
else
    echo "FAIL: prompt+completion format broken"
fi

echo ""
echo "=== Pass-to-pass: ValueError on invalid input still raised ==="
# [pr_diff] (0.10): Missing messages/prompt/completion must still raise ValueError
RESULT=$(cd "$REPO_ROOT" && python3 << 'PYEOF'
import sys
try:
    from datasets import Dataset
    from transformers import AutoTokenizer
    from prime_rl.trainer.sft.data import SFTDataset

    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    ds = Dataset.from_list([{"text": "irrelevant"}])
    sft_ds = SFTDataset(ds, tokenizer=tokenizer, max_examples=1)

    try:
        next(iter(sft_ds))
        print("0")
    except ValueError:
        print("1")
except Exception as e:
    print(f"FAIL: {e}", file=sys.stderr)
    print("0")
PYEOF
)
RESULT=$(echo "$RESULT" | tail -1)
if [ "$RESULT" = "1" ]; then
    echo "PASS: ValueError still raised on invalid input"
    add 0.10
else
    echo "FAIL: ValueError not raised on invalid input"
fi

echo ""
echo "=== Anti-stub: multi-turn messages produce longer sequences ==="
# [pr_diff] (0.10): Implementation must actually process multi-turn messages, not stub
RESULT=$(cd "$REPO_ROOT" && python3 << 'PYEOF'
import sys
try:
    from datasets import Dataset
    from transformers import AutoTokenizer
    from prime_rl.trainer.sft.data import SFTDataset

    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")

    multi = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "What is 2+2?"},
        {"role": "assistant", "content": "The answer is 4."},
        {"role": "user", "content": "And 3+3?"},
        {"role": "assistant", "content": "The answer is 6."},
    ]
    single = [
        {"role": "user", "content": "What is 2+2?"},
        {"role": "assistant", "content": "The answer is 4."},
    ]

    ds_multi = SFTDataset(Dataset.from_list([{"messages": multi}]), tokenizer=tokenizer, max_examples=1)
    ds_single = SFTDataset(Dataset.from_list([{"messages": single}]), tokenizer=tokenizer, max_examples=1)

    sample_multi = next(iter(ds_multi))
    sample_single = next(iter(ds_single))

    assert len(sample_multi["input_ids"]) > len(sample_single["input_ids"]), \
        "Multi-turn should produce more tokens"
    print("1")
except Exception as e:
    print(f"FAIL: {e}", file=sys.stderr)
    print("0")
PYEOF
)
RESULT=$(echo "$RESULT" | tail -1)
if [ "$RESULT" = "1" ]; then
    echo "PASS: multi-turn messages handled correctly"
    add 0.10
else
    echo "FAIL: multi-turn messages not handled correctly"
fi

echo ""
echo "=== Config-derived: no unnecessary try/except in _process ==="
# [agent_config] (0.05): "Avoid try/except blocks unless it's really necessary" — AGENTS.md:5
NO_TRYEXCEPT=$(python3 -c "
import ast, sys
source = open('$DATA_FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == '_process':
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                print('0')
                sys.exit(0)
print('1')
" 2>&1 | tail -1)
if [ "$NO_TRYEXCEPT" = "1" ]; then
    echo "PASS: no try/except in _process"
    add 0.05
else
    echo "FAIL: unnecessary try/except found in _process"
fi

echo ""
echo "=== Final Score ==="
echo "Score: $SCORE"
echo "$SCORE" > "/logs/verifier/reward.txt"

# Write detailed reward.json
python3 -c "
import json
score = float('$SCORE')
behavioral = min(0.30, score) + min(0.20, max(0, score - 0.30)) + min(0.10, max(0, score - 0.50))
regression = min(0.15, max(0, score - 0.60)) + min(0.10, max(0, score - 0.75))
anti_stub = min(0.10, max(0, score - 0.85))
config = min(0.05, max(0, score - 0.95))
json.dump({
    'reward': score,
    'behavioral': round(min(behavioral, 0.60), 2),
    'regression': round(min(regression, 0.25), 2),
    'anti_stub': round(min(anti_stub, 0.10), 2),
    'config': round(min(config, 0.05), 2),
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source "$TASK_DIR/tests/judge_hook.sh" 2>/dev/null || true
