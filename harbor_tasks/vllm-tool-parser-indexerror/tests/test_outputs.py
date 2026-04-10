"""
Task: vllm-tool-parser-indexerror
Repo: vllm-project/vllm @ 9d0351c91d3115215f84f3bd4b9f366d3fbd13b3
PR:   37958

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/vllm"
TARGET = Path(f"{REPO}/vllm/entrypoints/openai/chat_completion/serving.py")


# ---------------------------------------------------------------------------
# Helpers: extract code blocks from the target function
# ---------------------------------------------------------------------------


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via subprocess in the repo directory."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


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

    Stops at the if-statement that uses should_check/_should_check as a guard.
    """
    start = _find_block_start(func_lines)
    collected = []
    for i in range(start, min(start + 30, len(func_lines))):
        stripped = func_lines[i].strip()
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
    """Extract the boolean condition from the if-statement guarding prev_tool_call_arr access."""
    for i, line in enumerate(func_lines):
        if "_should_check" not in line and "should_check" not in line:
            continue
        if_start = None
        for j in range(i, max(i - 5, -1), -1):
            s = func_lines[j].strip()
            if s.startswith("if ") or s.startswith("if("):
                if_start = j
                break
        if if_start is None:
            continue
        if func_lines[if_start].strip() == "if tool_parser:":
            continue
        cond_parts = []
        for j in range(if_start, min(if_start + 10, len(func_lines))):
            cond_parts.append(func_lines[j].strip())
            if func_lines[j].strip().endswith(":"):
                break
        full = " ".join(cond_parts)
        m = re.match(r"if\s+(.+?)\s*:\s*$", full)
        if m:
            return m.group(1)
    raise AssertionError("Could not find should_check guard condition")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """serving.py must parse without syntax errors."""
    src = TARGET.read_text()
    ast.parse(src)


# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff linter passes on serving.py (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "vllm/entrypoints/openai/chat_completion/serving.py"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_python_syntax():
    """Python files in the modified module have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "vllm/entrypoints/openai/chat_completion/serving.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_index_always_defined():
    """index must be unconditionally defined before the if tool_parser block.

    Bug: index = 0 was only inside the 'else' branch. When tool_parser was set
    but prev_tool_call_arr raised, index was never assigned (NameError).
    Fix: unconditional 'index = 0' before the if/else.

    Extracts the assignment block and executes it in a subprocess with mock
    objects to verify index is always defined with value 0.
    """
    func_lines = _get_function_lines()
    snippet = _extract_assignment_block(func_lines)

    snippet_path = Path(REPO) / "_eval_snippet.txt"
    snippet_path.write_text(snippet)
    try:
        r = _run_py("""\
import sys
from pathlib import Path

snippet = Path("_eval_snippet.txt").read_text()

class MockSelf:
    def _should_check_for_unstreamed_tool_arg_tokens(self, dm, out):
        return True

class MockDelta:
    tool_calls = None

class BrokenParser:
    @property
    def prev_tool_call_arr(self):
        raise RuntimeError("broken")

# Scenario 1: tool_parser with broken prev_tool_call_arr
ns = {"tool_parser": BrokenParser(), "self": MockSelf(),
      "delta_message": MockDelta(), "output": None}
try:
    exec(compile(snippet, "<test>", "exec"), ns)
except (RuntimeError, TypeError, IndexError):
    pass

assert "index" in ns, "index not defined when tool_parser.prev_tool_call_arr raised"
assert ns["index"] == 0, f"Expected index=0, got {ns['index']}"

# Scenario 2: tool_parser is None
ns = {"tool_parser": None, "self": MockSelf(),
      "delta_message": MockDelta(), "output": None}
exec(compile(snippet, "<test>", "exec"), ns)
assert "index" in ns, "index not defined when tool_parser is None"
assert ns["index"] == 0, f"Expected index=0, got {ns['index']}"

# Scenario 3: tool_parser with empty prev_tool_call_arr
class EmptyParser:
    prev_tool_call_arr = []

ns = {"tool_parser": EmptyParser(), "self": MockSelf(),
      "delta_message": MockDelta(), "output": None}
exec(compile(snippet, "<test>", "exec"), ns)
assert "index" in ns, "index not defined with empty parser"
assert ns["index"] == 0, f"Expected index=0 with empty arr, got {ns['index']}"

print("PASS")
""")
    finally:
        snippet_path.unlink(missing_ok=True)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_guard_prevents_empty_arr_access():
    """The guard must prevent entry when no tool calls were detected.

    Bug: 'if (_should_check(...) and tool_parser):' was True even when
    prev_tool_call_arr was empty, causing IndexError on arr[-1].
    Fix: add auto_tools_called to the guard condition.

    Extracts the assignment block and guard condition, executes them in a
    subprocess with mock objects to verify the guard is False when appropriate.
    """
    func_lines = _get_function_lines()
    snippet = _extract_assignment_block(func_lines)
    guard = _extract_guard_condition(func_lines)

    data_path = Path(REPO) / "_eval_data.txt"
    data_path.write_text(f"{snippet}\n===GUARD===\n{guard}")
    try:
        r = _run_py("""\
import sys
from pathlib import Path

raw = Path("_eval_data.txt").read_text()
parts = raw.split("\\n===GUARD===\\n")
snippet = parts[0]
guard_cond = parts[1]

class MockSelf:
    def __init__(self, result):
        self._result = result
    def _should_check_for_unstreamed_tool_arg_tokens(self, dm, out):
        return self._result

class MockDelta:
    tool_calls = None

class MockToolParser:
    def __init__(self, calls):
        self.prev_tool_call_arr = calls

class MockToolCall:
    def __init__(self, index=0, arguments="{}"):
        self.index = index
        self.arguments = arguments

# Scenario 1: should_check=True, tool_parser with empty arr -> guard must be False
ns = {"self": MockSelf(True), "tool_parser": MockToolParser([]),
      "delta_message": MockDelta(), "output": None}
exec(compile(snippet, "<test>", "exec"), ns)
result = bool(eval(guard_cond, dict(ns)))
assert not result, (
    f"Guard '{guard_cond}' is True when prev_tool_call_arr is empty -> IndexError"
)

# Scenario 2: should_check=True, tool_parser=None -> guard must be False
ns = {"self": MockSelf(True), "tool_parser": None,
      "delta_message": MockDelta(), "output": None}
exec(compile(snippet, "<test>", "exec"), ns)
result = bool(eval(guard_cond, dict(ns)))
assert not result, "Guard must be False when tool_parser is None"

# Scenario 3: should_check=False, tool_parser with empty arr -> guard must be False
ns = {"self": MockSelf(False), "tool_parser": MockToolParser([]),
      "delta_message": MockDelta(), "output": None}
exec(compile(snippet, "<test>", "exec"), ns)
result = bool(eval(guard_cond, dict(ns)))
assert not result, "Guard must be False when should_check is False"

# Scenario 4: should_check=True, tool_parser with calls -> guard MUST be True
ns = {"self": MockSelf(True), "tool_parser": MockToolParser([MockToolCall()]),
      "delta_message": MockDelta(), "output": None}
exec(compile(snippet, "<test>", "exec"), ns)
result = bool(eval(guard_cond, dict(ns)))
assert result, "Guard must be True when tool calls exist and should_check is True"

print("PASS")
""")
    finally:
        data_path.unlink(missing_ok=True)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + normal flow
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_correct_index_with_tool_calls():
    """index must equal the last tool call's index when calls are present.

    Executes the assignment block with various tool_parser configurations and
    verifies index is computed correctly from prev_tool_call_arr.
    """
    func_lines = _get_function_lines()
    snippet = _extract_assignment_block(func_lines)

    class _Self:
        def _should_check_for_unstreamed_tool_arg_tokens(self, dm, out):
            return True

    class _Delta:
        tool_calls = None

    class _Parser:
        def __init__(self, calls):
            self.prev_tool_call_arr = calls

    class _Call:
        pass

    # index = len(prev_tool_call_arr) - 1 when calls exist
    for num_calls in [1, 3, 5, 10]:
        calls = [_Call() for _ in range(num_calls)]
        expected_idx = num_calls - 1
        ns: dict = {
            "tool_parser": _Parser(calls),
            "self": _Self(),
            "delta_message": _Delta(),
            "output": None,
        }
        exec(compile(snippet, "<test>", "exec"), ns)
        assert ns["index"] == expected_idx, (
            f"With {num_calls} calls, expected index={expected_idx}, got {ns['index']}"
        )
        assert ns["auto_tools_called"] is True

    # Empty arr — index should be 0
    ns = {
        "tool_parser": _Parser([]),
        "self": _Self(),
        "delta_message": _Delta(),
        "output": None,
    }
    exec(compile(snippet, "<test>", "exec"), ns)
    assert ns["index"] == 0, f"Expected index=0 with empty arr, got {ns['index']}"

    # No tool_parser — index should be 0
    ns = {
        "tool_parser": None,
        "self": _Self(),
        "delta_message": _Delta(),
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
