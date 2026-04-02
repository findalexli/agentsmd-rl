"""
Task: gradio-browserstate-pydantic-serialization
Repo: gradio-app/gradio @ 77e7871176e50a894190ac98aa9de8fbdbf3620f
PR:   12954

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import importlib.util
import subprocess
import sys
import types
from pathlib import Path

REPO = "/workspace/gradio"
TARGET = f"{REPO}/gradio/components/browser_state.py"


def _load_browser_state():
    """Load browser_state.py with mocked heavy gradio imports.

    BrowserState's direct imports cascade through gradio.__init__ which pulls
    numpy, aiofiles, PIL, etc.  We mock the gradio package hierarchy so only
    browser_state.py is loaded.  gradio_client (lightweight) is real.
    """
    # Mock the gradio package tree that browser_state.py imports from
    gradio_mod = types.ModuleType("gradio")
    gradio_components = types.ModuleType("gradio.components")
    gradio_components_base = types.ModuleType("gradio.components.base")
    gradio_events = types.ModuleType("gradio.events")

    class _FakeComponent:
        EVENTS = []

        def __init__(self, *a, **kw):
            pass

    gradio_components_base.Component = _FakeComponent
    gradio_components_base.FormComponent = _FakeComponent
    gradio_mod.components = gradio_components
    gradio_components.base = gradio_components_base

    class _FakeEvents:
        change = "change"

    gradio_events.Events = _FakeEvents
    gradio_mod.events = gradio_events

    saved = {}
    mock_names = [
        "gradio",
        "gradio.components",
        "gradio.components.base",
        "gradio.events",
    ]
    for name in mock_names:
        saved[name] = sys.modules.get(name)

    sys.modules["gradio"] = gradio_mod
    sys.modules["gradio.components"] = gradio_components
    sys.modules["gradio.components.base"] = gradio_components_base
    sys.modules["gradio.events"] = gradio_events

    try:
        spec = importlib.util.spec_from_file_location(
            "gradio.components.browser_state", TARGET
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        # Restore original modules
        for name in mock_names:
            if saved[name] is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = saved[name]


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md line 43
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:43 @ 77e7871176e50a894190ac98aa9de8fbdbf3620f
def test_ruff_formatting():
    """Modified file must pass ruff linting (AGENTS.md: 'Python code is formatted with ruff')."""
    result = subprocess.run(
        ["ruff", "check", TARGET],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"ruff check failed on browser_state.py:\n{result.stdout}\n{result.stderr}"
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """browser_state.py must parse without syntax errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_postprocess_converts_model():
    """postprocess() must convert a Pydantic BaseModel to a dict via model_dump()."""
    from pydantic import BaseModel

    mod = _load_browser_state()
    BrowserState = mod.BrowserState

    class Person(BaseModel):
        name: str
        age: int

    state = BrowserState()

    result = state.postprocess(Person(name="Dan", age=20))
    assert isinstance(result, dict), f"Expected dict, got {type(result).__name__}"
    assert result == {"name": "Dan", "age": 20}

    # Vary inputs — different model, different values
    class Config(BaseModel):
        debug: bool
        retries: int

    result2 = state.postprocess(Config(debug=True, retries=3))
    assert isinstance(result2, dict), f"Expected dict, got {type(result2).__name__}"
    assert result2 == {"debug": True, "retries": 3}

    # Third variation
    class Item(BaseModel):
        sku: str
        price: float
        qty: int

    result3 = state.postprocess(Item(sku="ABC-123", price=9.99, qty=5))
    assert isinstance(result3, dict)
    assert result3 == {"sku": "ABC-123", "price": 9.99, "qty": 5}


# [pr_diff] fail_to_pass
def test_default_value_converts_model():
    """BrowserState(default_value=<model>) must store default_value as a dict."""
    from pydantic import BaseModel

    mod = _load_browser_state()
    BrowserState = mod.BrowserState

    class Person(BaseModel):
        name: str
        age: int

    state = BrowserState(default_value=Person(name="Alice", age=30))
    assert isinstance(state.default_value, dict), (
        f"Expected dict, got {type(state.default_value).__name__}"
    )
    assert state.default_value == {"name": "Alice", "age": 30}

    # Second variation
    class Settings(BaseModel):
        theme: str
        verbose: bool

    state2 = BrowserState(default_value=Settings(theme="dark", verbose=False))
    assert isinstance(state2.default_value, dict)
    assert state2.default_value == {"theme": "dark", "verbose": False}


# [pr_diff] fail_to_pass
def test_postprocess_nested_model():
    """Nested Pydantic models are recursively converted to dicts."""
    from pydantic import BaseModel

    mod = _load_browser_state()
    BrowserState = mod.BrowserState

    class Address(BaseModel):
        city: str
        zip_code: str

    class Person(BaseModel):
        name: str
        address: Address

    state = BrowserState()
    result = state.postprocess(
        Person(name="Dan", address=Address(city="NYC", zip_code="10001"))
    )
    assert isinstance(result, dict), f"Expected dict, got {type(result).__name__}"
    assert result == {"name": "Dan", "address": {"city": "NYC", "zip_code": "10001"}}

    # Second nested variation
    class Tag(BaseModel):
        key: str
        value: str

    class Resource(BaseModel):
        id: int
        tag: Tag

    result2 = state.postprocess(Resource(id=42, tag=Tag(key="env", value="prod")))
    assert isinstance(result2, dict)
    assert result2 == {"id": 42, "tag": {"key": "env", "value": "prod"}}


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_plain_types_passthrough():
    """Plain JSON-serializable types must pass through postprocess unchanged."""
    mod = _load_browser_state()
    BrowserState = mod.BrowserState

    state = BrowserState()

    assert state.postprocess({"key": "value"}) == {"key": "value"}
    assert state.postprocess("hello") == "hello"
    assert state.postprocess(42) == 42
    assert state.postprocess(None) is None
    assert state.postprocess([1, 2, 3]) == [1, 2, 3]
    assert state.postprocess(True) is True
    assert state.postprocess(3.14) == 3.14


# ---------------------------------------------------------------------------
# Anti-stub (static) — pass_to_pass
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_not_stub():
    """BrowserState must be instantiable and postprocess must return its input for plain values."""
    mod = _load_browser_state()
    BrowserState = mod.BrowserState

    state = BrowserState()
    assert hasattr(state, "postprocess")
    assert hasattr(state, "default_value")
    # Behavioral anti-stub: must actually return the value, not None
    assert state.postprocess("test_value") == "test_value"
    assert state.postprocess(999) == 999
