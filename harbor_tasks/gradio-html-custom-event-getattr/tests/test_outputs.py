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
