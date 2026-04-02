"""
Task: vllm-streaming-toolcall-shared-state
Repo: vllm-project/vllm @ cc06b4e86b2beb04fbee3e6d9167cc97f1491b1f
PR:   38158

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import copy
from pathlib import Path

REPO = "/workspace/vllm"
TARGET = f"{REPO}/vllm/entrypoints/openai/chat_completion/serving.py"


def _find_method(tree, name="chat_completion_stream_generator"):
    """Find an async method by name in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == name:
            return node
    return None


def _find_assignment_expr(source, method_node, var_name, exclude_none=False):
    """Find the RHS expression string for a variable assignment within a method."""
    for node in ast.walk(method_node):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            target = node.target if isinstance(node, ast.AnnAssign) else (
                node.targets[0] if node.targets else None
            )
            value = node.value if isinstance(node, ast.AnnAssign) else node.value
            if isinstance(target, ast.Name) and target.id == var_name and value is not None:
                seg = ast.get_source_segment(source, value)
                if seg and (not exclude_none or "None" not in seg):
                    return seg
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse without syntax errors."""
    # AST-only because: syntax gate — intentionally structural
    source = Path(TARGET).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_token_ids_creates_independent_lists():
    """all_previous_token_ids must be independent lists — mutating one must not affect others."""
    # AST-only because: vllm requires torch/CUDA — extract assignment expr and eval behaviorally
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    method = _find_method(tree)
    assert method is not None, "chat_completion_stream_generator method not found"

    expr = _find_assignment_expr(source, method, "all_previous_token_ids")
    assert expr is not None, "all_previous_token_ids assignment not found in method"

    for num_choices in (2, 4, 7):
        result = eval(expr, {
            "num_choices": num_choices, "copy": copy,
            "list": list, "range": range, "__builtins__": __builtins__,
        })
        assert isinstance(result, list) and len(result) == num_choices, (
            f"Expected list of length {num_choices}, got {type(result).__name__} "
            f"len={len(result) if isinstance(result, list) else 'N/A'}"
        )
        # Identity: each element must be a distinct object
        for i in range(num_choices):
            for j in range(i + 1, num_choices):
                assert result[i] is not result[j], (
                    f"result[{i}] is result[{j}] — shared reference"
                )
        # Mutation: appending to one must not affect others
        result[0].append(99999)
        for k in range(1, num_choices):
            assert 99999 not in result[k], (
                f"Appending to result[0] mutated result[{k}]"
            )


# [pr_diff] fail_to_pass
def test_tool_parsers_creates_independent_instances():
    """tool_parsers must be independent parser instances — mutating one must not affect others."""
    # AST-only because: vllm requires torch/CUDA — extract assignment expr and eval behaviorally
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    method = _find_method(tree)
    assert method is not None, "chat_completion_stream_generator method not found"

    expr = _find_assignment_expr(source, method, "tool_parsers", exclude_none=True)
    assert expr is not None, "tool_parsers (non-None) assignment not found in method"

    class FakeParser:
        def __init__(self, tokenizer=None, tools=None):
            self.buffer = []

    class FakeParserFactory:
        def __call__(self, tokenizer=None, tools=None):
            return FakeParser(tokenizer, tools)

    class FakeSelf:
        tool_parser = FakeParserFactory()

    for num_choices in (2, 5):
        result = eval(expr, {
            "num_choices": num_choices,
            "self": FakeSelf(),
            "tokenizer": None,
            "request": type("R", (), {"tools": []})(),
            "copy": copy, "list": list, "range": range,
            "__builtins__": __builtins__,
        })
        assert isinstance(result, list) and len(result) == num_choices, (
            f"Expected list of length {num_choices}, got {type(result).__name__} "
            f"len={len(result) if isinstance(result, list) else 'N/A'}"
        )
        # Identity: each parser must be a distinct object
        for i in range(num_choices):
            for j in range(i + 1, num_choices):
                assert result[i] is not result[j], (
                    f"tool_parsers[{i}] is tool_parsers[{j}] — shared reference"
                )
        # Mutation: mutating one parser's state must not affect others
        result[0].buffer.append("token_from_choice_0")
        for k in range(1, num_choices):
            assert "token_from_choice_0" not in result[k].buffer, (
                f"Mutating parser[0].buffer affected parser[{k}]"
            )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_sibling_methods_preserved():
    """Key sibling methods must still exist — file must not be truncated."""
    # AST-only because: vllm requires torch/CUDA — check method existence structurally
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    expected = {
        "create_chat_completion",
        "chat_completion_stream_generator",
        "chat_completion_full_generator",
    }
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name in expected:
            found.add(node.name)
    missing = expected - found
    assert not missing, f"Missing methods: {sorted(missing)}"


# [static] pass_to_pass
def test_method_not_stub():
    """chat_completion_stream_generator must have a substantial body (not a stub)."""
    # AST-only because: vllm requires torch/CUDA — check body size structurally
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    method = _find_method(tree)
    assert method is not None, "chat_completion_stream_generator not found"
    stmt_count = sum(
        1 for child in ast.walk(method)
        if isinstance(child, (
            ast.Assign, ast.AnnAssign, ast.AugAssign,
            ast.For, ast.AsyncFor, ast.While, ast.If,
            ast.With, ast.AsyncWith, ast.Return,
            ast.Yield, ast.YieldFrom, ast.Try,
        ))
    )
    assert stmt_count >= 20, (
        f"Method body too small ({stmt_count} statements, expected >= 20)"
    )


# [pr_diff] pass_to_pass
def test_sibling_initializations_preserved():
    """Non-mutable sibling vars (added_content_delta_arr, reasoning_end_arr) must still be assigned."""
    # AST-only because: vllm requires torch/CUDA — check assignment existence structurally
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    method = _find_method(tree)
    assert method is not None, "chat_completion_stream_generator not found"
    needed = {"added_content_delta_arr", "reasoning_end_arr"}
    found = set()
    for node in ast.walk(method):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            target = node.target if isinstance(node, ast.AnnAssign) else (
                node.targets[0] if node.targets else None
            )
            if isinstance(target, ast.Name) and target.id in needed:
                found.add(target.id)
    missing = needed - found
    assert not missing, f"Missing assignments: {sorted(missing)}"
