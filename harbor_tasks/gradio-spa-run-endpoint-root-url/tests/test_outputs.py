"""
Task: gradio-spa-run-endpoint-root-url
Repo: gradio-app/gradio @ a8e6b7ba1e6af793b6a200d4cc6b07f3151f229e
PR:   12894

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/gradio"


def _run_python(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess with the repo on sys.path."""
    env = {**os.environ, "PYTHONPATH": REPO}
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO, env=env,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """gradio/routes.py must parse without syntax errors."""
    source = Path(f"{REPO}/gradio/routes.py").read_text()
    ast.parse(source)


# [repo_tests] pass_to_pass
def test_gradio_imports():
    """Gradio package imports successfully (pass_to_pass)."""
    r = _run_python("""
import gradio
from gradio.routes import App
print("PASS")
""")
    assert r.returncode == 0, f"Import failed:\n{r.stderr[-500:]}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass
def test_routes_module_ruff_check():
    """Ruff lint check passes on gradio/routes.py (pass_to_pass)."""
    # Install ruff if not available (lightweight, fast install)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "ruff"], capture_output=True, timeout=60)
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "gradio/routes.py", "--quiet"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_routes_module_ruff_format():
    """Ruff format check passes on gradio/routes.py (pass_to_pass)."""
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "ruff"], capture_output=True, timeout=60)
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", "gradio/routes.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_gradio_routes_imports():
    """Gradio routes module imports successfully (pass_to_pass)."""
    r = _run_python("""
from gradio.routes import App, APIRouter
print("PASS")
""")
    assert r.returncode == 0, f"Routes import failed:\n{r.stderr[-500:]}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass
def test_route_utils_imports():
    """Gradio route_utils module imports successfully (pass_to_pass)."""
    r = _run_python("""
from gradio import route_utils
from gradio.route_utils import get_root_url
print("PASS")
""")
    assert r.returncode == 0, f"route_utils import failed:\n{r.stderr[-500:]}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_get_root_url():
    """Repo's get_root_url unit tests pass (pass_to_pass).

    Tests the core get_root_url function from route_utils which is critical
    for the /run/ endpoint fix. Includes 8 parametrized test cases.
    """
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "pytest", "httpx", "requests"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "test/test_routes.py::test_get_root_url", "-x", "--no-header", "-q"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"get_root_url tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_get_root_url_headers():
    """Repo's get_root_url_headers unit tests pass (pass_to_pass).

    Tests get_root_url with various X-Forwarded headers (16 parametrized cases).
    Critical for proper root URL calculation in the /run/ endpoint context.
    """
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "pytest", "httpx", "requests"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "test/test_routes.py::test_get_root_url_headers", "-x", "--no-header", "-q"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"get_root_url_headers tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_get_api_call_path():
    """Repo's get_api_call_path unit tests pass (pass_to_pass).

    Tests the get_api_call_path function used for API route path extraction.
    Includes 9 parametrized test cases covering queue/join and call endpoints.
    """
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "pytest", "httpx", "requests"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "test/test_routes.py::test_get_api_call_path_queue_join", "-x", "--no-header", "-q"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"get_api_call_path tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_get_api_call_path_generic_call():
    """Repo's get_api_call_path_generic_call unit tests pass (pass_to_pass).

    Tests get_api_call_path for the /call/ endpoints (8 parametrized cases).
    """
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "pytest", "httpx", "requests"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "test/test_routes.py::test_get_api_call_path_generic_call", "-x", "--no-header", "-q"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"get_api_call_path_generic_call tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_get_request_origin():
    """Repo's get_request_origin unit tests pass (pass_to_pass).

    Tests the get_request_origin function with various headers (4 parametrized cases).
    Used for determining request origin in API endpoints.
    """
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "pytest", "httpx", "requests"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "test/test_routes.py::test_get_request_origin_with_headers", "-x", "--no-header", "-q"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"get_request_origin tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_starts_with_protocol():
    """Repo's starts_with_protocol unit tests pass (pass_to_pass).

    Tests URL protocol detection used for security checks in route_utils.
    Includes 16 parametrized test cases.
    """
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "pytest"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "test/test_routes.py::test_starts_with_protocol", "-x", "--no-header", "-q"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"starts_with_protocol tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_compare_passwords_securely():
    """Repo's compare_passwords_securely unit tests pass (pass_to_pass).

    Tests constant-time password comparison from route_utils.
    """
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "pytest"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "test/test_routes.py::test_compare_passwords_securely", "-x", "--no-header", "-q"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"compare_passwords_securely tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_slugify():
    """Repo's slugify unit tests pass (pass_to_pass).

    Tests the slugify utility function from route_utils.
    """
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "pytest"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "test/test_routes.py::test_slugify", "-x", "--no-header", "-q"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"slugify tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_predict_run_endpoint_passes_actual_path():
    """When hitting /gradio_api/run/<name>, predict must pass the actual request
    URL path to get_root_url, not a hardcoded /gradio_api/api/<name>."""
    r = _run_python("""
import gradio as gr
from gradio import route_utils
from unittest.mock import patch
from starlette.testclient import TestClient

captured = []
original_fn = route_utils.get_root_url

def spy(*args, **kwargs):
    route_path = kwargs.get('route_path') or (args[1] if len(args) > 1 else None)
    captured.append(str(route_path))
    return original_fn(*args, **kwargs)

with gr.Blocks() as demo:
    text = gr.Textbox()
    btn = gr.Button()
    btn.click(lambda x: x, text, text, api_name="echo")

app = gr.routes.App.create_app(demo)

with patch.object(route_utils, 'get_root_url', side_effect=spy):
    client = TestClient(app)
    response = client.post("/gradio_api/run/echo", json={"data": ["hello"]})

assert response.status_code == 200, f"Status {response.status_code}: {response.text[:300]}"

has_run = any('/run/echo' in rp for rp in captured)
assert has_run, f"Expected route_path containing /run/echo but got: {captured}"
print("PASS")
""")
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_predict_run_endpoint_varied_api_name():
    """Same fix verified with a different api_name to prevent hardcoding."""
    r = _run_python("""
import gradio as gr
from gradio import route_utils
from unittest.mock import patch
from starlette.testclient import TestClient

captured = []
original_fn = route_utils.get_root_url

def spy(*args, **kwargs):
    route_path = kwargs.get('route_path') or (args[1] if len(args) > 1 else None)
    captured.append(str(route_path))
    return original_fn(*args, **kwargs)

with gr.Blocks() as demo:
    t1 = gr.Textbox()
    t2 = gr.Textbox()
    btn = gr.Button()
    btn.click(lambda x: x.upper(), t1, t2, api_name="shout")

app = gr.routes.App.create_app(demo)

with patch.object(route_utils, 'get_root_url', side_effect=spy):
    client = TestClient(app)
    response = client.post("/gradio_api/run/shout", json={"data": ["world"]})

assert response.status_code == 200, f"Status {response.status_code}: {response.text[:300]}"

has_run = any('/run/shout' in rp for rp in captured)
assert has_run, f"Expected route_path containing /run/shout but got: {captured}"
print("PASS")
""")
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_root_url_correct_for_run_endpoint():
    """The root URL produced by get_root_url must not contain the /run/ path.
    On the buggy commit, the path is not stripped and the root URL includes
    /gradio_api/run/<name>, breaking file URLs in responses."""
    r = _run_python("""
import gradio as gr
from gradio import route_utils
from unittest.mock import patch
from starlette.testclient import TestClient

results = []
original_fn = route_utils.get_root_url

def spy(*args, **kwargs):
    result = original_fn(*args, **kwargs)
    results.append(result)
    return result

with gr.Blocks() as demo:
    text = gr.Textbox()
    btn = gr.Button()
    btn.click(lambda x: x, text, text, api_name="ping")

app = gr.routes.App.create_app(demo)

with patch.object(route_utils, 'get_root_url', side_effect=spy):
    client = TestClient(app)
    response = client.post("/gradio_api/run/ping", json={"data": ["test"]})

assert response.status_code == 200, f"Status {response.status_code}: {response.text[:300]}"

assert results, "get_root_url was never called — predict may be stubbed"
bad = [r for r in results if '/run/ping' in r]
assert not bad, f"Root URL still contains /run/ping route path: {bad}"
print("PASS")
""")
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_predict_api_endpoint_root_url():
    """The /gradio_api/api/<name> endpoint must also produce a correct root URL.
    This guards against a wrong fix that hardcodes /run/ instead of using
    request.url.path."""
    r = _run_python("""
import gradio as gr
from gradio import route_utils
from unittest.mock import patch
from starlette.testclient import TestClient

results = []
original_fn = route_utils.get_root_url

def spy(*args, **kwargs):
    result = original_fn(*args, **kwargs)
    results.append(result)
    return result

with gr.Blocks() as demo:
    text = gr.Textbox()
    btn = gr.Button()
    btn.click(lambda x: x, text, text, api_name="echo")

app = gr.routes.App.create_app(demo)

with patch.object(route_utils, 'get_root_url', side_effect=spy):
    client = TestClient(app)
    response = client.post("/gradio_api/api/echo", json={"data": ["hello"]})

assert response.status_code == 200, f"Status {response.status_code}: {response.text[:300]}"

assert results, "get_root_url was never called — predict may be stubbed"
bad = [r for r in results if '/api/echo' in r]
assert not bad, f"Root URL contains /api/echo route path: {bad}"
print("PASS")
""")
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
    assert "PASS" in r.stdout
