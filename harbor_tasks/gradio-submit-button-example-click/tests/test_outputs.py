"""
Task: gradio-submit-button-example-click
Repo: gradio-app/gradio @ fe955348f24115744015d85639e170b8518b28c1
PR:   12975

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"
TARGET = Path(REPO) / "gradio" / "chat_interface.py"


def _parse_setup_events():
    """Parse _setup_events method from ChatInterface class."""
    # AST-only because: gradio requires FastAPI, httpx, PIL, pydantic, etc. — not installed in test image
    source = TARGET.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "ChatInterface":
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "_setup_events":
                    return source, tree, item
    raise AssertionError("ChatInterface._setup_events not found")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """chat_interface.py must parse as valid Python."""
    source = TARGET.read_text()
    ast.parse(source)  # raises SyntaxError if invalid


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: gradio requires FastAPI, httpx, PIL, pydantic, etc. — not installed in test image
def test_example_select_not_in_stop_triggers():
    """example_select must NOT be in _setup_stop_events event_triggers.

    The base code registers a separate handler on chatbot.example_select via
    _setup_stop_events, creating a race condition. The fix removes it.
    """
    source, _, setup_events = _parse_setup_events()

    class StopEventsFinder(ast.NodeVisitor):
        def __init__(self):
            self.trigger_elements = []

        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "_setup_stop_events":
                for kw in node.keywords:
                    if kw.arg == "event_triggers" and isinstance(kw.value, ast.List):
                        for elt in kw.value.elts:
                            self.trigger_elements.append(ast.dump(elt))
            self.generic_visit(node)

    finder = StopEventsFinder()
    finder.visit(setup_events)
    assert finder.trigger_elements, "_setup_stop_events call with event_triggers not found"
    for dump in finder.trigger_elements:
        assert "example_select" not in dump, (
            f"example_select still in _setup_stop_events event_triggers: {dump}"
        )


# [pr_diff] fail_to_pass
# AST-only because: gradio requires FastAPI, httpx, PIL, pydantic, etc. — not installed in test image
def test_submit_btn_false_in_example_chain():
    """A .then() step with submit_btn=False must exist in the example select chain.

    The fix adds submit_btn=False as a sequential .then() step so the restore
    always fires strictly after it, preventing the race condition.
    """
    source, _, setup_events = _parse_setup_events()

    class ThenSubmitBtnFinder(ast.NodeVisitor):
        def __init__(self):
            self.found = False

        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "then":
                call_dump = ast.dump(node)
                if "submit_btn" in call_dump:
                    for arg in ast.walk(node):
                        if isinstance(arg, ast.keyword) and arg.arg == "submit_btn":
                            if isinstance(arg.value, ast.Constant) and arg.value.value is False:
                                self.found = True
                        # Also check inside lambda bodies
                        if isinstance(arg, ast.Lambda):
                            lambda_dump = ast.dump(arg)
                            if "submit_btn" in lambda_dump and "False" in lambda_dump:
                                self.found = True
            self.generic_visit(node)

    finder = ThenSubmitBtnFinder()
    finder.visit(setup_events)
    assert finder.found, (
        "No .then() step with submit_btn=False found in _setup_events. "
        "The example chain needs a sequential step to set submit_btn=False."
    )


# [pr_diff] fail_to_pass
# AST-only because: gradio requires FastAPI, httpx, PIL, pydantic, etc. — not installed in test image
def test_events_to_cancel_conditional():
    """events_to_cancel must only include example event when examples actually run.

    The base code unconditionally appends example_select_event when it's not None,
    but populate-only examples (run_examples_on_click=False) shouldn't be cancelled.
    The fix adds an additional condition beyond just `is not None`.
    """
    source, _, setup_events = _parse_setup_events()

    class ConditionalAppendChecker(ast.NodeVisitor):
        def __init__(self):
            self.has_compound_condition = False

        def visit_If(self, node):
            cond_dump = ast.dump(node.test)
            body_dump = ast.dump(ast.Module(body=node.body, type_ignores=[]))
            if "example_select" in cond_dump and "events_to_cancel" in body_dump:
                if isinstance(node.test, ast.BoolOp) and isinstance(node.test.op, ast.And):
                    self.has_compound_condition = True
            self.generic_visit(node)

    checker = ConditionalAppendChecker()
    checker.visit(setup_events)
    assert checker.has_compound_condition, (
        "events_to_cancel append must use a compound condition (e.g., "
        "`is not None and flag`), not just a simple None check"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
# AST-only because: gradio requires FastAPI, httpx, PIL, pydantic, etc. — not installed in test image
def test_setup_events_not_stub():
    """_setup_events must have substantial implementation (not a stub)."""
    _, _, setup_events = _parse_setup_events()
    body_stmts = [
        s for s in setup_events.body
        if not isinstance(s, ast.Pass)
        and not (isinstance(s, ast.Expr) and isinstance(getattr(s, "value", None), ast.Constant))
    ]
    assert len(body_stmts) >= 10, (
        f"_setup_events has only {len(body_stmts)} non-trivial statements — looks like a stub"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:43 @ fe955348f24115744015d85639e170b8518b28c1
def test_ruff_formatting():
    """Python code must be formatted with ruff (AGENTS.md line 43)."""
    subprocess.run(
        ["python3", "-m", "pip", "install", "-q", "ruff"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", "gradio/chat_interface.py"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"ruff format check failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )
