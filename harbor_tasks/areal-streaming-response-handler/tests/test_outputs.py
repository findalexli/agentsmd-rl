"""
Task: areal-streaming-response-handler
Repo: inclusionAI/AReaL @ 421e4e5d9816f9a173374331df96d5d799a40844
PR:   1053

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import asyncio
import json
from pathlib import Path

REPO = "/workspace/AReaL"
TARGET = f"{REPO}/areal/experimental/openai/proxy/proxy_rollout_server.py"


def _read_source():
    return Path(TARGET).read_text()


def _get_function(source, name):
    """Return (ast node, source text) for a named function."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            lines = source.splitlines()
            func_src = "\n".join(lines[node.lineno - 1 : node.end_lineno])
            return node, func_src
    return None, None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """proxy_rollout_server.py compiles without syntax errors."""
    source = _read_source()
    compile(source, TARGET, "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_stream_stripped_from_kwargs():
    """_call_client_create strips body 'stream' field so it doesn't leak to create_fn.

    The fix must pop/remove 'stream' from kwargs before conditionally re-adding it
    based on the explicit stream parameter.
    """
    # AST-only because: module imports areal.* + torch runtime at module level
    source = _read_source()
    _, func_src = _get_function(source, "_call_client_create")
    assert func_src is not None, "_call_client_create function not found"

    # Extract stream-handling code block and execute it behaviorally
    code_lines = []
    func_lines = func_src.splitlines()
    in_if_stream = False
    if_indent = 0

    for line in func_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # Collect any line that removes stream from kwargs
        if "stream" in stripped and any(
            kw in stripped for kw in ("pop(", "del ", ".remove", ".discard")
        ):
            code_lines.append(stripped)
            continue
        # Collect the `if stream:` conditional block
        if stripped.startswith("if stream") and ":" in stripped:
            in_if_stream = True
            if_indent = len(line) - len(line.lstrip())
            code_lines.append(stripped)
            continue
        if in_if_stream:
            cur_indent = len(line) - len(line.lstrip())
            if cur_indent > if_indent and stripped:
                code_lines.append("    " + stripped)
            else:
                in_if_stream = False

    assert code_lines, (
        "No stream-handling logic found in _call_client_create — "
        "the function must strip 'stream' from kwargs to prevent body leak"
    )
    code = "\n".join(code_lines)

    # Test 6 scenarios covering all combinations
    scenarios = [
        # (body_stream, param_stream, expect_in_kwargs, expected_value)
        (True, False, False, None),   # body stream=True, param False → stripped
        (True, True, True, True),     # body stream=True, param True → kept
        (False, False, False, None),  # body stream=False, param False → stripped
        (False, True, True, True),    # body stream=False, param True → overridden to True
        (None, False, False, None),   # no stream in body, param False → absent
        (None, True, True, True),     # no stream in body, param True → added
    ]

    for body_stream, param_stream, expect_in, expect_val in scenarios:
        kwargs = {"model": "gpt-4", "messages": []}
        if body_stream is not None:
            kwargs["stream"] = body_stream
        ns = {"kwargs": kwargs, "stream": param_stream}
        exec(code, ns)
        if expect_in:
            assert "stream" in ns["kwargs"], (
                f"stream should be in kwargs when param={param_stream}, body={body_stream}"
            )
            assert ns["kwargs"]["stream"] == expect_val, (
                f"stream should be {expect_val} when param={param_stream}, body={body_stream}"
            )
        else:
            assert "stream" not in ns["kwargs"], (
                f"stream should NOT be in kwargs when param={param_stream}, body={body_stream}"
            )


# [pr_diff] fail_to_pass
def test_sse_generator_format():
    """Streaming path produces SSE events: 'data: {json}\\n\\n' then 'data: [DONE]\\n\\n'.

    Extracts the inner SSE generator from chat_completions and runs it with
    mock chunk objects to verify the output format behaviorally.
    """
    # AST-only because: module imports areal.* + torch runtime at module level
    source = _read_source()
    _, func_src = _get_function(source, "chat_completions")
    assert func_src is not None, "chat_completions function not found"

    # Find inner async generator function that yields SSE events
    tree = ast.parse(func_src)
    sse_gen_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name != "chat_completions":
            inner_lines = func_src.splitlines()[node.lineno - 1 : node.end_lineno]
            inner_src = "\n".join(inner_lines)
            if "yield" in inner_src and "data" in inner_src:
                sse_gen_node = node
                break

    assert sse_gen_node is not None, (
        "chat_completions must contain an inner async generator that yields SSE data: events"
    )

    # Extract the generator source, dedented to top level
    inner_lines = func_src.splitlines()[sse_gen_node.lineno - 1 : sse_gen_node.end_lineno]
    min_indent = min(len(l) - len(l.lstrip()) for l in inner_lines if l.strip())
    dedented = "\n".join(l[min_indent:] for l in inner_lines)

    # Create mock chunk with model_dump_json
    mock_code = '''
class _MockChunk:
    def __init__(self, cid, content):
        self._id = cid
        self._content = content
    def model_dump_json(self):
        import json
        return json.dumps({"id": self._id, "content": self._content})
'''

    # Provide type-hint names so extracted code with annotations can exec.
    # The generator references AsyncGenerator and ChatCompletionChunk in type hints.
    import re
    from typing import AsyncGenerator as _AG

    # Strip type annotations from function signature to avoid NameError on
    # openai types (ChatCompletionChunk etc.) that aren't installed.
    dedented = re.sub(
        r"(async\s+def\s+\w+)\([^)]*\)(\s*->[^:]+)?:",
        r"\1(chunk_stream):",
        dedented,
    )

    ns = {"AsyncGenerator": _AG}
    exec(mock_code + "\n" + dedented, ns)

    # Find the generator function in namespace
    gen_fn = None
    for k, v in ns.items():
        if callable(v) and k.startswith("_") and k not in ("_MockChunk",):
            gen_fn = v
            break
    assert gen_fn is not None, "Could not find SSE generator function after extraction"

    # Create a mock async chunk stream with multiple chunks
    async def _mock_chunk_stream():
        for i, content in enumerate(["hello", "world", "!"]):
            yield ns["_MockChunk"](f"chunk-{i}", content)

    # Collect SSE output
    async def _collect():
        results = []
        async for item in gen_fn(_mock_chunk_stream()):
            results.append(item)
        return results

    results = asyncio.run(_collect())

    # Verify: 3 data chunks + 1 [DONE] = 4 events
    assert len(results) >= 4, (
        f"Expected at least 4 SSE events (3 chunks + DONE), got {len(results)}"
    )
    # All events must use "data: " prefix
    for r in results:
        assert r.startswith("data: "), f"SSE event must start with 'data: ', got: {r!r}"
    # Last event is [DONE] sentinel
    assert results[-1].strip() == "data: [DONE]", (
        f"Last SSE event must be 'data: [DONE]', got: {results[-1]!r}"
    )
    # Data events contain valid JSON with expected content
    for i, r in enumerate(results[:-1]):
        payload = r.removeprefix("data: ").strip()
        parsed = json.loads(payload)
        assert "content" in parsed, f"Chunk {i} must have 'content' field"
    # Verify double newline separators (SSE spec)
    for r in results:
        assert r.endswith("\n\n"), f"SSE events must end with \\n\\n: {r!r}"


# [pr_diff] fail_to_pass
def test_response_model_allows_streaming():
    """Endpoint decorator must not force ChatCompletion validation on StreamingResponse.

    Without response_model=None (or equivalent), FastAPI tries to validate
    StreamingResponse as ChatCompletion and raises ResponseValidationError.
    """
    # AST-only because: FastAPI decorator requires full app initialization
    source = _read_source()
    node, func_src = _get_function(source, "chat_completions")
    assert node is not None, "chat_completions function not found"

    lines = source.splitlines()
    # Check decorator area (10 lines above function def)
    decorator_start = max(0, node.lineno - 10)
    decorator_area = "\n".join(lines[decorator_start : node.lineno])

    # Also check return annotation
    return_annotation = ""
    if node.returns:
        return_annotation = ast.dump(node.returns)

    allows_streaming = (
        "response_model=None" in decorator_area
        or "response_model = None" in decorator_area
        or "StreamingResponse" in return_annotation
        or "StreamingResponse" in func_src.splitlines()[0]
    )
    assert allows_streaming, (
        "Endpoint must have response_model=None or StreamingResponse in return type "
        "to prevent FastAPI ResponseValidationError on streaming responses"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_not_stub_call_client_create():
    """_call_client_create has substantial implementation (not a stub)."""
    source = _read_source()
    node, _ = _get_function(source, "_call_client_create")
    assert node is not None, "_call_client_create not found"

    body_stmts = [
        s
        for s in node.body
        if not isinstance(s, ast.Pass)
        and not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
    ]
    assert len(body_stmts) >= 5, (
        f"_call_client_create has only {len(body_stmts)} statements — likely a stub"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:30 @ 421e4e5
def test_no_wildcard_imports():
    """No wildcard imports (from x import *)."""
    source = _read_source()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                assert alias.name != "*", (
                    f"Wildcard import: from {node.module} import *"
                )


# [agent_config] pass_to_pass — AGENTS.md:89-91 @ 421e4e5
def test_no_bare_print():
    """No bare print() — use areal.utils.logging.getLogger instead."""
    source = _read_source()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "print", (
                f"Bare print() at line {node.lineno} — use logger instead"
            )
