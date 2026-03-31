#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
SCORE=0.0

add_score() {
    SCORE=$(python3 -c "print($SCORE + $1)")
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}
add_total() {
    TOTAL=$(python3 -c "print($TOTAL + $1)")
}

cd /workspace/gradio

##############################################################################
# GATE: Syntax check — abort on failure
##############################################################################
# [pr_diff] (gate): routes.py must parse without syntax errors
python3 -c "import ast; ast.parse(open('gradio/routes.py').read())" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "GATE FAILED: gradio/routes.py has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

##############################################################################
# BEHAVIORAL: Fail-to-pass tests (0.65 total)
##############################################################################

# [pr_diff] (0.40): /cancel endpoint properly closes generator (finally block fires)
# Buggy code: del app.iterators[event_id] without close → finally never runs → FAIL
python3 -c "
import asyncio

async def test_cancel_closes_generator():
    import gradio as gr
    from gradio.routes import App
    from gradio.utils import SyncToAsyncIterator

    closed = []

    def gen():
        try:
            while True:
                yield 'running'
        finally:
            closed.append(True)

    with gr.Blocks() as demo:
        out = gr.Textbox()
        btn = gr.Button()
        btn.click(gen, None, out, api_name='predict')

    app = App.create_app(demo)

    event_id = 'test_event'
    g = gen()
    next(g)  # advance so GeneratorExit fires on close
    iterator = SyncToAsyncIterator(g, limiter=None)
    app.iterators[event_id] = iterator

    from starlette.testclient import TestClient
    client = TestClient(app)
    resp = client.post(
        '/api/cancel',
        json={
            'session_hash': 'test',
            'fn_index': 0,
            'event_id': event_id,
        },
    )
    assert resp.status_code == 200, f'Expected 200, got {resp.status_code}'
    assert resp.json()['success'], 'Cancel did not return success'
    assert closed, 'Generator was not closed by /cancel endpoint'

asyncio.run(test_cancel_closes_generator())
print('PASS: cancel closes generator')
" 2>&1
if [ $? -eq 0 ]; then
    add_score 0.40
    echo "  [PASS] cancel_closes_generator (0.40)"
else
    add_total 0.40
    echo "  [FAIL] cancel_closes_generator (0.00/0.40)"
fi

# [pr_diff] (0.25): Cancel gracefully handles generator whose finally block raises
# Buggy code: generator never closed → finally never runs → closed stays empty → FAIL
# Correct fix: safe_aclose wrapped in try/except → finally runs, exception caught → PASS
python3 -c "
import asyncio

async def test_cancel_handles_error_in_cleanup():
    import gradio as gr
    from gradio.routes import App
    from gradio.utils import SyncToAsyncIterator

    closed = []

    def gen_with_error():
        try:
            while True:
                yield 'running'
        finally:
            closed.append(True)
            raise ValueError('cleanup error')

    with gr.Blocks() as demo:
        out = gr.Textbox()
        btn = gr.Button()
        btn.click(gen_with_error, None, out, api_name='predict')

    app = App.create_app(demo)

    event_id = 'test_error_cleanup'
    g = gen_with_error()
    next(g)
    iterator = SyncToAsyncIterator(g, limiter=None)
    app.iterators[event_id] = iterator

    from starlette.testclient import TestClient
    client = TestClient(app)
    resp = client.post(
        '/api/cancel',
        json={
            'session_hash': 'test',
            'fn_index': 0,
            'event_id': event_id,
        },
    )
    assert resp.status_code == 200, f'Expected 200, got {resp.status_code}'
    assert resp.json()['success'], 'Cancel should succeed even with cleanup error'
    assert closed, 'Generator cleanup did not run'

asyncio.run(test_cancel_handles_error_in_cleanup())
print('PASS: cancel handles error in generator cleanup')
" 2>&1
if [ $? -eq 0 ]; then
    add_score 0.25
    echo "  [PASS] cancel_handles_cleanup_error (0.25)"
else
    add_total 0.25
    echo "  [FAIL] cancel_handles_cleanup_error (0.00/0.25)"
fi

##############################################################################
# PASS-TO-PASS: Regression checks (0.20 total)
##############################################################################

# [pr_diff] (0.10): Cancel for non-existent event still returns success
python3 -c "
import asyncio

async def test_cancel_nonexistent():
    import gradio as gr
    from gradio.routes import App

    with gr.Blocks() as demo:
        out = gr.Textbox()
        btn = gr.Button()
        btn.click(lambda: 'hi', None, out, api_name='predict')

    app = App.create_app(demo)

    from starlette.testclient import TestClient
    client = TestClient(app)
    resp = client.post(
        '/api/cancel',
        json={
            'session_hash': 'test',
            'fn_index': 0,
            'event_id': 'nonexistent',
        },
    )
    assert resp.status_code == 200
    assert resp.json()['success']

asyncio.run(test_cancel_nonexistent())
print('PASS: cancel nonexistent event')
" 2>&1
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "  [PASS] cancel_nonexistent (0.10)"
else
    add_total 0.10
    echo "  [FAIL] cancel_nonexistent (0.00/0.10)"
fi

# [pr_diff] (0.10): After cancel, iterator tracking state is consistent
# (P2P: buggy code already manages iterators dict and iterators_to_reset correctly)
python3 -c "
import asyncio

async def test_cancel_tracking():
    import gradio as gr
    from gradio.routes import App
    from gradio.utils import SyncToAsyncIterator

    def gen():
        while True:
            yield 'running'

    with gr.Blocks() as demo:
        out = gr.Textbox()
        btn = gr.Button()
        btn.click(gen, None, out, api_name='predict')

    app = App.create_app(demo)

    event_id = 'test_tracking'
    g = gen()
    next(g)
    iterator = SyncToAsyncIterator(g, limiter=None)
    app.iterators[event_id] = iterator

    from starlette.testclient import TestClient
    client = TestClient(app)
    resp = client.post(
        '/api/cancel',
        json={
            'session_hash': 'test',
            'fn_index': 0,
            'event_id': event_id,
        },
    )
    assert resp.status_code == 200
    assert event_id not in app.iterators, 'Iterator was not removed'
    assert event_id in app.iterators_to_reset, 'Event not in iterators_to_reset'

asyncio.run(test_cancel_tracking())
print('PASS: cancel tracking correct')
" 2>&1
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "  [PASS] cancel_tracking (0.10)"
else
    add_total 0.10
    echo "  [FAIL] cancel_tracking (0.00/0.10)"
fi

##############################################################################
# STRUCTURAL: Anti-stub (0.05)
##############################################################################

# [pr_diff] (0.05): safe_aclose_iterator is called inside cancel_event (not just imported)
python3 -c "
import ast, sys
source = open('gradio/routes.py').read()
tree = ast.parse(source)
found = False
for node in ast.walk(tree):
    if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) and node.name == 'cancel_event':
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                if isinstance(func, ast.Name) and func.id == 'safe_aclose_iterator':
                    found = True
                elif isinstance(func, ast.Attribute) and func.attr == 'safe_aclose_iterator':
                    found = True
        break
assert found, 'safe_aclose_iterator not called in cancel_event'
print('PASS: safe_aclose called in cancel_event')
" 2>&1
if [ $? -eq 0 ]; then
    add_score 0.05
    echo "  [PASS] safe_aclose_in_cancel_event (0.05)"
else
    add_total 0.05
    echo "  [FAIL] safe_aclose_in_cancel_event (0.00/0.05)"
fi

##############################################################################
# CONFIG-DERIVED: Style consistency (0.10)
##############################################################################

# [agent_config] (0.10): "Be consistent with the style of the surrounding code" — AGENTS.md:45
# The fix should use try/except pattern matching queueing.py:reset_iterators
python3 -c "
import ast
source = open('gradio/routes.py').read()
tree = ast.parse(source)

found_try_except = False
for node in ast.walk(tree):
    if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) and node.name == 'cancel_event':
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                for stmt in ast.walk(child):
                    if isinstance(stmt, ast.Call):
                        func = stmt.func
                        if (isinstance(func, ast.Name) and func.id == 'safe_aclose_iterator') or \
                           (isinstance(func, ast.Attribute) and func.attr == 'safe_aclose_iterator'):
                            if child.handlers:
                                found_try_except = True
        break

assert found_try_except, 'safe_aclose_iterator should be wrapped in try/except (matching reset_iterators pattern)'
print('PASS: try/except pattern matches queueing.py')
" 2>&1
if [ $? -eq 0 ]; then
    add_score 0.10
    echo "  [PASS] style_try_except_pattern (0.10)"
else
    add_total 0.10
    echo "  [FAIL] style_try_except_pattern (0.00/0.10)"
fi

##############################################################################
# Summary
##############################################################################

echo ""
echo "Total: $SCORE / $TOTAL"
echo "$SCORE" > /logs/verifier/reward.txt

python3 -c "
score = $SCORE
print('{\"reward\": ' + str(score) + ', \"behavioral\": ' + str(min(score, 0.65)) + ', \"regression\": ' + str(min(max(score - 0.65, 0), 0.20)) + ', \"config\": ' + str(min(max(score - 0.85, 0), 0.15)) + ', \"style_rubric\": 0.0}')
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
