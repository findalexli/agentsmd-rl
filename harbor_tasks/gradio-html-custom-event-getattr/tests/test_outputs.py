"""
Task: gradio-html-custom-event-getattr
Repo: gradio-app/gradio @ d610464e0eff5f200543c6bbc5fac616b1620b1e
PR:   12967

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/gradio"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    r = subprocess.run(
        ["python3", "-c", "import py_compile; py_compile.compile('gradio/components/html.py', doraise=True)"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in html.py:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_custom_event_attribute_access():
    """Custom event name in js_on_load can be accessed as a callable attribute."""
    r = subprocess.run(
        ["python3", "-c", """
import gradio as gr

with gr.Blocks():
    h = gr.HTML(
        js_on_load='''
        document.addEventListener('keydown', (e) => {
            trigger('keypress', {key: e.key});
        });
        '''
    )
    listener = h.keypress
    assert callable(listener), f"Expected callable, got {type(listener)}"

    # Also test with a different event name / quote style
    h2 = gr.HTML(js_on_load='trigger("my_custom_evt", {})')
    listener2 = h2.my_custom_evt
    assert callable(listener2), f"Expected callable for double-quoted event, got {type(listener2)}"
"""],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Custom event attribute access failed:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_custom_event_listener_wiring():
    """Custom event listener can be wired to a Python handler function."""
    r = subprocess.run(
        ["python3", "-c", """
import gradio as gr

with gr.Blocks() as demo:
    h = gr.HTML(
        js_on_load='''
        document.addEventListener('keydown', (e) => {
            trigger('keypress', {key: e.key});
        });
        '''
    )
    tb = gr.Textbox()
    dep = h.keypress(lambda: 'test', None, tb)
    assert dep is not None, "Wiring returned None — listener not connected"

    # Wire a second custom event on a different component
    h2 = gr.HTML(js_on_load="trigger('hover_custom', {x: 1})")
    tb2 = gr.Textbox()
    dep2 = h2.hover_custom(lambda: 'hovered', None, tb2)
    assert dep2 is not None, "Second custom event wiring failed"
"""],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Custom event listener wiring failed:\n{r.stderr.decode()}"


# [pr_diff] pass_to_pass
def test_nonexistent_event_raises():
    """AttributeError is raised for an event name NOT present in js_on_load."""
    r = subprocess.run(
        ["python3", "-c", """
import gradio as gr

with gr.Blocks():
    h = gr.HTML(js_on_load="trigger('click_custom')")
    try:
        _ = h.totally_made_up_event
        raise AssertionError("Should have raised AttributeError")
    except AttributeError:
        pass  # expected

    # Also check with no js_on_load at all
    h2 = gr.HTML('<p>plain</p>')
    try:
        _ = h2.some_event
        raise AssertionError("Should have raised AttributeError for HTML without js_on_load")
    except AttributeError:
        pass  # expected
"""],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"AttributeError test failed:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_multiple_custom_events():
    """Multiple custom events can be wired on the same HTML component."""
    r = subprocess.run(
        ["python3", "-c", """
import gradio as gr

with gr.Blocks() as demo:
    h = gr.HTML(
        js_on_load='''
        trigger('my_event_a', {});
        trigger('my_event_b', {});
        trigger('my_event_c', {val: 42});
        '''
    )
    tb = gr.Textbox()
    dep_a = h.my_event_a(lambda: 'a', None, tb)
    dep_b = h.my_event_b(lambda: 'b', None, tb)
    dep_c = h.my_event_c(lambda: 'c', None, tb)
    assert dep_a is not None, "Event A wiring failed"
    assert dep_b is not None, "Event B wiring failed"
    assert dep_c is not None, "Event C wiring failed"
"""],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Multiple custom events test failed:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_builtin_events_still_work():
    """Built-in events (click, change) still work on HTML component."""
    r = subprocess.run(
        ["python3", "-c", """
import gradio as gr

with gr.Blocks() as demo:
    h = gr.HTML('<p>test</p>')
    tb = gr.Textbox()
    dep = h.click(lambda: 'clicked', None, tb)
    assert dep is not None, "Built-in click event wiring failed"

    dep2 = h.change(lambda: 'changed', None, tb)
    assert dep2 is not None, "Built-in change event wiring failed"
"""],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Built-in events test failed:\n{r.stderr.decode()}"


# [pr_diff] pass_to_pass
def test_html_basic_construction():
    """HTML component can be constructed and produces valid config."""
    r = subprocess.run(
        ["python3", "-c", """
import gradio as gr

with gr.Blocks():
    h = gr.HTML('<p>Hello</p>')
    config = h.get_config()
    assert 'component_class_name' in config, f"Missing component_class_name in config: {config.keys()}"
    assert isinstance(config['component_class_name'], str), "component_class_name should be a string"

    # Also check HTML with js_on_load still constructs fine
    h2 = gr.HTML(js_on_load="console.log('hi')")
    config2 = h2.get_config()
    assert 'component_class_name' in config2
"""],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"HTML construction test failed:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:43 @ d610464e0eff5f200543c6bbc5fac616b1620b1e
def test_ruff_lint():
    """Python code is formatted with ruff — no new errors introduced (AGENTS.md line 43)."""
    # Only check for import sorting and basic errors, ignoring pre-existing long lines
    r = subprocess.run(
        ["ruff", "check", "gradio/components/html.py", "--select", "E,W,I", "--ignore", "E501", "--quiet"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"ruff lint failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — from .github/workflows/test-python.yml
def test_ruff_format():
    """Modified file passes ruff format check (repo CI)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "gradio/components/html.py", "--quiet"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass — from .github/workflows/test-python.yml
def test_repo_html_component_tests():
    """HTML component unit tests pass (repo CI test-python.yml)."""
    # Install pytest if not already available
    subprocess.run(["pip", "install", "pytest", "pytest-asyncio", "-q"], capture_output=True)
    r = subprocess.run(
        ["python", "-m", "pytest", "test/components/test_html.py", "-v", "--tb=short"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"HTML component tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — gradio import/initialization
def test_gradio_imports():
    """Gradio package imports correctly (basic smoke test from repo CI)."""
    r = subprocess.run(
        ["python", "-c", "import gradio; print(gradio.__version__)"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Gradio import failed:\n{r.stderr}"


# [repo_tests] pass_to_pass — from scripts/lint_backend.sh (CI test-python.yml)
def test_repo_lint_backend():
    """Backend lint script passes on modified file (repo CI)."""
    # The repo CI runs: ./scripts/lint_backend.sh which checks gradio, test, client
    # We run ruff check specifically on the modified file to avoid pre-existing issues
    r = subprocess.run(
        ["python", "-m", "ruff", "check", "gradio/components/html.py", "--quiet"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Backend lint failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — from test/test_events.py (events system)
def test_repo_events_unit_tests():
    """Event system unit tests pass (repo CI) — tests that don't need server."""
    # These test the event listener system that custom events extend
    # Only run specific test classes that don't launch the app
    subprocess.run(["pip", "install", "pytest", "pytest-asyncio", "-q"], capture_output=True)
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_events.py::TestEvent::test_clear_event", "test/test_events.py::TestEvent::test_consecutive_events", "test/test_events.py::TestEvent::test_on_listener", "test/test_events.py::TestEvent::test_load_chaining", "test/test_events.py::TestEvent::test_load_chaining_reuse", "test/test_events.py::TestEventErrors", "test/test_events.py::test_event_pyi_file_matches_source_code", "-v", "--tb=short"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Events unit tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — from test/test_blocks.py (blocks config tests)
def test_repo_blocks_config_tests():
    """Blocks config tests pass (repo CI) — test event wiring in blocks."""
    # Tests Blocks configuration and event wiring without launching server
    subprocess.run(["pip", "install", "pytest", "pytest-asyncio", "-q"], capture_output=True)
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_blocks.py::TestBlocksMethods::test_load_from_config_with_blocks_events", "-v", "--tb=short"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Blocks events config test failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — basic gradio functionality smoke test
def test_repo_gradio_version():
    """Gradio version can be retrieved (repo CI smoke test)."""
    r = subprocess.run(
        ["python", "-c", "import gradio; print(gradio.__version__)"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Gradio version check failed:\n{r.stderr}"
    assert len(r.stdout.strip()) > 0, "Gradio version is empty"


# [repo_tests] pass_to_pass — from test/test_component_props.py (CI tests)
def test_repo_component_props():
    """Component props tests pass (repo CI) — tests component property handling."""
    subprocess.run(["pip", "install", "pytest", "pytest-asyncio", "-q"], capture_output=True)
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_component_props.py", "-v", "--tb=short"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Component props tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — from test/test_blocks.py config tests (CI)
def test_repo_blocks_load_config():
    """Blocks load from config test passes (repo CI test-python.yml)."""
    subprocess.run(["pip", "install", "pytest", "pytest-asyncio", "-q"], capture_output=True)
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_blocks.py::TestBlocksMethods::test_load_from_config", "-v", "--tb=short"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Blocks load config test failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — from test/test_blocks.py partial fn config tests (CI)
def test_repo_blocks_partial_config():
    """Blocks partial function in config test passes (repo CI test-python.yml)."""
    subprocess.run(["pip", "install", "pytest", "pytest-asyncio", "-q"], capture_output=True)
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_blocks.py::TestBlocksMethods::test_partial_fn_in_config", "-v", "--tb=short"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Blocks partial config test failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — from client/python/test (CI test-python.yml)
def test_repo_client_documentation():
    """Client documentation tests pass (repo CI test-python.yml)."""
    subprocess.run(["pip", "install", "pytest", "pytest-asyncio", "-q"], capture_output=True)
    r = subprocess.run(
        ["python", "-m", "pytest", "client/python/test/test_documentation.py", "-v", "--tb=short"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Client documentation tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — from test/components/test_button.py (CI)
def test_repo_button_component():
    """Button component tests pass (repo CI test-python.yml)."""
    subprocess.run(["pip", "install", "pytest", "pytest-asyncio", "-q"], capture_output=True)
    r = subprocess.run(
        ["python", "-m", "pytest", "test/components/test_button.py", "-v", "--tb=short"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Button component tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — function types documented from test_blocks.py (CI)
def test_repo_function_types_documented():
    """Function types documented in config test passes (repo CI)."""
    subprocess.run(["pip", "install", "pytest", "pytest-asyncio", "-q"], capture_output=True)
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_blocks.py::TestBlocksMethods::test_function_types_documented_in_config", "-v", "--tb=short"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Function types documented test failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — from test/test_events.py clear event test (CI)
def test_repo_events_clear():
    """Event clear test passes (repo CI) — tests basic event system."""
    subprocess.run(["pip", "install", "pytest", "pytest-asyncio", "-q"], capture_output=True)
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_events.py::TestEvent::test_clear_event", "-v", "--tb=short"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Event clear test failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — from test/test_events.py consecutive events (CI)
def test_repo_events_consecutive():
    """Event consecutive/chaining test passes (repo CI test-python.yml)."""
    subprocess.run(["pip", "install", "pytest", "pytest-asyncio", "-q"], capture_output=True)
    r = subprocess.run(
        ["python", "-m", "pytest", "test/test_events.py::TestEvent::test_consecutive_events", "-v", "--tb=short"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Event consecutive test failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"
