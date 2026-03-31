#!/usr/bin/env bash
set -uo pipefail

SCORE=0
TOTAL=0
REPO="/workspace/gradio"

log() { echo "[TEST] $*"; }
add_score() {
    local weight="$1" desc="$2" pass="$3"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        log "PASS ($weight): $desc"
    else
        log "FAIL ($weight): $desc"
    fi
}

# ============================================================
# GATE: Syntax check — abort on failure
# ============================================================
# [pr_diff] (0.00): Python syntax must be valid
log "GATE: Checking syntax of gradio/components/html.py"
if ! python3 -c "import py_compile; py_compile.compile('$REPO/gradio/components/html.py', doraise=True)" 2>/dev/null; then
    log "GATE FAILED: syntax error in html.py"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
log "GATE: syntax OK"

# ============================================================
# Fail-to-pass: Behavioral tests (0.65 total)
# ============================================================

# [pr_diff] (0.30): Custom event name in js_on_load can be accessed as attribute
log "Testing: custom event attribute access"
RESULT=$(cd "$REPO" && python3 -c "
import gradio as gr

with gr.Blocks():
    h = gr.HTML(
        js_on_load=\"\"\"
        document.addEventListener('keydown', (e) => {
            trigger('keypress', {key: e.key});
        });
        \"\"\"
    )
    # This should NOT raise AttributeError
    listener = h.keypress
    print('OK' if callable(listener) else 'FAIL')
" 2>&1) || true
if echo "$RESULT" | grep -q "OK"; then
    add_score 0.30 "Custom event 'keypress' accessible as callable attribute" 1
else
    add_score 0.30 "Custom event 'keypress' accessible as callable attribute" 0
fi

# [pr_diff] (0.20): Custom event listener can be wired to a function
log "Testing: custom event listener wiring"
RESULT=$(cd "$REPO" && python3 -c "
import gradio as gr

with gr.Blocks() as demo:
    h = gr.HTML(
        js_on_load=\"\"\"
        document.addEventListener('keydown', (e) => {
            trigger('keypress', {key: e.key});
        });
        \"\"\"
    )
    tb = gr.Textbox()
    dep = h.keypress(lambda: 'test', None, tb)
    # dep should be a Dependency (dict-like) if wiring succeeded
    print('OK' if dep is not None else 'FAIL')
" 2>&1) || true
if echo "$RESULT" | grep -q "OK"; then
    add_score 0.20 "Custom event listener wires function successfully" 1
else
    add_score 0.20 "Custom event listener wires function successfully" 0
fi

# [pr_diff] (0.10): AttributeError raised for event NOT in js_on_load
log "Testing: AttributeError for non-existent custom event"
RESULT=$(cd "$REPO" && python3 -c "
import gradio as gr

with gr.Blocks():
    h = gr.HTML(js_on_load=\"trigger('click')\")
    try:
        _ = h.totally_made_up_event
        print('FAIL')
    except AttributeError:
        print('OK')
" 2>&1) || true
if echo "$RESULT" | grep -q "OK"; then
    add_score 0.10 "AttributeError for event not in js_on_load" 1
else
    add_score 0.10 "AttributeError for event not in js_on_load" 0
fi

# [pr_diff] (0.10): Multiple custom events on same component
log "Testing: multiple custom events"
RESULT=$(cd "$REPO" && python3 -c "
import gradio as gr

with gr.Blocks() as demo:
    h = gr.HTML(
        js_on_load=\"\"\"
        trigger('my_event_a', {});
        trigger('my_event_b', {});
        \"\"\"
    )
    tb = gr.Textbox()
    dep_a = h.my_event_a(lambda: 'a', None, tb)
    dep_b = h.my_event_b(lambda: 'b', None, tb)
    print('OK' if dep_a is not None and dep_b is not None else 'FAIL')
" 2>&1) || true
if echo "$RESULT" | grep -q "OK"; then
    add_score 0.10 "Multiple custom events on same component" 1
else
    add_score 0.10 "Multiple custom events on same component" 0
fi

# ============================================================
# Pass-to-pass: Regression tests (0.15 total)
# ============================================================

# [pr_diff] (0.10): Built-in events still work on HTML component
log "Testing: built-in events still work"
RESULT=$(cd "$REPO" && python3 -c "
import gradio as gr

with gr.Blocks() as demo:
    h = gr.HTML('<p>test</p>')
    tb = gr.Textbox()
    dep = h.click(lambda: 'clicked', None, tb)
    print('OK' if dep is not None else 'FAIL')
" 2>&1) || true
if echo "$RESULT" | grep -q "OK"; then
    add_score 0.10 "Built-in 'click' event still works" 1
else
    add_score 0.10 "Built-in 'click' event still works" 0
fi

# [pr_diff] (0.10): HTML component basic construction still works
log "Testing: HTML component basic functionality"
RESULT=$(cd "$REPO" && python3 -c "
import gradio as gr

with gr.Blocks():
    h = gr.HTML('<p>Hello</p>')
    config = h.get_config()
    print('OK' if 'component_class_name' in config else 'FAIL')
" 2>&1) || true
if echo "$RESULT" | grep -q "OK"; then
    add_score 0.10 "HTML component construction and config" 1
else
    add_score 0.10 "HTML component construction and config" 0
fi

# ============================================================
# Config-derived checks (0.10 total)
# ============================================================

# [agent_config] (0.10): "Python code is formatted with ruff" — AGENTS.md:43 @ d610464
log "Testing: ruff format compliance"
if command -v ruff &>/dev/null; then
    if ruff check "$REPO/gradio/components/html.py" --select E,W --quiet 2>/dev/null; then
        add_score 0.10 "ruff lint passes on html.py" 1
    else
        add_score 0.10 "ruff lint passes on html.py" 0
    fi
else
    # ruff not available, skip gracefully
    add_score 0.10 "ruff lint passes on html.py (ruff not found, skipped)" 1
fi

# ============================================================
# Final score
# ============================================================
REWARD=$(python3 -c "print(round($SCORE, 4))")
log "Final score: $REWARD (of $TOTAL)"
echo "$REWARD" > /logs/verifier/reward.txt

# Build reward.json
python3 -c "
import json
score = $SCORE
behavioral = min(score, 0.70)
remainder = max(score - 0.70, 0.0)
regression = min(remainder, 0.20)
remainder2 = max(remainder - 0.20, 0.0)
config = min(remainder2, 0.10)
print(json.dumps({
    'reward': round(score, 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'config': round(config, 4),
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
