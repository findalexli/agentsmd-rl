"""
Task: gradio-debug-flag-forward
Repo: gradio-app/gradio @ 4d97c68f8a5a55ba686ab5ce599b932b51754984
PR:   12950

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import sys

REPO = "/workspace/gradio"

# Ensure the repo is importable
sys.path.insert(0, REPO)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile

    for f in ["gradio/routes.py", "gradio/blocks.py"]:
        py_compile.compile(f"{REPO}/{f}", doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_default_debug_false():
    """create_app() with no debug arg produces a non-debug app."""
    from gradio import Interface
    from gradio.routes import App

    # Test with 3 different Interface configs to prevent hardcoding
    for fn, inp, out in [
        (lambda x: x, "text", "text"),
        (lambda x: x.upper(), "text", "text"),
        (lambda x: len(x), "text", "number"),
    ]:
        app = App.create_app(Interface(fn, inp, out))
        assert app.debug is False, f"Expected app.debug=False by default, got {app.debug}"


# [pr_diff] fail_to_pass
def test_create_app_accepts_debug_param():
    """create_app() signature includes a debug parameter with default False."""
    import inspect

    from gradio.routes import App

    sig = inspect.signature(App.create_app)
    assert "debug" in sig.parameters, (
        f"create_app() has no 'debug' parameter. Params: {list(sig.parameters)}"
    )
    debug_param = sig.parameters["debug"]
    assert debug_param.default is False, (
        f"Expected debug default=False, got {debug_param.default}"
    )


# [pr_diff] fail_to_pass
def test_debug_true_forwarded():
    """create_app(debug=True) correctly enables debug mode."""
    from gradio import Interface
    from gradio.routes import App

    app = App.create_app(Interface(lambda x: x, "text", "text"), debug=True)
    assert app.debug is True, f"Expected app.debug=True with debug=True, got {app.debug}"


# [pr_diff] fail_to_pass
def test_explicit_debug_false():
    """create_app(debug=False) explicitly yields debug=False."""
    from gradio import Interface
    from gradio.routes import App

    app = App.create_app(Interface(lambda x: x, "text", "text"), debug=False)
    assert app.debug is False, f"Expected app.debug=False with debug=False, got {app.debug}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_app_functional():
    """create_app still produces a fully functional Gradio app with routes."""
    from fastapi import FastAPI
    from gradio import Interface
    from gradio.routes import App

    app = App.create_app(Interface(lambda x: x + "!", "text", "text"))
    assert isinstance(app, FastAPI), "App is not a FastAPI instance"
    route_paths = [r.path for r in app.routes if hasattr(r, "path")]
    assert len(route_paths) > 5, f"Too few routes ({len(route_paths)}), app not functional"
    api_routes = [
        p for p in route_paths if "/api/" in p or "/queue/" in p or "/upload" in p
    ]
    assert len(api_routes) >= 1, f"No gradio API routes found in {route_paths[:10]}"


# [pr_diff] pass_to_pass
def test_app_class_preserved():
    """App class is still a FastAPI subclass with auth_dependency param."""
    import inspect

    from fastapi import FastAPI
    from gradio.routes import App

    assert issubclass(App, FastAPI), "App is not a FastAPI subclass"
    sig = inspect.signature(App.__init__)
    assert "auth_dependency" in sig.parameters, (
        "App.__init__ missing auth_dependency param"
    )
