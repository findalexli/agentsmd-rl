"""
Task: areal-data-proxy-batch-endpoint
Repo: inclusionAI/AReaL @ 0405b5c30c815044d858f15d04d2033c9a3d7760
PR:   1105

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: app.py transitively imports torch/transformers/peft which are unavailable
in the CPU-only test container. We AST-extract the POST /data/batch handler,
exec it inside a minimal FastAPI app with mocked deps, and test real HTTP
behavior via httpx AsyncClient.
"""

import ast
import asyncio
import json
import logging
import re
import textwrap
from pathlib import Path

import pytest

APP_FILE = Path(
    "/workspace/AReaL/areal/experimental/inference_service/data_proxy/app.py"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_handler_and_build_app():
    """AST-extract the POST /data/batch handler and mount it on a test app.

    # AST-only because: app.py transitively imports torch, transformers, peft,
    # and other GPU-oriented packages unavailable in the CPU-only container.
    # We extract just the handler function, exec it with mocked deps, then
    # test it behaviorally via real HTTP requests.
    """
    import fastapi
    import httpx
    import orjson
    from fastapi import HTTPException, Request
    from fastapi.responses import JSONResponse, StreamingResponse
    from fastapi.responses import Response as RawResponse
    from httpx import ASGITransport

    source = APP_FILE.read_text()
    tree = ast.parse(source)

    handler_node = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                if (
                    isinstance(dec, ast.Call)
                    and isinstance(dec.func, ast.Attribute)
                    and dec.func.attr == "post"
                    and dec.args
                    and isinstance(dec.args[0], ast.Constant)
                    and dec.args[0].value == "/data/batch"
                ):
                    handler_node = node
                    break
            if handler_node:
                break

    assert handler_node is not None, "POST /data/batch handler not found in app.py"

    lines = source.splitlines(keepends=True)
    func_source = textwrap.dedent(
        "".join(lines[handler_node.lineno - 1 : handler_node.end_lineno])
    )

    app = fastapi.FastAPI()

    class MockStorage:
        def __init__(self):
            self.data = {
                "shard_a": [1, 2, 3],
                "shard_b": [4, 5, 6],
                "shard_c": {"key": "value"},
                "shard_d": [10, 20],
                "shard_e": "scalar_string",
            }

        def fetch(self, sid):
            if sid in self.data:
                return self.data[sid]
            raise KeyError(sid)

    ns = {
        "Request": Request,
        "HTTPException": HTTPException,
        "JSONResponse": JSONResponse,
        "StreamingResponse": StreamingResponse,
        "RawResponse": RawResponse,
        "Response": fastapi.Response,
        "rtensor_storage": MockStorage(),
        "serialize_value": lambda v: v,
        "orjson": orjson,
        "json": json,
        "logger": logging.getLogger("test_batch"),
        "app": app,
        "__builtins__": __builtins__,
    }

    exec('@app.post("/data/batch")\n' + func_source, ns)

    # Register parametric routes AFTER batch (correct ordering in test app)
    @app.put("/data/{shard_id}")
    async def store_shard(shard_id: str):
        return {"status": "ok"}

    @app.get("/data/{shard_id}")
    async def get_shard(shard_id: str):
        return {"status": "ok"}

    return app


def _run_async(coro):
    """Run an async coroutine synchronously."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """app.py must be valid Python."""
    import py_compile

    py_compile.compile(str(APP_FILE), doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_batch_valid_request():
    """POST /data/batch with valid shard_ids returns 200 and correct payload."""
    import httpx
    import orjson
    from httpx import ASGITransport

    app = _extract_handler_and_build_app()

    async def _test():
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            # Test with 2 shards
            resp = await client.post(
                "/data/batch", json={"shard_ids": ["shard_a", "shard_b"]}
            )
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            body = orjson.loads(resp.content)
            assert isinstance(body, list), f"Expected list response, got {type(body)}"
            assert len(body) == 2, f"Expected 2 items, got {len(body)}"
            assert body[0] == [1, 2, 3], f"First shard data mismatch: {body[0]}"
            assert body[1] == [4, 5, 6], f"Second shard data mismatch: {body[1]}"

            # Test with 3 different shards to verify ordering
            resp2 = await client.post(
                "/data/batch", json={"shard_ids": ["shard_c", "shard_a", "shard_d"]}
            )
            assert resp2.status_code == 200
            body2 = orjson.loads(resp2.content)
            assert len(body2) == 3
            assert body2[0] == {"key": "value"}
            assert body2[1] == [1, 2, 3]
            assert body2[2] == [10, 20]

    _run_async(_test())


# [pr_diff] fail_to_pass
def test_batch_single_shard():
    """POST /data/batch with a single shard_id returns a list of one item."""
    import httpx
    import orjson
    from httpx import ASGITransport

    app = _extract_handler_and_build_app()

    async def _test():
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            resp = await client.post(
                "/data/batch", json={"shard_ids": ["shard_c"]}
            )
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
            body = orjson.loads(resp.content)
            assert isinstance(body, list) and len(body) == 1
            assert body[0] == {"key": "value"}, f"Unexpected payload: {body[0]}"

            # Also test with a different shard to avoid hardcoding
            resp2 = await client.post(
                "/data/batch", json={"shard_ids": ["shard_e"]}
            )
            assert resp2.status_code == 200
            body2 = orjson.loads(resp2.content)
            assert len(body2) == 1
            assert body2[0] == "scalar_string"

    _run_async(_test())


# [pr_diff] fail_to_pass
def test_batch_missing_shard_error():
    """POST /data/batch with a nonexistent shard returns an error status."""
    import httpx
    from httpx import ASGITransport

    app = _extract_handler_and_build_app()

    async def _test():
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            # Single missing shard
            resp = await client.post(
                "/data/batch", json={"shard_ids": ["nonexistent_xyz_123"]}
            )
            assert resp.status_code != 200, (
                f"Missing shard should not return 200, got {resp.status_code}"
            )
            assert resp.status_code in (400, 404, 422, 500), (
                f"Expected error status, got {resp.status_code}"
            )

            # Mix of valid and missing — should still error
            resp2 = await client.post(
                "/data/batch", json={"shard_ids": ["shard_a", "does_not_exist"]}
            )
            assert resp2.status_code != 200, (
                "Mix with missing shard should not return 200"
            )

    _run_async(_test())


# [pr_diff] fail_to_pass
def test_batch_invalid_input_rejected():
    """POST /data/batch with non-list shard_ids is rejected with 400 or 422."""
    import httpx
    from httpx import ASGITransport

    app = _extract_handler_and_build_app()

    async def _test():
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            # String instead of list
            resp = await client.post(
                "/data/batch", json={"shard_ids": "not_a_list"}
            )
            assert resp.status_code in (400, 422), (
                f"Expected 400/422 for string input, got {resp.status_code}"
            )

            # Integer instead of list
            resp2 = await client.post(
                "/data/batch", json={"shard_ids": 42}
            )
            assert resp2.status_code in (400, 422), (
                f"Expected 400/422 for integer input, got {resp2.status_code}"
            )

            # List of non-strings
            resp3 = await client.post(
                "/data/batch", json={"shard_ids": [1, 2, 3]}
            )
            assert resp3.status_code in (400, 422), (
                f"Expected 400/422 for non-string list, got {resp3.status_code}"
            )

    _run_async(_test())


# [pr_diff] fail_to_pass
def test_batch_empty_shard_ids():
    """POST /data/batch with empty shard_ids list returns 200 with empty result."""
    import httpx
    import orjson
    from httpx import ASGITransport

    app = _extract_handler_and_build_app()

    async def _test():
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            resp = await client.post(
                "/data/batch", json={"shard_ids": []}
            )
            assert resp.status_code == 200, (
                f"Empty shard list should return 200, got {resp.status_code}"
            )
            body = orjson.loads(resp.content)
            assert isinstance(body, list), f"Expected list, got {type(body)}"
            assert len(body) == 0, f"Expected empty list, got {len(body)} items"

    _run_async(_test())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — route ordering
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_batch_route_before_param_route():
    """/data/batch must be declared before /data/{shard_id} in app.py.

    FastAPI matches routes in declaration order; if the parametric route comes
    first, POST /data/batch will be swallowed by /data/{shard_id}.
    # AST-only because: checking source-level declaration order (not runtime behavior)
    """
    source = APP_FILE.read_text()
    tree = ast.parse(source)

    batch_line = None
    param_line = None

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                if (
                    isinstance(dec, ast.Call)
                    and isinstance(dec.func, ast.Attribute)
                    and dec.args
                    and isinstance(dec.args[0], ast.Constant)
                ):
                    path = dec.args[0].value
                    method = dec.func.attr
                    if path == "/data/batch" and method == "post":
                        batch_line = node.lineno
                    elif "{shard_id}" in str(path) and param_line is None:
                        param_line = node.lineno

    assert batch_line is not None, "POST /data/batch route not found"
    if param_line is not None:
        assert batch_line < param_line, (
            f"/data/batch (L{batch_line}) must come before "
            f"/data/{{shard_id}} (L{param_line})"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_existing_routes_preserved():
    """Existing PUT/GET/DELETE data routes must still be registered.
    # AST-only because: checking route registration across full module (can't import)
    """
    source = APP_FILE.read_text()
    tree = ast.parse(source)

    routes = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                if (
                    isinstance(dec, ast.Call)
                    and isinstance(dec.func, ast.Attribute)
                    and dec.args
                    and isinstance(dec.args[0], ast.Constant)
                ):
                    routes.add((dec.func.attr, dec.args[0].value))

    required = [
        ("put", "/data/{shard_id}"),
        ("get", "/data/{shard_id}"),
        ("delete", "/data/clear"),
    ]
    for method, path in required:
        assert (method, path) in routes, f"Missing route: {method.upper()} {path}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """POST /data/batch handler must have meaningful logic, not just pass/return.
    # AST-only because: structural check for stub detection
    """
    source = APP_FILE.read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                if (
                    isinstance(dec, ast.Call)
                    and isinstance(dec.func, ast.Attribute)
                    and dec.func.attr == "post"
                    and dec.args
                    and isinstance(dec.args[0], ast.Constant)
                    and dec.args[0].value == "/data/batch"
                ):
                    body_stmts = [
                        s
                        for s in ast.walk(node)
                        if isinstance(s, ast.stmt)
                        and not isinstance(s, (ast.Pass, ast.Expr))
                    ]
                    assert len(body_stmts) >= 5, (
                        f"Handler body too small ({len(body_stmts)} stmts) — likely a stub"
                    )
                    return
    assert False, "POST /data/batch handler not found"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:30 @ 0405b5c
def test_no_wildcard_imports():
    """No wildcard imports in app.py (AGENTS.md hard rule)."""
    source = APP_FILE.read_text()
    wildcard = re.findall(r"^\s*from\s+\S+\s+import\s+\*", source, re.MULTILINE)
    assert not wildcard, f"Wildcard imports found: {wildcard}"


# [agent_config] pass_to_pass — AGENTS.md:31 @ 0405b5c
def test_no_hardcoded_endpoints():
    """No hardcoded host:port endpoints in app.py (AGENTS.md hard rule)."""
    source = APP_FILE.read_text()
    # Strip comments before checking
    lines = [l for l in source.splitlines() if not l.strip().startswith("#")]
    code = "\n".join(lines)
    matches = re.findall(r"(?:localhost|127\.0\.0\.1|0\.0\.0\.0):\d+", code)
    assert not matches, f"Hardcoded endpoints found: {matches}"


# [agent_config] pass_to_pass — AGENTS.md:90-92 @ 0405b5c
def test_no_print_statements():
    """No print() calls in app.py — must use areal.utils.logging (AGENTS.md rule)."""
    source = APP_FILE.read_text()
    tree = ast.parse(source)

    prints_found = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "print"
        ):
            prints_found.append(f"line {node.lineno}")

    assert not prints_found, (
        f"print() calls found at {', '.join(prints_found)}. "
        "Use areal.utils.logging.getLogger() instead."
    )
