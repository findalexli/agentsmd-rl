"""
Task: slime-megatron-lr-scheduler-duplicate
Repo: THUDM/slime @ 0988f0f4a0ab55d1bb3ce6285a597d912144fa80
PR:   1775

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import textwrap
from pathlib import Path
from unittest.mock import MagicMock

REPO = "/workspace/slime"
TARGET = f"{REPO}/slime/backends/megatron_utils/model.py"


def _parse_function(name="initialize_model_and_optimizer"):
    """Parse TARGET and return the AST node for the named function."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node, source
    raise AssertionError(f"Function {name!r} not found in {TARGET}")


def _get_calls(func_node):
    """Return set of function/method names called inside a function node."""
    calls = set()
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                calls.add(func.id)
            elif isinstance(func, ast.Attribute):
                calls.add(func.attr)
    return calls


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """model.py must parse without syntax errors."""
    r = subprocess.run(
        ["python3", "-c", f"import ast; ast.parse(open('{TARGET}').read())"],
        capture_output=True, timeout=10,
    )
    assert r.returncode == 0, f"Syntax error:\n{r.stderr.decode()}"


# [static] pass_to_pass
# AST-only because: function requires Megatron distributed stack (torch, CUDA, NCCL)
def test_not_stub():
    """initialize_model_and_optimizer must have substantial body (not a stub)."""
    func_node, _ = _parse_function()

    meaningful = 0
    for stmt in ast.walk(func_node):
        if isinstance(stmt, (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.Return,
                              ast.If, ast.For, ast.While, ast.With, ast.Try,
                              ast.Assert, ast.Raise)):
            meaningful += 1
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            meaningful += 1

    calls = _get_calls(func_node)
    func_lines = func_node.end_lineno - func_node.lineno + 1

    assert meaningful >= 8, f"Function too simple: {meaningful} statements (need >= 8)"
    assert len(calls) >= 4, f"Too few distinct calls: {len(calls)} (need >= 4)"
    assert func_lines >= 15, f"Function too short: {func_lines} lines (need >= 15)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: function requires Megatron distributed stack (torch, CUDA, NCCL)
def test_no_unconditional_scheduler_step():
    """The redundant opt_param_scheduler.step() call must not appear unconditionally.

    The bug: after load_checkpoint() already restores scheduler state,
    an extra .step(increment=...) call fast-forwards the LR to min_lr.
    Fix: remove the unconditional .step() call entirely.
    """
    func_node, _ = _parse_function()

    SCHEDULER_NAMES = {"opt_param_scheduler", "scheduler", "param_scheduler", "lr_scheduler"}

    class UnconditionalStepFinder(ast.NodeVisitor):
        def __init__(self):
            self.found = False
            self.if_depth = 0

        def visit_If(self, node):
            self.if_depth += 1
            self.generic_visit(node)
            self.if_depth -= 1

        def visit_Call(self, node):
            if self.if_depth == 0 and isinstance(node.func, ast.Attribute):
                if (node.func.attr == "step" and
                    isinstance(node.func.value, ast.Name) and
                    node.func.value.id in SCHEDULER_NAMES):
                    self.found = True
            self.generic_visit(node)

    checker = UnconditionalStepFinder()
    checker.visit(func_node)
    assert not checker.found, (
        "opt_param_scheduler.step() is still called unconditionally — "
        "this causes duplicate LR fast-forwarding on resume"
    )


# [pr_diff] fail_to_pass
# AST-only because: function requires Megatron distributed stack (torch, CUDA, NCCL)
def test_no_step_between_clear_memory_and_return():
    """After the second clear_memory(), function should proceed to return.

    The bug inserts a scheduler.step() call between clear_memory() and the
    return statement. The fix removes it so the function goes straight from
    clear_memory() to return.
    """
    func_node, source = _parse_function()
    body = func_node.body

    last_clear_idx = None
    return_idx = None
    for i, stmt in enumerate(body):
        if (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)):
            call = stmt.value
            if isinstance(call.func, ast.Name) and call.func.id == "clear_memory":
                last_clear_idx = i
            elif isinstance(call.func, ast.Attribute) and call.func.attr == "clear_memory":
                last_clear_idx = i
        if isinstance(stmt, ast.Return):
            return_idx = i

    assert last_clear_idx is not None, "clear_memory() call not found"
    assert return_idx is not None, "return statement not found"
    assert return_idx > last_clear_idx, "return must come after clear_memory()"

    for i in range(last_clear_idx + 1, return_idx):
        stmt = body[i]
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            if isinstance(call.func, ast.Attribute) and call.func.attr == "step":
                raise AssertionError(
                    f"Found .step() call between clear_memory() and return (line {stmt.lineno}). "
                    "This scheduler.step() duplicates restoration done by load_checkpoint()."
                )


# [pr_diff] fail_to_pass
def test_function_tail_no_scheduler_step():
    """Extract the last statements of the function and execute them with mocks.
    Verify that opt_param_scheduler.step() is NOT called.

    This is a behavioral test: we mock the scheduler and run the tail of the
    function to confirm .step() is never invoked on it.
    """
    func_node, source = _parse_function()
    body = func_node.body

    # Find the last clear_memory() and the return
    last_clear_idx = None
    for i, stmt in enumerate(body):
        if (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)):
            call = stmt.value
            if isinstance(call.func, ast.Name) and call.func.id == "clear_memory":
                last_clear_idx = i
            elif isinstance(call.func, ast.Attribute) and call.func.attr == "clear_memory":
                last_clear_idx = i

    assert last_clear_idx is not None, "clear_memory() not found"

    # Extract source lines from clear_memory() to end of function
    start_line = body[last_clear_idx].lineno
    end_line = func_node.end_lineno
    lines = source.splitlines()
    tail_lines = lines[start_line - 1:end_line]
    tail_source = textwrap.dedent("\n".join(tail_lines))

    # Wrap in a function so `return` statements are valid
    wrapped = "def _tail_fn():\n" + textwrap.indent(tail_source, "    ") + "\n_tail_fn()"

    # Set up mocks for all variables the tail might reference
    mock_scheduler = MagicMock(name="opt_param_scheduler")
    mock_model = MagicMock(name="model")
    mock_optimizer = MagicMock(name="optimizer")
    mock_args = MagicMock(name="args")
    mock_args.global_batch_size = 4

    env = {
        "clear_memory": lambda: None,
        "opt_param_scheduler": mock_scheduler,
        "param_scheduler": mock_scheduler,
        "scheduler": mock_scheduler,
        "lr_scheduler": mock_scheduler,
        "model": mock_model,
        "optimizer": mock_optimizer,
        "args": mock_args,
        "iteration": 1000,
    }

    # Execute the function tail
    exec(compile(wrapped, "<function_tail>", "exec"), env)

    # The scheduler's .step() must NOT have been called
    assert not mock_scheduler.step.called, (
        "opt_param_scheduler.step() was called in the function tail — "
        "this means the duplicate scheduler fast-forward bug is still present. "
        f"Call args: {mock_scheduler.step.call_args_list}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
# AST-only because: function requires Megatron distributed stack (torch, CUDA, NCCL)
def test_function_calls_required_functions():
    """Function must still call setup_model_and_optimizer, load_checkpoint, clear_memory."""
    func_node, _ = _parse_function()
    calls = _get_calls(func_node)

    required = ["setup_model_and_optimizer", "load_checkpoint", "clear_memory"]
    for name in required:
        assert name in calls, f"Required call {name!r} is missing from function"


# [pr_diff] pass_to_pass
# AST-only because: function requires Megatron distributed stack (torch, CUDA, NCCL)
def test_return_tuple_has_four_elements():
    """Return value must be a tuple with model, optimizer, scheduler, iteration."""
    func_node, _ = _parse_function()

    found_good_return = False
    for node in ast.walk(func_node):
        if isinstance(node, ast.Return) and node.value is not None:
            val = node.value
            if isinstance(val, ast.Tuple) and len(val.elts) >= 4:
                found_good_return = True
                break

    assert found_good_return, "Function must return a tuple with at least 4 elements"
