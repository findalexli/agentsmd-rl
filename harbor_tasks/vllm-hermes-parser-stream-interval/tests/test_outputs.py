"""
Task: vllm-hermes-parser-stream-interval
Repo: vllm-project/vllm @ 0ae89f18fd75c5fcac48ff711ed84464c3da5d33
PR:   38168

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import re
import types
from pathlib import Path

REPO = "/workspace/vllm"
HERMES = f"{REPO}/vllm/tool_parsers/hermes_tool_parser.py"
LONGCAT = f"{REPO}/vllm/tool_parsers/longcat_tool_parser.py"


# ---------------------------------------------------------------------------
# Helpers — extract functions/methods via AST then exec for behavioral testing
# AST-only because: vllm imports require torch/GPU libs not in the container
# ---------------------------------------------------------------------------

def _load_hermes():
    """Parse hermes_tool_parser.py once and return (source, tree)."""
    source = Path(HERMES).read_text()
    tree = ast.parse(source)
    return source, tree


def _extract_module_function(source, tree, name):
    """Extract a module-level function's source by name."""
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(source, node)
    return None


def _extract_class_method(source, tree, class_name, method_name):
    """Extract a class method's source by name."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == method_name:
                    return ast.get_source_segment(source, item)
    return None


def _build_namespace(source, tree):
    """Build a namespace with module-level helpers needed by class methods."""
    ns = {"json": json, "re": re}
    for fname in ("_partial_tag_overlap", "_is_valid_json"):
        fn_src = _extract_module_function(source, tree, fname)
        if fn_src:
            exec(fn_src, ns)
    return ns


class _MockParser:
    """Minimal mock of Hermes2ProToolParser with needed attributes."""

    def __init__(self):
        self.tool_call_start_token = "<tool_call>"
        self.tool_call_end_token = "</tool_call>"
        self._sent_content_idx = 0
        self.prev_tool_call_arr = []
        self.streamed_args_for_tool = []


def _bind_method(ns, method_src, method_name):
    """Exec method source and return a callable bound to _MockParser instances."""
    exec(method_src, ns)
    fn = ns[method_name]
    return fn


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both modified parser files must parse without syntax errors."""
    for path in [HERMES, LONGCAT]:
        source = Path(path).read_text()
        compile(source, path, "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_partial_tag_overlap():
    """_partial_tag_overlap correctly detects partial XML tags at end of text."""
    source, tree = _load_hermes()
    fn_src = _extract_module_function(source, tree, "_partial_tag_overlap")
    assert fn_src is not None, "_partial_tag_overlap function not found"

    ns = {}
    exec(fn_src, ns)
    fn = ns["_partial_tag_overlap"]

    # Varied inputs: partial <tool_call> suffixes
    assert fn("hello<tool_", "<tool_call>") == 6
    assert fn("hello<", "<tool_call>") == 1
    assert fn("hello", "<tool_call>") == 0
    assert fn("<tool_call", "<tool_call>") == 10
    assert fn("x<tool_ca", "<tool_call>") == 8

    # Partial </tool_call> suffixes
    assert fn("text</to", "</tool_call>") == 4
    assert fn("text</tool_call", "</tool_call>") == 11
    assert fn("text</", "</tool_call>") == 2

    # Edge cases
    assert fn("", "<tool_call>") == 0
    assert fn("<", "<tool_call>") == 1
    assert fn("abc", "abcd") == 3  # text is full prefix of longer tag


# [pr_diff] fail_to_pass
def test_is_valid_json():
    """_is_valid_json correctly validates complete vs incomplete JSON."""
    source, tree = _load_hermes()
    fn_src = _extract_module_function(source, tree, "_is_valid_json")
    assert fn_src is not None, "_is_valid_json function not found"

    ns = {"json": json}
    exec(fn_src, ns)
    fn = ns["_is_valid_json"]

    # Valid JSON
    assert fn('{"name": "test"}') is True
    assert fn('{"a": 1, "b": [2, 3]}') is True
    assert fn('{"nested": {"x": "y"}}') is True
    assert fn("42") is True
    assert fn('"hello"') is True

    # Invalid / incomplete JSON
    assert fn('{"incomplete": ') is False
    assert fn("") is False
    assert fn("not json") is False
    assert fn('{"key": "val",') is False
    assert fn("{") is False


# [pr_diff] fail_to_pass
def test_extract_content():
    """_extract_content returns unsent text, holds back partial <tool_call> tags."""
    source, tree = _load_hermes()
    method_src = _extract_class_method(source, tree, "Hermes2ProToolParser", "_extract_content")
    assert method_src is not None, "_extract_content method not found"

    ns = _build_namespace(source, tree)
    _bind_method(ns, method_src, "_extract_content")
    fn = ns["_extract_content"]

    # Case 1: plain text, no tool call tag
    mock = _MockParser()
    result = fn(mock, "Hello world")
    assert result == "Hello world"
    assert mock._sent_content_idx == len("Hello world")

    # Case 2: text with partial <tool_call> at end — should hold back
    mock2 = _MockParser()
    result2 = fn(mock2, "Some text<tool_")
    assert result2 is not None
    assert "<tool_" not in result2  # partial tag held back
    assert result2 == "Some text"

    # Case 3: text with complete <tool_call> — return content before it
    mock3 = _MockParser()
    result3 = fn(mock3, 'Before<tool_call>{"name":"f"}</tool_call>')
    assert result3 == "Before"

    # Case 4: calling again with no new content returns None
    mock4 = _MockParser()
    fn(mock4, "Hello")
    result4 = fn(mock4, "Hello")  # same text, nothing new
    assert result4 is None

    # Case 5: incremental content growth
    mock5 = _MockParser()
    r1 = fn(mock5, "Hi")
    assert r1 == "Hi"
    r2 = fn(mock5, "Hi there")
    assert r2 == " there"


# [pr_diff] fail_to_pass
def test_extract_tool_call_jsons():
    """_extract_tool_call_jsons parses <tool_call> regions correctly."""
    source, tree = _load_hermes()
    method_src = _extract_class_method(
        source, tree, "Hermes2ProToolParser", "_extract_tool_call_jsons"
    )
    assert method_src is not None, "_extract_tool_call_jsons method not found"

    ns = _build_namespace(source, tree)
    _bind_method(ns, method_src, "_extract_tool_call_jsons")
    fn = ns["_extract_tool_call_jsons"]
    mock = _MockParser()

    # Complete single tool call
    text1 = '<tool_call>{"name": "f", "arguments": {"x": 1}}</tool_call>'
    result1 = fn(mock, text1)
    assert len(result1) == 1
    tc_json, is_complete = result1[0]
    assert is_complete is True
    parsed = json.loads(tc_json)
    assert parsed["name"] == "f"

    # Two complete tool calls
    text2 = (
        '<tool_call>{"name": "a", "arguments": {}}</tool_call>'
        '<tool_call>{"name": "b", "arguments": {}}</tool_call>'
    )
    result2 = fn(mock, text2)
    assert len(result2) == 2
    assert result2[0][1] is True
    assert result2[1][1] is True

    # Partial tool call (no closing tag, incomplete JSON)
    text3 = '<tool_call>{"name": "f", "arguments": {"x'
    result3 = fn(mock, text3)
    assert len(result3) == 1
    assert result3[0][1] is False  # not complete

    # No tool calls
    text4 = "Just plain text"
    result4 = fn(mock, text4)
    assert len(result4) == 0


# [pr_diff] fail_to_pass
def test_extract_tool_name():
    """_extract_tool_name extracts function name from tool call JSON."""
    source, tree = _load_hermes()
    method_src = _extract_class_method(
        source, tree, "Hermes2ProToolParser", "_extract_tool_name"
    )
    assert method_src is not None, "_extract_tool_name not found"

    # It's a @staticmethod, so no self needed
    ns = {"re": re}
    exec(method_src, ns)
    fn = ns["_extract_tool_name"]

    assert fn('{"name": "get_weather", "arguments": {}}') == "get_weather"
    assert fn('{"name": "search_api", "arguments": {"q": "test"}}') == "search_api"
    assert fn('{"name":  "spaced"  , "arguments": {}}') == "spaced"
    assert fn('{"incomplete') is None
    assert fn('{"name": "') is None  # name value not complete


# [pr_diff] fail_to_pass
def test_extract_tool_args():
    """_extract_tool_args extracts arguments portion from tool call JSON."""
    source, tree = _load_hermes()
    method_src = _extract_class_method(
        source, tree, "Hermes2ProToolParser", "_extract_tool_args"
    )
    assert method_src is not None, "_extract_tool_args not found"

    ns = {"re": re}
    exec(method_src, ns)
    fn = ns["_extract_tool_args"]

    # Complete tool call — should strip outer closing brace
    args1 = fn('{"name": "f", "arguments": {"x": 1}}', True)
    assert args1 is not None
    assert json.loads(args1) == {"x": 1}

    # Incomplete tool call — returns raw
    args2 = fn('{"name": "f", "arguments": {"x": 1', False)
    assert args2 is not None
    assert "x" in args2

    # No arguments key yet
    args3 = fn('{"name": "f"', False)
    assert args3 is None

    # Nested arguments
    args4 = fn('{"name": "f", "arguments": {"a": {"b": 2}}}', True)
    assert args4 is not None
    assert json.loads(args4) == {"a": {"b": 2}}


# [pr_diff] fail_to_pass
def test_old_buffer_approach_removed():
    """Buggy tool_call_delta_buffer and buffered_delta_text removed from parser."""
    # AST-only because: checking absence of old code (can't call what doesn't exist)
    source, tree = _load_hermes()

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Hermes2ProToolParser":
            method_names = [
                n.name for n in node.body if isinstance(n, ast.FunctionDef)
            ]
            assert "tool_call_delta_buffer" not in method_names, (
                "tool_call_delta_buffer method still present (buggy buffering)"
            )
            break
    else:
        assert False, "Hermes2ProToolParser class not found"

    assert "buffered_delta_text" not in source, (
        "buffered_delta_text still referenced"
    )


# [pr_diff] fail_to_pass
def test_longcat_token_arrays_removed():
    """Longcat parser no longer defines redundant token array attributes."""
    source = Path(LONGCAT).read_text()
    assert "tool_call_start_token_array" not in source, (
        "tool_call_start_token_array still in longcat parser"
    )
    assert "tool_call_end_token_array" not in source, (
        "tool_call_end_token_array still in longcat parser"
    )
    assert "tool_call_start_token_ids" not in source, (
        "tool_call_start_token_ids still in longcat parser"
    )
    assert "tool_call_end_token_ids" not in source, (
        "tool_call_end_token_ids still in longcat parser"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_nonstreaming_extract_intact():
    """Non-streaming extract_tool_calls and core init remain intact."""
    source, tree = _load_hermes()

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Hermes2ProToolParser":
            methods = [
                n.name for n in node.body if isinstance(n, ast.FunctionDef)
            ]
            assert "extract_tool_calls" in methods, "extract_tool_calls missing"
            assert "extract_tool_calls_streaming" in methods, (
                "extract_tool_calls_streaming missing"
            )
            assert "__init__" in methods, "__init__ missing"

            init_src = _extract_class_method(source, tree, "Hermes2ProToolParser", "__init__")
            assert "tool_call_start_token" in init_src, (
                "Init missing tool_call_start_token"
            )
            assert "tool_call_end_token" in init_src, (
                "Init missing tool_call_end_token"
            )
            return

    assert False, "Hermes2ProToolParser class not found"


# [static] pass_to_pass
def test_not_stub():
    """Both parser files have real implementation, not stubs."""
    hermes_src = Path(HERMES).read_text()
    hermes_lines = len(hermes_src.splitlines())
    assert hermes_lines >= 100, f"hermes parser too short ({hermes_lines} lines)"

    for name in [
        "Hermes2ProToolParser",
        "extract_tool_calls_streaming",
        "extract_tool_calls",
        "tool_call_start_token",
        "DeltaMessage",
    ]:
        assert name in hermes_src, f"hermes parser missing '{name}'"

    longcat_src = Path(LONGCAT).read_text()
    assert "Hermes2ProToolParser" in longcat_src, (
        "longcat parser no longer inherits from Hermes2ProToolParser"
    )
    assert len(longcat_src.splitlines()) >= 10, "longcat parser too short"
