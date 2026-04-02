"""
Task: gradio-cancel-iterator-leak
Repo: gradio-app/gradio @ 0a0378dee463fb10e5a95685d595801171cf641b
PR:   13163

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess

REPO = "/workspace/gradio"


def _make_app_with_gen(gen_fn):
    """Create a minimal Gradio app and register a generator as an iterator."""
    import gradio as gr
    from gradio.routes import App
    from gradio.utils import SyncToAsyncIterator

    with gr.Blocks() as demo:
        out = gr.Textbox()
        btn = gr.Button()
        btn.click(gen_fn, None, out, api_name="predict")

    app = App.create_app(demo)
    return app


def _register_iterator(app, event_id, gen):
    """Advance a generator and register it as an active iterator."""
    from gradio.utils import SyncToAsyncIterator

    next(gen)  # advance so GeneratorExit fires on close
    iterator = SyncToAsyncIterator(gen, limiter=None)
    app.iterators[event_id] = iterator
    return iterator


def _cancel(app, event_id):
    """POST to /gradio_api/cancel and return the response."""
    from starlette.testclient import TestClient

    client = TestClient(app)
    return client.post(
        "/gradio_api/cancel",
        json={"session_hash": "test", "fn_index": 0, "event_id": event_id},
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """gradio/routes.py must parse without syntax errors."""
    import ast
    from pathlib import Path

    src = Path(f"{REPO}/gradio/routes.py").read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cancel_closes_generator():
    """Cancel endpoint properly closes the generator (finally block fires)."""
    closed = []

    def gen():
        try:
            while True:
                yield "running"
        finally:
            closed.append(True)

    app = _make_app_with_gen(gen)
    g = gen()
    _register_iterator(app, "evt_close", g)

    resp = _cancel(app, "evt_close")
    assert resp.status_code == 200
    assert resp.json()["success"]
    assert closed, "Generator finally block was not executed by /cancel"


# [pr_diff] fail_to_pass
def test_cancel_handles_error_in_cleanup():
    """Cancel gracefully handles a generator whose finally block raises."""
    closed = []

    def gen_err():
        try:
            while True:
                yield "running"
        finally:
            closed.append(True)
            raise ValueError("cleanup error")

    app = _make_app_with_gen(gen_err)
    g = gen_err()
    _register_iterator(app, "evt_err", g)

    resp = _cancel(app, "evt_err")
    assert resp.status_code == 200
    assert resp.json()["success"], "Cancel should succeed even when cleanup raises"
    assert closed, "Generator finally block did not run"


# [pr_diff] fail_to_pass
def test_cancel_closes_resource_generator():
    """Cancel properly cleans up resources held by the generator."""
    resources = {"open": True}

    def gen_resource():
        try:
            while True:
                yield "data"
        finally:
            resources["open"] = False

    app = _make_app_with_gen(gen_resource)
    g = gen_resource()
    _register_iterator(app, "evt_resource", g)

    resp = _cancel(app, "evt_resource")
    assert resp.status_code == 200
    assert not resources["open"], "Resource was not cleaned up by cancel"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_cancel_nonexistent_event():
    """Cancel for a non-existent event still returns success."""
    app = _make_app_with_gen(lambda: (yield "x"))

    resp = _cancel(app, "nonexistent_event")
    assert resp.status_code == 200
    assert resp.json()["success"]


# [pr_diff] pass_to_pass
def test_cancel_removes_iterator_and_marks_reset():
    """After cancel, iterator is removed and event is in iterators_to_reset."""
    def gen():
        while True:
            yield "running"

    app = _make_app_with_gen(gen)
    g = gen()
    _register_iterator(app, "evt_track", g)

    resp = _cancel(app, "evt_track")
    assert resp.status_code == 200
    assert "evt_track" not in app.iterators, "Iterator was not removed"
    assert "evt_track" in app.iterators_to_reset, "Event not in iterators_to_reset"


# [pr_diff] pass_to_pass
def test_double_cancel_safe():
    """Cancelling the same event twice does not crash."""
    def gen():
        while True:
            yield "running"

    app = _make_app_with_gen(gen)
    g = gen()
    _register_iterator(app, "evt_double", g)

    resp1 = _cancel(app, "evt_double")
    assert resp1.status_code == 200

    resp2 = _cancel(app, "evt_double")
    assert resp2.status_code == 200
    assert resp2.json()["success"]


# ---------------------------------------------------------------------------
# Anti-stub (static) — modified function has real logic
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """cancel_event handler is not a stub (has real logic, not just pass/return)."""
    import ast
    from pathlib import Path

    src = Path(f"{REPO}/gradio/routes.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "cancel_event":
            # Count non-trivial statements (excluding Pass, docstrings)
            body_stmts = [s for s in ast.walk(node)
                          if isinstance(s, (ast.If, ast.For, ast.AsyncWith,
                                            ast.AsyncFor, ast.Try, ast.Delete,
                                            ast.Assign, ast.Return, ast.Await))]
            assert len(body_stmts) >= 3, (
                "cancel_event body is too simple — looks like a stub"
            )
            return

    raise AssertionError("cancel_event function not found in routes.py")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:43 @ 0a0378dee463fb10e5a95685d595801171cf641b
def test_ruff_format_compliance():
    """Modified file gradio/routes.py passes ruff format check."""
    r = subprocess.run(
        ["ruff", "format", "--check", "gradio/routes.py"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"ruff format check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )
