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


# [static] pass_to_pass
def test_ruff_check():
    """Modified files must pass ruff linting (repo's CI standard)."""
    import subprocess

    r = subprocess.run(
        ["python", "-m", "ruff", "check", "gradio/routes.py", "gradio/blocks.py"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD gates from the repo's own tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_analytics():
    """Repo's analytics tests pass (pass_to_pass - no external deps)."""
    import subprocess

    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_analytics.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Analytics tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_http_server():
    """Repo's HTTP server tests pass (pass_to_pass - no heavy deps)."""
    import subprocess

    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_http_server.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"HTTP server tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_gradio_import():
    """Gradio imports correctly (pass_to_pass - basic smoke test)."""
    import subprocess

    r = subprocess.run(
        ["python", "-c", "import gradio; from gradio import Interface; from gradio.routes import App; print('OK')"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Gradio import failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_external_utils():
    """Repo's external utils tests pass (pass_to_pass - no external deps)."""
    import subprocess

    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_external_utils.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"External utils tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_reload():
    """Repo's reload tests pass (pass_to_pass - tests config/reloading)."""
    import subprocess

    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_reload.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Reload tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_check_modified():
    """Modified files pass ruff linting (pass_to_pass - repo CI standard)."""
    import subprocess

    r = subprocess.run(
        ["python", "-m", "ruff", "check", "gradio/routes.py", "gradio/blocks.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_client_utils():
    """Repo's client utils tests pass (pass_to_pass - no external deps)."""
    import subprocess

    r = subprocess.run(
        ["python", "-m", "pytest", "client/python/test/test_utils.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Client utils tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"
