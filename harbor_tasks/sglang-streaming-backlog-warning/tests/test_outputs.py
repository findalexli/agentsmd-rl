"""
Task: sglang-streaming-backlog-warning
Repo: sgl-project/sglang @ 4dd4e06f1d5fd1d294cb82a84b803256760cbfff
PR:   21432

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import io
import logging
import textwrap
import types
from pathlib import Path

REPO = "/repo"
FILE = f"{REPO}/python/sglang/srt/managers/tokenizer_manager.py"


def _get_method_node():
    """Parse the file and return the _wait_one_response AST node."""
    # AST-only because: torch, vllm, triton deps prevent importing tokenizer_manager
    source = Path(FILE).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_wait_one_response":
            return node, source
    raise AssertionError("_wait_one_response method not found in tokenizer_manager.py")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """tokenizer_manager.py must parse without syntax errors."""
    source = Path(FILE).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_backlog_warning_in_method():
    """No logger.warning/warn calls about streaming backlog in _wait_one_response.

    Accepts: deletion of the warning, downgrade to debug/info, or any
    approach that eliminates WARNING-level log about backlog.
    """
    # AST-only because: torch, vllm, triton deps prevent importing tokenizer_manager
    method, source = _get_method_node()
    backlog_keywords = ["backlog", "queued chunks", "p99 tbt", "inflate"]

    for child in ast.walk(method):
        if not isinstance(child, ast.Call):
            continue
        func = child.func
        if not (isinstance(func, ast.Attribute) and func.attr in ("warning", "warn")):
            continue
        for arg in child.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                low = arg.value.lower()
                if any(kw in low for kw in backlog_keywords):
                    raise AssertionError(
                        f"WARNING-level streaming backlog log still present "
                        f"at line {child.lineno}: {arg.value!r}"
                    )


# [pr_diff] fail_to_pass
def test_no_warning_emitted_with_pending_chunks():
    """Execute any backlog-related code path and verify no WARNING output.

    Extracts if-blocks in _wait_one_response that reference backlog keywords,
    runs them with varied pending list sizes, and asserts no WARNING is captured.
    Covers fixes that restructure the code rather than deleting the block.
    """
    # AST-only because: torch, vllm, triton deps prevent importing tokenizer_manager
    method, source = _get_method_node()
    lines = source.splitlines()
    backlog_keywords = ["backlog", "queued chunks", "p99 tbt", "inflate"]

    # Vary inputs — test multiple pending list sizes to prevent hardcoding
    test_inputs = [
        [{"t": "a"}, {"t": "b"}],                          # 2 pending
        [{"t": "x"}, {"t": "y"}, {"t": "z"}],              # 3 pending
        [{"t": str(i)} for i in range(10)],                 # 10 pending
    ]

    for child in ast.walk(method):
        if not isinstance(child, ast.If):
            continue
        for sub in ast.walk(child):
            if not isinstance(sub, ast.Call):
                continue
            func = sub.func
            if not (isinstance(func, ast.Attribute) and func.attr in ("warning", "warn")):
                continue
            for arg in sub.args:
                if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
                    continue
                if not any(kw in arg.value.lower() for kw in backlog_keywords):
                    continue
                # Found the block — execute it with each input set
                block = textwrap.dedent("\n".join(lines[child.lineno - 1 : child.end_lineno]))
                for pending in test_inputs:
                    cap = io.StringIO()
                    handler = logging.StreamHandler(cap)
                    handler.setLevel(logging.WARNING)
                    lg = logging.getLogger(f"backlog_exec_test_{len(pending)}")
                    lg.handlers.clear()
                    lg.addHandler(handler)
                    lg.setLevel(logging.DEBUG)
                    ns = {
                        "is_stream": True,
                        "pending": pending,
                        "logger": lg,
                        "obj": types.SimpleNamespace(rid=f"test-rid-{len(pending)}"),
                        "len": len,
                    }
                    try:
                        exec(block, ns)
                    except Exception:
                        pass  # restructured code may reference unavailable vars
                    output = cap.getvalue().strip()
                    assert not output, (
                        f"WARNING-level log emitted with {len(pending)} pending chunks: {output!r}"
                    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_async_generator_preserved():
    """_wait_one_response must remain an async generator with drain loop and event handling."""
    # AST-only because: torch, vllm, triton deps prevent importing tokenizer_manager
    method, _ = _get_method_node()

    assert isinstance(method, ast.AsyncFunctionDef), (
        "_wait_one_response must be an async function"
    )

    yields = sum(1 for n in ast.walk(method) if isinstance(n, ast.Yield))
    assert yields >= 2, f"Expected >=2 yields (async generator), found {yields}"

    for_loops = sum(1 for n in ast.walk(method) if isinstance(n, ast.For))
    assert for_loops >= 1, "Drain loop (for-loop over pending chunks) is missing"

    has_event = any(
        isinstance(n, ast.Attribute) and n.attr in ("wait", "clear")
        for n in ast.walk(method)
    )
    assert has_event, "Event coordination (.wait/.clear) is missing"


# [static] pass_to_pass
def test_method_not_stubbed():
    """_wait_one_response must have a substantial body with real logic."""
    # AST-only because: torch, vllm, triton deps prevent importing tokenizer_manager
    method, _ = _get_method_node()

    line_count = method.end_lineno - method.lineno
    assert line_count >= 25, f"Method is only {line_count} lines (expected >=25)"

    meaningful = sum(
        1
        for n in ast.walk(method)
        if isinstance(
            n,
            (ast.Assign, ast.AugAssign, ast.If, ast.For, ast.While,
             ast.Try, ast.Yield, ast.Delete, ast.Raise),
        )
    )
    assert meaningful >= 15, f"Only {meaningful} meaningful statements (expected >=15)"

    has_try = any(isinstance(n, ast.Try) for n in ast.walk(method))
    assert has_try, "Error handling (try/except) is missing"

    has_finished = any(
        (isinstance(n, ast.Name) and n.id == "finished")
        or (isinstance(n, ast.Attribute) and n.attr == "finished")
        for n in ast.walk(method)
    )
    assert has_finished, "Completion detection ('finished' reference) is missing"
