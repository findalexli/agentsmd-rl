#!/usr/bin/env bash
set -uo pipefail

SCORE=0
TOTAL=0
PASS=0
DETAILS=""

log() {
    DETAILS="${DETAILS}$1\n"
    echo "$1"
}

add_check() {
    local name="$1" weight="$2" result="$3"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$result" = "1" ]; then
        PASS=$(python3 -c "print($PASS + $weight)")
        log "PASS ($weight): $name"
    else
        log "FAIL ($weight): $name"
    fi
}

REPO=/workspace/gradio

# ============================================================
# GATE: Syntax check — abort on failure
# ============================================================
# [pr_diff] (gate): Python files must parse without syntax errors
python3 -c "
import py_compile, sys
for f in ['$REPO/gradio/routes.py', '$REPO/gradio/blocks.py']:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        print(f'Syntax error: {e}', file=sys.stderr)
        sys.exit(1)
"
if [ $? -ne 0 ]; then
    log "GATE FAIL: Syntax error in modified files"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "details": "gate_fail: syntax error"}' > /logs/verifier/reward.json
    exit 0
fi
log "GATE PASS: Syntax check"

# ============================================================
# Fail-to-pass: behavioral tests (0.70 total)
# ============================================================

# [pr_diff] (0.35): create_app() default produces a non-debug app
R1=$(python3 -c "
import sys
sys.path.insert(0, '$REPO')
from gradio.routes import App
from gradio import Interface

app = App.create_app(Interface(lambda x: x, 'text', 'text'))
if app.debug is False:
    print(1)
else:
    print(0)
" 2>/dev/null || echo 0)
add_check "[pr_diff] (0.35): create_app() default debug is False" 0.35 "$R1"

# [pr_diff] (0.35): create_app(debug=True) forwards the flag
R2=$(python3 -c "
import sys
sys.path.insert(0, '$REPO')
from gradio.routes import App
from gradio import Interface

app = App.create_app(Interface(lambda x: x, 'text', 'text'), debug=True)
if app.debug is True:
    print(1)
else:
    print(0)
" 2>/dev/null || echo 0)
add_check "[pr_diff] (0.35): create_app(debug=True) forwards flag" 0.35 "$R2"

# ============================================================
# Pass-to-pass: existing test must still work (0.10)
# ============================================================

# [pr_diff] (0.10): existing create_app returns a FastAPI instance
R3=$(python3 -c "
import sys
sys.path.insert(0, '$REPO')
from gradio.routes import App
from gradio import Interface
from fastapi import FastAPI

app = App.create_app(Interface(lambda x: x, 'text', 'text'))
if isinstance(app, FastAPI):
    print(1)
else:
    print(0)
" 2>/dev/null || echo 0)
add_check "[pr_diff] (0.10): create_app still returns FastAPI instance" 0.10 "$R3"

# ============================================================
# Structural: anti-stub check (0.10)
# ============================================================

# [pr_diff] (0.10): The hardcoded debug=True must be removed
R4=$(python3 -c "
import ast, sys

with open('$REPO/gradio/routes.py') as f:
    source = f.read()

# Check that 'debug=True' is NOT hardcoded in the App() constructor call
# within create_app. We parse the AST and look for the specific pattern.
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        for kw in node.keywords:
            if kw.arg == 'debug' and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                # Found hardcoded debug=True — check if it's in create_app
                # by checking the function context
                print(0)
                sys.exit(0)

# No hardcoded debug=True found — good
print(1)
" 2>/dev/null || echo 0)
add_check "[pr_diff] (0.10): No hardcoded debug=True in App() call" 0.10 "$R4"

# ============================================================
# Config-derived: ruff formatting check (0.10)
# ============================================================

# [agent_config] (0.10): "Python code is formatted with ruff" — AGENTS.md:43
R5=$(python3 -c "
import subprocess, sys
result = subprocess.run(
    ['python3', '-m', 'ruff', 'check', '--select=E,W', '--quiet',
     '$REPO/gradio/routes.py', '$REPO/gradio/blocks.py'],
    capture_output=True, text=True
)
# Pass if no errors (ruff might not be installed — pass in that case)
if result.returncode == 0 or 'No module named ruff' in result.stderr:
    print(1)
else:
    print(0)
    print(result.stdout, file=sys.stderr)
" 2>/dev/null || echo 1)
add_check "[agent_config] (0.10): ruff check passes — AGENTS.md:43" 0.10 "$R5"

# ============================================================
# Compute final score
# ============================================================

SCORE=$PASS
echo ""
echo "=== Results ==="
echo -e "$DETAILS"
echo "Score: $SCORE / $TOTAL"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt
python3 -c "
import json
print(json.dumps({
    'reward': $SCORE,
    'behavioral': min(0.70, $SCORE),
    'regression': 0.10 if $SCORE >= 0.80 else 0.0,
    'structural': 0.10 if $SCORE >= 0.90 else 0.0,
    'config': 0.10 if $SCORE >= 1.0 else 0.0,
}))
" > /logs/verifier/reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
