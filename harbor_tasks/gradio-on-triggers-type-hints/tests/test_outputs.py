"""
Task: gradio-on-triggers-type-hints
Repo: gradio-app/gradio @ 429a9fad5207fb27648d860a4802ff52a5b38746
PR:   12984

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Fix: Define a `Trigger` type alias in events.py that accepts both
`EventListenerCallable` and `Callable[..., Dependency]` (bound component
event methods), then update gr.on() and gr.render() to use it.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/gradio"
EVENTS_PY = Path(REPO) / "gradio/events.py"
RENDERABLE_PY = Path(REPO) / "gradio/renderable.py"

# AST-only because: these are pure type annotation changes; runtime behavior
# is identical before/after the fix — only static type checkers see the diff.


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / import checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both modified files parse without errors."""
    for path in [EVENTS_PY, RENDERABLE_PY]:
        source = path.read_text()
        ast.parse(source, filename=str(path))


# [static] pass_to_pass
def test_event_listener_callable_still_importable():
    """EventListenerCallable remains importable from gradio.events (backward compat)."""
    # AST-only because: checking that the name still exists, not runtime behavior
    source = EVENTS_PY.read_text()
    tree = ast.parse(source)
    names = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
    }
    # Also check via assignment targets
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "EventListenerCallable":
                    return  # found
    # Also check for AnnAssign or augmented assigns
    for node in ast.walk(tree):
        if isinstance(node, (ast.AnnAssign,)):
            if isinstance(node.target, ast.Name) and node.target.id == "EventListenerCallable":
                return
    assert "EventListenerCallable" in source, \
        "EventListenerCallable has been removed from events.py — backward compat broken"


# [static] pass_to_pass
def test_not_stub():
    """Modified files have real logic, not stubs."""
    for path, min_lines in [(EVENTS_PY, 200), (RENDERABLE_PY, 50)]:
        source = path.read_text()
        n_lines = len(source.splitlines())
        assert n_lines >= min_lines, f"{path.name}: only {n_lines} lines (expected {min_lines}+)"
        tree = ast.parse(source)
        n_funcs = sum(
            1 for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
        assert n_funcs >= 3, f"{path.name}: only {n_funcs} functions (expected 3+)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural type-annotation checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_trigger_type_alias_defined():
    """A `Trigger` type alias must be defined in gradio/events.py.

    Base commit: no `Trigger` name anywhere in events.py.
    Fixed commit: `Trigger = Union[EventListenerCallable, Callable[..., Dependency]]`
    """
    # AST-only because: type alias definition is static; runtime doesn't use it
    source = EVENTS_PY.read_text()
    tree = ast.parse(source)

    # Walk all assignment targets looking for 'Trigger = ...'
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "Trigger":
                    return  # found — test passes
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "Trigger":
                return

    raise AssertionError(
        "No `Trigger` type alias found in gradio/events.py. "
        "Expected: `Trigger = Union[EventListenerCallable, Callable[..., Dependency]]`"
    )


# [pr_diff] fail_to_pass
def test_trigger_includes_callable_returning_dependency():
    """The Trigger alias must accept Callable[..., Dependency] (not just EventListenerCallable).

    Base commit: only EventListenerCallable exists (no Trigger alias).
    Fixed commit: Trigger = Union[EventListenerCallable, Callable[..., Dependency]].
    """
    # AST-only because: type alias is static
    source = EVENTS_PY.read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "Trigger":
                    rhs = ast.unparse(node.value)
                    # Must reference both EventListenerCallable and Callable
                    assert "EventListenerCallable" in rhs, \
                        f"Trigger definition does not include EventListenerCallable: {rhs}"
                    assert "Callable" in rhs, \
                        f"Trigger definition does not include Callable[...]: {rhs}"
                    return

    raise AssertionError("Trigger alias not found in gradio/events.py")


# [pr_diff] fail_to_pass
def test_on_function_triggers_uses_trigger_type():
    """gr.on() triggers parameter annotation must use Trigger, not EventListenerCallable.

    Base commit: triggers: Sequence[EventListenerCallable] | EventListenerCallable | None
    Fixed commit: triggers: Sequence[Trigger] | Trigger | None
    """
    # AST-only because: annotation change is static (no runtime behavior change)
    source = EVENTS_PY.read_text()
    tree = ast.parse(source)

    def _get_triggers_annotation(func_node):
        all_args = (
            func_node.args.posonlyargs
            + func_node.args.args
            + func_node.args.kwonlyargs
        )
        for arg in all_args:
            if arg.arg == "triggers" and arg.annotation is not None:
                return ast.unparse(arg.annotation)
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "on":
            annotation = _get_triggers_annotation(node)
            if annotation is None:
                raise AssertionError("on() has no `triggers` parameter annotation")
            assert "Trigger" in annotation, \
                f"on() triggers annotation does not use Trigger type: {annotation!r}"
            assert "EventListenerCallable" not in annotation, \
                f"on() triggers annotation still uses EventListenerCallable: {annotation!r}"
            return

    raise AssertionError("No `on()` function found in gradio/events.py")


# [pr_diff] fail_to_pass
def test_render_function_triggers_uses_trigger_type():
    """gr.render() triggers parameter annotation must use Trigger, not EventListenerCallable.

    Base commit: triggers: Sequence[EventListenerCallable] | EventListenerCallable | None
    Fixed commit: triggers: Sequence[Trigger] | Trigger | None
    """
    # AST-only because: annotation change is static (no runtime behavior change)
    source = RENDERABLE_PY.read_text()
    tree = ast.parse(source)

    def _get_triggers_annotation(func_node):
        all_args = (
            func_node.args.posonlyargs
            + func_node.args.args
            + func_node.args.kwonlyargs
        )
        for arg in all_args:
            if arg.arg == "triggers" and arg.annotation is not None:
                return ast.unparse(arg.annotation)
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "render":
            annotation = _get_triggers_annotation(node)
            if annotation is None:
                continue  # this render() has no triggers param, skip
            assert "Trigger" in annotation, \
                f"render() triggers annotation does not use Trigger type: {annotation!r}"
            assert "EventListenerCallable" not in annotation, \
                f"render() triggers annotation still uses EventListenerCallable: {annotation!r}"
            return

    raise AssertionError("No `render()` function with triggers param found in gradio/renderable.py")


# [pr_diff] fail_to_pass
def test_renderable_imports_trigger_not_event_listener_callable():
    """renderable.py must import Trigger (not EventListenerCallable) from gradio.events.

    Base commit: `from gradio.events import EventListenerCallable`
    Fixed commit: `from gradio.events import Trigger`
    """
    # AST-only because: TYPE_CHECKING import is never executed at runtime
    source = RENDERABLE_PY.read_text()
    tree = ast.parse(source)

    found_trigger_import = False
    found_event_listener_callable_import = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "gradio.events":
            imported_names = [alias.name for alias in node.names]
            if "Trigger" in imported_names:
                found_trigger_import = True
            if "EventListenerCallable" in imported_names:
                found_event_listener_callable_import = True

    assert found_trigger_import, \
        "renderable.py does not import `Trigger` from gradio.events"
    assert not found_event_listener_callable_import, \
        "renderable.py still imports `EventListenerCallable` from gradio.events (should import Trigger)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:43 @ 429a9fad5207fb27648d860a4802ff52a5b38746
def test_ruff_format():
    """Modified Python files pass ruff formatting check (AGENTS.md line 43)."""
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "ruff"],
        capture_output=True, timeout=120,
    )
    for rel in ["gradio/events.py", "gradio/renderable.py"]:
        r = subprocess.run(
            [sys.executable, "-m", "ruff", "format", "--check", rel],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, \
            f"ruff format check failed for {rel}:\n{r.stdout}\n{r.stderr}"
