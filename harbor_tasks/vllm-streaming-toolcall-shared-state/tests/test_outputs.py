"""
Task: vllm-streaming-toolcall-shared-state
Repo: vllm-project/vllm @ cc06b4e86b2beb04fbee3e6d9167cc97f1491b1f
PR:   38158

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/vllm"
TARGET = f"{REPO}/vllm/entrypoints/openai/chat_completion/serving.py"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess within the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _find_method(tree, name="chat_completion_stream_generator"):
    """Find an async method by name in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == name:
            return node
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse without syntax errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests (subprocess-executed)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_token_ids_creates_independent_lists():
    """all_previous_token_ids must create independent lists per choice — mutating one must not affect others."""
    r = _run_py("""
import ast, copy
from pathlib import Path

source = Path("vllm/entrypoints/openai/chat_completion/serving.py").read_text()
tree = ast.parse(source)

method = None
for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == "chat_completion_stream_generator":
        method = node
        break
assert method is not None, "chat_completion_stream_generator not found"

expr = None
for node in ast.walk(method):
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
        target = node.target if isinstance(node, ast.AnnAssign) else (node.targets[0] if node.targets else None)
        value = node.value if isinstance(node, ast.AnnAssign) else node.value
        if isinstance(target, ast.Name) and target.id == "all_previous_token_ids" and value is not None:
            expr = ast.get_source_segment(source, value)
            break
assert expr is not None, "all_previous_token_ids assignment not found"

for num_choices in (2, 4, 7):
    result = eval(expr, {"num_choices": num_choices, "copy": copy, "list": list, "range": range, "__builtins__": __builtins__})
    assert isinstance(result, list) and len(result) == num_choices, (
        f"Expected list of length {num_choices}, got {type(result).__name__}"
    )
    for i in range(num_choices):
        for j in range(i + 1, num_choices):
            assert result[i] is not result[j], f"result[{i}] is result[{j}] — shared reference"
    result[0].append(99999)
    for k in range(1, num_choices):
        assert 99999 not in result[k], f"Appending to result[0] mutated result[{k}]"

print("PASS")
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_tool_parsers_creates_independent_instances():
    """tool_parsers must create independent parser instances per choice — mutating one must not affect others."""
    r = _run_py("""
import ast, copy
from pathlib import Path

source = Path("vllm/entrypoints/openai/chat_completion/serving.py").read_text()
tree = ast.parse(source)

method = None
for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == "chat_completion_stream_generator":
        method = node
        break
assert method is not None, "chat_completion_stream_generator not found"

expr = None
for node in ast.walk(method):
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
        target = node.target if isinstance(node, ast.AnnAssign) else (node.targets[0] if node.targets else None)
        value = node.value if isinstance(node, ast.AnnAssign) else node.value
        if isinstance(target, ast.Name) and target.id == "tool_parsers" and value is not None:
            seg = ast.get_source_segment(source, value)
            if seg and "None" not in seg:
                expr = seg
                break
assert expr is not None, "tool_parsers assignment not found"

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
        f"Expected list of length {num_choices}, got {type(result).__name__}"
    )
    for i in range(num_choices):
        for j in range(i + 1, num_choices):
            assert result[i] is not result[j], f"tool_parsers[{i}] is tool_parsers[{j}] — shared reference"
    result[0].buffer.append("corrupt")
    for k in range(1, num_choices):
        assert "corrupt" not in result[k].buffer, f"Mutating parser[0].buffer affected parser[{k}]"

print("PASS")
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_sibling_methods_preserved():
    """Key sibling methods must still exist — file must not be truncated."""
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
