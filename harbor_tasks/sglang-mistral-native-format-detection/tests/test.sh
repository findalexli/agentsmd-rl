#!/usr/bin/env bash
set +e

TOTAL=0
EARNED=0

add_score() {
    local weight=$1 pass=$2 label=$3
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" -eq 1 ]; then
        EARNED=$(python3 -c "print($EARNED + $weight)")
        echo "PASS ($weight): $label"
    else
        echo "FAIL ($weight): $label"
    fi
}

cd /repo

########################################
# GATE: Syntax check
########################################
if ! python3 -c "import ast; ast.parse(open('python/sglang/srt/server_args.py').read())" 2>/dev/null; then
    echo "GATE FAIL: server_args.py has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASS: syntax check"

########################################
# Extract _is_mistral_native_format once
########################################
FUNC_FILE=$(mktemp /tmp/func_XXXXX.py)
python3 -c "
import ast, textwrap

with open('python/sglang/srt/server_args.py') as f:
    source = f.read()
    lines = source.splitlines(keepends=True)

tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_is_mistral_native_format':
        func_src = textwrap.dedent(''.join(lines[node.lineno-1:node.end_lineno]))
        with open('$FUNC_FILE', 'w') as out:
            out.write(func_src)
        break
else:
    import sys; sys.exit(1)
" 2>/dev/null

if [ ! -s "$FUNC_FILE" ]; then
    echo "GATE FAIL: _is_mistral_native_format not found"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# Helper that creates a model dir and calls the extracted function
HELPER=$(mktemp /tmp/helper_XXXXX.py)
cat > "$HELPER" << 'PYEOF'
import os, sys, types, tempfile

func_file = sys.argv[1]
model_name = sys.argv[2]       # e.g. "Mistral-Small-4-119B-2603"
has_params = sys.argv[3] == "1"
has_config = sys.argv[4] == "1"
expected = sys.argv[5]          # "True" or "False"

tmpdir = tempfile.mkdtemp()
model_dir = os.path.join(tmpdir, "models", model_name)
os.makedirs(model_dir, exist_ok=True)
if has_params:
    open(os.path.join(model_dir, "params.json"), "w").write("{}")
if has_config:
    open(os.path.join(model_dir, "config.json"), "w").write("{}")

with open(func_file) as f:
    func_src = f.read()

exec_ns = {"os": os, "re": __import__("re"), "__builtins__": __builtins__}
exec(compile("import os, re\n" + func_src, "<test>", "exec"), exec_ns)
func = exec_ns["_is_mistral_native_format"]

mock_self = types.SimpleNamespace(model_path=model_dir)
result = func(mock_self)

expected_bool = expected == "True"
if result != expected_bool:
    print(f"MISMATCH: got {result}, expected {expected_bool}", file=sys.stderr)
    sys.exit(1)
print("OK")
PYEOF

########################################
# Behavioral fail-to-pass tests (0.45)
# Bug: both files + matching model → wrongly returns False
########################################

# [pr_diff] (0.15): mistral-small-4 with both params.json+config.json returns True
PASS=0
python3 "$HELPER" "$FUNC_FILE" "Mistral-Small-4-119B-2603" 1 1 True 2>/dev/null && PASS=1
add_score 0.15 $PASS "[pr_diff] (0.15): mistral-small-4 with both files returns native=True"

# [pr_diff] (0.15): mistral-large-3 with both files returns True
PASS=0
python3 "$HELPER" "$FUNC_FILE" "Mistral-Large-3-2503" 1 1 True 2>/dev/null && PASS=1
add_score 0.15 $PASS "[pr_diff] (0.15): mistral-large-3 with both files returns native=True"

# [pr_diff] (0.15): leanstral with both files returns True
PASS=0
python3 "$HELPER" "$FUNC_FILE" "Leanstral-22B-v0.1" 1 1 True 2>/dev/null && PASS=1
add_score 0.15 $PASS "[pr_diff] (0.15): leanstral with both files returns native=True"

########################################
# Pass-to-pass regression: positive (0.10)
########################################

# [pr_diff] (0.05): params.json only (no config.json) still returns True
PASS=0
python3 "$HELPER" "$FUNC_FILE" "SomeMistralModel" 1 0 True 2>/dev/null && PASS=1
add_score 0.05 $PASS "[pr_diff] (0.05): params.json only → native=True (regression)"

# [pr_diff] (0.05): params-only with non-matching name still True
PASS=0
python3 "$HELPER" "$FUNC_FILE" "Mistral-7B-Instruct-v0.3" 1 0 True 2>/dev/null && PASS=1
add_score 0.05 $PASS "[pr_diff] (0.05): Mistral-7B params-only → native=True (regression)"

########################################
# Pass-to-pass regression: negative (0.35)
# Models that should NOT be native format
########################################

# [pr_diff] (0.10): Mistral-7B with both files → False
PASS=0
python3 "$HELPER" "$FUNC_FILE" "Mistral-7B-Instruct-v0.3" 1 1 False 2>/dev/null && PASS=1
add_score 0.10 $PASS "[pr_diff] (0.10): Mistral-7B with both files → native=False (regression)"

# [pr_diff] (0.05): Codestral-Mamba with both files → False
PASS=0
python3 "$HELPER" "$FUNC_FILE" "Codestral-Mamba-22B-v0.1" 1 1 False 2>/dev/null && PASS=1
add_score 0.05 $PASS "[pr_diff] (0.05): Codestral-Mamba with both files → native=False"

# [pr_diff] (0.05): Pixtral with both files → False
PASS=0
python3 "$HELPER" "$FUNC_FILE" "Pixtral-12B-2409" 1 1 False 2>/dev/null && PASS=1
add_score 0.05 $PASS "[pr_diff] (0.05): Pixtral with both files → native=False"

# [pr_diff] (0.05): Mistral-Small-3 (version 3, NOT 4) with both files → False
PASS=0
python3 "$HELPER" "$FUNC_FILE" "Mistral-Small-3-24B" 1 1 False 2>/dev/null && PASS=1
add_score 0.05 $PASS "[pr_diff] (0.05): Mistral-Small-3 (not 4) with both files → native=False"

# [pr_diff] (0.05): No params.json → False
PASS=0
python3 "$HELPER" "$FUNC_FILE" "SomeModel" 0 1 False 2>/dev/null && PASS=1
add_score 0.05 $PASS "[pr_diff] (0.05): no params.json → native=False"

# [pr_diff] (0.05): Neither file → False
PASS=0
python3 "$HELPER" "$FUNC_FILE" "EmptyModel" 0 0 False 2>/dev/null && PASS=1
add_score 0.05 $PASS "[pr_diff] (0.05): neither file → native=False"

########################################
# Anti-stub structural (0.10)
########################################

# [pr_diff] (0.10): Method exists and is non-trivial
PASS=0
python3 -c "
import ast
with open('python/sglang/srt/server_args.py') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_is_mistral_native_format':
        stmts = [n for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.Call, ast.Compare, ast.BoolOp))]
        assert len(stmts) >= 3, f'Stub: only {len(stmts)} control/call nodes'
        break
else:
    assert False, 'function not found'
print('OK')
" 2>/dev/null && PASS=1
add_score 0.10 $PASS "[pr_diff] (0.10): _is_mistral_native_format is non-trivial (anti-stub)"

########################################
# Compute final reward
########################################

REWARD=$(python3 -c "print(round($EARNED, 4))")
echo ""
echo "Total: $REWARD / $TOTAL"
echo "$REWARD" > /logs/verifier/reward.txt

echo "{\"reward\": $REWARD, \"behavioral\": $REWARD, \"regression\": 0.0, \"config\": 0.0, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
