"""
Task: vllm-tool-parser-indexerror
Repo: vllm-project/vllm @ 9d0351c91d3115215f84f3bd4b9f366d3fbd13b3
PR:   37958

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import textwrap
from pathlib import Path

TARGET = Path(
    "/workspace/vllm/vllm/entrypoints/openai/chat_completion/serving.py"
)


# ---------------------------------------------------------------------------
# Helpers: extract code blocks from the target function for behavioral exec
# AST-only because: chat_completion_stream_generator is an async generator
# deeply embedded in vLLM's OpenAIServingChat class, requiring model/tokenizer/
# engine state that cannot be instantiated without GPU.
# ---------------------------------------------------------------------------


def _get_function_lines() -> list[str]:
    """Return the lines of chat_completion_stream_generator."""
    src = TARGET.read_text()
    tree = ast.parse(src)
    lines = src.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "chat_completion_stream_generator":
                return lines[node.lineno - 1 : node.end_lineno]
    raise AssertionError("chat_completion_stream_generator not found")


def _find_block_start(func_lines: list[str]) -> int:
    """Find the start index of the index/auto_tools_called assignment block."""
    for i, line in enumerate(func_lines):
        if "auto_tools_called" in line and "False" in line:
            # Look back for unconditional index = 0
            for j in range(i - 1, max(i - 5, -1), -1):
                s = func_lines[j].strip()
                if not s or s.startswith("#"):
                    continue
                if "index" in s and "=" in s and "==" not in s:
                    return j
                break
            return i
    raise AssertionError("auto_tools_called = False not found in function")


def _extract_assignment_block(func_lines: list[str]) -> str:
    """Extract the assignment block up through should_check assignment (if present).

    Stops at the if-statement that uses should_check/_should_check as a guard
    condition (not the assignment itself).
    """
    start = _find_block_start(func_lines)
    collected = []
    for i in range(start, min(start + 30, len(func_lines))):
        stripped = func_lines[i].strip()
        # Stop at: if should_check ... : or if ( ... _should_check ... ):
        if re.match(r"if\b.*should_check", stripped):
            break
        if re.match(r"if\b.*_should_check", stripped):
            break
        if stripped == "if (" and i + 1 < len(func_lines):
            next_s = func_lines[i + 1].strip()
            if "should_check" in next_s or "_should_check" in next_s:
                break
        collected.append(func_lines[i])
    while collected and not collected[-1].strip():
        collected.pop()
    return textwrap.dedent("\n".join(collected))


def _extract_guard_condition(func_lines: list[str]) -> str:
    """Extract the boolean condition from the if-statement guarding prev_tool_call_arr access.

    Returns the condition as a string suitable for eval().
    """
    for i, line in enumerate(func_lines):
        if "_should_check" not in line and "should_check" not in line:
            continue

        # Look back for the start of an if-statement (up to 5 lines)
        if_start = None
        for j in range(i, max(i - 5, -1), -1):
            s = func_lines[j].strip()
            if s.startswith("if ") or s.startswith("if("):
                if_start = j
                break

        if if_start is None:
            # This is a should_check = ... assignment, skip
            continue

        # Skip `if tool_parser:` — that's the assignment block, not the guard
        if func_lines[if_start].strip() == "if tool_parser:":
            continue

        # Collect the full condition (may span multiple lines)
        cond_parts = []
        for j in range(if_start, min(if_start + 10, len(func_lines))):
            cond_parts.append(func_lines[j].strip())
            if func_lines[j].strip().endswith(":"):
                break

        full = " ".join(cond_parts)
        # Extract between 'if' and the trailing ':'
        m = re.match(r"if\s+(.+?)\s*:\s*$", full)
        if m:
            return m.group(1)

    raise AssertionError("Could not find should_check guard condition")


# ---------------------------------------------------------------------------
# Mock objects for behavioral execution
# ---------------------------------------------------------------------------


class _MockSelf:
    """Mock self with _should_check_for_unstreamed_tool_arg_tokens."""

    def __init__(self, result: bool):
        self._result = result

    def _should_check_for_unstreamed_tool_arg_tokens(self, delta_message, output):
        return self._result


class _MockToolParser:
    """Mock tool_parser with configurable prev_tool_call_arr."""

    def __init__(self, calls: list):
        self.prev_tool_call_arr = calls


class _MockToolCall:
    """Mock tool call with index and arguments."""

    def __init__(self, index: int = 0, arguments: str = "{}"):
        self.index = index
        self.arguments = arguments


class _MockDeltaMessage:
    tool_calls = None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """serving.py must parse without syntax errors."""
    src = TARGET.read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_index_always_defined():
    """index must be defined after the assignment block regardless of tool_parser state.

    Bug: index = 0 was only inside the 'else' branch. If tool_parser was truthy
    but prev_tool_call_arr raised, index was never assigned (NameError).
    Fix: unconditional 'index = 0' before the if/else.

    Executes the extracted assignment block with multiple broken tool_parser
    configurations and verifies index is always defined with value 0.
    """
    func_lines = _get_function_lines()
    snippet = _extract_assignment_block(func_lines)

    # Scenario 1: tool_parser whose prev_tool_call_arr raises RuntimeError
    class BrokenRuntime:
        @property
        def prev_tool_call_arr(self):
            raise RuntimeError("broken")

    ns: dict = {"tool_parser": BrokenRuntime(), "self": _MockSelf(True),
                "delta_message": _MockDeltaMessage(), "output": None}
    try:
        exec(compile(snippet, "<test>", "exec"), ns)
    except (RuntimeError, TypeError, IndexError):
        pass
    assert "index" in ns, (
        "index was not defined when tool_parser.prev_tool_call_arr raised RuntimeError"
    )
    assert ns["index"] == 0, f"Expected index=0, got {ns['index']}"

    # Scenario 2: tool_parser whose prev_tool_call_arr raises AttributeError
    class BrokenAttr:
        @property
        def prev_tool_call_arr(self):
            raise AttributeError("no such attribute")

    ns = {"tool_parser": BrokenAttr(), "self": _MockSelf(True),
          "delta_message": _MockDeltaMessage(), "output": None}
    try:
        exec(compile(snippet, "<test>", "exec"), ns)
    except (AttributeError, TypeError, RuntimeError):
        pass
    assert "index" in ns, (
        "index was not defined when tool_parser.prev_tool_call_arr raised AttributeError"
    )
    assert ns["index"] == 0, f"Expected index=0, got {ns['index']}"

    # Scenario 3: tool_parser whose prev_tool_call_arr raises TypeError
    class BrokenType:
        @property
        def prev_tool_call_arr(self):
            raise TypeError("not iterable")

    ns = {"tool_parser": BrokenType(), "self": _MockSelf(True),
          "delta_message": _MockDeltaMessage(), "output": None}
    try:
        exec(compile(snippet, "<test>", "exec"), ns)
    except (TypeError, RuntimeError, AttributeError):
        pass
    assert "index" in ns, (
        "index was not defined when tool_parser.prev_tool_call_arr raised TypeError"
    )
    assert ns["index"] == 0, f"Expected index=0, got {ns['index']}"


# [pr_diff] fail_to_pass
def test_guard_prevents_empty_arr_access():
    """The should_check guard must not allow entry when no tool calls were detected.

    Bug: 'if (_should_check(...) and tool_parser):' evaluated True even when
    prev_tool_call_arr was empty, causing IndexError on arr[-1] inside the body.
    Fix: add 'auto_tools_called' (or equivalent) to the guard condition.

    Executes the assignment block with an empty tool_parser, then evaluates the
    guard condition. If the guard is True, the buggy code would crash.
    """
    func_lines = _get_function_lines()
    assignment_block = _extract_assignment_block(func_lines)

    # Scenario 1: should_check True, tool_parser with empty arr
    ns: dict = {
        "self": _MockSelf(result=True),
        "tool_parser": _MockToolParser([]),
        "delta_message": _MockDeltaMessage(),
        "output": None,
    }
    exec(compile(assignment_block, "<test>", "exec"), ns)

    guard_cond = _extract_guard_condition(func_lines)
    enters_block = bool(eval(guard_cond, dict(ns)))
    assert not enters_block, (
        f"Guard condition '{guard_cond}' evaluates to True when "
        "prev_tool_call_arr is empty. This causes IndexError on "
        "prev_tool_call_arr[-1]. Add auto_tools_called to the guard."
    )

    # Scenario 2: should_check True, tool_parser is None
    ns = {
        "self": _MockSelf(result=True),
        "tool_parser": None,
        "delta_message": _MockDeltaMessage(),
        "output": None,
    }
    exec(compile(assignment_block, "<test>", "exec"), ns)
    enters_block = bool(eval(guard_cond, dict(ns)))
    assert not enters_block, (
        "Guard condition must be False when tool_parser is None"
    )

    # Scenario 3: should_check False, tool_parser with empty arr
    ns = {
        "self": _MockSelf(result=False),
        "tool_parser": _MockToolParser([]),
        "delta_message": _MockDeltaMessage(),
        "output": None,
    }
    exec(compile(assignment_block, "<test>", "exec"), ns)
    enters_block = bool(eval(guard_cond, dict(ns)))
    assert not enters_block, (
        "Guard condition must be False when should_check is False"
    )

    # Scenario 4: should_check True, tool_parser with calls → guard SHOULD be True
    ns = {
        "self": _MockSelf(result=True),
        "tool_parser": _MockToolParser([_MockToolCall(index=0, arguments="{}")]),
        "delta_message": _MockDeltaMessage(),
        "output": None,
    }
    exec(compile(assignment_block, "<test>", "exec"), ns)
    enters_block = bool(eval(guard_cond, dict(ns)))
    assert enters_block, (
        "Guard condition must be True when tool calls exist and should_check is True"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + normal flow
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_correct_index_with_tool_calls():
    """index must equal the last tool call's index when tool calls are present.

    Executes the assignment block with various tool_parser configurations and
    verifies index is computed correctly from prev_tool_call_arr.
    """
    func_lines = _get_function_lines()
    snippet = _extract_assignment_block(func_lines)

    # index = len(prev_tool_call_arr) - 1 when calls exist
    for num_calls in [1, 3, 5, 10]:
        calls = [_MockToolCall() for _ in range(num_calls)]
        expected_idx = num_calls - 1
        ns: dict = {
            "tool_parser": _MockToolParser(calls),
            "self": _MockSelf(True),
            "delta_message": _MockDeltaMessage(),
            "output": None,
        }
        exec(compile(snippet, "<test>", "exec"), ns)
        assert ns["index"] == expected_idx, (
            f"With {num_calls} calls, expected index={expected_idx}, got {ns['index']}"
        )
        assert ns["auto_tools_called"] is True

    # Empty arr — index should be 0
    ns = {
        "tool_parser": _MockToolParser([]),
        "self": _MockSelf(True),
        "delta_message": _MockDeltaMessage(),
        "output": None,
    }
    exec(compile(snippet, "<test>", "exec"), ns)
    assert ns["index"] == 0, f"Expected index=0 with empty arr, got {ns['index']}"

    # No tool_parser — index should be 0
    ns = {
        "tool_parser": None,
        "self": _MockSelf(True),
        "delta_message": _MockDeltaMessage(),
        "output": None,
    }
    exec(compile(snippet, "<test>", "exec"), ns)
    assert ns["index"] == 0, f"Expected index=0 with no parser, got {ns['index']}"


# [static] pass_to_pass
def test_function_preserved():
    """chat_completion_stream_generator must exist with core identifiers."""
    src = TARGET.read_text()
    tree = ast.parse(src)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "chat_completion_stream_generator":
                found = True
                break
    assert found, "chat_completion_stream_generator not found"

    for pattern in [
        "tool_parser",
        "delta_message",
        "_should_check_for_unstreamed_tool_arg_tokens",
        "prev_tool_call_arr",
    ]:
        assert pattern in src, f"Missing key identifier: {pattern}"


# [static] pass_to_pass
def test_not_stub():
    """serving.py must not be replaced with a stub."""
    src = TARGET.read_text()
    line_count = len(src.splitlines())
    assert line_count >= 500, f"File too small ({line_count} lines), likely a stub"

    tree = ast.parse(src)
    funcs = sum(
        1 for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    assert funcs >= 5, f"Only {funcs} functions, expected 5+"

    for kw in ["OpenAIServing", "ChatCompletionRequest", "async"]:
        assert kw in src, f"Missing expected pattern: {kw}"
