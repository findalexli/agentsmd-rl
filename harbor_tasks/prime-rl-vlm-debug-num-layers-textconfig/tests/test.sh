#!/usr/bin/env bash
set -euo pipefail

SCORE=0

# ── GATE: syntax check ──────────────────────────────────────────────
python3 -c "
import ast
ast.parse(open('src/prime_rl/trainer/model.py').read())
" || { echo "GATE FAILED: syntax error in model.py"; echo '{"reward": 0.0}' > /logs/verifier/reward.json; echo "0.0" > /logs/verifier/reward.txt; exit 0; }
echo "GATE: syntax check passed"

# ── Helper: extract the debug.num_layers code block from model.py ──
# We exec() the actual code from the file to test behavior, not structure.
EXTRACT_AND_TEST=$(cat <<'PYEOF'
import re, sys

with open("src/prime_rl/trainer/model.py") as f:
    source = f.read()

# Extract the if-block for debug.num_layers
pattern = r'(    if config\.debug\.num_layers is not None:\n(?:        [^\n]*\n)*)'
match = re.search(pattern, source)
if not match:
    print("FAIL: could not find debug.num_layers block in model.py", file=sys.stderr)
    sys.exit(1)

code_block = match.group(1)

# Mock logger
class FakeLogger:
    def warning(self, *a, **kw): pass
    def debug(self, *a, **kw): pass

# --- Test setup from argv ---
test_name = sys.argv[1]

if test_name == "vlm_no_toplevel":
    # VLM config: num_hidden_layers only under text_config
    class TextConfig:
        num_hidden_layers = 32
    class ModelConfig:
        text_config = TextConfig()
    class DebugConfig:
        num_layers = 4
    class Config:
        debug = DebugConfig()

    model_config = ModelConfig()
    config = Config()
    logger = FakeLogger()

    try:
        exec(code_block, {"config": config, "model_config": model_config,
                          "logger": logger, "min": min})
    except AttributeError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)

    # Verify text_config was modified
    if model_config.text_config.num_hidden_layers != 4:
        print(f"FAIL: text_config.num_hidden_layers={model_config.text_config.num_hidden_layers}, expected 4", file=sys.stderr)
        sys.exit(1)

    print("OK: VLM config with text_config handled correctly")

elif test_name == "vlm_both_attrs":
    # VLM config that has num_hidden_layers at BOTH levels (edge case)
    class TextConfig:
        num_hidden_layers = 32
    class ModelConfig:
        text_config = TextConfig()
        num_hidden_layers = 64  # top-level (wrong one to modify)
    class DebugConfig:
        num_layers = 4
    class Config:
        debug = DebugConfig()

    model_config = ModelConfig()
    config = Config()
    logger = FakeLogger()

    exec(code_block, {"config": config, "model_config": model_config,
                      "logger": logger, "min": min})

    # The fix should modify text_config, not top-level
    if model_config.text_config.num_hidden_layers != 4:
        print(f"FAIL: text_config.num_hidden_layers={model_config.text_config.num_hidden_layers}, expected 4", file=sys.stderr)
        sys.exit(1)

    print("OK: VLM config with both attrs — text_config modified correctly")

elif test_name == "non_vlm":
    # Standard LM config: no text_config, num_hidden_layers at top level
    class ModelConfig:
        num_hidden_layers = 32
    class DebugConfig:
        num_layers = 4
    class Config:
        debug = DebugConfig()

    model_config = ModelConfig()
    config = Config()
    logger = FakeLogger()

    exec(code_block, {"config": config, "model_config": model_config,
                      "logger": logger, "min": min})

    if model_config.num_hidden_layers != 4:
        print(f"FAIL: num_hidden_layers={model_config.num_hidden_layers}, expected 4", file=sys.stderr)
        sys.exit(1)

    print("OK: Non-VLM config still works")

PYEOF
)

# ── [pr_diff] (0.35): VLM config without top-level num_hidden_layers ─
# Buggy code: AttributeError. Fixed code: reads text_config.
if python3 -c "$EXTRACT_AND_TEST" vlm_no_toplevel; then
    SCORE=$((SCORE + 35))
    echo "  +0.35 VLM config (text_config only) handled"
else
    echo "  +0.00 VLM config (text_config only) FAILED"
fi

# ── [pr_diff] (0.25): VLM config — correct sub-config is modified ────
# Buggy code: modifies model_config.num_hidden_layers (wrong).
# Fixed code: modifies model_config.text_config.num_hidden_layers (correct).
if python3 -c "$EXTRACT_AND_TEST" vlm_both_attrs; then
    SCORE=$((SCORE + 25))
    echo "  +0.25 VLM config modifies text_config correctly"
else
    echo "  +0.00 VLM config modifies wrong attribute"
fi

# ── [pr_diff] (0.10): Non-VLM config backward compat ─────────────────
# Standard LM config should continue to work.
if python3 -c "$EXTRACT_AND_TEST" non_vlm; then
    SCORE=$((SCORE + 10))
    echo "  +0.10 Non-VLM config backward compat OK"
else
    echo "  +0.00 Non-VLM config backward compat FAILED"
fi

# ── [pr_diff] (0.10): Pass-to-pass — file parseable and get_model exists ─
python3 -c "
import ast
tree = ast.parse(open('src/prime_rl/trainer/model.py').read())
funcs = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
assert 'get_model' in funcs, f'get_model not found, functions: {funcs}'
" && {
    SCORE=$((SCORE + 10))
    echo "  +0.10 get_model function exists"
} || {
    echo "  +0.00 get_model function missing"
}

# ── [pr_diff] (0.10): Anti-stub — debug.num_layers block is substantive ──
python3 -c "
import ast

with open('src/prime_rl/trainer/model.py') as f:
    tree = ast.parse(f.read())

# Find the get_model function
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'get_model':
        # Count total statements — must be substantial
        stmts = sum(1 for _ in ast.walk(node) if isinstance(_, ast.stmt))
        assert stmts > 20, f'get_model too short ({stmts} stmts) — likely stubbed'
        break
else:
    assert False, 'get_model not found'
" && {
    SCORE=$((SCORE + 10))
    echo "  +0.10 Anti-stub: get_model is substantive"
} || {
    echo "  +0.00 Anti-stub: get_model appears stubbed"
}

# ── [agent_config] (0.10): No unnecessary try/except around the fix ──
# "Avoid try/except blocks unless it's really necessary" — AGENTS.md:5
python3 -c "
import ast, re

with open('src/prime_rl/trainer/model.py') as f:
    source = f.read()

# Find the debug.num_layers block
pattern = r'if config\.debug\.num_layers is not None:'
for i, line in enumerate(source.splitlines(), 1):
    if re.search(pattern, line):
        start_line = i
        break
else:
    exit(0)  # Can't find block, don't penalize

# Parse and check for try/except wrapping the debug.num_layers block
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Try):
        # Check if the try block overlaps with the debug.num_layers area
        if hasattr(node, 'lineno') and abs(node.lineno - start_line) < 5:
            print(f'FAIL: try/except wrapping debug.num_layers at line {node.lineno}')
            exit(1)

print('OK: no unnecessary try/except around the fix')
" && {
    SCORE=$((SCORE + 10))
    echo "  +0.10 Config: no unnecessary try/except"
} || {
    echo "  +0.00 Config: unnecessary try/except found"
}

# ── Compute final reward ─────────────────────────────────────────────
REWARD=$(python3 -c "print(f'{$SCORE / 100:.4f}')")
echo ""
echo "Total: $REWARD (raw=$SCORE/100)"
echo "$REWARD" > /logs/verifier/reward.txt

# Build reward.json with per-category breakdown
python3 -c "
import json
s = $SCORE
behavioral = 0
if s >= 35: behavioral += 0.35
if s >= 60: behavioral += 0.25
regression = 0
if s >= 70: regression += 0.10
if s >= 80: regression += 0.10
config = 0.10 if s >= 100 else 0.0
json.dump({
    'reward': s / 100,
    'behavioral': behavioral,
    'regression': regression,
    'config': config,
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
